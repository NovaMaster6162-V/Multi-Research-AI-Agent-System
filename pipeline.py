import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
import time

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Nova Master Research AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Advanced Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
    --bg-deep:       #050810;
    --bg-surface:    #0b0f1a;
    --bg-elevated:   #111828;
    --border:        rgba(255,255,255,0.07);
    --border-bright: rgba(255,255,255,0.14);
    --accent-cyan:   #00e5ff;
    --accent-violet: #7c3aed;
    --accent-amber:  #f59e0b;
    --accent-green:  #10b981;
    --accent-red:    #ef4444;
    --text-primary:  #f1f5f9;
    --text-muted:    #64748b;
    --text-dim:      #334155;
    --glow-cyan:     0 0 20px rgba(0,229,255,0.25);
    --glow-violet:   0 0 20px rgba(124,58,237,0.3);
    --radius-lg:     14px;
    --radius-xl:     20px;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1100px !important; }

/* ── Animated background grid ── */
.main::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Hero Banner ── */
.nexus-hero {
    position: relative;
    background: linear-gradient(135deg, #0d1424 0%, #0b0f1a 50%, #10071f 100%);
    border: 1px solid var(--border-bright);
    border-radius: var(--radius-xl);
    padding: 2.8rem 3rem;
    margin-bottom: 2.5rem;
    overflow: hidden;
}
.nexus-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.nexus-hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(0,229,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.nexus-hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-cyan) 60%, var(--accent-violet) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem !important;
    line-height: 1.1 !important;
}
.nexus-hero p {
    color: var(--text-muted) !important;
    font-size: 1.05rem !important;
    font-weight: 300;
    margin: 0 !important;
    letter-spacing: 0.02em;
}
.nexus-badge {
    display: inline-block;
    background: rgba(0,229,255,0.1);
    border: 1px solid rgba(0,229,255,0.25);
    color: var(--accent-cyan) !important;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 100px;
    margin-bottom: 1rem;
}

/* ── Pipeline Timeline ── */
.pipeline-timeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 2.5rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 1.4rem 2rem;
    overflow-x: auto;
}
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
    min-width: 130px;
    position: relative;
}
.pipeline-step:not(:last-child)::after {
    content: '';
    position: absolute;
    right: -12px;
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 2px;
    background: var(--border-bright);
}
.step-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    transition: all 0.3s ease;
}
.step-icon.idle     { background: rgba(255,255,255,0.05); border: 1px solid var(--border); }
.step-icon.active   { background: rgba(0,229,255,0.12); border: 1px solid rgba(0,229,255,0.4); box-shadow: var(--glow-cyan); animation: pulse-icon 1.5s infinite; }
.step-icon.done     { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.4); }
.step-icon.warn     { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.4); }
.step-label { font-size: 0.75rem; font-weight: 500; color: var(--text-muted); line-height: 1.3; }
.step-label strong { display: block; font-size: 0.82rem; color: var(--text-primary); font-weight: 600; }

@keyframes pulse-icon {
    0%, 100% { box-shadow: 0 0 10px rgba(0,229,255,0.2); }
    50%       { box-shadow: 0 0 25px rgba(0,229,255,0.5); }
}

/* ── Agent Cards ── */
.agent-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease;
}
.agent-card.active  { border-color: rgba(0,229,255,0.35); }
.agent-card.done    { border-color: rgba(16,185,129,0.3); }
.agent-card.report  { border-color: rgba(124,58,237,0.35); background: linear-gradient(135deg, #0b0f1a 0%, #0f0a1f 100%); }
.agent-card.critic  { border-color: rgba(245,158,11,0.3); }

.agent-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.agent-card.active::before  { background: linear-gradient(90deg, var(--accent-cyan), transparent); }
.agent-card.done::before    { background: linear-gradient(90deg, var(--accent-green), transparent); }
.agent-card.report::before  { background: linear-gradient(90deg, var(--accent-violet), var(--accent-cyan)); }
.agent-card.critic::before  { background: linear-gradient(90deg, var(--accent-amber), transparent); }

.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
}
.card-header .icon-chip {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}
.icon-chip.cyan   { background: rgba(0,229,255,0.12);   border: 1px solid rgba(0,229,255,0.25); }
.icon-chip.green  { background: rgba(16,185,129,0.12);  border: 1px solid rgba(16,185,129,0.25); }
.icon-chip.violet { background: rgba(124,58,237,0.12);  border: 1px solid rgba(124,58,237,0.3); }
.icon-chip.amber  { background: rgba(245,158,11,0.12);  border: 1px solid rgba(245,158,11,0.25); }

.card-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    letter-spacing: -0.01em;
}
.card-subtitle {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin: 0;
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-left: auto;
    flex-shrink: 0;
}
.status-dot.running { background: var(--accent-cyan); box-shadow: 0 0 8px var(--accent-cyan); animation: blink 1s infinite; }
.status-dot.done    { background: var(--accent-green); }
.status-dot.warn    { background: var(--accent-amber); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Report display ── */
.report-section {
    background: linear-gradient(135deg, #0b0f1a 0%, #0f0a1f 100%);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: var(--radius-lg);
    padding: 2rem 2.2rem;
    margin: 1rem 0;
    position: relative;
}
.report-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-violet), var(--accent-cyan));
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.report-section h1, .report-section h2, .report-section h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
.report-section h2 { color: var(--accent-cyan) !important; font-size: 1.3rem !important; }
.report-section h3 { color: #c4b5fd !important; font-size: 1.1rem !important; }

/* ── Feedback section ── */
.feedback-section {
    background: rgba(245,158,11,0.04);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: var(--radius-lg);
    padding: 1.8rem 2rem;
    margin: 1rem 0;
    position: relative;
}
.feedback-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-amber), transparent);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

