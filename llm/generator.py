from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


# -------- FORMAT HELPERS --------

def format_relations(graph, target):
    deps = graph.get(target, [])
    return "\n".join([f"{d} -> {target}" for d in deps])


def format_paths(paths):
    lines = []
    for p in paths[:5]:
        lines.append(" -> ".join(p))
    return "\n".join(lines)


# -------- MAIN GENERATOR --------

def generate_assertions(context, graph, paths, target):
    relations = format_relations(graph, target)
    path_text = format_paths(paths)

    prompt = f"""
You are a hardware formal verification expert.

Generate VALID SystemVerilog Assertions (SVA) using ONLY the given dependency information.

========================================
STRICT RULES (MANDATORY)
========================================

1. Output ONLY SystemVerilog assertions
   - NO explanation
   - NO markdown

2. Use ONLY signals explicitly provided
   - DO NOT invent signals
   - DO NOT use placeholders like:
     some_condition, enable_signal, expected_value

3. Follow correct syntax:
   property <name>;
     @(posedge clk) disable iff (reset)
     <expression>;
   endproperty
   assert property (<name>);

4. DO NOT assume arithmetic behavior
   - NO +1 / -1 unless signal name clearly implies (count, ptr)

5. DO NOT chain implications
   ❌ a |-> b |-> c
   ✅ a |-> (b && c)

6. DO NOT guess missing logic
   - If relation is unclear → SKIP

7. RHS of implication MUST be a valid boolean expression:
   - For data/address signals:
     use (signal != $past(signal))

   - For enable signals:
     use (signal != 0)

8. NEVER generate:
   - signal == signal
   - signal != signal

9. ALWAYS use $past() for state comparison
10. Assertion Templates (MANDATORY):

For dependency A -> B:

- If B is a data/address signal:
  A |-> (B != $past(B))

- If B is an enable/valid signal:
  A |-> (B != 0)

For stability:
  !A |-> (B == $past(B))

For multiple dependencies:
  (A && C) |-> (B != $past(B))

11. Always prefer $past() comparisons for non-boolean signals.

12. Avoid weak assertions like:
  B != 0 (unless B is clearly a control signal)

13. Only generate A |-> B if A DIRECTLY controls B.
If unsure, SKIP the assertion.

14. Only generate dependency assertions when the relationship is STRONG and direct.
    If the dependency is indirect or uncertain, SKIP it.

15. Prefer fewer HIGH-QUALITY assertions over many weak ones.

16. If multiple dependencies exist for a target:
    - Prefer combining them using (A && C)

17. Avoid generating the same pattern repeatedly across signals.

18. Only generate A |-> B if A directly controls or enables B.
If relationship is indirect → SKIP.
    
========================================
DEPENDENCY INTERPRETATION
========================================

- "A -> B" means:
  A influences or controls B

- VALID assertion patterns:

  (A) |-> (B changes or holds relation)
  (!A) |-> (B remains stable)

- If multiple dependencies:
  (A && C) |-> B

========================================
TARGET
========================================
{target}

========================================
DEPENDENCIES (GRAPH)
========================================
{relations}

========================================
DEPENDENCY PATHS
========================================
{path_text}

========================================
OUTPUT REQUIREMENTS
========================================

Generate EXACTLY 3 to 5 assertions.

Include ONLY these types:

1. Dependency assertion
   - cause → effect

2. Stability assertion
   - no enable → no change

3. Multi-signal dependency (if available)

DO NOT generate:
- arithmetic updates
- random enable conditions
- unrelated assertions

Only generate assertions that are DIRECTLY supported by dependencies.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=800
        )

        output = response.choices[0].message.content

        # -------- BASIC SANITY CLEAN --------
        if not output or len(output.strip()) < 10:
            return ""
        if "some_" in output or "enable_condition" in output:
            return ""

        return output.strip()

    except Exception as e:
        print(f"❌ LLM Error for {target}: {e}")
        return ""