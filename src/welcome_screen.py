"""
Pragya-Saarthi — Welcome Screen
Converted from welcome_screen.html to Python/Streamlit
"""

import streamlit as st
import streamlit.components.v1 as components


# ─────────────────────────────────────────────────────────────────────────────
# CSS  (all styles from the original HTML)
# ─────────────────────────────────────────────────────────────────────────────
WELCOME_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Yatra+One&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=Nunito:wght@300;400;500;600&display=swap" rel="stylesheet"/>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --gold:        #d4a843;
  --gold-bright: #ffd700;
  --gold-dim:    rgba(212,168,67,0.15);
  --saffron:     #e8681a;
  --cosmos:      #05080f;
  --surface:     #0d1525;
  --text:        #ddd8cc;
  --muted:       #6a7490;
}

/* ── Starfield Canvas ── */
#stars { position: fixed; inset: 0; z-index: 0; pointer-events: none; }

/* ── Ambient Glows ── */
.ps-ambient {
  position: fixed; inset: 0; z-index: 1; pointer-events: none;
  background:
    radial-gradient(ellipse 60% 40% at 20% 10%, rgba(212,168,67,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 50% 50% at 80% 90%, rgba(200,80,30,0.05) 0%, transparent 70%),
    radial-gradient(ellipse 40% 60% at 50% 50%, rgba(13,21,37,0.4) 0%, transparent 80%);
}

/* ── Main Card ── */
.ps-welcome {
  position: relative; z-index: 2;
  max-width: 680px; width: 92%;
  text-align: center;
  padding: 3.5rem 3rem 3rem;
  margin: 2rem auto;
  background: linear-gradient(160deg, rgba(15,24,44,0.85), rgba(8,12,22,0.92));
  border: 1px solid rgba(212,168,67,0.18);
  border-radius: 36px;
  backdrop-filter: blur(24px);
  box-shadow:
    0 0 0 1px rgba(212,168,67,0.06) inset,
    0 30px 80px rgba(0,0,0,0.7),
    0 0 60px rgba(212,168,67,0.07);
  animation: cardIn 1s cubic-bezier(0.22,1,0.36,1) both;
}

@keyframes cardIn {
  from { opacity:0; transform: translateY(30px) scale(0.97); }
  to   { opacity:1; transform: translateY(0)   scale(1); }
}

/* Corner accents */
.ps-welcome::before, .ps-welcome::after {
  content: "";
  position: absolute;
  width: 60px; height: 60px;
  border-color: rgba(212,168,67,0.25);
  border-style: solid;
}
.ps-welcome::before {
  top: 18px; left: 18px;
  border-width: 1px 0 0 1px;
  border-radius: 10px 0 0 0;
}
.ps-welcome::after {
  bottom: 18px; right: 18px;
  border-width: 0 1px 1px 0;
  border-radius: 0 0 10px 0;
}

/* ── OM Ring ── */
.ps-om-ring {
  position: relative;
  display: inline-block;
  width: 96px; height: 96px;
  margin-bottom: 1.4rem;
  animation: fadeSlide 0.8s 0.1s both;
}
.ps-om-ring svg {
  position: absolute; inset: 0;
  animation: rotateSlow 20s linear infinite;
}
.ps-om-glyph {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.2rem;
  color: var(--gold);
  filter: drop-shadow(0 0 14px rgba(212,168,67,0.7));
  animation: omPulse 3.5s ease-in-out infinite;
}

@keyframes rotateSlow { to { transform: rotate(360deg); } }
@keyframes omPulse {
  0%,100% { filter: drop-shadow(0 0 10px rgba(212,168,67,0.5)); }
  50%      { filter: drop-shadow(0 0 24px rgba(255,215,0,0.9)); }
}

/* ── Mantra ── */
.ps-mantra {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  color: #e8d89a;
  letter-spacing: 2.5px;
  line-height: 1.3;
  animation: fadeSlide 0.8s 0.2s both;
}
.ps-mantra-meaning {
  font-size: 0.82rem;
  color: var(--muted);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-top: 0.3rem;
  font-style: italic;
  animation: fadeSlide 0.8s 0.3s both;
}

/* ── Divider ── */
.ps-divider {
  display: flex; align-items: center; gap: 1rem;
  margin: 1.6rem auto;
  max-width: 340px;
  animation: fadeSlide 0.8s 0.35s both;
}
.ps-divider::before, .ps-divider::after {
  content: ""; flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(212,168,67,0.3), transparent);
}
.ps-divider-icon {
  color: rgba(212,168,67,0.5);
  font-size: 0.8rem;
  letter-spacing: 4px;
}

