from fastapi import FastAPI
from database.database import init_db
from backend.routers import analysis

app = FastAPI(title="AI-Sentinel", version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized")

app.include_router(analysis.router)

@app.get("/")
def root():
    return {"message": "AI-Sentinel is running!"}