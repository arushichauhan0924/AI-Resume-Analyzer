import csv
import re
from pathlib import Path

from src.preprocessing.text_cleaner import clean_text

# Root folder / data / skills_list.csv
SKILLS_PATH = Path(__file__).resolve().parents[2] / "data" / "skills_list.csv"


def load_skills() -> tuple[dict, dict]:
    """CSV se do dictionary banata hai: alias -> skill, aur skill -> category."""
    alias_to_skill = {}
    skill_to_category = {}

    with open(SKILLS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            skill = row["skill"].strip().lower()
            skill_to_category[skill] = row["category"].strip()
            alias_to_skill[skill] = skill
            for alias in (row["aliases"] or "").split("|"):
                if alias.strip():
                    alias_to_skill[alias.strip().lower()] = skill

    return alias_to_skill, skill_to_category


ALIAS_TO_SKILL, SKILL_TO_CATEGORY = load_skills()


def extract_skills(text: str) -> dict:
    """Text me se skills dhundta hai. Output: {skills: [...], by_category: {...}}."""
    text = clean_text(text)
    found = set()
    used_spans = []

    # Lambe naam pehle, taaki "java script" ke time "java" alag se na pakda jaye
    for alias in sorted(ALIAS_TO_SKILL, key=len, reverse=True):
        pattern = r"(?<![a-z0-9+#.])" + re.escape(alias) + r"(?![a-z0-9+#])"
        for m in re.finditer(pattern, text):
            start, end = m.span()
            if any(start < e and end > s for s, e in used_spans):
                continue  # ye hissa pehle hi kisi lambe match me aa chuka hai
            used_spans.append((start, end))
            found.add(ALIAS_TO_SKILL[alias])

    by_category = {}
    for skill in sorted(found):
        by_category.setdefault(SKILL_TO_CATEGORY[skill], []).append(skill)

    return {"skills": sorted(found), "by_category": by_category}