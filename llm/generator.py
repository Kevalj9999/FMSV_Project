from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def format_relations(graph, target):
    rels = []

    deps = graph.get(target, [])

    for d in deps:
        rels.append(f"{d} -> {target}")

    return "\n".join(rels)


def format_paths(paths):
    lines = []

    for p in paths[:5]:
        lines.append(" -> ".join(p))

    return "\n".join(lines)


def generate_assertions(context, graph, paths, target):
    relations = format_relations(graph, target)
    path_text = format_paths(paths)

    prompt = f"""
You are a formal verification expert.

Generate SystemVerilog assertions for the given target signal.

STRICT RULES:
- Output ONLY valid SystemVerilog assertions
- Use property/assert property syntax
- No explanation
- No markdown
- Use posedge clk
- Use $past where needed
- DO NOT generate speculative relationships
- ONLY generate assertions directly supported by RTL logic
- Follow SPEC relationships strictly.
- Use RTL only for signal naming and conditions.
- Do NOT infer behavior from RTL.
- The behavior MUST follow the specification-derived dependencies.
- RTL is only for implementation details like conditions and syntax.
- If there is conflict, prioritize the specification.

TARGET:
{target}

DEPENDENCIES (from spec knowledge graph):
{relations}

DEPENDENCY PATHS:
{path_text}

RTL CONTEXT:
{context}

Generate assertions that:
- Capture increment/decrement behavior
- Capture enable conditions
- Capture dependencies between signals
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )


    output = response.choices[0].message.content

    return output