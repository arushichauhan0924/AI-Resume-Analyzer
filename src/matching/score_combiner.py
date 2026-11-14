def combine_scores(tfidf: float, emb: float, skill_pct: float) -> dict:
    """Final score: 50% transformer, 20% tfidf, 30% skill match."""
    tfidf_n = min(tfidf / 0.5, 1.0)   # tfidf scores kam aate hain, isliye scale
    emb_n = min(emb / 0.7, 1.0)
    final = 0.5 * emb_n + 0.2 * tfidf_n + 0.3 * (skill_pct / 100)
    final = round(final * 100, 1)
    if final >= 70:
        verdict = "Strong match"
    elif final >= 45:
        verdict = "Moderate match"
    else:
        verdict = "Weak match"
    return {"final": final, "verdict": verdict}