"""
embed.py
--------
Milestone 4: Embed all chunks and store them in ChromaDB.
Also provides a retrieve() function used by Milestone 5 (generate.py).

Stages (from pipeline diagram):
  Chunking -> Embedding (all-MiniLM-L6-v2) -> Vector Store (ChromaDB) -> Retrieval

Usage:
    # Build the vector store (run once, or re-run to rebuild):
    python embed.py

    # Then test retrieval interactively:
    python embed.py --query "which apartments have the best bus access on 34th street"
"""

import argparse
import os

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import build_chunks

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "uf_housing"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


# ---------------------------------------------------------------------------
# Embedding model (loaded once, reused for both indexing and querying)
# ---------------------------------------------------------------------------

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"  Loading embedding model: {EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


# ---------------------------------------------------------------------------
# ChromaDB client + collection
# ---------------------------------------------------------------------------

def get_collection(chroma_dir: str = CHROMA_DIR) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine distance for similarity
    )
    return collection


# ---------------------------------------------------------------------------
# Build the vector store
# ---------------------------------------------------------------------------

def build_vector_store(chroma_dir: str = CHROMA_DIR) -> chromadb.Collection:
    """
    Load all chunks from ingest.py, embed them with all-MiniLM-L6-v2,
    and upsert into ChromaDB with source metadata.

    Safe to re-run — upsert overwrites existing entries by chunk_id.
    """
    print("Building vector store...")
    chunks = build_chunks()
    print(f"  {len(chunks)} chunks to embed")

    model = get_model()
    collection = get_collection(chroma_dir)

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    print(f"  Embedding {len(texts)} chunks (this takes ~10–30 seconds)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    # Upsert in one batch
    collection.upsert(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    print(f"  Stored {collection.count()} chunks in ChromaDB at '{chroma_dir}'")
    return collection


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(query: str, k: int = TOP_K, chroma_dir: str = CHROMA_DIR) -> list[dict]:
    """
    Embed the query and return the top-k most relevant chunks.

    Returns a list of dicts:
        {
            "text":     str,   # chunk content
            "source":   str,   # source filename
            "chunk_id": str,   # unique chunk identifier
            "distance": float, # cosine distance (lower = more similar)
        }
    """
    model = get_model()
    collection = get_collection(chroma_dir)

    query_embedding = model.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text":     results["documents"][0][i],
            "source":   results["metadatas"][0][i]["source"],
            "chunk_id": results["ids"][0][i],
            "distance": round(results["distances"][0][i], 4),
        })
    return chunks


# ---------------------------------------------------------------------------
# Retrieval test — run against evaluation plan queries
# ---------------------------------------------------------------------------

EVAL_QUERIES = [
    "Which RTS bus routes serve apartments on the SW 34th Street corridor?",
    "What do residents say about maintenance response times at Stoneridge Apartments?",
    "When should UF students start apartment hunting to secure a unit for fall semester?",
    "What is the typical monthly rent for a room in a 4-bedroom apartment near UF?",
    "Which Gainesville neighborhoods are walkable to UF without a car or bus?",
]


def run_retrieval_test(queries: list[str], k: int = TOP_K) -> None:
    print(f"\n{'='*70}")
    print(f"RETRIEVAL TEST  (top-{k} results per query)")
    print(f"{'='*70}")

    for query in queries:
        print(f"\nQUERY: {query}")
        print("-" * 70)
        results = retrieve(query, k=k)
        for rank, chunk in enumerate(results, 1):
            distance_flag = "OK" if chunk["distance"] < 0.5 else "HIGH"
            print(f"  [{rank}] dist={chunk['distance']} {distance_flag}  source={chunk['source']}")
            # Print first 220 chars of the chunk so we can judge relevance
            preview = chunk["text"].replace("\n", " ")[:220]
            print(f"      {preview}...")
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default=None,
                        help="Run a single ad-hoc retrieval query")
    parser.add_argument("--rebuild", action="store_true",
                        help="Force rebuild even if chroma_db already exists")
    args = parser.parse_args()

    # Build or reuse the vector store
    already_built = (
        os.path.exists(CHROMA_DIR)
        and not args.rebuild
    )

    if already_built:
        collection = get_collection()
        count = collection.count()
        if count > 0:
            print(f"Vector store already exists ({count} chunks). Use --rebuild to regenerate.")
        else:
            build_vector_store()
    else:
        build_vector_store()

    # Run test
    if args.query:
        print(f"\nQUERY: {args.query}")
        print("-" * 70)
        for rank, chunk in enumerate(retrieve(args.query), 1):
            print(f"  [{rank}] dist={chunk['distance']}  source={chunk['source']}")
            print(f"      {chunk['text'].replace(chr(10), ' ')[:300]}...")
    else:
        run_retrieval_test(EVAL_QUERIES[:3])  # test first 3 eval queries
