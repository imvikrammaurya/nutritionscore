"""
HealthScorer Sub-Agent (2026 Australian HSR Edition)
Calculates HSR stars (0.5-5.0), identifies Traffic Light categories, 
and provides specialized dietician feedback using Vertex AI.
"""
import json
from google.genai import types
from tools.vertex_client import client, MODEL_FLASH

def score_product(nutrition_data: dict) -> dict:
    data_str = json.dumps(nutrition_data, indent=2)

    # Updated prompt with strict Australian 2026 HSR Logic
    prompt = f"""You are a Senior Nutritionist for the Australian Health Star Rating (HSR) Board.
Review this product data:
{data_str}

TASKS:
1. Calculate the HSR (0.5 to 5 stars) based on 2026 standards (Strictly per 100g/100mL).
2. Calculate Baseline Points: Energy (kJ), Sat Fat (g), Total Sugars (g), and Sodium (mg).
3. Calculate Modifying Points: Protein (g), Fiber (g), and estimate FVNL % (Fruit/Veg/Nuts/Legumes).
4. Assign a School Canteen Traffic Light Category:
   - GREEN (4.5 - 5.0 stars): "Everyday Choice"
   - AMBER (3.5 - 4.0 stars): "Select Carefully"
   - RED (0.5 - 3.0 stars): "Discretionary / Occasional"

Return ONLY valid JSON, no markdown:
{{
  "score": 3.5,
  "hsr_stars": 3.5,
  "traffic_light": "AMBER",
  "verdict": "Amber Choice - Select Carefully",
  "bad_ingredients": [
    {{
      "name": "Sodium",
      "amount": "value",
      "reason": "High baseline points contribution under HSR 2026 rules",
      "severity": "high"
    }}
  ],
  "good_aspects": ["High Fiber (Modifier)", "Natural Ingredients"],
  "explanation": "2-3 sentences explaining the Baseline vs. Modifier points that resulted in this star rating."
}}"""

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    )
    
    text = response.text.strip()
    
    # Clean up markdown if the model includes it
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
        
    try:
        return json.loads(text)
    except Exception as e:
        # Fallback if AI output is malformed
        return {
            "score": 0,
            "verdict": "Error processing nutrition data",
            "explanation": f"The Scorer Agent encountered an error: {str(e)}"
        }