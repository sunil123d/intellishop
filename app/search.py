# app/search.py
"""
Semantic search using pgvector.
This replaces ChromaDB from your RAG project —
now vector search happens directly in PostgreSQL.
"""
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import EMBED_MODEL
from app.database import Product

print("Loading embedding model...")
_model = SentenceTransformer(EMBED_MODEL)
print("Embedding model ready.")


def embed_text(text_input: str) -> list:
    """Converts text to a 384-dim vector"""
    vector = _model.encode([text_input], convert_to_numpy=True)
    return vector[0].tolist()


def semantic_search(
    db: Session,
    query: str,
    top_k: int = 5,
    category: str = None
) -> list:
    """
    Finds products most semantically similar to the query.

    Uses pgvector's <-> operator which calculates
    cosine distance directly in SQL — this is the
    key advantage of pgvector: vector search using
    plain SQL syntax, no separate vector database needed.
    """
    query_vector = embed_text(query)

    # Build SQL query using pgvector's distance operator
    sql = """
        SELECT id, name, category, description, price, rating,
               1 - (embedding <=> :query_vector) AS similarity
        FROM products
        WHERE 1=1
    """
    params = {"query_vector": str(query_vector)}

    if category:
        sql += " AND category = :category"
        params["category"] = category

    sql += " ORDER BY embedding <=> :query_vector LIMIT :top_k"
    params["top_k"] = top_k

    result = db.execute(text(sql), params)

    return [
        {
            "id":          row.id,
            "name":        row.name,
            "category":    row.category,
            "description": row.description,
            "price":       row.price,
            "rating":      row.rating,
            "similarity":  round(row.similarity, 4)
        }
        for row in result
    ]