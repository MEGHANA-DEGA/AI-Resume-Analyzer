import unittest
from modules.skill_extractor import extract_skills_from_text as extract_skills


def test_extract_python_and_sql():
    text = "I know Python and SQL."

    skills = extract_skills(text)

    assert "python" in skills
    assert "sql" in skills


def test_unknown_skills():
    text = "I enjoy reading books."

    skills = extract_skills(text)

    assert skills == []


def test_case_insensitive():
    text = "PYTHON and SQL"

    skills = extract_skills(text)

    assert "python" in skills
    assert "sql" in skills

