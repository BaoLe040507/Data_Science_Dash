from pathlib import Path
import streamlit as st


pages = [
    st.Page("pages/home.py", title="Home", icon="🏠"),
    st.Page("pages/stocks.py", title="Stocks Dashboard", icon="📈")
]

logo_path = Path(__file__).parent / "assets" / "data-science.png"
st.logo(str(logo_path))
pg = st.navigation(pages, position="sidebar",expanded=True)

pg.run()