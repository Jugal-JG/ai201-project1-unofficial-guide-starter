# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Off-campus housing in Gainesville, FL for University of Florida students. This knowledge is hard to find through official channels because UF's housing office only covers on-campus options, while the real student experience — which complexes have mold problems, which landlords ignore maintenance requests, which neighborhoods flood, and what a fair price looks like — lives scattered across Reddit threads, Yelp reviews, ApartmentRatings posts, and word of mouth. A student trying to lease their first apartment has no single place to compare neighborhoods, bus access, price ranges, and landlord reputation at once.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | UF Off Campus Life — Housing Resources | Official UF off-campus housing portal with listings, tenant rights info, and neighborhood guides | https://offcampus.ufl.edu/resources/off-campus-housing/ |
| 2 | Off Campus Universe — UF Housing Guide | Comprehensive student-written guide covering neighborhoods, pricing, and lease tips for Gainesville | https://www.offcampus-universe.com/post/student-apartments-gainesville-fl-where-to-live-off-campus-at-uf |
| 3 | Sweetwater Gainesville — Best Student Apartments Guide | Ranked list of top student apartment complexes near UF with amenity comparisons and pricing tiers | https://sweetwatergainesville.com/resources/best-student-apartments-uf-gainesville/ |
| 4 | Sweetwater Gainesville — Freshman Housing Guide | Advice for first-year students navigating on-campus vs off-campus decisions, updated for 2026 | https://sweetwatergainesville.com/resources/freshman-uf-housing/ |
| 5 | prked.com — Ultimate UF Off-Campus Housing Guide | Detailed guide covering neighborhoods, Archer Road corridor, lease timing, and commute options | https://prked.com/post/the-ultimate-university-of-florida-off-campus-housing-guide |
| 6 | Off Campus Universe — UF Off-Campus Housing Guide | Covers RTS bus routes, neighborhood safety, and walkability for UF students | https://www.offcampus-universe.com/post/uf-off-campus-housing-guide-for-students-in-gainesville |
| 7 | Swamp Rentals — Apartments on Bus Routes | Lists Gainesville apartments served by RTS campus bus routes with route numbers | https://www.swamprentals.com/uf-parent-guide/apartments-in-gainesville-on-bus-route |
| 8 | UF TAPS — Transportation & Parking | Official UF commuter and transit resource explaining the free RTS bus benefit for students | https://offcampus.ufl.edu/resources/transportation/ |
| 9 | ApartmentRatings — Gainesville Place Apartments | Tenant reviews of a major student complex covering maintenance, staff, and living conditions | https://www.apartmentratings.com/fl/gainesville/gainesville-place-apartments_352271313132608/ |
| 10 | Yelp — Student Apartments Gainesville FL | Aggregated student reviews of multiple Gainesville apartment complexes | https://www.yelp.com/search?find_desc=Student+Apartments&find_loc=Gainesville,+FL |
| 11 | Yelp — UF Apartments Gainesville FL | Broader Yelp apartment search for UF-area complexes with ratings and reviews | https://www.yelp.com/search?find_desc=Uf+Apartments&find_loc=Gainesville%2C+FL |
| 12 | ForRentUniversity — UF Off-Campus Housing | Aggregator listing apartments near UF with pricing, photos, and availability filters | https://www.forrentuniversity.com/University-of-Florida |
| 13 | Quora — Best Areas in Gainesville for UF Students | Community Q&A covering neighborhood comparisons from current and former UF students | https://www.quora.com/What-areas-of-Gainsville-are-the-most-pleasant-to-live-for-a-UF-student |
| 14 | UF PHHP — Living in Gainesville | Graduate student-focused housing and neighborhood guide from UF's College of Public Health | https://phhp.ufl.edu/admissions/living-in-gainesville/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
