"""
NutritionScore Main API
Exposes the Coordinator agent via a FastAPI endpoint.
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from agents.coordinator import run_coordinator

app = FastAPI(title="NutritionScore API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.get("/")
def root():
    return {
        "name":     "NutritionScore",
        "version":  "1.0.0",
        "agents":   ["NutritionCoordinator","VisionAnalyzer","HealthScorer","AlternativeFinder"],
        "ai":       "Vertex AI (google-genai SDK) — no API keys",
        "database": "AlloyDB PostgreSQL + pg_trgm similarity search",
        "storage":  "Google Cloud Storage (temp image uploads)",
        "protocol": "MCP"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    category: str = Form(default="snack")
):
    image_bytes = await file.read()
    return run_coordinator(image_bytes, category)