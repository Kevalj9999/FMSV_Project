import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def generate_assertions(context, spec, signals):

    prompt = f"""
You are an expert in SystemVerilog Assertions (SVA) and RTL verification.

Your task is to generate ONLY syntactically correct, tool-ready SystemVerilog assertions STRICTLY based on the given RTL.

----------------------------------------
STRICT RULES (MANDATORY)
----------------------------------------

1. ONLY use signals from this list:
{signals}

2. DO NOT invent any signals, states, constants, or logic.

3. DO NOT assume fixed cycle delays (NO ##5, ##10, etc.)
   → Use explicit RTL conditions (e.g., counter == N)

4. ALL behavior MUST come directly from RTL.

5. DO NOT skip any important behavior:
   - reset behavior
   - register updates
   - counter transitions
   - control conditions
   - safety constraints

6. DO NOT generate tautological assertions like:
  (x == 1) |=> (x == 1)
  (x == 0) |=> (x == 0)s

7. DO NOT infer relationships not explicitly present in RTL
8. NEVER assume behavior based on intuition (e.g., empty → pointer reset)
9. ONLY generate assertions for signals present in the CURRENT context.
10. DO NOT generate assertions for unrelated signals.
11. DO NOT infer behavior not explicitly written in RTL.
12. DO NOT generate inequality-based behavior (like !=) unless explicitly present.
13. Avoid redundant assertions (same logic written differently).
14. Each assertion must directly map to a line in RTL.
15. ONLY generate assertions directly related to the current target signal.
16. DO NOT generate assertions for unrelated registers.
17. If the target is an output (like full/empty), focus on its defining logic.
18. If the target is a counter/pointer, focus on its update behavior.
19. DO NOT generate tautologies (always true conditions).
20. DO NOT generate assertions that simplify to constants.
21. Each assertion must enforce a meaningful design constraint.
22. Generate ONLY assertions that directly define the target signal behavior.
23. DO NOT generate assertions for other signals in the same context.
24. Avoid repeating reset assertions across multiple targets.
25. Prefer simple and minimal conditions over complex boolean expressions.
26. When asserting outputs like full/empty:
    - Prefer direct equivalence:
        (count == DEPTH) |-> (full == 1)

----------------------------------------
TIMING RULES (CRITICAL)
----------------------------------------

1. Use correct implication operators:

   - |->  : SAME cycle (combinational check)
   - |=>  : NEXT cycle (sequential register update)

2. ALWAYS use |=> for:
   - register updates
   - counters (increment/decrement)
   - pointer updates

3. NEVER use |-> for sequential logic.

----------------------------------------
RESET RULES (VERY IMPORTANT)
----------------------------------------

1. For reset assertions:
   - DO NOT use "disable iff"
   - Use:
        reset |=> (signal == value)

2. For normal assertions:
   - ALWAYS use:
        disable iff (reset)

3. NEVER combine:
        disable iff (reset) + reset condition

----------------------------------------
BOOLEAN RULES
----------------------------------------

1. ALWAYS use explicit comparisons:
   (empty == 1)
   (full == 0)

2. NEVER write:
   reset |=> empty

3. ALWAYS write:
   reset |=> (empty == 1)

----------------------------------------
REGISTER / COUNTER RULES
----------------------------------------

1. Use $past() for next-state behavior:
   Example:
        (wr_en) |=> (ptr == $past(ptr) + 1)

2. For counters with multiple conditions:
   MUST cover ALL cases:
   - increment
   - decrement
   - no change

3. Example:
   (wr && !rd) |=> count + 1  
   (rd && !wr) |=> count - 1  
   (wr && rd)  |=> count unchanged  

----------------------------------------
MEMORY RULES (CRITICAL)
----------------------------------------

1. NEVER generate assertions using memory arrays:
   - NO mem[...]
   - NO mem[$past(...)]

2. If behavior depends on memory:
   → SKIP that assertion

3. NEVER use memory signals (mem, array access)
- SKIP data-path assertions involving memory

----------------------------------------
SIMPLICITY RULES
----------------------------------------

1. Prefer simple and deterministic assertions.

2. DO NOT generate overly complex or nested logic.

3. DO NOT generate redundant assertions.

----------------------------------------
SYNTAX RULES (MANDATORY)
----------------------------------------

1. EVERY assertion MUST follow EXACT format:

   assert property (@(posedge clk) <property>);

2. NEVER output raw expressions like:
   reset |=> (count == 0)

3. ALWAYS wrap them like:
   assert property (@(posedge clk) reset |=> (count == 0));

4. Each assertion MUST be on its own line.

5. NO comments
6. NO explanation
7. NO markdown

----------------------------------------
RTL CONTEXT
----------------------------------------
{context}

----------------------------------------
SPECIFICATION (REFERENCE ONLY)
----------------------------------------
{spec}

----------------------------------------
OUTPUT FORMAT (STRICT)
----------------------------------------

- ONLY SystemVerilog assertions
- NO explanation
- NO comments
- NO markdown
- CLEAN, VALID SVA ONLY

----------------------------------------

Generate assertions now.
"""

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "RTL Assertion Generator"
        }
    )

    return response.choices[0].message.content

def clean_assertions(assertions):
    cleaned = []

    for line in assertions.split("\n"):
        l = line.strip()

        if not l:
            continue

        # remove invalid implication
        if "|=>" in l and l.startswith("!"):
            continue

        # remove inequality hallucinations
        if "!=" in l:
            continue

        # remove trivial self assertions
        if "== $past(" in l and "+ 0" in l:
            continue

        cleaned.append(l)

    return "\n".join(cleaned)