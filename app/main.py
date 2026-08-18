# app/main.py
"""
FastAPI application — the main entry point.
Auto-generates interactive docs at /docs
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time

from app.database import init_db, get_db
from app.models import (SearchRequest, SearchResponse,
                        RecommendRequest, RecommendResponse)
from app.search    import semantic_search
from app.recommend import generate_recommendation

app = FastAPI(
    title       = "IntelliShop API",
    description = "AI-powered product search and recommendation engine",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)


@app.on_event("startup")
def startup():
    """Runs once when the app starts — initializes database"""
    init_db()


@app.get("/")
def root():
    return {
        "service": "IntelliShop API",
        "status":  "running",
        "docs":    "/docs"
    }


from sqlalchemy import text

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503,
                           detail=f"Database unavailable: {e}")


@app.post("/search", response_model=SearchResponse)
def search_products(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Semantic product search using pgvector.

    Example: "comfortable shoes for running in winter"
    Finds products by MEANING not just keyword matching.
    """
    start = time.time()

    results = semantic_search(
        db       = db,
        query    = request.query,
        top_k    = request.top_k,
        category = request.category
    )

    elapsed = time.time() - start
    print(f"Search completed in {elapsed:.3f}s")

    return SearchResponse(
        query   = request.query,
        results = results,
        count   = len(results)
    )


@app.post("/recommend", response_model=RecommendResponse)
def recommend_products(
    request: RecommendRequest,
    db: Session = Depends(get_db)
):
    """
    Full RAG-style recommendation pipeline:
    1. Semantic search finds matching products (pgvector)
    2. LangChain generates a natural language explanation
    """
    products = semantic_search(
        db    = db,
        query = request.query,
        top_k = request.top_k
    )

    recommendation = generate_recommendation(
        request.query, products
    )

    return RecommendResponse(
        query          = request.query,
        recommendation = recommendation,
        products       = products
    )


@app.get("/products/count")
def product_count(db: Session = Depends(get_db)):
    """Returns total products indexed"""
    from app.database import Product
    count = db.query(Product).count()
    return {"total_products": count}