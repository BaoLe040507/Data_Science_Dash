import streamlit as st


PRIMARY = "#A05AFF"
BG_DARK = "#0f172a"


st.markdown(
    f"""
    <style>
        .hero-card {{
            background: linear-gradient(120deg, {PRIMARY}, #6b21a8);
            border-radius: 18px;
            padding: 2.5rem;
            color: white;
            text-align: center;
            box-shadow: 0 20px 45px rgba(160, 90, 255, 0.25);
        }}
        .info-card {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            height: 100%;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.3rem 0.85rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.15);
            font-size: 0.82rem;
            margin-right: 0.4rem;
            margin-bottom: 0.4rem;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown(
        """
        <div class="hero-card">
            <h1 style="margin-bottom:0.4rem;">Data Science Portfolio Hub</h1>
            <p style="font-size:1.1rem;margin-bottom:1.5rem;">
                A living dashboard where I curate every project, experiment, and concept that has shaped my journey as a data scientist.
            </p>
            <div style="display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;">
                <span class="badge">Projects & Case Studies</span>
                <span class="badge">Tools & Workflows</span>
                <span class="badge">Market Research</span>
                <span class="badge">Learning Notes</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.subheader("Why this space exists")
st.write(
    "This application is my single source of truth for everything I build and learn:"
    "\n- **Archive projects** with context, code links, and outcomes."
    "\n- **Track concepts & tools** (frameworks, libraries, workflows) so I can revisit them quickly."
    "\n- **Log experiments** from market analysis or model tuning without losing insight."
)

st.write("")
cols = st.columns(3)
cards = [
    (
        "Project Library",
        "Chronological stories of every analysis, model, and dashboard I’ve delivered—complete with links, lessons, and future improvements.",
    ),
    (
        "Concept & Tool Vault",
        "My personal wiki for statistical methods, ML techniques, data engineering tricks, and the stack I rely on.",
    ),
    (
        "Execution Playbook",
        "Reusable templates for data prep, visualization, deployment, and reporting so I can spin up new work fast.",
    ),
]
for col, (title, body) in zip(cols, cards):
    with col:
        st.markdown(
            f"""
            <div class="info-card">
                <h4 style="color:{PRIMARY};margin-bottom:0.7rem;">{title}</h4>
                <p style="margin:0;">{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
st.subheader("Current focus")
with st.container():
    st.markdown(
        f"""
        <div class="info-card" style="border-color:{PRIMARY};">
            <strong>Active track:</strong> market structure analysis & long/short thesis generation.<br>
            <strong>Tooling:</strong> Streamlit, Supabase, PostgreSQL, Pandas, Polars, DuckDB.<br>
            <strong>Next up:</strong> automate nightly portfolio snapshots and add ML-driven anomaly alerts.
        </div>
        """,
        unsafe_allow_html=True,
    )

