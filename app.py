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

    /* ---- Chat thread ---- */
    #chat-thread {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-bottom: 8px;
    }

    /* New chat bar */
    .new-chat-bar {
      display: none;
      justify-content: flex-end;
      margin-bottom: 4px;
    }
    .new-chat-bar.visible { display: flex; }
    button#new-chat-btn {
      background: transparent;
      border: 1.5px solid var(--border);
      border-radius: 20px;
      padding: 5px 16px;
      font-size: 0.8rem;
      color: var(--muted);
      cursor: pointer;
      transition: border-color 0.2s, color 0.2s;
    }
    button#new-chat-btn:hover { border-color: var(--gator-blue); color: var(--gator-blue); }

    /* Individual Q&A turn */
    .turn { animation: fadeIn 0.3s ease; }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* User bubble */
    .user-bubble {
      display: flex;
      justify-content: flex-end;
      margin-bottom: 6px;
    }
    .user-bubble span {
      background: var(--gator-blue);
      color: #fff;
      border-radius: 18px 18px 4px 18px;
      padding: 10px 16px;
      font-size: 0.93rem;
      max-width: 85%;
      line-height: 1.5;
    }

    /* Answer bubble */
    .answer-bubble {
      background: var(--card);
      border-radius: 4px 18px 18px 18px;
      box-shadow: var(--shadow);
      padding: 18px 20px;
    }
    .answer-text {
      font-size: 0.97rem;
      line-height: 1.7;
      white-space: pre-wrap;
      color: var(--text);
    }

    /* ---- Sources section ---- */
    .sources-section {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid var(--border);
    }
    .sources-label {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 7px;
    }
    .source-pill {
      display: inline-block;
      background: #eef7f0;
      border: 1px solid #b6dfc1;
      color: #1a5c2e;
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 0.76rem;
      margin: 3px 4px 3px 0;
    }

    /* ---- Chunks debug section ---- */
    details.chunks-debug {
      margin-top: 12px;
      border-top: 1px solid var(--border);
      padding-top: 10px;
    }
    details summary {
      font-size: 0.78rem;
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
      font-size: 0.76rem;
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
  <!-- New Chat button — only visible after first message -->
  <div class="new-chat-bar" id="new-chat-bar">
    <button id="new-chat-btn" onclick="newChat()">+ New Chat</button>
  </div>

  <!-- Chat history thread — Q&A pairs stack here -->
  <div id="chat-thread"></div>

  <!-- Input card — stays at bottom -->
  <div class="search-card">
    <label for="question">What do you want to know?</label>
    <div class="input-row">
      <textarea id="question" rows="2"
        placeholder="e.g. Which apartments on 34th Street have bus access to UF?"></textarea>
      <button id="ask-btn" onclick="submitQuery()">Ask</button>
    </div>
    <!-- Chips hidden after first message -->
    <div class="chips" id="chips">
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
</main>

<footer>
  Answers are grounded in collected student reviews and housing guides &mdash;
  always verify details with the landlord before signing a lease.
</footer>

<script>
  let turnCount = 0;
  let chatHistory = [];   // [{question, answer}, ...] — sent with each request

  function setQuery(el) {
    const q = el.getAttribute("data-query") || el.textContent.trim();
    document.getElementById("question").value = q;
    submitQuery();
  }

  function submitQuery() {
    const q = document.getElementById("question").value.trim();
    if (!q) return;

    const btn     = document.getElementById("ask-btn");
    const spinner = document.getElementById("spinner");

    btn.disabled = true;
    spinner.classList.add("visible");

    // Hide chips after first question
    if (turnCount === 0) {
      document.getElementById("chips").style.display = "none";
    }

    // Show "New Chat" button
    document.getElementById("new-chat-bar").classList.add("visible");

    // Build a placeholder turn immediately so user sees their question
    turnCount++;
    const turnId = "turn-" + turnCount;
    const chunkId = "chunks-" + turnCount;

    const thread = document.getElementById("chat-thread");
    const turn = document.createElement("div");
    turn.className = "turn";
    turn.id = turnId;
    turn.innerHTML = `
      <div class="user-bubble"><span>${escapeHtml(q)}</span></div>
      <div class="answer-bubble">
        <div class="answer-text" style="color:var(--muted);font-style:italic;">Thinking&hellip;</div>
      </div>
    `;
    thread.appendChild(turn);

    // Clear input
    document.getElementById("question").value = "";

    // Scroll to the new turn
    turn.scrollIntoView({ behavior: "smooth", block: "start" });

    fetch("/ask", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ question: q, history: chatHistory }),
    })
    .then(r => r.json())
    .then(data => {
      const sourcePills = data.sources
        .map(s => `<span class="source-pill">${s}</span>`).join("");

      const chunkItems = data.chunks.map((c, i) => `
        <div class="chunk-item">
          <div class="chunk-meta">#${i+1} &mdash; ${c.source} &mdash; dist: ${c.distance}</div>
          ${escapeHtml(c.text.slice(0, 300))}${c.text.length > 300 ? "&hellip;" : ""}
        </div>
      `).join("");

      turn.querySelector(".answer-bubble").innerHTML = `
        <div class="answer-text">${escapeHtml(data.answer)}</div>
        <div class="sources-section">
          <div class="sources-label">Retrieved from</div>
          <div>${sourcePills}</div>
        </div>
        <details class="chunks-debug" id="${chunkId}">
          <summary>Show retrieved chunks (debug)</summary>
          <div>${chunkItems}</div>
        </details>
      `;

      // Save this completed turn to history for follow-up questions
      chatHistory.push({ question: q, answer: data.answer });
    })
    .catch(() => {
      turn.querySelector(".answer-bubble").innerHTML =
        `<div class="answer-text" style="color:#c0392b;">Something went wrong. Please try again.</div>`;
    })
    .finally(() => {
      btn.disabled = false;
      spinner.classList.remove("visible");
      turn.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  }

  function newChat() {
    // Clear conversation and reset history
    document.getElementById("chat-thread").innerHTML = "";
    document.getElementById("question").value = "";
    document.getElementById("chips").style.display = "flex";
    document.getElementById("new-chat-bar").classList.remove("visible");
    turnCount = 0;
    chatHistory = [];
    window.scrollTo({ top: 0, behavior: "smooth" });
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

    history = data.get("history") or []
    result = ask(question, history=history)
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
