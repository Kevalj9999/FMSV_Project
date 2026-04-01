import json
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

import re

def clean_graph(graph):
    cleaned = {}

    for target, deps in graph.items():
        valid_deps = []

        for d in deps:
            # ❌ Remove self loops only
            if d == target:
                continue

            # ❌ Remove obvious wrong patterns
            if ("ptr" in d and "count" in target):
                continue

            if ("count" in d and "ptr" in target):
                continue

            valid_deps.append(d)

        cleaned[target] = list(set(valid_deps))


    return cleaned

def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        # Extract JSON inside ```json ... ```
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return {"nodes": [], "edges": []}

# -------- STEP 1: chunk spec --------
def chunk_text(text, size=1200):
    chunks = []
    start = 0

    while start < len(text):
        chunks.append(text[start:start + size])
        start += size

    return chunks


# -------- STEP 2: LLM extraction --------
def extract_kg_from_chunk(chunk):
    prompt = f"""
You are a hardware verification expert.

Extract ONLY CAUSAL signal relationships from this specification.

STRICT RULES:
- Output ONLY valid JSON
- No explanation
- No markdown
- No extra text
- ONLY include relationships where source DIRECTLY influences target
- DO NOT create bidirectional edges
- DO NOT guess relationships
- DO NOT include symmetric relations

IMPORTANT:
- Control signals (wr_en, rd_en) affect state signals (count, ptr)
- State signals affect status signals (full, empty)
- Pointers affect memory/data

Correct examples:
wr_en → count (increment)
rd_en → count (decrement)
count → full (equals)
rd_ptr → data_out (depends)

WRONG examples (DO NOT DO):
count → wr_ptr
count → rd_ptr

Format:
{{
  "nodes": ["signal1", "signal2"],
  "edges": [
    {{
      "source": "signalA",
      "target": "signalB",
      "relation": "increment/decrement/reset/depends/equals"
    }}
  ]
}}

Specification:
{chunk}
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return safe_json_parse(content)
    except:
        return {"nodes": [], "edges": []}


# -------- STEP 3: merge partial KGs --------
def merge_kgs(kgs):
    nodes = set()
    edges = []

    for kg in kgs:
        nodes.update(kg.get("nodes", []))
        edges.extend(kg.get("edges", []))

    return {
        "nodes": list(nodes),
        "edges": edges
    }


# -------- STEP 4: MAIN FUNCTION --------
def build_spec_kg(spec_text):
    chunks = chunk_text(spec_text)

    all_kgs = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        kg = extract_kg_from_chunk(chunk)
        all_kgs.append(kg)

    return merge_kgs(all_kgs)


# -------- STEP 5: convert to your graph format --------
def kg_to_graph(kg):
    graph = {}

    for edge in kg["edges"]:
        target = edge["target"]
        source = edge["source"]

        if target not in graph:
            graph[target] = []

        graph[target].append(source)

    return graph