from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


# -------- BUILD EMBEDDINGS --------
def embed_text(text):
    return model.encode([text])[0]


# -------- SPEC SIGNAL DESCRIPTIONS --------
def build_spec_descriptions(kg):
    """
    Create simple descriptions for spec signals
    """
    descriptions = {}

    for edge in kg["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        rel = edge.get("relation", "depends")

        if tgt not in descriptions:
            descriptions[tgt] = []

        descriptions[tgt].append(f"{src} {rel} {tgt}")

    # join sentences
    return {
        k: " ".join(v)
        for k, v in descriptions.items()
    }


# -------- RTL SIGNAL DESCRIPTIONS --------
def build_rtl_descriptions(rtl_signals):
    """
    Very simple for now (can improve later)
    """
    return {
        s: s.replace("_", " ")
        for s in rtl_signals
    }


# -------- SEMANTIC MATCHING --------
def map_spec_to_rtl_semantic(kg, rtl_signals, threshold=0.5):

    spec_desc = build_spec_descriptions(kg)
    rtl_desc = build_rtl_descriptions(rtl_signals)

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

        if best_score > threshold:
            mapping[spec_sig] = best_match

    return mapping