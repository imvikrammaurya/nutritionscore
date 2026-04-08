"""
NutritionCoordinator — Primary ADK Agent
Manages the full multi-step workflow:
  1. Upload image to GCS (temp storage)
  2. VisionAnalyzer sub-agent reads the label
  3. HealthScorer sub-agent scores the product
  4. MCP Server checks AlloyDB similarity cache
  5. If cache miss: AlternativeFinder sub-agent + save to AlloyDB via MCP
"""
import os, uuid
from google.cloud import storage
from agents.vision_agent      import analyze_label
from agents.scorer_agent      import score_product
from agents.alternatives_agent import find_alternatives
from tools.mcp_client import check_product_cache, save_product_to_cache

GCS_BUCKET = os.getenv("GCS_BUCKET_NAME", "nutritionscore-temp-uploads")

def _upload_to_gcs(image_bytes: bytes, filename: str) -> str:
    """Upload image to GCS and return gs:// URI"""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(f"uploads/{filename}")
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    return f"gs://{GCS_BUCKET}/uploads/{filename}"

def run_coordinator(image_bytes: bytes, category: str) -> dict:
    log = []

    # ── Step 1: Upload to GCS ──────────────────────────────────────────────
    log.append("Coordinator: uploading image to GCS temp bucket...")
    filename  = f"{uuid.uuid4().hex}.jpg"
    gcs_uri   = _upload_to_gcs(image_bytes, filename)
    log.append(f"GCS upload complete: {gcs_uri}")

    # ── Step 2: VisionAnalyzer Sub-Agent ──────────────────────────────────
    log.append("Coordinator: calling VisionAnalyzer sub-agent (Vertex AI)...")
    nutrition = analyze_label(gcs_uri)
    product_name = nutrition.get("product_name", "Unknown")
    ingredient_count = len(nutrition.get("ingredients", []))
    log.append(f"VisionAnalyzer: found {ingredient_count} ingredients for '{product_name}'")

    # ── Step 3: HealthScorer Sub-Agent ────────────────────────────────────
    log.append("Coordinator: calling HealthScorer sub-agent (Vertex AI)...")
    scoring = score_product(nutrition)
    log.append(f"HealthScorer: score {scoring['score']}/10 — {scoring['verdict']}")

    # ── Step 4: MCP → AlloyDB similarity search ───────────────────────────
    log.append("Coordinator: calling MCP Server → AlloyDB similarity search...")
    cache = check_product_cache(category, product_name)
    cached_result = cache.get("result")

    alternatives = None
    source = "alloydb_cache"

    if isinstance(cached_result, dict) and cached_result.get("cached"):
        alternatives = cached_result["alternatives"]
        matched = cached_result.get("matched_product", "similar product")
        log.append(f"MCP: cache HIT! Matched '{matched}' — {len(alternatives)} alternatives from AlloyDB")
    else:
        # ── Step 5: AlternativeFinder Sub-Agent ───────────────────────────
        log.append("MCP: cache MISS. Coordinator: calling AlternativeFinder sub-agent...")
        alternatives = find_alternatives(
            category, scoring["score"],
            scoring.get("bad_ingredients", []), product_name
        )
        log.append(f"AlternativeFinder: found {len(alternatives)} alternatives")
        source = "ai_generated"

        # ── Step 6: MCP → Save to AlloyDB ─────────────────────────────────
        log.append("Coordinator: saving to AlloyDB via MCP for future users...")
        save_product_to_cache(
            category        = category,
            product_name    = product_name,
            score           = scoring["score"],
            explanation     = scoring["explanation"],
            bad_ingredients = scoring.get("bad_ingredients", []),
            good_aspects    = scoring.get("good_aspects", []),
            alternatives    = alternatives
        )
        log.append("MCP: saved to AlloyDB — future users get instant results!")

    log.append("Coordinator: workflow complete. Returning results.")

    return {
        "nutrition_data":      nutrition,
        "product_name":        product_name,
        "health_score":        scoring["score"],
        "verdict":             scoring["verdict"],
        "explanation":         scoring["explanation"],
        "bad_ingredients":     scoring.get("bad_ingredients", []),
        "good_aspects":        scoring.get("good_aspects", []),
        "alternatives":        alternatives,
        "alternatives_source": source,
        "agent_log":           log,
    }