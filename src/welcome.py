"""
welcome.py  —  Pragya-Saarthi Welcome Screen
Drop-in Streamlit module. Call render_welcome() from app.py.
Converts welcome_screen.html to pure Python/Streamlit.
"""

import streamlit as st


# ── Full HTML/CSS/JS for the welcome screen ──────────────────────────────────
WELCOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=Nunito:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --gold: #d4a843;
  --gold-bright: #ffd700;
  --saffron: #e8681a;
  --cosmos: #05080f;
  --surface: #0d1525;
  --text: #ddd8cc;
  --muted: #6a7490;
}

body {
  background: transparent;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Nunito', sans-serif;
  position: relative;
  overflow: hidden;
}

/* Starfield */
#stars { position: fixed; inset: 0; z-index: 0; pointer-events: none; }

/* Ambient */
.ambient {
  position: fixed; inset: 0; z-index: 1; pointer-events: none;
  background:
    radial-gradient(ellipse 60% 40% at 20% 10%, rgba(212,168,67,0.07) 0%, transparent 70%),
    radial-gradient(ellipse 50% 50% at 80% 90%, rgba(200,80,30,0.05) 0%, transparent 70%);
}

/* Main Card */
.welcome {
  position: relative; z-index: 2;
  max-width: 680px; width: 92%;
  text-align: center;
  padding: 3rem 2.5rem 2.5rem;
  background: linear-gradient(160deg, rgba(15,24,44,0.90), rgba(8,12,22,0.95));
  border: 1px solid rgba(212,168,67,0.18);
  border-radius: 36px;
  backdrop-filter: blur(24px);
  box-shadow:
    0 0 0 1px rgba(212,168,67,0.06) inset,
    0 30px 80px rgba(0,0,0,0.7),
    0 0 60px rgba(212,168,67,0.07);
  animation: cardIn 1s cubic-bezier(0.22,1,0.36,1) both;
  margin: 2rem auto;
}

/* Corner accents */
.welcome::before, .welcome::after {
  content: "";
  position: absolute;
  width: 56px; height: 56px;
  border-color: rgba(212,168,67,0.25);
  border-style: solid;
}
.welcome::before { top: 16px; left: 16px; border-width: 1px 0 0 1px; border-radius: 8px 0 0 0; }
.welcome::after  { bottom: 16px; right: 16px; border-width: 0 1px 1px 0; border-radius: 0 0 8px 0; }

/* OM Ring */
.om-ring {
  position: relative;
  display: inline-block;
  width: 92px; height: 92px;
  margin-bottom: 1.3rem;
  animation: fadeSlide 0.8s 0.1s both;
}
.om-ring svg {
  position: absolute; inset: 0;
  animation: rotateSlow 20s linear infinite;
}
.om-glyph {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Cormorant Garamond', serif;
  font-size: 3rem;
  color: var(--gold);
  filter: drop-shadow(0 0 14px rgba(212,168,67,0.7));
  animation: omPulse 3.5s ease-in-out infinite;
}

/* Mantra */
.mantra {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.65rem;
  color: #e8d89a;
  letter-spacing: 2.5px;
  line-height: 1.3;
  animation: fadeSlide 0.8s 0.2s both;
}
.mantra-meaning {
  font-size: 0.8rem;
  color: var(--muted);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-top: 0.3rem;
  font-style: italic;
  animation: fadeSlide 0.8s 0.3s both;
}

/* Divider */
.divider {
  display: flex; align-items: center; gap: 1rem;
  margin: 1.5rem auto;
  max-width: 320px;
  animation: fadeSlide 0.8s 0.35s both;
}
.divider::before, .divider::after {
  content: ""; flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(212,168,67,0.3), transparent);
}
.divider-icon { color: rgba(212,168,67,0.5); font-size: 0.78rem; letter-spacing: 4px; }

/* Description */
.description {
  font-size: 0.95rem;
  color: #9ea8c4;
  line-height: 1.85;
  max-width: 440px;
  margin: 0 auto 1.8rem;
  animation: fadeSlide 0.8s 0.4s both;
}
.description b { color: var(--gold); font-weight: 600; }

/* Chips title */
.chips-title {
  font-family: 'Nunito', sans-serif;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 2.5px;
  color: var(--muted);
  margin-bottom: 0.9rem;
  animation: fadeSlide 0.8s 0.45s both;
}

