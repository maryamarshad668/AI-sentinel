import os
import shutil
import zipfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db, AnalysisRun, FileResult
from backend.services.analyzer import analyze_codebase
from backend.services.risk_scorer import score_files

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/upload")
async def upload_repo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip repository")

    # Save zip
    upload_dir = os.path.join(os.getcwd(), "uploaded_repos")
    os.makedirs(upload_dir, exist_ok=True)
    zip_path = os.path.join(upload_dir, file.filename)
    with open(zip_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    # Extract zip
    extract_dir = zip_path.replace(".zip", "_extracted")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    # Run analysis pipeline
    raw_metrics = analyze_codebase(extract_dir)
    if not raw_metrics:
        raise HTTPException(status_code=422, detail="No Python files found in the uploaded zip.")

    scored = score_files(raw_metrics)

    # Compute summary stats
    avg_risk     = sum(f["risk_score"] for f in scored) / len(scored)
    health_score = round(100 - avg_risk, 2)
    total_tdc    = round(sum(f["tdc_annual"] for f in scored), 2)
    critical     = sum(1 for f in scored if f["risk_tier"] == "Critical")
    high         = sum(1 for f in scored if f["risk_tier"] == "High")
    moderate     = sum(1 for f in scored if f["risk_tier"] == "Moderate")
    low          = sum(1 for f in scored if f["risk_tier"] == "Low")

    # Save AnalysisRun
    run = AnalysisRun(
        repo_name      = file.filename,
        repo_url       = None,
        health_score   = health_score,
        total_files    = len(scored),
        total_tdc      = total_tdc,
        critical_count = critical,
        high_count     = high,
        moderate_count = moderate,
        low_count      = low,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Save FileResult rows
    for f in scored:
        row = FileResult(
            run_id                = run.id,
            filename              = f.get("filename", ""),
            filepath              = f.get("filepath", ""),
            loc                   = f.get("loc", 0),
            cyclomatic_complexity = f.get("cc_avg", 0),
            halstead_effort       = f.get("halstead_effort", 0),
            maintainability_index = f.get("maintainability_index", 0),
            churn_rate            = f.get("churn_rate", 0),
            risk_score            = f.get("risk_score", 0),
            risk_tier             = f.get("risk_tier", "Low"),
            is_hotspot            = f.get("is_hotspot", False),
            hotspot_score         = f.get("hotspot_score", 0),
            tdc_annual            = f.get("tdc_annual", 0),
        )
        db.add(row)
    db.commit()

    return {
        "message":        "Analysis complete",
        "run_id":         run.id,
        "health_score":   health_score,
        "files_analyzed": len(scored),
        "critical":       critical,
        "high":           high,
        "total_tdc":      total_tdc,
    }