def score_label(score: float, high: float = 0.40, medium: float = 0.20) -> str:
    """Score (0-1) ko Low / Medium / High label deta hai."""
    if score >= high:
        return "High"
    if score >= medium:
        return "Medium"
    return "Low"