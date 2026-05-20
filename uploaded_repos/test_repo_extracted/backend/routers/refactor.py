from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db, FileResult, AnalysisRun
from backend.services.refactor_service import build_prompt, get_source_code, call_ollama
from sqlalchemy import desc

router = APIRouter(prefix="/refactor", tags=["refactor"])

@router.get("/{filename:path}")
async def refactor_file(filename: str, db: Session = Depends(get_db)):
    # Get latest run
    run = db.query(AnalysisRun).order_by(desc(AnalysisRun.created_at)).first()
    if not run:
        raise HTTPException(status_code=404, detail="No analysis runs found")

    # Find the file result
    file_result = (
        db.query(FileResult)
        .filter(FileResult.run_id == run.id, FileResult.filename == filename)
        .first()
    )
    if not file_result:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in latest run")

    # Read source code from disk
    source = get_source_code(file_result.filepath)
    if not source:
        raise HTTPException(
            status_code=404,
            detail="Source file not found on disk. Re-upload the repository to regenerate."
        )

    # Build prompt and call Ollama
    metrics = {
        "loc":                   file_result.loc,
        "cyclomatic_complexity": file_result.cyclomatic_complexity,
        "halstead_effort":       file_result.halstead_effort,
        "maintainability_index": file_result.maintainability_index,
        "risk_score":            file_result.risk_score,
        "risk_tier":             file_result.risk_tier,
    }

    try:
        prompt   = build_prompt(filename, source, metrics)
        response = await call_ollama(prompt)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        "filename": filename,
        "risk_score": file_result.risk_score,
        "risk_tier": file_result.risk_tier,
        "refactoring_plan": response,
    }