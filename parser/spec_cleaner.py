import fitz  # PyMuPDF
from openai import OpenAI
import os
from dotenv import load_dotenv

def get_client():
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("❌ OPENROUTER_API_KEY not found")

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
import re

client = get_client()

# -------- STEP 1: EXTRACT TEXT --------
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text()

        # skip empty pages
        if text.strip():
            pages.append(text)

    return pages


# -------- STEP 2: CHUNKING --------
def chunk_text(pages, max_chars=8000):
    chunks = []
    current = ""

    for page in pages:
        if len(current) + len(page) < max_chars:
            current += page + "\n"
        else:
            chunks.append(current)
            current = page + "\n"

    if current:
        chunks.append(current)

    return chunks


# -------- STEP 3: CLEAN EACH CHUNK --------
def clean_chunk(chunk):
    prompt = f"""
You are a hardware specification analyzer.

Convert the following documentation into a CLEAN structured hardware spec.

REMOVE:
- revision history
- tables
- benchmark data
- tool descriptions
- long explanations

KEEP ONLY:
- signals
- behavior
- dependencies between signals
- module descriptions

OUTPUT FORMAT STRICTLY:

Signals:
- signal1
- signal2

Behavior:
- description

Dependencies:
- A depends on B
- C depends on D

TEXT:
{chunk}
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


# -------- STEP 4: MERGE CLEANED CHUNKS --------
def merge_cleaned_chunks(cleaned_chunks):
    final_spec = "\n\n".join(cleaned_chunks)

    # optional: deduplicate lines
    lines = final_spec.split("\n")
    unique_lines = list(dict.fromkeys(line.strip() for line in lines if line.strip()))

    return "\n".join(unique_lines)


# -------- MAIN FUNCTION --------
def build_clean_spec(pdf_path, output_file="spec/spec.txt"):
    print("Extracting PDF...")
    pages = extract_pdf_text(pdf_path)

    print(f"Total pages extracted: {len(pages)}")

    print("Chunking...")
    chunks = chunk_text(pages)

    print(f"Total chunks: {len(chunks)}")

    cleaned_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"Cleaning chunk {i+1}/{len(chunks)}...")
        cleaned = clean_chunk(chunk)
        cleaned_chunks.append(cleaned)

    print("Merging cleaned chunks...")
    final_spec = merge_cleaned_chunks(cleaned_chunks)

    with open(output_file, "w") as f:
        f.write(final_spec)

    print(f"✅ Clean spec saved to {output_file}")

    return final_spec