"""
Pragya-Saarthi — The Wisdom Charioteer
Bhagavad Gita AI Agent: Multi-language Spiritual Guidance
"""

import warnings
warnings.simplefilter("ignore")
import sys, os, io
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime
import random

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "src"))

from agent.gita_agent import PragyaSaarthiAgent
from agent.language import LANGUAGES, get_text, get_problem_type_text
from welcome_screen import render_welcome_screen

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pragya-Saarthi · Wisdom Charioteer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
def load_css():
    css_path = ROOT / "assets" / "custom_style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp{background:#050810!important}</style>", unsafe_allow_html=True)

load_css()

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in {
    "agent": None,
    "language": "english",
    "chat_history": [],
    "total_queries": 0,
    "verses_revealed": 0,
    "uploaded_query": "",
    "last_uploaded_name": "",
    "selected_chip": "",
    "chat_timestamps": [],
    "chat_categories": [],
    "lang_used": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state.agent is None:
    with st.spinner("🕉️ Awakening the Wisdom Charioteer..."):
        st.session_state.agent = PragyaSaarthiAgent()

# ── File extractor ─────────────────────────────────────────────────────────────
def extract_text_from_file(uploaded_file) -> str:
    try:
        ft = uploaded_file.type
        name = uploaded_file.name.lower()
        if "text" in ft or name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")[:800]
        if "pdf" in ft or name.endswith(".pdf"):
            try:
                import PyPDF2
                r = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                return " ".join(p.extract_text() or "" for p in r.pages[:3])[:800].strip()
            except ImportError:
                return "I uploaded a PDF about my life situation and need spiritual guidance."
    except Exception:
        pass
    return ""

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_answer(response, lang):
    a = response.get("answer", {})
    if isinstance(a, dict):
        return a.get(lang, a.get("english", ""))
    return str(a)

def get_relevance(verse, lang):
    return verse.get(f"relevance_{lang}", verse.get("relevance_english", ""))

# ── DASHBOARD FUNCTION (Premium) ──────────────────────────────────────────────
def render_dashboard():
    st.markdown('<div class="dashboard-section-title">📊 Wisdom Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#9ea8c4; margin-bottom:1rem;">Insights from your spiritual journey</p>', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.info("✨ No data yet. Start a conversation to see your dashboard come alive.")
        return

    # Metric Cards
    total_q = st.session_state.total_queries
    total_v = st.session_state.verses_revealed
    unique_topics = len(set(st.session_state.chat_categories))
    avg_verses = round(total_v / max(total_q, 1), 1)

    metrics_html = f"""
    <div class="dashboard-metric-grid">
        <div class="dashboard-metric-card"><div class="dashboard-metric-icon">📝</div><div class="dashboard-metric-value">{total_q}</div><div class="dashboard-metric-label">Questions Asked</div></div>
        <div class="dashboard-metric-card"><div class="dashboard-metric-icon">📖</div><div class="dashboard-metric-value">{total_v}</div><div class="dashboard-metric-label">Verses Revealed</div></div>
        <div class="dashboard-metric-card"><div class="dashboard-metric-icon">🧭</div><div class="dashboard-metric-value">{unique_topics}</div><div class="dashboard-metric-label">Topics Explored</div></div>
        <div class="dashboard-metric-card"><div class="dashboard-metric-icon">🎯</div><div class="dashboard-metric-value">{avg_verses}</div><div class="dashboard-metric-label">Avg Verses/Query</div></div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

    # Custom Plotly template (dark + gold)
    def gold_template():
        return go.layout.Template(
            layout=dict(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Nunito', color='#e8e0d0'),
                title=dict(font=dict(family='Cormorant Garamond', size=20, color='#d4a843')),
                xaxis=dict(gridcolor='rgba(212,168,67,0.15)', tickfont=dict(color='#9ea8c4')),
                yaxis=dict(gridcolor='rgba(212,168,67,0.15)', tickfont=dict(color='#9ea8c4')),
                legend=dict(font=dict(color='#9ea8c4')),
                hoverlabel=dict(bgcolor='#0d1525', font_color='#ffd700'),
            )
        )

    # Top 5 Most Used Verses
    st.markdown('<div class="dashboard-section-title">🔥 Most Referenced Verses</div>', unsafe_allow_html=True)
    verse_counter = Counter()
    for chat in st.session_state.chat_history:
        for v in chat["response"].get("verses", []):
            chap = v.get("Chapter", "")
            verse_num = v.get("Verse", "")
            if chap and verse_num:
                verse_counter[f"Ch {chap} · V {verse_num}"] += 1

    if verse_counter:
        top_verses = dict(verse_counter.most_common(5))
        fig = px.bar(
            x=list(top_verses.values()), y=list(top_verses.keys()), orientation='h',
            labels={'x': 'Times Used', 'y': ''}, color_discrete_sequence=['#d4a843'],
            template=gold_template()
        )
        fig.update_traces(marker_line_color='#ffd700', marker_line_width=1, opacity=0.85)
        fig.update_layout(height=350, title=None, margin=dict(l=20, r=20))
        with st.container():
            st.markdown('<div class="dashboard-chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("No verses recorded yet.")

    # Problem Category Distribution
    st.markdown('<div class="dashboard-section-title">🧩 What You Asked About</div>', unsafe_allow_html=True)
    cat_counts = Counter(st.session_state.chat_categories)
    display_counts = {get_problem_type_text(cat, st.session_state.language): count for cat, count in cat_counts.items()}
    if display_counts:
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(display_counts.keys()), values=list(display_counts.values()), hole=0.45,
            marker=dict(colors=px.colors.sequential.YlOrBr_r, line=dict(color='#0d1525', width=2)),
            textinfo='percent+label', textfont=dict(family='Nunito', size=12, color='#e8e0d0')
        )])
        fig_pie.update_layout(template=gold_template(), height=450, title=None, legend=dict(orientation='h', yanchor='bottom', y=1.02))
        with st.container():
            st.markdown('<div class="dashboard-chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    # Queries Over Time
    if len(st.session_state.chat_timestamps) > 1:
        st.markdown('<div class="dashboard-section-title">📈 Your Inquiry Flow</div>', unsafe_allow_html=True)
        dates = st.session_state.chat_timestamps
        date_counts = Counter(d.date() for d in dates)
        dates_sorted = sorted(date_counts.keys())
        counts = [date_counts[d] for d in dates_sorted]
        fig_line = px.line(x=dates_sorted, y=counts, labels={'x': 'Date', 'y': 'Questions'}, markers=True, template=gold_template())
        fig_line.update_traces(line_color='#d4a843', line_width=3, marker=dict(size=8, color='#ffd700', symbol='diamond'))
        fig_line.update_layout(height=400, title=None, xaxis=dict(tickangle=45))
        with st.container():
            st.markdown('<div class="dashboard-chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    # Language Usage
    if st.session_state.lang_used:
        st.markdown('<div class="dashboard-section-title">🌐 Language Preference</div>', unsafe_allow_html=True)
        lang_counts = Counter(st.session_state.lang_used)
        fig_lang = go.Figure(data=[go.Pie(
            labels=[LANGUAGES[l]["name"] for l in lang_counts.keys()], values=list(lang_counts.values()), hole=0.5,
            marker=dict(colors=['#d4a843', '#ffd700', '#c87fa0'], line=dict(color='#0d1525', width=2)),
            textinfo='percent', textfont=dict(family='Nunito', size=12, color='#e8e0d0')
        )])
        fig_lang.update_layout(template=gold_template(), height=400, title=None)
        with st.container():
            st.markdown('<div class="dashboard-chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_lang, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    # Verse of the Day
    st.markdown('<div class="dashboard-section-title">✨ Verse of the Day</div>', unsafe_allow_html=True)
    if verse_counter:
        top_verses_list = list(verse_counter.keys())
        if top_verses_list:
            random_verse_key = random.choice(top_verses_list[:10])
            verse_data = None
            for chat in st.session_state.chat_history:
                for v in chat["response"].get("verses", []):
                    key = f"Ch {v.get('Chapter', '')} · V {v.get('Verse', '')}"
                    if key == random_verse_key:
                        verse_data = v
                        break
                if verse_data:
                    break
            if verse_data:
                meaning = verse_data.get('HinMeaning' if st.session_state.language == 'hindi' else 'EngMeaning', verse_data['EngMeaning'])
                st.markdown(f"""
                    <div class="verse-of-day-card">
                        <div class="verse-of-day-label">🕉️ Today's Wisdom</div>
                        <div class="verse-of-day-text">{verse_data['Shloka'][:300]}</div>
                        <div class="verse-of-day-ref">— {get_text('chapter', st.session_state.language)} {verse_data['Chapter']}, {get_text('verse_word', st.session_state.language)} {verse_data['Verse']}</div>
                        <div style="font-family:'Nunito',sans-serif; font-size:0.85rem; color:#d4a843; margin-top:0.8rem;">{meaning[:150]}...</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Keep asking questions – the Gita will reveal its gems.")
        else:
            st.info("No verses recorded yet. Ask a question to see daily wisdom.")
    else:
        st.info("Start a conversation to receive daily wisdom.")

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-logo">🎯</div><div class="sidebar-title">Pragya-Saarthi</div><div class="sidebar-sub">Wisdom Charioteer</div></div><div class="sidebar-divider"></div>', unsafe_allow_html=True)
    selected_lang = st.selectbox("Language", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x]["name"], index=list(LANGUAGES.keys()).index(st.session_state.language), key="lang_select", label_visibility="collapsed")
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-row"><div class="stat-box"><div class="stat-number">{st.session_state.total_queries}</div><div class="stat-label">Questions</div></div><div class="stat-box"><div class="stat-number">{st.session_state.verses_revealed}</div><div class="stat-label">Verses</div></div><div class="stat-box"><div class="stat-number">18</div><div class="stat-label">Chapters</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("🔄 " + get_text("clear_chat", st.session_state.language), use_container_width=True):
        st.session_state.agent.clear_history()
        st.session_state.update({"chat_history": [], "total_queries": 0, "verses_revealed": 0, "uploaded_query": "", "last_uploaded_name": "", "chat_timestamps": [], "chat_categories": [], "lang_used": []})
        st.rerun()
    with st.expander("⚙️ Settings"):
        api_key_input = st.text_input("Gemini API Key", type="password", placeholder="AIza… (from .env or paste here)")
        if api_key_input and api_key_input != os.getenv("GEMINI_API_KEY", ""):
            os.environ["GEMINI_API_KEY"] = api_key_input
            st.session_state.agent = PragyaSaarthiAgent()
            st.success("✅ API key updated!")

# ── MAIN HEADER ────────────────────────────────────────────────────────────────
lang = st.session_state.language
st.markdown(f'<div style="text-align:center;padding:1.5rem 0 .5rem"><h1 class="main-title">🎯 {get_text("greeting", lang)}</h1><p class="title-devanagari">{get_text("subtitle", lang)}</p><div class="title-divider"><span>✦</span><span style="font-family:\'Cormorant Garamond\',serif;font-size:.85rem;color:#5a6480;letter-spacing:2px">BHAGAVAD GITA · भगवद गीता · भगवद गीता</span><span>✦</span></div></div>', unsafe_allow_html=True)

# ── WELCOME + CHIPS ────────────────────────────────────────────────────────────
CHIP_TOPICS = {
    "Anxiety & Stress": "I am feeling overwhelming anxiety and stress every day. My mind races constantly. What does the Bhagavad Gita teach about finding peace?",
    "Career Confusion": "I am completely confused about my career path. I don't know which direction to take and my work feels meaningless. What does the Gita say?",
    "Financial Worry": "I am worried about my financial situation. I have money problems and debt that feels crushing. What wisdom does the Gita offer?",
    "Relationship Pain": "I am going through deep relationship pain with someone close to me. There is conflict and hurt. What does the Gita teach about this?",
    "Study Pressure": "I am under immense pressure from my studies and upcoming board exams. I am scared of failing. What motivation does the Gita give?",
    "Grief & Loss": "I am dealing with grief after losing someone very dear to me. The pain is unbearable. What comfort does the Gita offer?",
    "Anger & Conflict": "I struggle with anger that is ruining my relationships and inner peace. I need to control it. What does the Gita teach?",
    "Life Purpose": "I feel completely lost and have no sense of purpose or direction in life. What does the Gita say about finding one's dharma?",
    "Spiritual Growth": "I want to grow spiritually and deepen my connection with the divine. What path does the Gita recommend?",
    "Fear & Doubt": "I am paralyzed by fear and constant self-doubt. I feel I am not good enough. What wisdom does the Gita offer to overcome this?",
}

if not st.session_state.chat_history:
    render_welcome_screen()
    chip_list = list(CHIP_TOPICS.items())
    for row in range(2):
        cols = st.columns(5)
        for ci in range(5):
            idx = row * 5 + ci
            if idx < len(chip_list):
                topic, question = chip_list[idx]
                with cols[ci]:
                    if st.button(topic, key=f"chip_{idx}"):
                        st.session_state.selected_chip = question
                        st.rerun()
    st.markdown('<div class="welcome-hint">Type your question above <span>✦</span> or tap a topic to begin</div>', unsafe_allow_html=True)

# ── MAIN LAYOUT WITH TABS ──────────────────────────────────────────────────────
_, center_col, _ = st.columns([1, 10, 1])

with center_col:
    st.markdown('<div class="input-sanctum">', unsafe_allow_html=True)

    default_query = ""
    if st.session_state.selected_chip:
        default_query = st.session_state.selected_chip
        st.session_state.selected_chip = ""

    typed_query = st.text_input(
        "Question",
        placeholder=get_text("input_placeholder", lang),
        key="query_input",
        label_visibility="collapsed",
        value=default_query,
    )

    st.markdown(
        """
    <div style="display:flex;align-items:center;gap:.8rem;margin:.9rem 0 .6rem">
      <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(212,168,67,.2))"></div>
      <span style="font-family:'Nunito',sans-serif;font-size:.7rem;color:#5a6480;
                   text-transform:uppercase;letter-spacing:2px;white-space:nowrap">📎 or upload a file</span>
      <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(212,168,67,.2),transparent)"></div>
    </div>""",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload",
        type=["pdf", "txt", "png", "jpg", "jpeg"],
        key="file_upload",
        label_visibility="collapsed",
    )

    image_query_override = ""
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.last_uploaded_name:
            st.session_state.last_uploaded_name = uploaded_file.name
            if "image" not in uploaded_file.type:
                st.session_state.uploaded_query = extract_text_from_file(uploaded_file)
            else:
                st.session_state.uploaded_query = ""
        if "image" in uploaded_file.type:
            c1, c2 = st.columns([1, 3])
            with c1:
                st.image(uploaded_file, width=110)
            with c2:
                st.markdown(
                    '<div style="font-size:.82rem;color:#9ea8c4;padding-top:.4rem">'
                    '📸 <b style="color:#d4a843">Image uploaded.</b><br>'
                    "Type your question about it:</div>",
                    unsafe_allow_html=True,
                )
                image_query_override = st.text_input(
                    "img_q",
                    placeholder="e.g. This image reflects my anxiety. What does Gita say?",
                    key="img_query",
                    label_visibility="collapsed",
                )
        elif st.session_state.uploaded_query:
            preview = st.session_state.uploaded_query[:130].replace("\n", " ")
            st.markdown(
                f"""
            <div style="background:rgba(212,168,67,.05);border:1px solid rgba(212,168,67,.18);
                        border-radius:14px;padding:.75rem 1.1rem;margin-top:.5rem">
              <div style="font-size:.7rem;color:#d4a843;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.35rem">
                📄 {uploaded_file.name}</div>
              <div style="font-size:.84rem;color:#9ea8c4;line-height:1.5">
                "{preview}{"..." if len(st.session_state.uploaded_query) > 130 else ""}"</div>
              <div style="font-size:.7rem;color:#5a6480;margin-top:.4rem">
                ✅ Text extracted — click <b style="color:#d4a843">Seek Wisdom</b></div>
            </div>""",
                unsafe_allow_html=True,
            )

    if image_query_override.strip():
        final_query = image_query_override.strip()
    elif st.session_state.uploaded_query.strip() and not typed_query.strip():
        final_query = st.session_state.uploaded_query.strip()
    else:
        final_query = typed_query.strip()

    st.markdown("<div style='margin-top:1.1rem'>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 3, 1])
    with btn_col:
        ask_btn = st.button(
            get_text("ask_button", lang),
            use_container_width=True,
            type="primary",
            key="ask_btn",
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Process query ──────────────────────────────────────────────────────────
    if ask_btn and final_query:
        with st.spinner(get_text("thinking", lang)):
            response = st.session_state.agent.get_response(final_query, lang)
            st.session_state.chat_history.append(
                {
                    "query": final_query,
                    "response": response,
                    "from_file": uploaded_file.name
                    if uploaded_file and not typed_query.strip()
                    else None,
                }
            )
            st.session_state.total_queries += 1
            st.session_state.verses_revealed += len(response.get("verses", []))
            st.session_state.uploaded_query = ""
            st.session_state.last_uploaded_name = ""
            # Dashboard data
            st.session_state.chat_timestamps.append(datetime.now())
            st.session_state.chat_categories.append(response.get("problem_type", "general"))
            st.session_state.lang_used.append(lang)
        st.rerun()

    # ══════════════════════════════════════════════
    # TABS: CHAT HISTORY & DASHBOARD
    # ══════════════════════════════════════════════
    if st.session_state.chat_history:
        tab1, tab2 = st.tabs(["🕉️ Divine Conversation", "📊 Wisdom Dashboard"])
        with tab1:
            for idx, chat in enumerate(reversed(st.session_state.chat_history)):
                response = chat["response"]
                verses = response.get("verses", [])
                ptype = response.get("problem_type", "general")
                answer_text = get_answer(response, lang)
                key_teaching = response.get("key_teaching", "")
                key_meaning = response.get("key_teaching_meaning", {})
                from_file = chat.get("from_file")

                # Seeker bubble
                file_tag = ""
                if from_file:
                    file_tag = (
                        f'<span style="font-size:.7rem;color:#d4a843;background:rgba(212,168,67,.1);'
                        f"border:1px solid rgba(212,168,67,.2);border-radius:20px;padding:.15rem .6rem;"
                        f'margin-left:.5rem">📄 {from_file}</span>'
                    )
                disp_q = chat["query"][:300] + ("..." if len(chat["query"]) > 300 else "")
                st.markdown(
                    f"""
                <div class="seeker-bubble">
                  <div class="seeker-bubble-inner">
                    <div class="seeker-label">🙏 {get_text("you_asked", lang)} {file_tag}</div>
                    <div class="seeker-text">{disp_q}</div>
                  </div>
                </div>""",
                    unsafe_allow_html=True,
                )

                # Problem badge
                if ptype != "general":
                    pt_display = get_problem_type_text(ptype, lang)
                    st.markdown(
                        f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:.5rem">
                      <div class="problem-badge">
                        <span class="problem-badge-label">{get_text("identified_as", lang)}</span>
                        <span class="problem-badge-value">{pt_display}</span>
                      </div>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                # Verses panel
                if verses:
                    st.markdown(
                        f"""
                    <div class="verses-panel">
                      <div class="verses-header">
                        <span class="verses-header-title">📿 {get_text("verse_label", lang)}</span>
                        <span class="verse-count-badge">{len(verses)} {get_text("verses_found", lang)}</span>
                      </div>""",
                        unsafe_allow_html=True,
                    )
                    for verse in verses:
                        ch = verse.get("Chapter", "")
                        vs = verse.get("Verse", "")
                        sanskrit = verse.get("Shloka", "")
                        tlit = verse.get("Transliteration", "")
                        meaning = verse.get(
                            "HinMeaning" if lang == "hindi" else "EngMeaning",
                            verse.get("EngMeaning", ""),
                        )
                        relevance = get_relevance(verse, lang)
                        st.markdown(
                            f"""
                        <div class="verse-item">
                          <div class="verse-ref">{get_text("chapter", lang)} {ch} · {get_text("verse_word", lang)} {vs}</div>
                          <div class="verse-sanskrit">{sanskrit[:200]}{"..." if len(sanskrit) > 200 else ""}</div>
                          {'<div class="verse-transliteration">' + tlit[:120] + ("..." if len(tlit) > 120 else "") + "</div>" if tlit else ""}
                          <div class="verse-meaning">{meaning}</div>
                          {'<div class="verse-relevance">💡 ' + relevance + "</div>" if relevance else ""}
                        </div>""",
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

                # Wisdom response
                if answer_text:
                    answer_html = answer_text.replace("\n", "<br>")
                    st.markdown(
                        f"""
                    <div class="wisdom-response">
                      <div class="wisdom-header">
                        <span class="wisdom-name">🎯 Pragya-Saarthi</span>
                        <span class="wisdom-subtitle">{get_text("agent_title", lang)}</span>
                      </div>
                      <div class="wisdom-body">{answer_html}</div>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                # Key teaching
                if key_teaching:
                    km = key_meaning.get(lang, key_meaning.get("english", ""))
                    st.markdown(
                        f"""
                    <div class="key-teaching">
                      <div>
                        <div class="key-teaching-sanskrit">✦ {key_teaching}</div>
                        {'<div class="key-teaching-meaning">' + km + "</div>" if km else ""}
                      </div>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                # Divider
                if idx < len(st.session_state.chat_history) - 1:
                    st.markdown(
                        """
                    <div class="conv-divider">
                      <div class="conv-divider-line"></div>
                      <div class="conv-divider-icon">✦</div>
                      <div class="conv-divider-line"></div>
                    </div>""",
                        unsafe_allow_html=True,
                    )
        with tab2:
            render_dashboard()
    else:
        render_welcome_screen(height=680)