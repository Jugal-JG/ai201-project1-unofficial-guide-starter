"""
generate.py
-----------
Milestone 5: Grounded answer generation using Groq (llama-3.3-70b-versatile).

Pipeline stage: Retrieval -> Generation

The system prompt hard-enforces grounding: the model is explicitly told to
answer ONLY from the provided context and to say "I don't have enough
information" when the context is insufficient. Source attribution is also
programmatically guaranteed — retrieved source filenames are always appended
to the response regardless of what the model says.

Public API:
    ask(question) -> {"answer": str, "sources": list[str], "chunks": list[dict]}
"""

import os
from groq import Groq
from dotenv import load_dotenv
from embed import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5

# Human-readable source labels (strips numbering prefix and .txt suffix)
def _label(source: str) -> str:
    name = source.replace(".txt", "").replace("_", " ")
    # Drop the leading number prefix e.g. "01 uf offcampus housing" -> "uf offcampus housing"
    parts = name.split(" ", 1)
    if parts[0].isdigit():
        name = parts[1] if len(parts) > 1 else name
    return name.title()


SYSTEM_PROMPT = """\
You are the UF Off-Campus Housing Guide — a helpful assistant that answers \
questions about renting apartments in Gainesville, FL near the University of Florida.

STRICT GROUNDING RULE:
- Answer ONLY using information from the CONTEXT DOCUMENTS provided below.
- Do NOT use your general training knowledge about Gainesville, UF, or apartments.
- If the context documents do not contain enough information to answer the question, \
respond with exactly: "I don't have enough information in my documents to answer that."
- Never fabricate prices, addresses, bus routes, or reviews not present in the context.

RESPONSE FORMAT:
- Give a clear, direct answer in 2-5 sentences.
- Where possible, include specific facts (prices, distances, route numbers, complex names).
- End with a "Sources:" line listing the document names you drew from.
"""


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        label = _label(chunk["source"])
        parts.append(f"[Document {i} — {label}]\n{chunk['text']}")
    return "\n\n".join(parts)


def ask(question: str, k: int = TOP_K) -> dict:
    """
    Retrieve top-k chunks for the question, then generate a grounded answer.

    Returns:
        {
            "answer":  str,          # LLM response text
            "sources": list[str],    # unique source filenames (programmatic)
            "chunks":  list[dict],   # raw retrieved chunks with distances
        }
    """
    chunks = retrieve(question, k=k)
    context = build_context(chunks)

    user_message = f"CONTEXT DOCUMENTS:\n{context}\n\nQUESTION: {question}"

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,   # low temperature keeps answers factual and consistent
        max_tokens=512,
    )

    answer_text = response.choices[0].message.content.strip()

    # Programmatically guaranteed source list — always present regardless of model output
    seen = []
    for chunk in chunks:
        label = _label(chunk["source"])
        if label not in seen:
            seen.append(label)

    return {
        "answer":  answer_text,
        "sources": seen,
        "chunks":  chunks,
    }


# ---------------------------------------------------------------------------
# Quick CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "Which RTS bus routes serve apartments on the SW 34th Street corridor?",
        "What do residents say about maintenance at Stoneridge Apartments?",
        "When should UF students start apartment hunting for fall semester?",
        # Out-of-scope query — should get "I don't have enough information"
        "What are the best Thai restaurants near UF campus?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("-" * 70)
        result = ask(q)
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources'])}")
