
import re

SKILLS_LIST = [
    "python",
    "java",
    "javascript",
    "sql",
    "mysql",
    "html",
    "css",
    "react",
    "flask",
    "django",
    "machine learning",
    "excel",
    "power bi",
    "tableau",
    "git",
    "github",
    "communication",
    "teamwork",
    "problem solving",
    "leadership"
]


def clean_text(text):
    """Convert text to lowercase and remove extra spaces."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills_from_text(text):
    """Extract matching skills from resume or job description."""
    text = clean_text(text)

    found_skills = []

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills
