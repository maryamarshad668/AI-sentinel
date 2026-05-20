from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.database import init_db
from backend.routers import analysis, auth, reports, refactor

app = FastAPI(title="AI-Sentinel", version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized")

app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(refactor.router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def root():
    return {"message": "AI-Sentinel is running!"}

@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/dashboard.html")