import pytest

from app.services.job_analyzer import analyze_job_description
from app.services.matching_engine import calculate_match, extract_skills


def test_extracts_supported_skills_without_false_partial_matches() -> None:
    assert extract_skills("Python, FastAPI, PostgreSQL and Docker") == ["Python", "FastAPI", "PostgreSQL", "Docker"]
    assert "SQL" not in extract_skills("NoSQL is used")


def test_matching_is_deterministic_and_lists_missing_skills() -> None:
    result = calculate_match(
        "I built APIs with Python, FastAPI and PostgreSQL. English language. Bachelor's degree.",
        "Required skills: Python, FastAPI, PostgreSQL, Docker. English bachelor's degree.",
    )
    assert result.matched_skills == ["Python", "FastAPI", "PostgreSQL"]
    assert result.missing_skills == ["Docker"]
    assert result.breakdown["skills"] == 75
    assert result.score == calculate_match(
        "I built APIs with Python, FastAPI and PostgreSQL. English language. Bachelor's degree.",
        "Required skills: Python, FastAPI, PostgreSQL, Docker. English bachelor's degree.",
    ).score
    assert 0 <= result.score <= 100


def test_custom_weights_must_sum_to_one() -> None:
    with pytest.raises(ValueError):
        calculate_match("Python", "Python", weights={"skills": .9, "experience": .1, "education": .1, "languages": .1})


def test_job_analyzer_requires_useful_input_and_returns_structured_data() -> None:
    with pytest.raises(ValueError):
        analyze_job_description("too short")
    result = analyze_job_description("Junior Backend Engineer\nRequirements: Python, FastAPI, PostgreSQL. 2 years of experience. English.\nResponsibilities: Develop REST APIs")
    assert result.extraction_method == "local_keyword_baseline"
    assert "Python" in result.technologies
    assert result.years_experience == 2