/* ── Metrics Row ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.3rem;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Welcome Screen ── */
.welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    text-align: center;
    padding: 3rem;
}
.welcome-screen .big-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    filter: drop-shadow(0 0 30px rgba(0,229,255,0.4));
    animation: float 4s ease-in-out infinite;
}
@keyframes float {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-10px); }
}
.welcome-screen h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #fff 30%, var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.75rem !important;
}
.welcome-screen p { color: var(--text-muted) !important; font-size: 1rem !important; max-width: 380px; line-height: 1.6; }
.feature-pills {
    display: flex; gap: 0.6rem; flex-wrap: wrap; justify-content: center; margin-top: 1.5rem;
}
.feature-pill {
    background: var(--bg-elevated);
    border: 1px solid var(--border-bright);
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem !important; }

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.brand-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, var(--accent-violet), var(--accent-cyan));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3);
}
.brand-text { font-family: 'Syne', sans-serif !important; font-size: 1.05rem; font-weight: 700; }
.brand-sub  { font-size: 0.7rem; color: var(--text-muted); letter-spacing: 0.1em; text-transform: uppercase; }

/* ── Streamlit widget overrides ── */
div[data-testid="stTextInput"] input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,229,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.08) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.4rem !important;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-violet) 0%, #5b21b6 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
    color: white !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.5) !important;
}

/* ── Expanders ── */
details {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.3rem !important;
    margin: 0.5rem 0 1rem 0 !important;
}
summary {
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    padding: 0.7rem 1rem !important;
}
summary:hover { color: var(--text-primary) !important; }

