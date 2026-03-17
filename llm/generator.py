import os
from openai import OpenAI, api_key
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = os.getenv("OPENROUTER_API_KEY"),
)


def generate_assertions(context, spec, signals):
    
    prompt = f"""
    You are a hardware verification expert.

    STRICT RULES:
    - Use ONLY signals listed below
    - Use standard assertion style like: assert property (!(full && empty))
    - Avoid writing (condition) |-> 0
    - Do NOT invent signals like rst_n, wr_en
    - Do NOT use modulo (%) operations
    - Reset signal is: reset
    - Avoid trivial assertions like count >= 0

    Available Signals:
    {signals}

    RTL Context:
    {context}

    Specification:
    {spec}

    Task:
    Generate SystemVerilog assertions.

    Focus on:
    - overflow (count <= DEPTH)
    - underflow (count >= 0)
    - full/empty correctness
    - read/write safety

    Output ONLY assertions.
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