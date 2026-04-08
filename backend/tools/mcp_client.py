"""HTTP client that ADK agents use to call MCP server tools."""
import requests, os

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

def call_mcp(tool_name: str, args: dict) -> dict:
    try:
        r = requests.post(
            f"{MCP_URL}/tools/call",
            json={"name": tool_name, "arguments": args},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"error": str(e), "result": None}

def check_product_cache(category: str, product_name: str = None) -> dict:
    return call_mcp("check_product_cache", {
        "category": category,
        **({"product_name": product_name} if product_name else {})
    })

def save_product_to_cache(category, product_name, score,
                          explanation, bad_ingredients, good_aspects, alternatives):
    return call_mcp("save_product_to_cache", {
        "category":        category,
        "product_name":    product_name,
        "score":           score,
        "explanation":     explanation,
        "bad_ingredients": bad_ingredients,
        "good_aspects":    good_aspects,
        "alternatives":    alternatives
    })