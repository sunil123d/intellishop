# app/mlops/train_embeddings.py
"""
MLflow experiment tracking — compares different
embedding models for the search system.
"""
import sys, os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
))

import mlflow
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Product-Search-Embeddings")

TEST_QUERIES = [
    "comfortable running shoes",
    "laptop for students",
    "warm winter clothing"
]

MODELS_TO_TEST = [
    "all-MiniLM-L6-v2",     # 384 dim, fast
    "all-mpnet-base-v2",    # 768 dim, more accurate
]


def evaluate_model(model_name: str):
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_name", model_name)

        start = time.time()
        model = SentenceTransformer(model_name)
        load_time = time.time() - start
        mlflow.log_metric("load_time_seconds", round(load_time, 3))

        # Test embedding speed
        start = time.time()
        embeddings = model.encode(TEST_QUERIES)
        encode_time = time.time() - start
        mlflow.log_metric("encode_time_seconds", round(encode_time, 4))
        mlflow.log_metric("embedding_dimension", embeddings.shape[1])

        # Test semantic similarity quality
        # Similar queries should have high similarity
        sim_matrix = cosine_similarity(embeddings)
        avg_similarity = np.mean(sim_matrix[np.triu_indices(3, k=1)])
        mlflow.log_metric("avg_query_similarity", round(float(avg_similarity), 4))

        mlflow.set_tag("purpose", "embedding model comparison")

        print(f"\n{model_name}:")
        print(f"  Load time:   {load_time:.3f}s")
        print(f"  Encode time: {encode_time:.4f}s")
        print(f"  Dimension:   {embeddings.shape[1]}")


if __name__ == "__main__":
    print("Comparing embedding models with MLflow tracking...\n")
    for model_name in MODELS_TO_TEST:
        evaluate_model(model_name)

    print("\nView results: http://localhost:5000")
    print("Experiment: Product-Search-Embeddings")