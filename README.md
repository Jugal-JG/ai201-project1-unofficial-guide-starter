# UF Off-Campus Housing Unofficial Guide

A retrieval-augmented generation (RAG) system that answers questions about off-campus housing in Gainesville, FL for University of Florida students. Ask it about rent prices, bus routes, apartment reviews, neighborhoods, and which complexes are popular with the Indian student community — and get grounded answers cited to real documents.

**GitHub:** https://github.com/Jugal-JG/ai201-project1-unofficial-guide-starter  
**Demo Video:** https://drive.google.com/file/d/1ls-RJvFhqUwKJivR0duEa60JBQtvfJR3/view?usp=sharing  
**Run the app:** `python app.py` → open `http://localhost:5000`

---

## Domain

**Off-campus housing in Gainesville, FL for University of Florida students.**

UF's official housing office covers only on-campus dormitories. The real student experience — which complexes have maintenance problems, which landlords ignore requests, which neighborhoods flood, how much rent really costs, and which areas have Indian grocery access — is scattered across Yelp reviews, Reddit threads, ApartmentRatings posts, student guides, and word of mouth. A first-year student trying to sign their first lease has no single place to compare neighborhoods, bus access, pricing, and landlord reputation.

This system makes that scattered knowledge searchable. A student can ask "which apartments near 34th Street are popular with Indian students?" or "when should I start apartment hunting?" and get a grounded, cited answer drawn from real sources rather than generic LLM knowledge.

---

## Document Sources

| # | Source | Type | URL |
|---|--------|------|-----|
| 1 | UF Off Campus Life — Housing Resources | Official UF portal | https://offcampus.ufl.edu/resources/off-campus-housing/ |
| 2 | Off Campus Universe — UF Housing Guide | Student guide | https://www.offcampus-universe.com/post/student-apartments-gainesville-fl-where-to-live-off-campus-at-uf |
| 3 | Sweetwater Gainesville — Best Student Apartments | Ranked guide | https://sweetwatergainesville.com/resources/best-student-apartments-uf-gainesville/ |
| 4 | Sweetwater Gainesville — Freshman Housing Guide | Student guide | https://sweetwatergainesville.com/resources/freshman-uf-housing/ |
| 5 | prked.com — Ultimate UF Off-Campus Housing Guide | Detailed guide | https://prked.com/post/the-ultimate-university-of-florida-off-campus-housing-guide |
| 6 | Off Campus Universe — UF Off-Campus Housing Guide 2 | Student guide | https://www.offcampus-universe.com/post/uf-off-campus-housing-guide-for-students-in-gainesville |
| 7 | Swamp Rentals — Apartments on Bus Routes | Bus route guide | https://www.swamprentals.com/uf-parent-guide/apartments-in-gainesville-on-bus-route |
| 8 | UF TAPS — Transportation & Parking | Official UF resource | https://offcampus.ufl.edu/resources/transportation/ |
| 9 | ApartmentRatings — Gainesville Place Apartments | Tenant reviews | https://www.apartmentratings.com/fl/gainesville/gainesville-place-apartments_352271313132608/ |
| 10 | Yelp — Student Apartments Gainesville FL | Aggregated reviews | https://www.yelp.com/search?find_desc=Student+Apartments&find_loc=Gainesville,+FL |
| 11 | Yelp — UF Apartments Gainesville FL | Aggregated reviews | https://www.yelp.com/search?find_desc=Uf+Apartments&find_loc=Gainesville%2C+FL |
| 12 | ForRentUniversity — UF Off-Campus Housing | Listing aggregator | https://www.forrentuniversity.com/University-of-Florida |
| 13 | Quora — Best Areas in Gainesville for UF Students | Community Q&A | https://www.quora.com/What-areas-of-Gainsville-are-the-most-pleasant-to-live-for-a-UF-student |
| 14 | UF PHHP — Living in Gainesville | Grad student guide | https://phhp.ufl.edu/admissions/living-in-gainesville/ |
| 15 | Stoneridge Apartments | Complex website | https://www.stoneridgegainesville.com/ |
| 16 | Centric on 34th Apartments | Complex website | https://centricaptsgainesville.com/ |
| 17 | The Quarters Gainesville | Complex website | https://thequartersgainesville.com/ |
| 18 | Greenwich Green Apartments | Complex website | https://www.greenwichgreen.net/ |