/* ── Description ── */
.ps-description {
  font-size: 0.98rem;
  color: #9ea8c4;
  line-height: 1.85;
  max-width: 460px;
  margin: 0 auto 2rem;
  font-family: 'Nunito', sans-serif;
  animation: fadeSlide 0.8s 0.4s both;
}
.ps-description b { color: var(--gold); font-weight: 600; }

/* ── Chips ── */
.ps-chips-title {
  font-family: 'Nunito', sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 2.5px;
  color: var(--muted);
  margin-bottom: 1rem;
  animation: fadeSlide 0.8s 0.45s both;
}
.ps-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.55rem;
  animation: fadeSlide 0.8s 0.5s both;
}
.ps-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1.05rem;
  border-radius: 100px;
  font-size: 0.82rem;
  font-weight: 500;
  color: #a0aac0;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(212,168,67,0.14);
  cursor: pointer;
  transition: all 0.28s cubic-bezier(0.34,1.3,0.64,1);
  user-select: none;
  position: relative;
  overflow: hidden;
  font-family: 'Nunito', sans-serif;
}
.ps-chip::before {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(circle at 50% 120%, rgba(212,168,67,0.12), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.ps-chip:hover {
  color: var(--gold-bright);
  border-color: rgba(212,168,67,0.45);
  background: rgba(212,168,67,0.07);
  transform: translateY(-3px) scale(1.04);
  box-shadow: 0 6px 20px rgba(212,168,67,0.15);
}
.ps-chip:hover::before { opacity: 1; }
.ps-chip .emoji {
  font-size: 1rem;
  transition: transform 0.3s ease;
}
.ps-chip:hover .emoji { transform: scale(1.25) rotate(-5deg); }

/* Staggered chip animations */
.ps-chip:nth-child(1)  { animation: chipIn 0.5s 0.55s both; }
.ps-chip:nth-child(2)  { animation: chipIn 0.5s 0.60s both; }
.ps-chip:nth-child(3)  { animation: chipIn 0.5s 0.65s both; }
.ps-chip:nth-child(4)  { animation: chipIn 0.5s 0.70s both; }
.ps-chip:nth-child(5)  { animation: chipIn 0.5s 0.75s both; }
.ps-chip:nth-child(6)  { animation: chipIn 0.5s 0.80s both; }
.ps-chip:nth-child(7)  { animation: chipIn 0.5s 0.85s both; }
.ps-chip:nth-child(8)  { animation: chipIn 0.5s 0.90s both; }
.ps-chip:nth-child(9)  { animation: chipIn 0.5s 0.95s both; }
.ps-chip:nth-child(10) { animation: chipIn 0.5s 1.00s both; }

@keyframes chipIn {
  from { opacity:0; transform: scale(0.7) translateY(8px); }
  to   { opacity:1; transform: scale(1)   translateY(0); }
}
@keyframes fadeSlide {
  from { opacity:0; transform: translateY(14px); }
  to   { opacity:1; transform: translateY(0); }
}

/* ── Hint ── */
.ps-hint {
  margin-top: 2rem;
  font-size: 0.76rem;
  color: rgba(106,116,144,0.6);
  letter-spacing: 1px;
  font-family: 'Nunito', sans-serif;
  animation: fadeSlide 0.8s 1.1s both;
}
.ps-hint span { color: rgba(212,168,67,0.4); }

/* Hide Streamlit chrome behind welcome card */
.stApp { background: #05080f !important; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# OM RING SVG
# ─────────────────────────────────────────────────────────────────────────────
OM_RING_SVG = """
<svg viewBox="0 0 96 96" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="48" cy="48" r="44"
          stroke="url(#ringGrad)" stroke-width="1"
          stroke-dasharray="5 4" opacity="0.5"/>
  <circle cx="48" cy="48" r="38"
          stroke="rgba(212,168,67,0.15)" stroke-width="0.5"/>
  <!-- 8 diamond accents at cardinal & diagonal points -->
  <g fill="rgba(212,168,67,0.45)">
    <polygon points="48,3  49.2,4.8  48,6.5  46.8,4.8"/>
    <polygon points="93,48 91.2,49.2 89.5,48 91.2,46.8"/>
    <polygon points="48,93 46.8,91.2 48,89.5 49.2,91.2"/>
    <polygon points="3,48  4.8,46.8  6.5,48  4.8,49.2"/>
    <polygon points="79,17 79.8,19.2 78,20.2 77.2,18"/>
    <polygon points="79,79 77.2,78  78,76   79.8,76.8"/>
    <polygon points="17,79 18,76.8  19.8,77.8 19,80"/>
    <polygon points="17,17 19,18   18.2,20.2 16.2,19.2"/>
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
"""

# ─────────────────────────────────────────────────────────────────────────────
# STARFIELD JAVASCRIPT  (unchanged from original)
# ─────────────────────────────────────────────────────────────────────────────
STARFIELD_JS = """
<script>
const canvas = document.getElementById('stars');
const ctx    = canvas.getContext('2d');
let W, H, stars = [];

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}

function initStars() {
  stars = Array.from({length: 160}, () => ({
    x:     Math.random() * W,
    y:     Math.random() * H,
    r:     Math.random() * 1.2 + 0.2,
    a:     Math.random(),
    speed: Math.random() * 0.006 + 0.002,
    gold:  Math.random() < 0.15
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

window.addEventListener('resize', () => { resize(); initStars(); });
resize(); initStars(); draw();
</script>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CHIP DATA  (topics shown on welcome screen)
# ─────────────────────────────────────────────────────────────────────────────
CHIPS = [
    ("😰", "Anxiety & Stress"),
    ("💼", "Career Confusion"),
    ("💰", "Financial Worry"),
    ("💔", "Relationship Pain"),
    ("📚", "Study Pressure"),
    ("😢", "Grief & Loss"),
    ("😡", "Anger & Conflict"),
    ("🧭", "Life Purpose"),
    ("🧘", "Spiritual Growth"),
    ("🫶", "Fear & Doubt"),
]


# ─────────────────────────────────────────────────────────────────────────────
# BUILDER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def build_om_ring() -> str:
    """Return the animated OM ring HTML block."""
    return f"""
    <div class="ps-om-ring">
      {OM_RING_SVG}
      <div class="ps-om-glyph">ॐ</div>
    </div>
    """


def build_chips_html(chips: list[tuple[str, str]]) -> str:
    """Return the chips row HTML from a list of (emoji, label) tuples."""
    items = "\n".join(
        f'    <div class="ps-chip"><span class="emoji">{emoji}</span> {label}</div>'
        for emoji, label in chips
    )
    return f"""
    <div class="ps-chips-title">What brings you here today?</div>
    <div class="ps-chips">
    {items}
    </div>
    """


def build_welcome_html(chips: list[tuple[str, str]] | None = None) -> str:
    """
    Assemble the complete welcome-screen HTML string.

    Parameters
    ----------
    chips : list of (emoji, label) tuples, optional
        Pass a custom list to override the default CHIPS constant.
    """
    if chips is None:
        chips = CHIPS

    return f"""
<!-- ── Starfield canvas (fixed, behind everything) ── -->
<canvas id="stars"></canvas>

<!-- ── Ambient glow overlay ── -->
<div class="ps-ambient"></div>

<!-- ── Main card ── -->
<div class="ps-welcome">

  <!-- OM Ring -->
  {build_om_ring()}

  <!-- Sacred Mantra -->
  <div class="ps-mantra">ॐ नमो भगवते वासुदेवाय</div>
  <div class="ps-mantra-meaning">I bow to the divine Lord Vasudeva</div>

  <!-- Decorative divider -->
  <div class="ps-divider">
    <div class="ps-divider-icon">✦ ✦ ✦</div>
  </div>

  <!-- Description -->
  <p class="ps-description">
    Share any challenge of life — big or small, material or spiritual.<br>
    The eternal wisdom of <b>Bhagavad Gita</b> holds guidance for every situation.
  </p>

  <!-- Topic chips -->
  {build_chips_html(chips)}

  <!-- Bottom hint -->
  <div class="ps-hint">
    Type your question above <span>✦</span> or tap a topic to begin
  </div>

</div>

<!-- Starfield animation script -->
{STARFIELD_JS}
"""


# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT RENDER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def render_welcome_screen(
    chips: list[tuple[str, str]] | None = None,
    height: int = 820,
) -> None:
    """
    Render the animated welcome screen inside a Streamlit app.

    This function uses st.components.v1.html() so the starfield canvas,
    CSS animations, and JavaScript all run correctly inside an iframe.

    Parameters
    ----------
    chips  : list of (emoji, label) tuples — topics shown on screen.
    height : iframe height in pixels (increase if card is clipped).

    Usage
    -----
    In your app.py:

        from welcome_screen import render_welcome_screen

        if not st.session_state.chat_history:
            render_welcome_screen()
    """
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  {WELCOME_CSS}
  <style>
    /* Make the iframe body match the dark cosmos background */
    body {{
      background: #05080f;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}
  </style>
</head>
<body>
  {build_welcome_html(chips)}
</body>
</html>"""

    components.html(full_html, height=height, scrolling=False)


def inject_welcome_css() -> None:
    """
    Inject the welcome CSS into the Streamlit page.
    FIX: Uses @import inside <style> tag instead of a <link> tag,
    because st.markdown renders bare <link> tags as raw text.
    """
    import re as _re
    style_match = _re.search(r"<style>(.*?)</style>", WELCOME_CSS, _re.DOTALL)
    style_content = style_match.group(1) if style_match else ""
    font_url = (
        "https://fonts.googleapis.com/css2?"
        "family=Yatra+One&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400"
        "&family=Nunito:wght@300;400;500;600&display=swap"
    )
    st.markdown(
        f"<style>@import url('{font_url}');{style_content}</style>",
        unsafe_allow_html=True,
    )


def render_welcome_markdown(chips: list[tuple[str, str]] | None = None) -> None:
    """
    Render the welcome card.
    FIX: The old st.markdown approach was broken because:
      - WELCOME_CSS starts with a <link> tag → rendered as raw text
      - SVG HTML comments stripped by Streamlit
      - CSS variables undefined outside iframe context
    Solution: delegate to render_welcome_screen (components.html).
    """
    if chips is None:
        chips = CHIPS
    render_welcome_screen(chips=chips, height=680)


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE DEMO  (python welcome_screen.py)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(
        page_title="Pragya-Saarthi · Welcome",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Hide Streamlit header/footer
    st.markdown(
        """<style>
        #MainMenu, header, footer { visibility: hidden; }
        .block-container { padding-top: 0 !important; }
        </style>""",
        unsafe_allow_html=True,
    )

    # ── Option A: full iframe with starfield (recommended) ──
    render_welcome_screen()

    # ── Option B: inline markdown without starfield (no iframe) ──
    # render_welcome_markdown()
