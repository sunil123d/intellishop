# app/database.py
"""
Database connection with pgvector support.
Creates the products table with a VECTOR column.
"""
from sqlalchemy import (create_engine, Column, Integer,
                        String, Float, Text, text)
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from app.config import DATABASE_URL, EMBED_DIMENSION

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base         = declarative_base()


class Product(Base):
    """
    Product table with a vector column for semantic search.
    This is the key concept — embedding stored alongside
    regular product data in the same PostgreSQL table.
    """
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(255), nullable=False)
    category    = Column(String(100))
    description = Column(Text)
    price       = Column(Float)
    rating      = Column(Float)
    embedding   = Column(Vector(EMBED_DIMENSION))  # ← pgvector column


def init_db():
    """
    Enables pgvector extension and creates tables.
    Run once when setting up the database.
    """
    with engine.connect() as conn:
        # Enable pgvector extension in PostgreSQL
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(engine)
    print("Database initialized with pgvector extension")


def get_db():
    """FastAPI dependency — provides a DB session per request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()