**Collection method:** 9 documents were fetched automatically using `fetch_documents.py` (requests + BeautifulSoup). 9 documents required manual collection because the sites use JavaScript rendering or block automated requests (Yelp, Quora, ApartmentRatings, ForRentUniversity, and the apartment complex sites). Manual documents were written from verified research data gathered during the collection phase.

---

## How to Run

```bash
# 1. Clone and set up environment
git clone https://github.com/Jugal-JG/ai201-project1-unofficial-guide-starter.git
cd ai201-project1-unofficial-guide-starter
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# 2. Add your Groq API key
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here
# Free key at https://console.groq.com

# 3. Build the vector store (run once)
python embed.py

# 4. Launch the web app
python app.py
# Open http://localhost:5000
```

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit the documents:**

The corpus is a mix of two document types. Short Yelp and ApartmentRatings reviews are typically 100–400 characters (1–4 sentences), so a 500-character chunk keeps most individual reviews intact rather than splitting them mid-sentence. Long student guides (prked.com, Sweetwater, Off Campus Universe) run several paragraphs; 500 characters breaks these into roughly one coherent topic per chunk — one chunk covers bus routes, the next covers pricing — which maps well to the narrow factual questions users ask.

The 100-character overlap handles boundary fragmentation: if a review names a complex at the end of one chunk and gives its maintenance rating at the start of the next, the overlap ensures at least one chunk carries both pieces, making it retrievable for a query like "Stoneridge maintenance issues."

**Preprocessing before chunking:**
- Stripped `SOURCE: <url>` header line prepended during fetch
- Replaced HTML entities (`&amp;`, `&nbsp;`, `&#39;`, etc.)
- Removed lines consisting only of dashes/equals (visual separators)
- Dropped lines shorter than 4 characters (stray nav remnants)
- Collapsed 3+ consecutive blank lines to one

**Final chunk count:** 258 chunks across 18 documents (avg 484 chars/chunk)

---

## Sample Chunks

Each chunk below is from a real document in `documents/`. Every chunk should be readable and answerable on its own.

**Chunk 1 — `07_swamprentals_bus_routes.txt`** *(bus route information)*
```
The most student-friendly bus routes along the SW 34th Street and Archer Road
corridors include:
- Route 1: Runs along University Avenue and connects the main campus entrance
  to downtown and west Gainesville.
- Route 9: Serves the SW 34th Street corridor and connects to the Reitz Union
  bus depot on campus.
- Route 35: Serves SW 34th Street and Butler Plaza area.
- Route 38: Connects apartments along SW 34th Street to the Health Science Center.
```

**Chunk 2 — `09_apartmentratings_gainesville_place.txt`** *(tenant review)*
```
"Maintenance is hit or miss. Small things like a broken light fixture or a
dripping faucet can take 2–3 weeks to get addressed. For an urgent issue like
an AC failure in Florida summer, they were actually responsive and had it fixed
within 24 hours."
```

**Chunk 3 — `13_quora_gainesville_areas.txt`** *(neighborhood comparison)*
```
University Avenue Corridor (0–0.5 miles from campus)
This is the closest you can get to campus. Complexes like Sweetwater, Lark, and
The Standard are here. The walkability is unbeatable — you're 5–10 minutes on
foot from most classroom buildings. The downside is price: expect to pay
$900–$1,300/month per person.
```

**Chunk 4 — `13_quora_gainesville_areas.txt`** *(Indian student community)*
```
The 34th Street area between Archer Road and SW 39th Blvd has become the de
facto hub for UF's South Asian student community. Complexes like Stoneridge,
Centric on 34th, Greenwich Green, and The Quarters have high concentrations of
Indian, Pakistani, and Bangladeshi graduate students. Students organize
WhatsApp groups for finding roommates, sharing rides, and grocery runs to
Patel Brothers and Apna Bazar on Archer Road.
```

**Chunk 5 — `06_offcampus_universe_guide2.txt`** *(pricing)*
```
$850 to $1,200 per month. One-bedroom units average $1,000 to $1,400. Shared
two-bedroom apartments can bring individual costs to $600 to $900 per person,
making roommate arrangements highly popular among undergraduates managing
tuition and living costs simultaneously.
```

