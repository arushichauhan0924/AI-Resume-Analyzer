def compare_skills(resume_skills: list, jd_skills: list) -> dict:
    """Resume aur JD ki skills compare karta hai."""
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra = sorted(resume_set - jd_set)

    match_percent = round(len(matched) / len(jd_set) * 100, 1) if jd_set else 0.0

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_percent": match_percent,
    }