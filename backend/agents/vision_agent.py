"""
VisionAnalyzer Sub-Agent
Reads nutrition label image from GCS using Vertex AI Gemini Vision.
Returns structured nutrition data as a Python dict.
"""
import json, os
from google.genai import types
from tools.vertex_client import client, MODEL_FLASH

def analyze_label(gcs_uri: str) -> dict:
    """
    Args:
        gcs_uri: full GCS path e.g. gs://nutritionscore-temp-uploads-PROJECT/abc.jpg
    Returns:
        dict with product_name, ingredients, nutrition values
    """
    image_part = types.Part.from_uri(file_uri=gcs_uri, mime_type="image/jpeg")

    prompt = types.Part.from_text(text="""
Read this nutrition label image carefully.
Return ONLY valid JSON with no markdown fences and no explanation text:
{
  "product_name": "exact name on label or Unknown",
  "ingredients": ["every","single","ingredient","listed"],
  "calories_per_serving": number_or_null,
  "total_fat_g": number_or_null,
  "saturated_fat_g": number_or_null,
  "trans_fat_g": number_or_null,
  "sodium_mg": number_or_null,
  "total_sugar_g": number_or_null,
  "added_sugar_g": number_or_null,
  "protein_g": number_or_null,
  "fiber_g": number_or_null,
  "serving_size": "text description"
}
Return ONLY the JSON object. Nothing else.""")

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=types.Content(
            role="user",
            parts=[image_part, prompt]
        )
    )

    text = response.text.strip()
    # Strip markdown fences if model adds them anyway
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    return json.loads(text)