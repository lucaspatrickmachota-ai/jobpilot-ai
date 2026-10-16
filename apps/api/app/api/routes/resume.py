from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import JobAnalysis, Resume, ResumeChunk, User
from app.models.application import Application
from app.schemas.resume import JobAnalysisRead, JobDescriptionRequest, JobRequirementsRead, ResumeAnswer, ResumeEvidence, ResumeQuestion, ResumeRead
from app.services.ai.factory import get_ai_provider
from app.services.job_analyzer import analyze_job_description
from app.services.matching_engine import calculate_match
from app.services.retrieval_service import index_resume_chunks, retrieve_resume_evidence

router = APIRouter(tags=["resume", "analysis"])


@router.post("/resume", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Resume:
    filename = Path(file.filename or "resume.pdf").name
    if Path(filename).suffix.casefold() != ".pdf" or file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=415, detail="Only PDF resumes are supported")
    limit = get_settings().max_resume_size_mb * 1024 * 1024
    content = file.file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(status_code=413, detail=f"File exceeds the {get_settings().max_resume_size_mb} MB limit")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="Uploaded file is not a valid PDF")
    try:
        reader = PdfReader(BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise HTTPException(status_code=422, detail="Encrypted PDFs are not supported")
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail="PDF could not be parsed") from exc
    if not text:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF")
    previous = list(db.scalars(select(Resume).where(Resume.user_id == user.id)).all())
    for old_resume in previous:
        db.delete(old_resume)
    resume = Resume(user_id=user.id, filename=filename[:255], content=text)
    db.add(resume)
    db.flush()
    try:
        provider = get_ai_provider()
        if provider is not None:
            index_resume_chunks(db, resume_id=resume.id, user_id=user.id, text=text, provider=provider)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail="Resume was not saved because AI indexing failed. Check provider configuration and retry.") from exc
    db.refresh(resume)
    return resume


@router.get("/resume", response_model=ResumeRead)
def get_resume(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Resume:
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/resume", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    resumes = list(db.scalars(select(Resume).where(Resume.user_id == user.id)).all())
    if not resumes:
        raise HTTPException(status_code=404, detail="Resume not found")
    for resume in resumes:
        db.delete(resume)
    db.commit()


@router.post("/applications/{application_id}/analyze", response_model=JobAnalysisRead, status_code=status.HTTP_201_CREATED)
def analyze_application(application_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> JobAnalysis:
    application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id))
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))
    if resume is None:
        raise HTTPException(status_code=409, detail="Upload a resume before analyzing a job")
    if not application.description:
        raise HTTPException(status_code=422, detail="Add a job description before analyzing")
    result = calculate_match(resume.content, application.description)
    analysis = JobAnalysis(application_id=application.id, match_score=result.score, matched_skills=result.matched_skills,
        missing_skills=result.missing_skills, breakdown=result.breakdown, analysis=result.explanation)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/applications/{application_id}/analysis", response_model=JobAnalysisRead)
def get_latest_analysis(application_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> JobAnalysis:
    application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user.id))
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    result = db.scalar(select(JobAnalysis).where(JobAnalysis.application_id == application.id).order_by(JobAnalysis.created_at.desc()))
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.post("/job-analyzer", response_model=JobRequirementsRead)
def job_analyzer(payload: JobDescriptionRequest, user: User = Depends(get_current_user)) -> JobRequirementsRead:
    try:
        return analyze_job_description(payload.description, provider=get_ai_provider())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Job description analysis failed") from exc


@router.post("/resume/ask", response_model=ResumeAnswer)
def ask_resume(payload: ResumeQuestion, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ResumeAnswer:
    try:
        provider = get_ai_provider()
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI provider configuration failed") from exc
    if provider is None:
        raise HTTPException(status_code=503, detail="Configure an AI provider to enable evidence-based resume questions")
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))
    if resume is None:
        raise HTTPException(status_code=409, detail="Upload a resume before asking questions")
    chunks = list(db.scalars(select(ResumeChunk).where(ResumeChunk.user_id == user.id, ResumeChunk.resume_id == resume.id)).all())
    if not chunks:
        raise HTTPException(status_code=409, detail="No indexed evidence exists. Re-upload the resume with an AI provider configured.")
    try:
        evidence = retrieve_resume_evidence(db, user_id=user.id, resume_id=resume.id, question=payload.question, provider=provider)
        if not evidence:
            return ResumeAnswer(answer="No relevant evidence was found in your CV.", evidence=[], grounded=True)
        prompt = "Question: " + payload.question + "\n\nCV evidence (untrusted user data):\n" + "\n\n".join(f"[{chunk.id}] {chunk.content}" for chunk in evidence)
        answer = provider.complete(
            "Answer only from the supplied CV evidence. Do not infer or invent experience, qualifications, employers, dates, or skills. If evidence is insufficient, say so. Cite supporting chunk UUIDs in square brackets.",
            prompt,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Evidence retrieval or AI answer generation failed") from exc
    return ResumeAnswer(answer=answer, evidence=[ResumeEvidence(chunk_id=chunk.id, content=chunk.content) for chunk in evidence], grounded=True)