**Chunk 6 — `04_sweetwater_freshman_guide.txt`** *(lease timing)*
```
With acceptances coming out in late February, the housing process can be
competitive, especially for student apartments. Since you're competing with the
upperclassmen who already know the area, it's important to start looking early.
The best student apartments Gainesville FL — especially close to UF campus —
get leased in February, so early signing is recommended.
```

**Chunk 7 — `12_forrentuniversity_uf.txt`** *(4BR pricing)*
```
4 Bedroom / 4 Bathroom (furnished):
- Square footage: approximately 1,400 sq ft
- Per-person rent: $560–$680/month (2025 rates, all-inclusive)
- This is one of the most affordable per-person options in the Gainesville
  student market
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key)

**Why this model:** It is fast, free, runs entirely on-device with no API cost or rate limits, and produces 384-dimensional embeddings that capture semantic meaning well for short-to-medium English text. At our corpus size (258 chunks), local inference takes under 5 seconds on CPU.

**Production tradeoff reflection:**

In a real deployment I would evaluate the following alternatives:

| Factor | all-MiniLM-L6-v2 (current) | text-embedding-3-large (OpenAI) | e5-large-v2 |
|--------|----------------------------|---------------------------------|-------------|
| **Context length** | 256 tokens (truncates longer chunks) | 8,191 tokens | 512 tokens |
| **Accuracy** | Good for general English | Higher accuracy on domain-specific text | Strong on retrieval benchmarks |
| **Cost** | Free, local | ~$0.13/million tokens | Free, local |
| **Latency** | ~5ms/chunk locally | ~80ms/chunk (network) | ~25ms/chunk locally |
| **Multilingual** | English only | 100+ languages | Primarily English |

The biggest production concern is **context length**: MiniLM truncates at 256 tokens (~1,000 chars). Our 500-char chunks are near that limit. If chunk size increases, MiniLM starts truncating meaningful content and retrieval quality drops. `e5-large-v2` with its 512-token window would be the best free upgrade. For multilingual support (serving international students who search in Hindi, Telugu, or Gujarati), a multilingual model like `paraphrase-multilingual-MiniLM-L12-v2` would be necessary.

---

## Retrieval Test Results

**Setup:** ChromaDB with cosine similarity, top-k=8, model `all-MiniLM-L6-v2`. Distances below 0.5 are considered strong matches.

---

**Query 1:** *"Which RTS bus routes serve apartments on the SW 34th Street corridor?"*

| Rank | Source | Distance |
|------|--------|----------|
| 1 | `07_swamprentals_bus_routes.txt` | 0.2709 |
| 2 | `16_centric_on_34th.txt` | 0.2904 |
| 3 | `07_swamprentals_bus_routes.txt` | 0.3037 |
| 4 | `11_yelp_uf_apartments.txt` | 0.3724 |
| 5 | `16_centric_on_34th.txt` | 0.3735 |

**Why the top results are relevant:** Chunks #1 and #3 are from the SwampRentals bus route guide, which explicitly lists Routes 9, 35, 38 serving 34th Street — a direct textual match. Chunk #2 (Centric on 34th) is relevant because it mentions the 34th Street RTS stop by name and its connection to campus. All top results score below 0.40, indicating strong semantic alignment.

---

**Query 2:** *"Which Gainesville neighborhoods are walkable to UF campus without needing a car or bus?"*

| Rank | Source | Distance |
|------|--------|----------|
| 1 | `13_quora_gainesville_areas.txt` | 0.2276 |
| 2 | `06_offcampus_universe_guide2.txt` | 0.2428 |
| 3 | `02_offcampus_universe_guide.txt` | 0.2513 |
| 4 | `10_yelp_student_apartments.txt` | 0.2667 |
| 5 | `14_uf_phhp_living.txt` | 0.2805 |

**Why the top results are relevant:** Chunk #1 (Quora) is a detailed neighborhood breakdown explicitly comparing walkability distances — "5–10 minutes on foot" for University Ave, "15–20 minute walk" for Midtown. Chunk #2 and #3 both discuss Midtown and the Archer Road corridor's transit characteristics. The entire top-5 scored below 0.30, the strongest retrieval performance of any query.

---

**Query 3:** *"What do residents say about maintenance response times at Stoneridge Apartments?"*

| Rank | Source | Distance |
|------|--------|----------|
| 1 | `11_yelp_uf_apartments.txt` | 0.4536 |
| 2 | `09_apartmentratings_gainesville_place.txt` | 0.4769 |
| 3 | `11_yelp_uf_apartments.txt` | 0.5004 |
| 4 | `10_yelp_student_apartments.txt` | 0.5159 |
| 5 | `15_stoneridge_apartments.txt` | 0.5642 |

**Note:** This query produces the highest distances of all five. The Stoneridge website document (source #5, rank 8) is the official property page and has no tenant reviews — it ranks weakly because it doesn't contain the word "maintenance." Chunk #3 from Yelp does mention Stoneridge by name with a maintenance comment, but ranks 3rd. The distances (0.45–0.56) are near the 0.5 warning threshold, which is the honest failure case discussed below.

---

## Grounded Generation

**LLM:** `llama-3.3-70b-versatile` via Groq API (`GROQ_API_KEY` in `.env`)  
**Temperature:** 0.2 (low — keeps answers factual, reduces hallucination risk)

**System prompt grounding instruction** (from `generate.py`):

```
You are the UF Off-Campus Housing Guide — a helpful assistant that answers
questions about renting apartments in Gainesville, FL near the University of Florida.