/* ── Spinners / Progress ── */
div[data-testid="stSpinner"] { color: var(--accent-cyan) !important; }
div[data-testid="stSpinner"] > div { border-top-color: var(--accent-cyan) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ── History items ── */
.history-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 0.9rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 0.5rem;
    cursor: default;
    transition: border-color 0.2s;
}
.history-item:hover { border-color: var(--border-bright); }
.history-num {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    width: 22px; height: 22px;
    background: rgba(124,58,237,0.2);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    color: #c4b5fd;
    flex-shrink: 0;
}
.history-topic { font-size: 0.8rem; color: var(--text-muted); line-height: 1.3; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Tip box ── */
.tip-box {
    background: rgba(0,229,255,0.04);
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.6;
    margin-top: 1rem;
}
.tip-box strong { color: var(--accent-cyan); }

/* ── Section label ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.8rem;
    padding-left: 0.1rem;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Pipeline Function (streamlit-aware)
# ──────────────────────────────────────────────
def render_agent_card(emoji, chip_class, title, subtitle, status="running"):
    status_html = f'<div class="status-dot {status}"></div>' if status else ''
    st.markdown(f"""
    <div class="agent-card {'active' if status=='running' else 'done' if status=='done' else 'critic' if status=='warn' else ''}">
        <div class="card-header">
            <div class="icon-chip {chip_class}">{emoji}</div>
            <div>
                <p class="card-title">{title}</p>
                <p class="card-subtitle">{subtitle}</p>
            </div>
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def run_research_pipeline(topic: str) -> dict:
    state = {}
    t0 = time.time()

    # ── Step 1: Search ──────────────────────────
    st.markdown('<p class="section-label">Deep Research</p>', unsafe_allow_html=True)

    render_agent_card("🔍", "cyan", "Search Agent", "Scanning the web for relevant sources…", "running")
    with st.spinner(""):
        search_agent = build_search_agent()
        search_result = search_agent.invoke(
            {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
        )
    state["search_result"] = search_result["messages"][-1].content

    render_agent_card("🔍", "cyan", "Search Agent", "Sources retrieved successfully", "done")
    with st.expander("📄 View raw search results", expanded=False):
        st.write(state["search_result"])

    # ── Step 2: Reader ──────────────────────────
    render_agent_card("🌐", "cyan", "Reader Agent", "Scraping the most relevant source…", "running")
    with st.spinner(""):
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Result:\n{state['search_result'][:800]}",
            )]
        })
    state["scraped_content"] = reader_result["messages"][-1].content

    render_agent_card("🌐", "cyan", "Reader Agent", "Deep content extracted", "done")
    with st.expander("📄 View scraped content", expanded=False):
        st.write(state["scraped_content"])

    # ── Step 3: Writer ──────────────────────────
    render_agent_card("✍️", "violet", "Writer Agent", "Synthesising research into a structured report…", "running")
    with st.spinner(""):
        research_combined = (
            f"SEARCH RESULT:\n{state['search_result']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})

    render_agent_card("✍️", "violet", "Writer Agent", "Report drafted and ready", "done")

    # ── Report Output ──
    st.markdown('<p class="section-label" style="margin-top:1.5rem">Generated Report</p>', unsafe_allow_html=True)
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.markdown(state["report"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 4: Critic ──────────────────────────
    st.markdown('<p class="section-label" style="margin-top:1.5rem">Quality Review</p>', unsafe_allow_html=True)
    render_agent_card("🧐", "amber", "Critic Agent", "Evaluating the report for accuracy & gaps…", "warn")
    with st.spinner(""):
        state["feedback"] = critic_chain.invoke({"report": state["report"]})

    render_agent_card("🧐", "amber", "Critic Agent", "Review complete", "done")

    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    st.markdown(state["feedback"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Metrics ──
    elapsed = round(time.time() - t0, 1)
    word_count = len(state["report"].split())
    st.markdown('<p class="section-label" style="margin-top:2rem">Run Summary</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-card">
            <div class="metric-value" style="color:var(--accent-cyan)">{elapsed}s</div>
            <div class="metric-label">Total Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:var(--accent-violet)">{word_count:,}</div>
            <div class="metric-label">Words Generated</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:var(--accent-green)">4</div>
            <div class="metric-label">Agents Used</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return state


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">⚡</div>
        <div>
            <div class="brand-text">Nexus Research</div>
            <div class="brand-sub">AI Pipeline v2</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Input
    st.markdown('<p class="section-label">New Research</p>', unsafe_allow_html=True)
    topic_input = st.text_input(
        "TOPIC",
        placeholder="e.g. Quantum computing in 2025",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Deep Research", type="primary", use_container_width=True)

    # Tip
    st.markdown("""
    <div class="tip-box">
        <strong>Pro tip:</strong> Be specific for better results — include a year, domain, or angle for richer reports.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # How it works
    st.markdown('<p class="section-label">Pipeline Steps</p>', unsafe_allow_html=True)
    steps = [
        ("🔍", "Search", "Finds recent sources"),
        ("🌐", "Reader", "Scrapes top result"),
        ("✍️", "Writer", "Drafts the report"),
        ("🧐", "Critic", "Reviews & critiques"),
    ]
    for emoji, name, desc in steps:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.55rem;">
            <span style="font-size:1rem;">{emoji}</span>
            <div>
                <div style="font-size:0.8rem;font-weight:600;color:var(--text-primary)">{name}</div>
                <div style="font-size:0.72rem;color:var(--text-muted)">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Past runs
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.session_state.history:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Past Runs</p>', unsafe_allow_html=True)
        for i, entry in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
            <div class="history-item">
                <div class="history-num">{i+1}</div>
                <div class="history-topic">{entry['topic']}</div>
            </div>
            """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Main Area
# ──────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if run_btn:
    if not topic_input.strip():
        st.error("⚠️  Please enter a research topic before running the pipeline.")
    else:
        # Hero banner
        st.markdown(f"""
        <div class="nexus-hero">
            <div class="nexus-badge">⚡ Run Deep Research</div>
            <h1>Researching<br>{topic_input}</h1>
            <p>4-stage AI pipeline · Search → Scrape → Write → Critique</p>
        </div>
        """, unsafe_allow_html=True)

        result = run_research_pipeline(topic_input)
        st.session_state.history.append({"topic": topic_input, "result": result})
        st.balloons()

elif not st.session_state.history:
    # Welcome / empty state
    st.markdown("""
    <div class="nexus-hero" style="margin-bottom:2rem">
        <div class="nexus-badge">Powered by LangChain + Claude</div>
        <h1>Deep Research,<br>On Demand.</h1>
        <p>A 4-stage AI pipeline that searches, scrapes, writes, and self-critiques — all in one click.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="welcome-screen">
        <div class="big-icon">🔬</div>
        <h2>Ready to Research</h2>
        <p>Enter any topic in the sidebar and hit <strong style="color:var(--accent-cyan)">Run Pipeline</strong> to generate a structured, critiqued research report.</p>
        <div class="feature-pills">
            <span class="feature-pill">🌐 Web Search</span>
            <span class="feature-pill">📄 Auto Scraping</span>
            <span class="feature-pill">✍️ AI Writing</span>
            <span class="feature-pill">🧐 Self-Critique</span>
            <span class="feature-pill">📜 Run History</span>
        </div>
    </div>
    """, unsafe_allow_html=True)