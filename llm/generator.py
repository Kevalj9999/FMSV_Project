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

Your task is to generate VALID SystemVerilog Assertions (SVA).

-----------------------------------
STRICT RULES (MANDATORY)
-----------------------------------

1. Output ONLY valid SystemVerilog (NO explanation)
2. Use proper syntax:
   property ... endproperty
   assert property (...)

3. Use ONLY signals present in context or dependencies
4. DO NOT invent signals like:
   - some_condition
   - enable_signal
   - expected_value

5. DO NOT chain implications:
   ❌ a |-> b |-> c
   ✅ a |-> (b && c)

6. DO NOT assume increment/decrement unless clearly implied
   (only for count/ptr type signals)

7. Prefer SAFE assertions:
   - enable conditions
   - stability (!en -> no change)
   - valid/ready relationships
   - dependency checks

8. If unsure → DO NOT generate that assertion

-----------------------------------
TARGET
-----------------------------------
{target}

-----------------------------------
DEPENDENCIES (SPEC GRAPH)
-----------------------------------
{relations}

-----------------------------------
DEPENDENCY PATHS
-----------------------------------
{path_text}

-----------------------------------
RTL CONTEXT
-----------------------------------
{context}

-----------------------------------
OUTPUT REQUIREMENTS
-----------------------------------

Generate 3 to 5 HIGH-QUALITY assertions.

Each assertion must:
- Be logically correct
- Be synthesizable SVA style
- Use @(posedge clk) disable iff (reset)

Focus on:
- enable → behavior
- dependency → implication
- no-change conditions

DO NOT generate weak or generic assertions.
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