import os, json
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect(
        host=os.getenv("ALLOYDB_IP"),
        database="nutritionscore",
        user="postgres",
        password=os.getenv("ALLOYDB_PASSWORD"),
        port=5432
    )

def similarity_search(category: str, product_name: str = None) -> dict | None:
    """
    Use pg_trgm similarity search to find cached results.
    Checks by category first, then by product name similarity if provided.
    Returns None if no similar result found above threshold.
    """
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if product_name:
            # Similarity search on product name (threshold 0.3 = 30% similar)
            cur.execute("""
                SELECT *, similarity(product_name, %s) AS sim_score
                FROM product_cache
                WHERE similarity(product_name, %s) > 0.3
                   OR category = %s
                ORDER BY sim_score DESC, created_at DESC
                LIMIT 1
            """, (product_name, product_name, category))
        else:
            # Exact category match
            cur.execute(
                "SELECT * FROM product_cache WHERE category=%s ORDER BY created_at DESC LIMIT 1",
                (category,)
            )

        row = cur.fetchone()
        conn.close()

        if row:
            _increment(row["id"])
            return {
                "alternatives":    row["alternatives"],
                "health_score":    row["health_score"],
                "explanation":     row["explanation"],
                "bad_ingredients": row["bad_ingredients"],
                "good_aspects":    row["good_aspects"],
                "cached":          True,
                "matched_product": row["product_name"],
                "scan_count":      row["scan_count"],
            }
    except Exception as e:
        print(f"DB similarity_search error: {e}")
    return None

def save_to_cache(category: str, product_name: str, score: int,
                  explanation: str, bad_ingredients: list,
                  good_aspects: list, alternatives: list):
    """Save full product analysis to AlloyDB for future users."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO product_cache
              (category, product_name, health_score, explanation,
               bad_ingredients, good_aspects, alternatives)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            category, product_name, score, explanation,
            json.dumps(bad_ingredients), json.dumps(good_aspects),
            json.dumps(alternatives)
        ))
        conn.commit()
        conn.close()
        print(f"Saved '{product_name}' ({category}) to AlloyDB")
    except Exception as e:
        print(f"DB save error: {e}")

def _increment(row_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE product_cache SET scan_count=scan_count+1, updated_at=NOW() WHERE id=%s",
            (row_id,)
        )
        conn.commit()
        conn.close()
    except:
        pass