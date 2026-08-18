# app/models.py
"""
Pydantic models — FastAPI uses these to automatically
validate incoming requests and format outgoing responses.
This is the request/response contract of your API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500,
                       description="Natural language search query")
    top_k: int = Field(5, ge=1, le=20,
                       description="Number of results to return")
    category: Optional[str] = Field(None,
                       description="Filter by product category")


class ProductResult(BaseModel):
    id:          int
    name:        str
    category:    str
    description: str
    price:       float
    rating:      float
    similarity:  float


class SearchResponse(BaseModel):
    query:   str
    results: List[ProductResult]
    count:   int


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=10)


class RecommendResponse(BaseModel):
    query:          str
    recommendation: str
    products:       List[ProductResult]