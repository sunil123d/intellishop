# app/mlops/ingest_products.py
"""
Loads sample e-commerce products, generates embeddings,
and stores them in pgvector.
"""
import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
))

from app.database import SessionLocal, Product, init_db
from app.search import embed_text

SAMPLE_PRODUCTS = [
    {"name": "Nike Air Zoom Pegasus", "category": "Footwear",
     "description": "Lightweight running shoes with responsive cushioning, breathable mesh upper, ideal for daily training and winter running", "price": 8999, "rating": 4.5},
    {"name": "Adidas Ultraboost 22", "category": "Footwear",
     "description": "Premium running shoes with Boost midsole technology for maximum energy return, comfortable for long distance runs", "price": 12999, "rating": 4.7},
    {"name": "Sony WH-1000XM5", "category": "Electronics",
     "description": "Industry-leading noise cancelling wireless headphones with 30-hour battery life and crystal clear calls", "price": 24999, "rating": 4.8},
    {"name": "Apple MacBook Air M2", "category": "Electronics",
     "description": "Ultra-thin laptop with M2 chip, all-day battery life, perfect for students and professionals", "price": 99999, "rating": 4.9},
    {"name": "Instant Pot Duo 7-in-1", "category": "Kitchen",
     "description": "Multi-functional pressure cooker for quick and easy home cooking, saves time on meal preparation", "price": 6999, "rating": 4.6},
    {"name": "Yoga Mat Premium", "category": "Fitness",
     "description": "Extra thick non-slip yoga mat with carrying strap, perfect for home workouts and studio classes", "price": 1499, "rating": 4.4},
    {"name": "Winter Wool Jacket", "category": "Clothing",
     "description": "Warm insulated jacket for cold weather, water-resistant outer shell, comfortable fit for outdoor activities", "price": 3999, "rating": 4.3},
    {"name": "Stainless Steel Water Bottle", "category": "Accessories",
     "description": "Insulated bottle keeps drinks cold for 24 hours or hot for 12 hours, leak-proof design for gym and travel", "price": 899, "rating": 4.5},
    {"name": "Ergonomic Office Chair", "category": "Furniture",
     "description": "Adjustable lumbar support chair for long work sessions, breathable mesh back reduces back pain", "price": 15999, "rating": 4.6},
    {"name": "Wireless Gaming Mouse", "category": "Electronics",
     "description": "High precision gaming mouse with customizable buttons and RGB lighting for competitive gaming", "price": 2999, "rating": 4.4},
]


def ingest():
    init_db()
    db = SessionLocal()

    print("Ingesting products with embeddings...")
    for item in SAMPLE_PRODUCTS:
        combined_text = f"{item['name']} {item['description']}"
        embedding     = embed_text(combined_text)

        product = Product(
            name        = item["name"],
            category    = item["category"],
            description = item["description"],
            price       = item["price"],
            rating      = item["rating"],
            embedding   = embedding
        )
        db.add(product)

    db.commit()
    count = db.query(Product).count()
    print(f"Ingested {count} products with embeddings")
    db.close()


if __name__ == "__main__":
    ingest()