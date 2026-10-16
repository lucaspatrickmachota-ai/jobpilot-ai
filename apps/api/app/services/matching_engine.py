"""Deterministic baseline matching; no LLM-generated score is used."""
from dataclasses import dataclass
import re

from app.core.config import get_settings

SKILL_TAXONOMY: dict[str, tuple[str, ...]] = {
    "Python": ("python",), "FastAPI": ("fastapi",), "Django": ("django",),
    "Flask": ("flask",), "JavaScript": ("javascript", "js"), "TypeScript": ("typescript",),
    "React": ("react",), "Next.js": ("next.js", "nextjs"), "SQL": ("sql",),
    "PostgreSQL": ("postgresql", "postgres"), "MySQL": ("mysql",), "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"), "AWS": ("aws", "amazon web services"),
    "Azure": ("azure",), "GCP": ("google cloud", "gcp"), "Git": ("git",),
    "REST APIs": ("rest api", "restful api", "rest apis"), "Linux": ("linux",),
    "Machine Learning": ("machine learning", "ml"), "LLM": ("llm", "large language model"),
    "RAG": ("rag", "retrieval-augmented generation"), "HTML": ("html",), "CSS": ("css",),
    "CI/CD": ("ci/cd", "continuous integration", "continuous delivery"),
    "pytest": ("pytest",), "Pydantic": ("pydantic",), "SQLAlchemy": ("sqlalchemy",),
}


@dataclass(frozen=True)
class MatchResult:
    score: int
    breakdown: dict[str, int]
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


def extract_skills(text: str) -> list[str]:
    normalized = text.casefold()
    found = []
    for skill, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            pattern = r"(?<![\w+#])" + re.escape(alias.casefold()) + r"(?![\w+#])"
            if re.search(pattern, normalized):
                found.append(skill)
                break
    return found


def calculate_match(candidate_text: str, job_text: str, *, weights: dict[str, float] | None = None) -> MatchResult:
    """Return reproducible score with skills 50%, experience 30%, education 10%, languages 10%."""
    settings = get_settings()
    weights = weights or {"skills": settings.match_weight_skills, "experience": settings.match_weight_experience,
                          "education": settings.match_weight_education, "languages": settings.match_weight_languages}
    if set(weights) != {"skills", "experience", "education", "languages"} or any(v < 0 for v in weights.values()) or abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("Weights must contain skills, experience, education, languages and sum to 1")
    candidate_skills = set(extract_skills(candidate_text))
    job_skills = extract_skills(job_text)
    matched = [skill for skill in job_skills if skill in candidate_skills]
    missing = [skill for skill in job_skills if skill not in candidate_skills]
    skill_score = round(len(matched) / len(job_skills) * 100) if job_skills else 0

    def phrase_overlap(terms: tuple[str, ...]) -> int:
        candidate, job = candidate_text.casefold(), job_text.casefold()
        required = [term for term in terms if term in job]
        if not required:
            return 100
        return round(sum(term in candidate for term in required) / len(required) * 100)

    breakdown = {
        "skills": skill_score,
        "experience": phrase_overlap(("years of experience", "professional experience", "work experience", "senior", "junior")),
        "education": phrase_overlap(("bachelor", "degree", "master", "phd", "university")),
        "languages": phrase_overlap(("english", "spanish", "portuguese", "french", "german")),
    }
    score = round(sum(breakdown[key] * weights[key] for key in weights))
    explanation = (f"Score calculated deterministically with weights skills={weights['skills']:.0%}, "
                   f"experience={weights['experience']:.0%}, education={weights['education']:.0%}, languages={weights['languages']:.0%}. "
                   "Skill detection uses an explicit vocabulary; other dimensions use textual overlap and require human review.")
    return MatchResult(max(0, min(100, score)), breakdown, matched, missing, explanation)
