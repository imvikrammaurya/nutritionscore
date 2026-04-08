"""
Shared Vertex AI client using the new google-genai SDK.
Uses IAM service account credentials — no API keys required.
"""
import os
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION   = os.getenv("GCP_LOCATION", "us-central1")

# Initialize Vertex AI client once (reused by all agents)
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

MODEL_FLASH = "gemini-2.5-flash"   # fast + multimodal
MODEL_PRO   = "gemini-1.5-pro"     # deeper reasoning