STRICT GROUNDING RULE:
- Answer ONLY using information from the CONTEXT DOCUMENTS provided below.
- Do NOT use your general training knowledge about Gainesville, UF, or apartments.
- If the context documents do not contain enough information to answer the question,
  respond with exactly: "I don't have enough information in my documents to answer that."
- Never fabricate prices, addresses, bus routes, or reviews not present in the context.
```

The user message wraps retrieved chunks as numbered `[Document N — Source Name]` blocks, followed by the question. This structure makes the boundary between context and question explicit.

**How source attribution is enforced:**

Source attribution is **programmatically guaranteed** — it is not left to the model to add on its own. After generation, `generate.py` builds the `sources` list by iterating the retrieved chunk metadata and deduplicating by source filename. The Flask app renders these as pill badges in the UI regardless of whether the model mentioned sources in its prose. Even if the model omits a citation, the user always sees which documents were retrieved.

---

## Example Responses

**Example 1 — Bus routes query (strong retrieval + grounded answer):**

> **Q:** Which RTS bus routes serve apartments on the SW 34th Street corridor?
>
> **A:** The SW 34th Street corridor is served by several RTS bus routes, including Routes 9, 35, and 38. Route 9 connects the SW 34th Street corridor to the Reitz Union bus depot on campus, while Route 35 serves SW 34th Street and the Butler Plaza area. Route 38 connects apartments along SW 34th Street to the Health Science Center.
>
> **Sources:** Swamprentals Bus Routes, Centric On 34Th, Yelp Uf Apartments, Quora Gainesville Areas

---

**Example 2 — Indian community apartments (grounded, specific):**

> **Q:** Which apartments on SW 34th Street in Gainesville are popular with Indian and South Asian students near UF?
>
> **A:** According to the provided documents, the 34th Street area between Archer Road and SW 39th Blvd has become a hub for UF's South Asian student community. Complexes like Stoneridge, Centric on 34th, Greenwich Green, and The Quarters have high concentrations of international and Indian students. The Quarters, in particular, is a large student-oriented apartment community at 4000 SW 37th Blvd, approximately 2.6 miles from UF.
>
> **Sources:** Offcampus Universe Guide2, Offcampus Universe Guide, The Quarters, Quora Gainesville Areas, Yelp Student Apartments

---

**Example 3 — Out-of-scope query (correct refusal):**

> **Q:** What are the best Thai restaurants near UF campus?
>
> **A:** I don't have enough information in my documents to answer that.
>
> **Sources:** Quora Gainesville Areas, Yelp Uf Apartments, Sweetwater Freshman Guide

The system correctly declined to answer — it retrieved neighborhood-adjacent chunks (which mention restaurants generally) but recognized there was no Thai restaurant content in the context and refused to generate from training knowledge.

---

## Query Interface

**Interface type:** Mobile-first Flask web app (`app.py`)  
**Run:** `python app.py` → `http://localhost:5000`

**Input fields:**
- Textarea — type any question about Gainesville off-campus housing; press Enter or click Ask
- Six quick-question chips — tap to auto-fill and submit a pre-written query

**Output fields:**
- **Answer panel** — LLM-generated response grounded in retrieved documents
- **Retrieved from** — colored pill badges showing which source documents were used
- **Show retrieved chunks (debug)** — expandable panel showing raw chunk text, source filename, and cosine distance score for each of the 8 retrieved chunks

