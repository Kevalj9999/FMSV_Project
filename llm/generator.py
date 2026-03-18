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