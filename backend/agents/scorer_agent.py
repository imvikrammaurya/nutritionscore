"""
HealthScorer Sub-Agent
Scores the product 1-10, identifies bad ingredients with severity,
and notes positive aspects. Uses Vertex AI — no API key.
"""
import json
from google.genai import types
from tools.vertex_client import client, MODEL_FLASH

def score_product(nutrition_data: dict) -> dict:
    data_str = json.dumps(nutrition_data, indent=2)

    prompt = f"""You are a certified nutritionist reviewing this product:
{data_str}

Score the product from 1 to 10 (1 = extremely unhealthy, 10 = very healthy).

Deduct points for:
- Total sugar above 10g per serving: minus 2
- Sodium above 600mg per serving: minus 2
- Saturated fat above 5g per serving: minus 1.5
- Trans fat present at all: minus 2
- Artificial preservatives or colours in ingredients: minus 1

Add points for:
- Dietary fibre above 5g per serving: plus 1
- Protein above 10g per serving: plus 1

Return ONLY valid JSON, no markdown:
{{
  "score": 6,
  "verdict": "Average",
  "bad_ingredients": [
    {{
      "name": "Sugar",
      "amount": "12g per serving",
      "reason": "Exceeds recommended daily limit in a single serving",
      "severity": "high"
    }}
  ],
  "good_aspects": ["High protein", "No trans fat"],
  "explanation": "Write 2 to 3 plain English sentences explaining this exact score."
}}"""

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    )
    text = response.text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)