**Sample interaction transcript:**

```
User input:  When should UF students start apartment hunting for fall semester?

System output:
  UF students should start apartment hunting as soon as possible, ideally in
  February, to secure a unit for the fall semester. This is because the best
  apartments near UF lease out between February and May for the following fall
  semester. Waiting until summer often means limited options and higher prices
  on remaining units. It's also common for students to sign leases 12 months
  prior to move-in, so starting early is crucial to getting the best options.

  Sources: Sweetwater Freshman Guide · Offcampus Universe Guide ·
           Forrentuniversity Uf · Uf Offcampus Housing
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which RTS bus routes serve apartments on the SW 34th Street corridor? | Routes 1, 9, 12, 34, 35, 38, 75 serve the corridor; students ride free with UF ID | Named Routes 9, 35, 38; mentioned Route 75 with caveat; cited SwampRentals correctly | Relevant | Partially accurate — Routes 1, 12, 34 not mentioned |
| 2 | What do residents say about maintenance response times at Stoneridge Apartments? | Slow/inconsistent for non-urgent issues; building built 1977 | Correctly stated maintenance is slow for non-urgent; cited 2–3 week delays for small repairs; accurately noted 24hr response for AC emergencies | Partially relevant | Partially accurate — mixed Stoneridge-specific and Gainesville Place reviews |
| 3 | When should UF students start apartment hunting for fall semester? | No later than February; best units lease Feb–May | Correctly said start in February; cited the Feb–May leasing window; mentioned 12-month-early signing | Relevant | Accurate |
| 4 | What is the typical monthly rent per person for a 4-bedroom apartment near UF? | $560–$750/month all-inclusive | Correctly returned $560–$750/month all-inclusive citing The Quarters and ForRentUniversity | Relevant | Accurate |
| 5 | Which Gainesville neighborhoods are walkable to UF without a car or bus? | University Ave corridor (5–10 min walk); Midtown (15–20 min walk); 34th St requires bus/bike | Correctly identified University Ave as walkable (5–10 min); mentioned Midtown; noted East Gainesville requires a longer walk | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 3 fully accurate, 2 partially accurate, 0 inaccurate. The partially accurate responses (Q1 and Q2) trace to the root causes described below.

---

## Failure Case Analysis

**Question that failed (partially):**  
*"What do residents say about maintenance response times at Stoneridge Apartments?"*

**What the system returned:**  
> "Residents at Stoneridge Apartments report that maintenance can be slow for non-urgent issues. According to one review, maintenance can be slow, but another review from a different complex mentions that maintenance requests get handled within a day or two, though it's unclear if this applies to Stoneridge. At Stoneridge, the general sentiment is that maintenance is responsive for urgent issues but slower for less pressing concerns."

The 2–3 week delay detail in the answer actually came from a review of **Gainesville Place Apartments** (`09_apartmentratings_gainesville_place.txt`), not Stoneridge. The model did hedge ("another review from a different complex"), but the answer still partially mis-attributes a different complex's review to Stoneridge.

**Root cause — source contamination at the retrieval stage:**  
The query "maintenance response times at Stoneridge Apartments" produced high cosine distances across the board (0.45–0.56) because Stoneridge has very few tenant-written maintenance reviews in the corpus — the Stoneridge website (`15_stoneridge_apartments.txt`) is a marketing page with no review content, and the Yelp chunk that mentions Stoneridge by name is embedded inside a larger chunk that also contains Trimark Properties reviews. The embedding model cannot separate them at query time.

Because Stoneridge-specific maintenance content is sparse, the retrieval system cast a wide net and returned the second-closest semantic match: a Gainesville Place ApartmentRatings chunk (dist=0.4769) which has detailed maintenance reviews. This chunk was passed to the LLM alongside the genuine Stoneridge Yelp chunk. The model correctly flagged the ambiguity with "another review from a different complex" but still folded the Gainesville Place details into its summary.

**What I would change to fix it:**  
Two approaches: (1) Add more Stoneridge-specific tenant review content to the corpus — the current Stoneridge document is a marketing page, not a review source. Adding reviews from ApartmentRatings or Google Reviews specifically for Stoneridge would give the retrieval system on-target chunks to find. (2) Add apartment complex name as a metadata field on each chunk during ingestion, and filter retrieval to only return chunks whose `complex` metadata matches the complex named in the query. This prevents reviews from a different complex from polluting the context even when cosine distances are high.

---

## Spec Reflection

**One way the spec helped during implementation:**

Writing the evaluation plan in `planning.md` before touching any code forced me to define what "correct" looks like for each query before I could accidentally tune the system to produce the answer I expected. Question 2 (Stoneridge maintenance) had a specific expected answer — "slow/inconsistent for non-urgent issues" — that I could check against the actual response. When the system returned a plausible-sounding answer that mixed in Gainesville Place reviews, the pre-written expected answer made the contamination obvious. Without the spec, a reader might have accepted the response as correct because it hedged appropriately. The spec made the failure visible.

**One way the implementation diverged from the spec, and why:**

The spec called for `top-k = 5` at retrieval. During Milestone 5 testing, two queries ("Rent for a 4-bedroom" and "Indian community apartments") returned "I don't have enough information" even though the answers existed in the corpus — the relevant chunks ranked 6th and 7th. I increased `top-k` to 8. This divergence was necessary: the spec was written before seeing real retrieval scores, and the assumption that 5 chunks would cover the answer space was too conservative for a corpus where multiple closely-scored chunks compete from the same document. The planning.md was updated to reflect the change.

---

## AI Usage

**Instance 1 — Generating the chunking and ingestion pipeline**

*What I gave the AI:* The `## Chunking Strategy` and `## Architecture` sections of `planning.md`, specifying 500-char chunks, 100-char overlap, and a character-based sliding window. I asked Claude to implement `load_documents()` and `chunk_text()` in `ingest.py`.

