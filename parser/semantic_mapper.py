from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load once (global)
model = SentenceTransformer("all-MiniLM-L6-v2")


# -------- EMBEDDING --------
def embed_text(text):
    return model.encode([text])[0]


# -------- TOKEN MATCH (CRITICAL FIX) --------
def token_overlap(a, b):
    tokens_a = set(a.split("_"))
    tokens_b = set(b.split("_"))
    return len(tokens_a & tokens_b)


def is_safe_mapping(spec_sig, rtl_sig, min_overlap=1):
    return token_overlap(spec_sig, rtl_sig) >= min_overlap


# -------- SPEC DESCRIPTIONS --------
def build_spec_descriptions(kg):
    descriptions = {}

    for edge in kg["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        rel = edge.get("relation", "depends")

        if tgt not in descriptions:
            descriptions[tgt] = []

        descriptions[tgt].append(f"{src} {rel} {tgt}")

    return {
        k: " ".join(v)
        for k, v in descriptions.items()
    }


# -------- RTL DESCRIPTIONS --------
def build_rtl_descriptions(rtl_signals):
    return {
        s: s.replace("_", " ")
        for s in rtl_signals
    }


# -------- MAIN MAPPING --------
def map_spec_to_rtl_semantic(kg, rtl_signals, threshold=0.75):
    """
    Improved semantic mapping with:
    - strict similarity threshold
    - token validation
    - safe fallback
    """

    spec_desc = build_spec_descriptions(kg)
    rtl_desc = build_rtl_descriptions(rtl_signals)

    # Precompute RTL embeddings
    rtl_embeddings = {
        s: embed_text(desc)
        for s, desc in rtl_desc.items()
    }

    mapping = {}

    for spec_sig, desc in spec_desc.items():
        spec_vec = embed_text(desc)

        best_match = None
        best_score = 0

        for rtl_sig, rtl_vec in rtl_embeddings.items():
            score = cosine_similarity([spec_vec], [rtl_vec])[0][0]

            if score > best_score:
                best_score = score
                best_match = rtl_sig

        # -------- STRICT FILTERING --------
        if best_match:
            overlap = token_overlap(spec_sig, best_match)

            if best_score >= threshold and overlap >= 1:
                mapping[spec_sig] = best_match
            else:
                # ❗ IMPORTANT: keep original (DO NOT MAP)
                mapping[spec_sig] = spec_sig
        else:
            mapping[spec_sig] = spec_sig

    return mapping