"""
ingest.py
---------
Milestone 3: Document pipeline for the UF Off-Campus Housing Unofficial Guide.

Stages:
  1. Load all .txt files from documents/
  2. Clean each document (strip source header, normalize whitespace)
  3. Chunk with a character-based sliding window (size=500, overlap=100)
  4. Print 5 sample chunks for inspection
  5. Report total chunk count

Run:
    python ingest.py

The list of chunks returned by build_chunks() will be imported by
embed.py (Milestone 4) to embed and store in ChromaDB.
"""

import os
import random
import re

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 500      # characters — fits most reviews whole; splits guides by topic
CHUNK_OVERLAP = 100  # characters — keeps apartment name + key fact in the same chunk


# ---------------------------------------------------------------------------
# Stage 1 & 2: Load and clean
# ---------------------------------------------------------------------------

def load_documents(docs_dir: str = DOCUMENTS_DIR) -> list[dict]:
    """
    Load every .txt file in docs_dir.
    Returns a list of {"text": str, "source": str} dicts.
    """
    docs = []
    for fname in sorted(os.listdir(docs_dir)):
        if not fname.endswith(".txt") or fname == ".gitkeep":
            continue
        path = os.path.join(docs_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        text = clean(raw)
        if len(text) < 50:
            print(f"  [warn] {fname} produced fewer than 50 chars after cleaning — skipping")
            continue
        docs.append({"text": text, "source": fname})
    return docs


def clean(text: str) -> str:
    """
    Remove boilerplate from our .txt files:
    - The "SOURCE: <url>" header line we prepended during fetch
    - HTML entities left over from BeautifulSoup extraction
    - Repeated dashes/equals used as visual separators
    - Leading/trailing whitespace on each line
    - Sequences of 3+ blank lines collapsed to one
    """
    # Drop the SOURCE header line
    text = re.sub(r"^SOURCE:.*\n\n?", "", text, flags=re.MULTILINE)

    # HTML entities
    html_entities = {
        "&amp;": "&", "&nbsp;": " ", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&apos;": "'", "&#x27;": "'",
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Lines that are purely dashes, equals, or asterisks (visual separators)
    text = re.sub(r"^[-=*]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Strip each line
    lines = [ln.strip() for ln in text.splitlines()]

    # Remove lines that are too short to be content (single words, stray chars)
    lines = [ln for ln in lines if len(ln) >= 4 or ln == ""]

    # Collapse 3+ consecutive blank lines to one blank line
    cleaned: list[str] = []
    blank_run = 0
    for ln in lines:
        if ln == "":
            blank_run += 1
            if blank_run <= 1:
                cleaned.append(ln)
        else:
            blank_run = 0
            cleaned.append(ln)

    return "\n".join(cleaned).strip()


# ---------------------------------------------------------------------------
# Stage 3: Chunk
# ---------------------------------------------------------------------------

def chunk_text(text: str, source: str,
               size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Character-based sliding window chunker.

    Returns a list of {"text": str, "source": str, "chunk_id": str} dicts.
    Empty or whitespace-only chunks are dropped.
    """
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + size
        chunk_text_str = text[start:end].strip()
        if chunk_text_str:
            chunks.append({
                "text": chunk_text_str,
                "source": source,
                "chunk_id": f"{source}::chunk_{idx:04d}",
            })
            idx += 1
        start += size - overlap  # slide forward by (size - overlap)
    return chunks


def build_chunks(docs_dir: str = DOCUMENTS_DIR) -> list[dict]:
    """Load, clean, and chunk all documents. Returns flat list of chunk dicts."""
    docs = load_documents(docs_dir)
    all_chunks: list[dict] = []
    for doc in docs:
        chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(chunks)
    return all_chunks


# ---------------------------------------------------------------------------
# Inspection helpers
# ---------------------------------------------------------------------------

def print_sample_chunks(chunks: list[dict], n: int = 5, seed: int = 42) -> None:
    random.seed(seed)
    sample = random.sample(chunks, min(n, len(chunks)))
    print(f"\n{'='*70}")
    print(f"SAMPLE CHUNKS (randomly selected {len(sample)} of {len(chunks)} total)")
    print(f"{'='*70}")
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} | source: {chunk['source']} | id: {chunk['chunk_id']} ---")
        print(chunk["text"])
    print(f"\n{'='*70}")


def chunk_stats(chunks: list[dict]) -> None:
    lengths = [len(c["text"]) for c in chunks]
    by_source: dict[str, int] = {}
    for c in chunks:
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1

    print(f"\nCHUNK STATISTICS")
    print(f"  Total chunks   : {len(chunks)}")
    print(f"  Min length     : {min(lengths)} chars")
    print(f"  Max length     : {max(lengths)} chars")
    print(f"  Avg length     : {sum(lengths)//len(lengths)} chars")
    print(f"\n  Chunks per document:")
    for src, count in sorted(by_source.items()):
        print(f"    {src:<50} {count:>4} chunks")

    if len(chunks) < 50:
        print("\n  [warn] Fewer than 50 chunks — chunks may be too large or documents too short.")
    elif len(chunks) > 2000:
        print("\n  [warn] More than 2000 chunks — chunks may be too small.")
    else:
        print(f"\n  [ok] Chunk count is in the healthy 50–2000 range.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading and cleaning documents...")
    docs = load_documents()
    print(f"  Loaded {len(docs)} documents")

    print("\nChunking documents...")
    all_chunks = build_chunks()

    print_sample_chunks(all_chunks, n=5)
    chunk_stats(all_chunks)