*What it produced:* A working implementation of both functions with a sliding window chunker and a `clean()` function that stripped HTML entities and visual separators. The `build_chunks()` wrapper and `print_sample_chunks()` inspection helper were also generated.

*What I changed or overrode:* The generated `clean()` function initially used `soup.get_text()` directly without selecting a main content container first, which would have included navigation menus on scraped pages. I added logic to prefer `<main>`, `<article>`, or content-class `<div>` elements before falling back to the full body — matching the actual cleaning requirement for the auto-fetched documents.

---

**Instance 2 — Generating the grounded system prompt and generation layer**

*What I gave the AI:* The `## Grounded Generation` requirement from the milestone instructions (answer only from context, refuse out-of-scope), the Groq SDK usage pattern, and the architecture diagram showing the retrieval→generation flow.

*What it produced:* A `generate.py` with `ask()`, a system prompt, and a `build_context()` function that numbered each retrieved chunk as `[Document N — Source Name]`.

*What I changed or overrode:* The initial system prompt said "try to answer from the provided documents" — a suggestion, not a constraint. I hardened it to "Answer ONLY using information from the CONTEXT DOCUMENTS" and added an explicit instruction to respond with the exact phrase "I don't have enough information in my documents to answer that" for out-of-scope queries. I also moved source attribution from being LLM-generated (prone to omission or hallucination) to programmatically built from chunk metadata — the model's prose may or may not cite sources, but the pill badges in the UI always appear from the retrieval metadata regardless.

---

## Pipeline Architecture

```
documents/*.txt
      |
      v
[Ingestion + Cleaning]          ingest.py: load_documents(), clean()
      |                         - Strip SOURCE headers, HTML entities
      |                         - Drop lines < 4 chars, collapse blanks
      v
[Chunking]                      ingest.py: chunk_text(size=500, overlap=100)
      |                         - Character sliding window
      |                         - Returns {text, source, chunk_id} dicts
      v
[Embedding]                     embed.py: SentenceTransformer(all-MiniLM-L6-v2)
      |                         - 384-dim vectors, local CPU inference
      v
[Vector Store]                  embed.py: ChromaDB persistent collection
      |                         - Cosine distance index
      |                         - Metadata: source filename per chunk
      |
User query
      |
      v
[Retrieval]                     embed.py: retrieve(query, k=8)
      |                         - Embed query, cosine similarity search
      |                         - Returns top-8 chunks + distances
      v
[Generation]                    generate.py: ask(question)
      |                         - System prompt enforces grounding
      |                         - Context = numbered Document blocks
      |                         - Model: llama-3.3-70b-versatile (Groq)
      |                         - Temperature: 0.2
      v
[Interface]                     app.py: Flask + mobile-first HTML/CSS/JS
                                - Answer panel + source pills + chunk debug
```
