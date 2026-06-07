"""
app.py
------
Milestone 5: Flask web interface for the UF Off-Campus Housing Guide.

Mobile-first design — works on phones, tablets, and laptops.

Run:
    python app.py
Then open: http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template_string

from generate import ask

app = Flask(__name__)

# ---------------------------------------------------------------------------
# HTML template — single-file, no external JS frameworks
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>UF Housing Guide</title>
  <style>
    /* ---- Reset & base ---- */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --gator-blue:   #003087;
      --gator-orange: #FA4616;
      --bg:           #f4f6fb;
      --card:         #ffffff;
      --border:       #dde3ef;
      --text:         #1a1a2e;
      --muted:        #6b7280;
      --radius:       14px;
      --shadow:       0 4px 24px rgba(0,48,135,0.09);
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }

    /* ---- Header ---- */
    header {
      background: var(--gator-blue);
      padding: 18px 20px 14px;
      text-align: center;
    }
    header h1 {
      color: #fff;
      font-size: clamp(1.1rem, 4vw, 1.55rem);
      font-weight: 700;
      letter-spacing: -0.3px;
    }
    header p {
      color: rgba(255,255,255,0.75);
      font-size: 0.82rem;
      margin-top: 4px;
    }
    .orange-bar {
      height: 4px;
      background: var(--gator-orange);
    }

    /* ---- Main layout ---- */
    main {
      max-width: 760px;
      margin: 0 auto;
      padding: 24px 16px 48px;
    }

    /* ---- Search card ---- */
    .search-card {
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 22px 20px;
      margin-bottom: 22px;
    }
    .search-card label {
      display: block;
      font-weight: 600;
      font-size: 0.9rem;
      margin-bottom: 10px;
      color: var(--gator-blue);
    }
    .input-row {
      display: flex;
      gap: 10px;
    }
    textarea {
      flex: 1;
      border: 1.5px solid var(--border);
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 0.95rem;
      resize: none;
      font-family: inherit;
      transition: border-color 0.2s;
      min-height: 60px;
    }
    textarea:focus { outline: none; border-color: var(--gator-blue); }
    button#ask-btn {
      background: var(--gator-orange);
      color: #fff;
      border: none;
      border-radius: 10px;
      padding: 0 22px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
      white-space: nowrap;
    }
    button#ask-btn:hover  { background: #d93d10; }
    button#ask-btn:active { transform: scale(0.97); }
    button#ask-btn:disabled { background: #aaa; cursor: not-allowed; }

    /* ---- Suggestion chips ---- */
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }
    .chip {
      background: #eef1f9;
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 5px 13px;
      font-size: 0.78rem;
      color: var(--gator-blue);
      cursor: pointer;
      transition: background 0.15s;
    }
    .chip:hover { background: #dde4f5; }

    /* ---- Answer card ---- */
    .answer-card {
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 22px 20px;
      display: none;
      animation: fadeIn 0.3s ease;
    }
    .answer-card.visible { display: block; }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .answer-label {
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .answer-text {
      font-size: 0.97rem;
      line-height: 1.7;
      white-space: pre-wrap;
      color: var(--text);
    }

    /* ---- Sources section ---- */
    .sources-section {
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
    }
    .sources-label {
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }
    .source-pill {
      display: inline-block;
      background: #eef7f0;
      border: 1px solid #b6dfc1;
      color: #1a5c2e;
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 0.78rem;
      margin: 3px 4px 3px 0;
    }

    /* ---- Chunks debug section ---- */
    details.chunks-debug {
      margin-top: 16px;
      border-top: 1px solid var(--border);
      padding-top: 12px;
    }
    details summary {
      font-size: 0.8rem;
      color: var(--muted);
      cursor: pointer;
      user-select: none;
    }
    .chunk-item {
      background: #f9fafc;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      margin-top: 8px;
      font-size: 0.78rem;
      line-height: 1.6;
    }
    .chunk-meta {
      font-weight: 600;
      color: var(--gator-blue);
      margin-bottom: 4px;
    }

    /* ---- Loading spinner ---- */
    .spinner {
      display: none;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 0.88rem;
      margin-top: 16px;
    }
    .spinner.visible { display: flex; }
    .dot-flashing {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--gator-orange);
      animation: dotFlash 1s infinite alternate;
    }
    .dot-flashing:nth-child(2) { animation-delay: 0.2s; }
    .dot-flashing:nth-child(3) { animation-delay: 0.4s; }
    @keyframes dotFlash {
      from { opacity: 0.2; } to { opacity: 1; }
    }

    /* ---- Footer ---- */
    footer {
      text-align: center;
      padding: 24px 16px;
      font-size: 0.75rem;
      color: var(--muted);
    }
  </style>
</head>
<body>

<header>
  <h1>&#127968; UF Off-Campus Housing Guide</h1>
  <p>Ask anything about renting near the University of Florida, Gainesville</p>
</header>
<div class="orange-bar"></div>

<main>
  <div class="search-card">
    <label for="question">What do you want to know?</label>
    <div class="input-row">
      <textarea id="question" rows="2"
        placeholder="e.g. Which apartments on 34th Street have bus access to UF?"></textarea>
      <button id="ask-btn" onclick="submitQuery()">Ask</button>
    </div>
    <div class="chips">
      <span class="chip" onclick="setQuery(this)"
        data-query="Which RTS bus routes serve apartments on the SW 34th Street corridor?">
        Bus routes on 34th Street
      </span>
      <span class="chip" onclick="setQuery(this)"
        data-query="What is the typical monthly rent per person for a 4-bedroom apartment near UF campus in Gainesville?">
        Rent for a 4-bedroom near UF
      </span>
      <span class="chip" onclick="setQuery(this)"
        data-query="When should UF students start apartment hunting to secure a unit for the fall semester?">
        When to start apartment hunting
      </span>
      <span class="chip" onclick="setQuery(this)"
        data-query="What do residents say about maintenance response times at Stoneridge Apartments on SW 34th Street?">
        Stoneridge maintenance reviews
      </span>
      <span class="chip" onclick="setQuery(this)"
        data-query="Which Gainesville neighborhoods are walkable to UF campus without needing a car or bus?">
        Walkable neighborhoods near campus
      </span>
      <span class="chip" onclick="setQuery(this)"
        data-query="Which apartments on SW 34th Street in Gainesville are popular with Indian and South Asian students near UF?">
        Indian community apartments
      </span>
    </div>
    <div class="spinner" id="spinner">
      <div class="dot-flashing"></div>
      <div class="dot-flashing"></div>
      <div class="dot-flashing"></div>
      <span>Searching documents&hellip;</span>
    </div>
  </div>

  <div class="answer-card" id="answer-card">
    <div class="answer-label">Answer</div>
    <div class="answer-text" id="answer-text"></div>

    <div class="sources-section">
      <div class="sources-label">Retrieved from</div>
      <div id="sources-list"></div>
    </div>

    <details class="chunks-debug">
      <summary>Show retrieved chunks (debug)</summary>
      <div id="chunks-list"></div>
    </details>
  </div>
</main>

<footer>
  Answers are grounded in collected student reviews and housing guides &mdash;
  always verify details with the landlord before signing a lease.
</footer>

<script>
  function setQuery(el) {
    // Use data-query attribute if present, else fall back to visible text
    const q = el.getAttribute("data-query") || el.textContent.trim();
    document.getElementById("question").value = q;
    submitQuery();
  }

  function submitQuery() {
    const q = document.getElementById("question").value.trim();
    if (!q) return;

    const btn     = document.getElementById("ask-btn");
    const spinner = document.getElementById("spinner");
    const card    = document.getElementById("answer-card");

    btn.disabled = true;
    spinner.classList.add("visible");
    card.classList.remove("visible");

    fetch("/ask", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ question: q }),
    })
    .then(r => r.json())
    .then(data => {
      document.getElementById("answer-text").textContent = data.answer;

      const srcEl = document.getElementById("sources-list");
      srcEl.innerHTML = data.sources
        .map(s => `<span class="source-pill">${s}</span>`)
        .join("");

      const chunkEl = document.getElementById("chunks-list");
      chunkEl.innerHTML = data.chunks.map((c, i) => `
        <div class="chunk-item">
          <div class="chunk-meta">#${i+1} &mdash; ${c.source} &mdash; dist: ${c.distance}</div>
          ${escapeHtml(c.text.slice(0, 300))}${c.text.length > 300 ? "&hellip;" : ""}
        </div>
      `).join("");

      card.classList.add("visible");
    })
    .catch(err => {
      document.getElementById("answer-text").textContent =
        "Something went wrong. Please try again.";
      card.classList.add("visible");
    })
    .finally(() => {
      btn.disabled = false;
      spinner.classList.remove("visible");
    });
  }

  function escapeHtml(str) {
    return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  // Submit on Enter (Shift+Enter for newline)
  document.getElementById("question").addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitQuery();
    }
  });
</script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/ask", methods=["POST"])
def ask_route():
    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    result = ask(question)
    return jsonify({
        "answer":  result["answer"],
        "sources": result["sources"],
        "chunks":  [
            {
                "source":   c["source"],
                "distance": c["distance"],
                "text":     c["text"],
            }
            for c in result["chunks"]
        ],
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting UF Housing Guide at http://localhost:5000")
    app.run(debug=True, port=5000)
