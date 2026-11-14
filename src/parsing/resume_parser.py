import re
from src.skills.skill_extractor import extract_skills
from datetime import datetime
SECTION_HEADINGS = {
    "summary": ["summary", "objective", "profile", "about me", "career objective"],
    "skills": ["skills", "technical skills", "key skills", "core competencies", "technologies"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "internship", "internships"],
    "education": ["education", "academic background", "qualifications", "academics"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "courses"],
    "achievements": ["achievements", "awards", "accomplishments"],
}


def detect_heading(line: str):
    """Agar line koi section heading hai to uska naam wapas deta hai, warna None."""
    cleaned = line.strip().lower().rstrip(":")
    for section, keywords in SECTION_HEADINGS.items():
        if cleaned in keywords:
            return section
    return None


def split_into_sections(text: str) -> dict:
    """Resume text ko sections me todta hai. Output: {section_name: text}."""
    sections = {"header": []}
    current = "header"

    for line in text.split("\n"):
        heading = detect_heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
        else:
            sections[current].append(line)

    return {name: "\n".join(lines).strip() for name, lines in sections.items() if lines}
EMAIL_PATTERN = r"[\w\.-]+@[\w\.-]+\.\w+"
PHONE_PATTERN = r"\+?\d[\d\s\-()]{8,}\d"
LINKEDIN_PATTERN = r"linkedin\.com/in/[\w\-]+"
GITHUB_PATTERN = r"github\.com/[\w\-]+"


def extract_contact_info(text: str) -> dict:
    """Resume text se naam, email, phone, linkedin, github nikalta hai."""
    email = re.search(EMAIL_PATTERN, text)
    phone = re.search(PHONE_PATTERN, text)
    linkedin = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    github = re.search(GITHUB_PATTERN, text, re.IGNORECASE)

    # Naam: pehli khaali-nahi line
    name = ""
    for line in text.split("\n"):
        if line.strip():
            name = line.strip()
            break

    return {
        "name": name,
        "email": email.group() if email else "Not found",
        "phone": phone.group().strip() if phone else "Not found",
        "linkedin": linkedin.group() if linkedin else "Not found",
        "github": github.group() if github else "Not found",
    }   
DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e", "m.tech", "mtech", "bca", "mca",
    "b.sc", "bsc", "m.sc", "msc", "bba", "mba",
    "b.com", "bcom", "m.com", "mcom", "phd",
    "bachelor", "master", "diploma", "12th", "10th",
]

YEAR_PATTERN = r"(?:19|20)\d{2}"
CGPA_PATTERN = r"(?:cgpa|gpa)\s*[:\-]?\s*(\d+(?:\.\d+)?)"
PERCENT_PATTERN = r"(\d{2,3}(?:\.\d+)?)\s*%"


def extract_education(education_text: str) -> dict:
    """Education section se degrees, years aur CGPA/percentage nikalta hai."""
    lower = education_text.lower()

    degrees = [d for d in DEGREE_KEYWORDS if d in lower]
    years = sorted(set(re.findall(YEAR_PATTERN, education_text)))
    cgpa = re.findall(CGPA_PATTERN, lower)
    percentages = re.findall(PERCENT_PATTERN, education_text)

    return {
        "degrees": degrees,
        "years": years,
        "cgpa": cgpa,
        "percentages": percentages,
    }
MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DATE_RANGE_PATTERN = (
    r"((?:[A-Za-z]{3,9}\.?\s+)?(?:19|20)\d{2})"
    r"\s*(?:-|–|—|to)\s*"
    r"((?:[A-Za-z]{3,9}\.?\s+)?(?:19|20)\d{2}|present|current|ongoing)"
)


def _parse_date(date_str: str):
    """'Jun 2023' ya '2023' ya 'Present' ko (year, month) me badalta hai."""
    s = date_str.strip().lower().replace(".", "")
    if s in ("present", "current", "ongoing"):
        now = datetime.now()
        return now.year, now.month

    year_match = re.search(r"(?:19|20)\d{2}", s)
    if not year_match:
        return None
    year = int(year_match.group())

    month = 1
    for key, num in MONTHS.items():
        if s.startswith(key):
            month = num
            break
    return year, month


def extract_experience(experience_text: str) -> dict:
    """Experience section se date ranges aur total months nikalta hai."""
    ranges = []
    total_months = 0

    for start_str, end_str in re.findall(DATE_RANGE_PATTERN, experience_text, re.IGNORECASE):
        start = _parse_date(start_str)
        end = _parse_date(end_str)
        if not start or not end:
            continue

        months = (end[0] - start[0]) * 12 + (end[1] - start[1])
        if months < 0:
            continue
        months = max(months, 1)

        ranges.append({"start": start_str.strip(), "end": end_str.strip(), "months": months})
        total_months += months

    return {
        "ranges": ranges,
        "total_months": total_months,
        "total_years": round(total_months / 12, 1),
    }
def parse_resume(text: str) -> dict:
    """Poore resume text ko ek structured dictionary me badalta hai."""
    sections = split_into_sections(text)

    return {
        "contact": extract_contact_info(text),
        "sections": sections,
        "education": extract_education(sections.get("education", "")),
        "experience": extract_experience(sections.get("experience", "")),
        "skills": extract_skills(text),
    }