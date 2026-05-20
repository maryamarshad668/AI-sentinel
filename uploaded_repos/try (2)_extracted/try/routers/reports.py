from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import get_db, AnalysisRun, FileResult

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/latest")
def latest_report(db: Session = Depends(get_db)):
    run = db.query(AnalysisRun).order_by(desc(AnalysisRun.created_at)).first()
    if not run:
        return {"message": "no runs yet"}

    files = db.query(FileResult).filter(FileResult.run_id == run.id).all()

    return {
        "run": {
            "id":             run.id,
            "repo_name":      run.repo_name,
            "created_at":     run.created_at.isoformat(),
            "health_score":   run.health_score,
            "total_files":    run.total_files,
            "critical_count": run.critical_count,
            "high_count":     run.high_count,
            "moderate_count": run.moderate_count,
            "low_count":      run.low_count,
        },
        "file_count": len(files),
        "files": [
            {
                "filename":               f.filename,
                "loc":                    f.loc,
                "cyclomatic_complexity":  f.cyclomatic_complexity,
                "halstead_effort":        f.halstead_effort,
                "maintainability_index":  f.maintainability_index,
                "churn_rate":             f.churn_rate,
                "risk_score":             f.risk_score,
                "risk_tier":              f.risk_tier.lower(),
                "is_hotspot":             f.is_hotspot,
                "hotspot_score":          f.hotspot_score,
                "tdc_annual":             f.tdc_annual,
            }
            for f in files
        ],
    }