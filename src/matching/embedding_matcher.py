from functools import lru_cache
from sentence_transformers import SentenceTransformer, util


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def _chunks(text: str, size: int = 150) -> list:
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]


def embedding_score(resume_text: str, jd_text: str) -> float:
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    model = get_model()
    resume_emb = model.encode(_chunks(resume_text), convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    sims = util.cos_sim(jd_emb, resume_emb)[0].tolist()
    top = sorted(sims, reverse=True)[:3]
    return round(max(0.0, sum(top) / len(top)), 4)