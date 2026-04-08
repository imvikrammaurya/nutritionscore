"""
NutritionScore MCP Server
Strictly handles AlloyDB product cache: similarity search + save.
ADK agents call this via HTTP. It never touches Vertex AI directly.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.db_tool import similarity_search, save_to_cache

mcp_app = FastAPI(title="NutritionScore MCP Server")

# ── Tool definitions (exposed to ADK agents) ──────────────────────────────
MCP_TOOLS = [
    {
        "name": "check_product_cache",
        "description": (
            "Check AlloyDB for a similar product using pg_trgm similarity search. "
            "Returns cached health score, bad ingredients, and alternatives if found. "
            "Use this BEFORE calling any Vertex AI agents."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category":     {"type": "string", "description": "Food category e.g. chips, biscuits, drinks"},
                "product_name": {"type": "string", "description": "Product name extracted from label (optional)"}
            },
            "required": ["category"]
        }
    },
    {
        "name": "save_product_to_cache",
        "description": (
            "Save a complete product analysis to AlloyDB. "
            "Call this after AlternativeFinder completes so future users get instant results."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category":        {"type": "string"},
                "product_name":    {"type": "string"},
                "score":           {"type": "integer", "minimum": 1, "maximum": 10},
                "explanation":     {"type": "string"},
                "bad_ingredients": {"type": "array"},
                "good_aspects":    {"type": "array"},
                "alternatives":    {"type": "array"}
            },
            "required": ["category", "product_name", "score", "explanation", "alternatives"]
        }
    }
]

@mcp_app.get("/tools")
def list_tools():
    """MCP endpoint: list available tools"""
    return {"tools": MCP_TOOLS}

class CallReq(BaseModel):
    name: str
    arguments: dict

@mcp_app.post("/tools/call")
def call_tool(req: CallReq):
    """MCP endpoint: execute a tool call"""

    if req.name == "check_product_cache":
        result = similarity_search(
            category=req.arguments["category"],
            product_name=req.arguments.get("product_name")
        )
        if result:
            return {
                "result": result,
                "message": f"Cache HIT via similarity search (matched: {result.get('matched_product')})"
            }
        return {"result": None, "message": "Cache MISS — no similar product found"}

    elif req.name == "save_product_to_cache":
        save_to_cache(
            category=req.arguments["category"],
            product_name=req.arguments.get("product_name", "Unknown"),
            score=req.arguments["score"],
            explanation=req.arguments["explanation"],
            bad_ingredients=req.arguments.get("bad_ingredients", []),
            good_aspects=req.arguments.get("good_aspects", []),
            alternatives=req.arguments["alternatives"]
        )
        return {"result": "success", "message": "Saved to AlloyDB successfully"}

    return {"error": f"Unknown tool: {req.name}"}