/* Chips */
.chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  animation: fadeSlide 0.8s 0.5s both;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.42rem 1rem;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #a0aac0;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(212,168,67,0.14);
  cursor: pointer;
  transition: all 0.28s cubic-bezier(0.34,1.3,0.64,1);
  user-select: none;
  position: relative;
  overflow: hidden;
}
.chip::before {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(circle at 50% 120%, rgba(212,168,67,0.12), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.chip:hover {
  color: var(--gold-bright);
  border-color: rgba(212,168,67,0.45);
  background: rgba(212,168,67,0.07);
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 6px 20px rgba(212,168,67,0.15);
}
.chip:hover::before { opacity: 1; }
.chip .emoji { font-size: 0.95rem; transition: transform 0.3s ease; }
.chip:hover .emoji { transform: scale(1.25) rotate(-5deg); }

/* Staggered chip reveal */
.chip:nth-child(1)  { animation: chipIn 0.5s 0.55s both; }
.chip:nth-child(2)  { animation: chipIn 0.5s 0.60s both; }
.chip:nth-child(3)  { animation: chipIn 0.5s 0.65s both; }
.chip:nth-child(4)  { animation: chipIn 0.5s 0.70s both; }
.chip:nth-child(5)  { animation: chipIn 0.5s 0.75s both; }
.chip:nth-child(6)  { animation: chipIn 0.5s 0.80s both; }
.chip:nth-child(7)  { animation: chipIn 0.5s 0.85s both; }
.chip:nth-child(8)  { animation: chipIn 0.5s 0.90s both; }
.chip:nth-child(9)  { animation: chipIn 0.5s 0.95s both; }
.chip:nth-child(10) { animation: chipIn 0.5s 1.00s both; }

/* Hint */
.hint {
  margin-top: 1.8rem;
  font-size: 0.73rem;
  color: rgba(106,116,144,0.6);
  letter-spacing: 1px;
  animation: fadeSlide 0.8s 1.1s both;
}
.hint span { color: rgba(212,168,67,0.4); }

/* Animations */
@keyframes cardIn {
  from { opacity:0; transform: translateY(30px) scale(0.97); }
  to   { opacity:1; transform: translateY(0) scale(1); }
}
@keyframes rotateSlow { to { transform: rotate(360deg); } }
@keyframes omPulse {
  0%,100% { filter: drop-shadow(0 0 10px rgba(212,168,67,0.5)); }
  50%      { filter: drop-shadow(0 0 24px rgba(255,215,0,0.9)); }
}
@keyframes fadeSlide {
  from { opacity:0; transform: translateY(14px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes chipIn {
  from { opacity:0; transform: scale(0.7) translateY(8px); }
  to   { opacity:1; transform: scale(1) translateY(0); }
}
</style>
</head>
<body>

<canvas id="stars"></canvas>
<div class="ambient"></div>

<div class="welcome">

  <!-- OM Ring -->
  <div class="om-ring">
    <svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="48" cy="48" r="44"
        stroke="url(#ringGrad)" stroke-width="1" stroke-dasharray="5 4" opacity="0.5"/>
      <circle cx="48" cy="48" r="38"
        stroke="rgba(212,168,67,0.15)" stroke-width="0.5"/>
      <!-- 8 diamond accents -->
      <g fill="rgba(212,168,67,0.45)">
        <polygon points="48,3 49.2,4.8 48,6.5 46.8,4.8"/>
        <polygon points="93,48 91.2,49.2 89.5,48 91.2,46.8"/>
        <polygon points="48,93 46.8,91.2 48,89.5 49.2,91.2"/>
        <polygon points="3,48 4.8,46.8 6.5,48 4.8,49.2"/>
        <polygon points="79,17 79.8,19.2 78,20.2 77.2,18"/>
        <polygon points="79,79 77.2,78 78,76 79.8,76.8"/>
        <polygon points="17,79 18,76.8 19.8,77.8 19,80"/>
        <polygon points="17,17 19,18 18.2,20.2 16.2,19.2"/>
      </g>
      <defs>
        <linearGradient id="ringGrad" x1="0" y1="0" x2="96" y2="96"
          gradientUnits="userSpaceOnUse">
          <stop offset="0%"   stop-color="#8b6000"/>
          <stop offset="50%"  stop-color="#ffd700"/>
          <stop offset="100%" stop-color="#8b6000"/>
        </linearGradient>
      </defs>
    </svg>
    <div class="om-glyph">ॐ</div>
  </div>

  <!-- Mantra -->
  <div class="mantra">ॐ नमो भगवते वासुदेवाय</div>
  <div class="mantra-meaning">I bow to the divine Lord Vasudeva</div>

  <!-- Divider -->
  <div class="divider">
    <div class="divider-icon">✦ ✦ ✦</div>
  </div>

  <!-- Description -->
  <p class="description">
    Share any challenge of life — big or small, material or spiritual.<br>
    The eternal wisdom of <b>Bhagavad Gita</b> holds guidance for every situation.
  </p>

  <!-- Chips -->
  <div class="chips-title">What brings you here today?</div>
  <div class="chips" id="chips-container"></div>

  <div class="hint">Type your question above <span>✦</span> or tap a topic to begin</div>
</div>

<!-- Starfield + Chip logic -->
<script>
/* ── Chip data ── */
const CHIPS = [
  ["😰", "Anxiety & Stress",    "I am overwhelmed with anxiety and constant stress. My mind races and I cannot stop worrying."],
  ["💼", "Career Confusion",    "I am confused about my career path and don't know which direction to take."],
  ["💰", "Financial Worry",     "I have serious financial problems. Debt and bills are crushing me."],
  ["💔", "Relationship Pain",   "I am hurting deeply because of a broken relationship and emotional pain."],
  ["📚", "Study Pressure",      "I am terrified of my exams. The pressure from family is immense."],
  ["😢", "Grief & Loss",        "I lost someone very dear to me and the grief is unbearable. I cannot move on."],
  ["😡", "Anger & Conflict",    "I struggle with anger that ruins my relationships and inner peace."],
  ["🧭", "Life Purpose",        "I feel completely lost and have no sense of purpose or dharma in life."],
  ["🧘", "Spiritual Growth",    "I want to deepen my spiritual practice and connect with the divine."],
  ["🫶", "Fear & Doubt",        "I am paralyzed by fear and constant self-doubt. I feel I am not good enough."],
];

const container = document.getElementById("chips-container");
CHIPS.forEach(([emoji, label, question], i) => {
  const chip = document.createElement("div");
  chip.className = "chip";
  chip.style.animationDelay = (0.55 + i * 0.05) + "s";
  chip.innerHTML = `<span class="emoji">${emoji}</span>${label}`;
  chip.addEventListener("click", () => {
    /* Post the selected question to the Streamlit parent frame */
    window.parent.postMessage(
      { type: "streamlit:setComponentValue", value: question },
      "*"
    );
  });
  container.appendChild(chip);
});

/* ── Starfield ── */
const canvas = document.getElementById("stars");
const ctx    = canvas.getContext("2d");
let W, H, stars = [];

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}

function initStars() {
  stars = Array.from({ length: 160 }, () => ({
    x:     Math.random() * W,
    y:     Math.random() * H,
    r:     Math.random() * 1.2 + 0.2,
    a:     Math.random(),
    speed: Math.random() * 0.006 + 0.002,
    gold:  Math.random() < 0.15,
  }));
}

function draw() {
  ctx.clearRect(0, 0, W, H);
  stars.forEach(s => {
    s.a += s.speed;
    const alpha = (Math.sin(s.a) + 1) / 2 * 0.7 + 0.1;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = s.gold
      ? `rgba(212,168,67,${alpha * 0.8})`
      : `rgba(200,210,230,${alpha * 0.5})`;
    ctx.fill();
  });
  requestAnimationFrame(draw);
}

window.addEventListener("resize", () => { resize(); initStars(); });
resize(); initStars(); draw();
</script>
</body>
</html>
"""


# ── Chip data (Python-side, mirrors JS) ─────────────────────────────────────
CHIP_QUESTIONS = {
    "😰 Anxiety & Stress":
        "I am overwhelmed with anxiety and constant stress. My mind races and I cannot stop worrying.",
    "💼 Career Confusion":
        "I am confused about my career path and don't know which direction to take.",
    "💰 Financial Worry":
        "I have serious financial problems. Debt and bills are crushing me.",
    "💔 Relationship Pain":
        "I am hurting deeply because of a broken relationship and emotional pain.",
    "📚 Study Pressure":
        "I am terrified of my exams. The pressure from family is immense.",
    "😢 Grief & Loss":
        "I lost someone very dear to me and the grief is unbearable. I cannot move on.",
    "😡 Anger & Conflict":
        "I struggle with anger that ruins my relationships and inner peace.",
    "🧭 Life Purpose":
        "I feel completely lost and have no sense of purpose or dharma in life.",
    "🧘 Spiritual Growth":
        "I want to deepen my spiritual practice and connect with the divine.",
    "🫶 Fear & Doubt":
        "I am paralyzed by fear and constant self-doubt. I feel I am not good enough.",
}


def render_welcome(language: str = "english") -> str | None:
    """
    Renders the full animated welcome screen using st.components.v1.html.

    Returns:
        str | None  — the chip question text if a chip button was clicked,
                      otherwise None.

    Usage in app.py:
        from welcome import render_welcome, CHIP_QUESTIONS

        selected = render_welcome(language=st.session_state.language)
        if selected:
            st.session_state.selected_chip = selected
            st.rerun()
    """
    import streamlit.components.v1 as components

    # 1. Render the animated HTML card (560 px tall; no scroll bar)
    components.html(WELCOME_HTML, height=560, scrolling=False)

    # 2. Fallback: plain Streamlit chip buttons below the card
    #    (chip clicks inside the iframe also work via postMessage, but Streamlit
    #     cannot capture those directly — the buttons below are the reliable path)
    st.markdown(
        "<div style='text-align:center; margin-top:0.5rem;'>"
        "<span style='font-size:0.68rem; color:#5a6480; letter-spacing:2px; "
        "text-transform:uppercase;'>Quick Start</span></div>",
        unsafe_allow_html=True,
    )

    selected: str | None = None
    chip_list = list(CHIP_QUESTIONS.items())

    # Two rows of 5
    for row in range(2):
        cols = st.columns(5)
        for col_idx in range(5):
            idx = row * 5 + col_idx
            if idx < len(chip_list):
                label, question = chip_list[idx]
                with cols[col_idx]:
                    if st.button(label, key=f"welcome_chip_{idx}", use_container_width=True):
                        selected = question

    return selected
