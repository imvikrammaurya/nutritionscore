"""
AlternativeFinder Sub-Agent
Finds 3 healthier alternatives for a given product category.
Only called by Coordinator when AlloyDB similarity search returns no match.
Uses Vertex AI — no API key.
"""
import json
from google.genai import types
from tools.vertex_client import client, MODEL_FLASH

def find_alternatives(category: str, score: int,
                      bad_ingredients: list, product_name: str = "Unknown") -> list:
    bad_names = [x.get("name","") for x in bad_ingredients]

    prompt = f"""A user scanned a product called '{product_name}' in the '{category}' category.
It scored {score} out of 10.
The main problems were: {bad_names}

Suggest exactly 3 healthier alternatives that are:
1. Real, named products available to buy in India
2. Directly address each problem listed above
3. In the same '{category}' category

Return ONLY a valid JSON array with no markdown:
[
  {{
    "name": "Exact Product Name",
    "brand": "Brand Name",
    "why_better": "Specifically addresses: lower sugar (3g vs 12g), no artificial colours",
    "estimated_score": 8,
    "where_to_buy": "BigBasket, DMart, or Amazon India"
  }}
]
Return exactly 3 items. Only JSON array. Nothing else."""

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    )
    text = response.text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)