# ============================================================
# ReviewSense – All-in-One App
# Roles: admin (full dashboard) | customer (product reviews)
# CSV Upload → runs Milestone 1→2→3 pipeline in-memory
# ============================================================

import hashlib, re, string, io
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from datetime import datetime
from textblob import TextBlob
from wordcloud import WordCloud

# ─────────────────────────────────────────────
# 0. CONFIG  (must be FIRST st call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ReviewSense",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 1. USERS  {username: (hashed_pw, role)}
# ─────────────────────────────────────────────
def _h(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "admin":    (_h("admin123"),    "admin"),
    "customer": (_h("customer123"), "customer"),
}

# ─────────────────────────────────────────────
# 2. SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
for key, val in {
    "authenticated": False,
    "username": "",
    "role": "",
    "pipeline_df": None,
    "keywords_df": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# 3. PIPELINE FUNCTIONS  (milestone 1-2-3)
# ─────────────────────────────────────────────
STOPWORDS = {
    "is","the","and","a","an","to","of","in","on","for","with","this",
    "that","it","was","are","as","at","be","by","from","or","but","i",
    "my","me","we","our","you","your","they","their","its","very","so",
    "just","not","no","have","has","had","do","did","does","will","would",
    "could","should","more","much","all","also","get","got","been","being",
}

def milestone1_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw feedback → add clean_feedback column."""
    def clean(text):
        text = str(text).lower()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"\d+", "", text)
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r"\s+", " ", text).strip()
        words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
        return " ".join(words)
    df = df.copy()
    df["clean_feedback"] = df["feedback"].apply(clean)
    return df

def milestone2_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Add sentiment + confidence_score columns."""
    def get_sent(text):
        pol = TextBlob(str(text)).sentiment.polarity
        label = "positive" if pol > 0 else ("negative" if pol < 0 else "neutral")
        return label, round(pol, 4)
    df = df.copy()
    df[["sentiment","confidence_score"]] = df["clean_feedback"].apply(
        lambda x: pd.Series(get_sent(x))
    )
    return df

def milestone3_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """Extract keyword frequencies from clean_feedback."""
    all_words = []
    for text in df["clean_feedback"].dropna():
        words = re.sub(r"[^a-z\s]", "", str(text)).split()
        all_words.extend([w for w in words if len(w) > 2])
    freq = Counter(all_words)
    kdf = pd.DataFrame(freq.items(), columns=["keyword","frequency"])
    return kdf.sort_values("frequency", ascending=False).reset_index(drop=True)

def run_pipeline(uploaded_file) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run full M1→M2→M3 pipeline on an uploaded file."""
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            raw = pd.read_csv(uploaded_file)
        else:
            raw = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to read file: {str(e)}")
        st.stop()
        return None, None

    required = {"feedback", "date", "product"}
    missing = required - set(raw.columns)
    if missing:
        st.error(f"❌ Missing columns: {missing}. File needs: feedback, date, product.")
        st.stop()
        return None, None

    try:
        with st.spinner("🔄 Running Milestone 1 – Cleaning text…"):
            df = milestone1_clean(raw)
        with st.spinner("🧠 Running Milestone 2 – Sentiment analysis…"):
            df = milestone2_sentiment(df)
        with st.spinner("🔑 Running Milestone 3 – Keyword extraction…"):
            kdf = milestone3_keywords(df)

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["sentiment"] = df["sentiment"].str.lower().str.strip()
        return df, kdf
    except Exception as e:
        st.error(f"❌ Pipeline error: {str(e)}")
        return None, None

# ─────────────────────────────────────────────
# 4. GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

/* ══════════════════════════════════════════
   FULL DARK THEME
══════════════════════════════════════════ */

/* Main background — target every Streamlit container layer */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, .block-container {
    background-color: #0d1120 !important;
    background:       #0d1120 !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Force ALL text dark-theme */
p, span, div, label, li, td, th,
.stMarkdown p,
[data-testid="stMarkdownContainer"] p,
[data-testid="stText"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #e2e8f0 !important;
}
h1, h2, h3, h4, h5, h6 { color: #f0f4ff !important; }

/* Hide Streamlit chrome */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: #080c18 !important;
    border-right: 1px solid #1b2240 !important;
}
[data-testid="stSidebar"] * { color: #c8d0e8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span { color: #111 !important; }

/* ── Native st.metric ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#141929,#0c1019) !important;
    border: 1px solid #1e2845 !important;
    border-radius: 14px !important;
    padding: 1.2rem 1.4rem !important;
}

/* ── Custom metric cards ── */
.rs-metric {
    background: linear-gradient(135deg,#141929 0%,#0c1019 100%);
    border: 1px solid #1e2845;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    box-shadow: 0 6px 24px rgba(0,0,0,0.5);
}
.rs-metric .label {
    font-size: 0.75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .08em;
    color: #6b7799 !important; margin-bottom: .5rem;
}
.rs-metric .value {
    font-family: 'Syne', sans-serif; font-size: 2.2rem;
    font-weight: 800; color: #ffffff !important; line-height: 1;
}
.rs-metric .sub {
    font-size: 0.78rem; color: #4a5270 !important;
    margin-top: .35rem;
}

/* ── Section headings ── */
.rs-section {
    font-family: 'Syne', sans-serif; font-size: 1.1rem;
    font-weight: 700; color: #e2e8f0 !important;
    margin: 2rem 0 1rem;
    border-left: 3px solid #38c9a4; padding-left: .75rem;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzone"] {
    background: #111827 !important;
    border: 1.5px dashed #2a3560 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"] * { color: #8892b0 !important; }
[data-testid="stFileUploader"] small { color: #555e7a !important; }

/* ── Alerts / banners ── */
[data-testid="stAlert"] {
    background: #111827 !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div { color: #c8d0e8 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { background: #111827 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1e2845 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary p { color: #c8d0e8 !important; }

/* ── Selectbox / multiselect dropdowns ── */
[data-baseweb="select"] > div,
[data-baseweb="popover"] { background: #111827 !important; }
[data-baseweb="menu"] { background: #111827 !important; }
[data-baseweb="menu"] li { color: #e2e8f0 !important; }

/* ── Slider ── */
[data-testid="stSlider"] p { color: #8892b0 !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #111827 !important;
    border: 1px solid #2a3560 !important;
    color: #38c9a4 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #1a2540 !important;
    border-color: #38c9a4 !important;
}

/* ── Text inputs (login) ── */
.stTextInput input {
    background: #1a2035 !important;
    color: #e2e8f0 !important;
    border: 1.5px solid #2a3560 !important;
    border-radius: 10px !important;
    -webkit-text-fill-color: #e2e8f0 !important;
}
.stTextInput input::placeholder { color: #4a5580 !important; }
.stTextInput input:focus {
    border-color: #1d63dc !important;
    box-shadow: 0 0 0 3px rgba(29,99,220,.25) !important;
}
.stTextInput label { color: #8892b0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg,#1d63dc,#1a52b8) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px rgba(29,99,220,.4) !important;
    transition: transform .15s, box-shadow .2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(29,99,220,.55) !important;
}

/* ── Review cards ── */
.review-card {
    background: #111827;
    border: 1px solid #1e2845;
    border-radius: 14px; padding: 1.1rem 1.4rem;
    margin-bottom: .8rem; transition: border-color .2s;
}
.review-card:hover { border-color: #38c9a4; }
.review-sentiment {
    display: inline-block; font-size: 0.73rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .08em;
    padding: .2rem .65rem; border-radius: 20px; margin-bottom: .5rem;
}
.sent-positive { background:#0d2e10; color:#4CAF50; border:1px solid #1a5e20; }
.sent-negative { background:#2e0d0d; color:#F44336; border:1px solid #5e1a1a; }
.sent-neutral  { background:#1e2030; color:#9E9E9E; border:1px solid #2e3050; }

/* ── Role badge ── */
.role-badge {
    display: inline-block; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .1em;
    padding: .2rem .7rem; border-radius: 20px;
    background: rgba(29,99,220,.2); color: #6ea8fe;
    border: 1px solid rgba(29,99,220,.35);
}
.role-badge.customer {
    background: rgba(56,201,164,.12); color: #38c9a4;
    border-color: rgba(56,201,164,.35);
}

/* ── Dividers ── */
hr { border-color: #1e2845 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 5. LOGIN PAGE
# ─────────────────────────────────────────────
def show_login():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(ellipse 80% 55% at 50% -5%, rgba(29,99,220,.4) 0%, transparent 70%),
          radial-gradient(ellipse 45% 35% at 90% 85%, rgba(56,201,164,.15) 0%, transparent 60%),
          #07090f !important;
    }
    [data-testid="stSidebar"] { display:none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Brand
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 1.5rem;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
           width:76px;height:76px;border-radius:22px;
           background:linear-gradient(135deg,#1d63dc 0%,#38c9a4 100%);
           font-size:2.4rem;box-shadow:0 10px 36px rgba(29,99,220,.5);
           margin-bottom:1.1rem;">📊</div>
      <div style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
           letter-spacing:-.03em;
           background:linear-gradient(90deg,#fff 30%,#38c9a4 100%);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
           background-clip:text;">ReviewSense</div>
      <div style="color:rgba(255,255,255,.4);font-size:.9rem;letter-spacing:.04em;margin-top:.3rem;">
        Customer Feedback Intelligence Platform
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Card
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("""
        <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);
             border-radius:22px;padding:2.2rem 2.4rem 2.6rem;
             backdrop-filter:blur(20px);
             box-shadow:0 28px 72px rgba(0,0,0,.45),0 1px 0 rgba(255,255,255,.07) inset;">
          <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:#fff;margin-bottom:.25rem;">
            Welcome back
          </div>
          <div style="color:rgba(255,255,255,.35);font-size:.84rem;margin-bottom:1.8rem;">
            Sign in to access your workspace
          </div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username", key="li_user")
        password = st.text_input("Password", placeholder="Enter your password",
                                 type="password", key="li_pass")
        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", use_container_width=True):
            u = username.strip().lower()
            if not u or not password:
                st.error("⚠️ Please enter both username and password.")
            elif u in USERS and USERS[u][0] == _h(password):
                st.session_state.authenticated = True
                st.session_state.username = u
                st.session_state.role = USERS[u][1]
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

        st.markdown("""
        <div style="text-align:center;margin-top:1.4rem;color:rgba(255,255,255,.28);font-size:.78rem;">
          <b style="color:rgba(56,201,164,.7);">Admin</b> → admin / admin123
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <b style="color:rgba(56,201,164,.7);">Customer</b> → customer / customer123
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 6. SIDEBAR (shared by both roles)
# ─────────────────────────────────────────────
def render_sidebar(df, role):
    with st.sidebar:
        # User info
        badge_cls = "customer" if role == "customer" else ""
        st.markdown(f"""
        <div style="padding:.8rem 0 1.2rem;">
          <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
               color:#fff;margin-bottom:.4rem;">📊 ReviewSense</div>
          <div style="margin-bottom:.6rem;">
            <span style="font-size:.85rem;color:rgba(255,255,255,.5);">Logged in as </span>
            <span style="font-size:.85rem;color:#fff;font-weight:600;">
              {st.session_state.username}
            </span>
          </div>
          <span class="role-badge {badge_cls}">{role}</span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        filters = {}

        if df is not None and not df.empty:
            # Sentiment filter
            st.markdown("**🎯 Sentiment**")
            sent_opts = ["positive","negative","neutral"]
            sent_sel = st.multiselect(
                "Sentiment", sent_opts, default=sent_opts, label_visibility="collapsed"
            )
            filters["sentiment"] = sent_sel

            # Product filter
            st.markdown("**📦 Product**")
            products = sorted(df["product"].dropna().unique().tolist())
            prod_sel = st.multiselect(
                "Product", products, default=products, label_visibility="collapsed"
            )
            filters["product"] = prod_sel

            # Date range
            if "date" in df.columns and df["date"].notna().any():
                st.markdown("**📅 Date Range**")
                d_min = df["date"].min().date()
                d_max = df["date"].max().date()
                start = st.date_input("From", value=d_min, min_value=d_min, max_value=d_max)
                end   = st.date_input("To",   value=d_max, min_value=d_min, max_value=d_max)
                filters["start_date"] = start
                filters["end_date"]   = end

            # Admin: keyword search
            if role == "admin":
                st.markdown("**🔍 Keyword Search**")
                kw = st.text_input("Search in reviews", placeholder="e.g. battery life",
                                   label_visibility="collapsed")
                filters["keyword"] = kw

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.pipeline_df = None
            st.session_state.keywords_df = None
            st.rerun()

    return filters

def apply_filters(df, filters):
    f = df.copy()
    if "sentiment" in filters and filters["sentiment"]:
        f = f[f["sentiment"].isin(filters["sentiment"])]
    if "product" in filters and filters["product"]:
        f = f[f["product"].isin(filters["product"])]
    if "start_date" in filters:
        f = f[f["date"] >= pd.to_datetime(filters["start_date"])]
    if "end_date" in filters:
        f = f[f["date"] <= pd.to_datetime(filters["end_date"])]
    if filters.get("keyword","").strip():
        kw = filters["keyword"].strip().lower()
        f = f[f["feedback"].str.lower().str.contains(kw, na=False)]
    return f

# ─────────────────────────────────────────────
# 7. SHARED: UPLOAD & PIPELINE SECTION
# ─────────────────────────────────────────────
def upload_section():
    st.markdown('<div class="rs-section">📁 Upload Feedback File</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(29,99,220,.08);border:1px solid rgba(29,99,220,.2);
         border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem;font-size:.88rem;
         color:rgba(255,255,255,.65);">
      Upload a <b style="color:#fff;">.csv</b> or <b style="color:#fff;">.xlsx</b> file
      with columns: <code>feedback</code>, <code>date</code>, <code>product</code>.
      The pipeline will automatically clean, analyse sentiment, and extract keywords.
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your file here",
        type=["csv","xlsx"],
        label_visibility="collapsed",
    )

    if uploaded:
        df, kdf = run_pipeline(uploaded)
        st.session_state.pipeline_df  = df
        st.session_state.keywords_df  = kdf
        st.success(f"✅ Pipeline complete! {len(df):,} reviews processed.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reviews", f"{len(df):,}")
        col2.metric("Products", df["product"].nunique())
        col3.metric("Unique Keywords", len(kdf))
        st.markdown("<hr style='border-color:rgba(255,255,255,.08);margin:1.5rem 0'>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 8. ADMIN DASHBOARD
# ─────────────────────────────────────────────
SENT_COLORS = {"positive":"#4CAF50","negative":"#F44336","neutral":"#9E9E9E"}
SENT_DISPLAY = {"positive":"Positive","negative":"Negative","neutral":"Neutral"}

def admin_dashboard():
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
         color:#fff;margin-bottom:.2rem;">
        📊 Admin Dashboard
    </div>
    <div style="color:rgba(255,255,255,.4);font-size:.9rem;margin-bottom:1.5rem;">
        Full analytics — sentiment, trends, keywords & exports
    </div>
    """, unsafe_allow_html=True)

    # ── Upload ──────────────────────────────
    upload_section()

    df  = st.session_state.pipeline_df
    kdf = st.session_state.keywords_df

    if df is None:
        st.info("⬆️ Upload a feedback file above to get started.")
        return

    # ── Sidebar filters ──────────────────────
    filters = render_sidebar(df, "admin")
    fdf = apply_filters(df, filters)

    if fdf.empty:
        st.warning("No data matches the current filters.")
        return

    # ── KPI Metrics ──────────────────────────
    st.markdown('<div class="rs-section">📈 Key Metrics</div>', unsafe_allow_html=True)
    total = len(fdf)
    pos = (fdf["sentiment"]=="positive").sum()
    neg = (fdf["sentiment"]=="negative").sum()
    neu = (fdf["sentiment"]=="neutral").sum()
    avg_score = fdf["confidence_score"].mean()

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, label, value, sub in [
        (c1,"Total Reviews", f"{total:,}", f"{df['product'].nunique()} products"),
        (c2,"Positive",      f"{pos/total*100:.1f}%", f"{pos:,} reviews"),
        (c3,"Negative",      f"{neg/total*100:.1f}%", f"{neg:,} reviews"),
        (c4,"Neutral",       f"{neu/total*100:.1f}%", f"{neu:,} reviews"),
        (c5,"Avg Score",     f"{avg_score:+.3f}", "–1 negative · +1 positive"),
    ]:
        col.markdown(f"""
        <div class="rs-metric">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # ── Sentiment Distribution ────────────────
    st.markdown('<div class="rs-section">😊 Sentiment Distribution</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([3,2])
    with col_a:
        counts = fdf["sentiment"].value_counts()
        fig, ax = plt.subplots(figsize=(8,4))
        fig.patch.set_facecolor("#0d1120")
        ax.set_facecolor("#0d1120")
        bars = ax.bar(
            [SENT_DISPLAY.get(s,s) for s in counts.index],
            counts.values,
            color=[SENT_COLORS.get(s,"gray") for s in counts.index],
            width=0.5, edgecolor="none"
        )
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+15,
                    f"{int(b.get_height()):,}", ha="center", color="#fff", fontsize=11)
        ax.set_xlabel("Sentiment", color="#aaa"); ax.set_ylabel("Reviews", color="#aaa")
        ax.tick_params(colors="#aaa"); ax.spines[:].set_visible(False)
        ax.yaxis.grid(True, color=(1,1,1,0.06), linewidth=.8)
        plt.tight_layout()
        st.pyplot(fig); plt.close()
    with col_b:
        fig2, ax2 = plt.subplots(figsize=(5,4))
        fig2.patch.set_facecolor("#0d1120")
        ax2.set_facecolor("#0d1120")
        wedges, texts, autotexts = ax2.pie(
            counts.values,
            labels=[SENT_DISPLAY.get(s,s) for s in counts.index],
            colors=[SENT_COLORS.get(s,"gray") for s in counts.index],
            autopct="%1.1f%%", startangle=90,
            wedgeprops=dict(edgecolor="#0d1120", linewidth=2)
        )
        for t in texts+autotexts: t.set_color("#ddd")
        plt.tight_layout()
        st.pyplot(fig2); plt.close()

    # ── Product Sentiment Table + Heatmap ────
    st.markdown('<div class="rs-section">📦 Product-wise Sentiment</div>', unsafe_allow_html=True)
    prod_sent = fdf.groupby("product")["sentiment"].value_counts().unstack(fill_value=0)
    for s in ["positive","negative","neutral"]:
        if s not in prod_sent.columns: prod_sent[s] = 0
    prod_sent["Total"]     = prod_sent.sum(axis=1)
    prod_sent["Positive%"] = (prod_sent["positive"]/prod_sent["Total"]*100).round(1)
    prod_sent = prod_sent.sort_values("Positive%", ascending=False)

    display_df = prod_sent[["positive","negative","neutral","Total","Positive%"]].copy()
    display_df.columns = ["👍 Positive","👎 Negative","➖ Neutral","Total","✅ Positive %"]
    display_df["✅ Positive %"] = display_df["✅ Positive %"].round(1)
    st.dataframe(display_df, use_container_width=True)

    # Heatmap
    if len(prod_sent) <= 20:
        fig_hm, ax_hm = plt.subplots(figsize=(10, max(4, len(prod_sent)*0.55)))
        fig_hm.patch.set_facecolor("#0d1120")
        sns.heatmap(prod_sent[["positive","negative","neutral"]], annot=True, fmt="d",
                    cmap="RdYlGn", ax=ax_hm, linewidths=.5, linecolor="#0d1120")
        ax_hm.set_facecolor("#0d1120")
        ax_hm.set_title("Product Sentiment Heatmap", color="#ddd")
        ax_hm.tick_params(colors="#aaa")
        plt.tight_layout()
        st.pyplot(fig_hm); plt.close()

    # ── Trend Over Time ───────────────────────
    st.markdown('<div class="rs-section">📈 Monthly Sentiment Trend</div>', unsafe_allow_html=True)
    if fdf["date"].notna().any():
        tmp = fdf.copy()
        tmp["month"] = tmp["date"].dt.to_period("M")
        trend = tmp.groupby(["month","sentiment"]).size().unstack(fill_value=0)
        fig_t, ax_t = plt.subplots(figsize=(12,5))
        fig_t.patch.set_facecolor("#0d1120")
        ax_t.set_facecolor("#0d1120")
        for sent in trend.columns:
            ax_t.plot(trend.index.astype(str), trend[sent], marker="o",
                      linewidth=2.5, label=SENT_DISPLAY.get(sent,sent),
                      color=SENT_COLORS.get(sent,"gray"))
        ax_t.set_xlabel("Month", color="#aaa"); ax_t.set_ylabel("Reviews", color="#aaa")
        ax_t.legend(labelcolor="#ddd", facecolor="#1a1f2e", edgecolor="none")
        ax_t.tick_params(axis="x", rotation=45, colors="#aaa")
        ax_t.tick_params(axis="y", colors="#aaa")
        ax_t.spines[:].set_visible(False)
        ax_t.yaxis.grid(True, color=(1,1,1,0.06))
        plt.tight_layout()
        st.pyplot(fig_t); plt.close()

    # ── Confidence Score Distribution ─────────
    st.markdown('<div class="rs-section">📊 Confidence Score Distribution</div>',
                unsafe_allow_html=True)
    fig_h, ax_h = plt.subplots(figsize=(10,4))
    fig_h.patch.set_facecolor("#0d1120")
    ax_h.set_facecolor("#0d1120")
    ax_h.hist(fdf["confidence_score"].dropna(), bins=30,
              color="#1d63dc", alpha=.8, edgecolor="none")
    ax_h.axvline(0, color="#38c9a4", linewidth=1.5, linestyle="--", label="Neutral (0)")
    ax_h.set_xlabel("Polarity Score (–1 to +1)", color="#aaa")
    ax_h.set_ylabel("Count", color="#aaa")
    ax_h.tick_params(colors="#aaa"); ax_h.spines[:].set_visible(False)
    ax_h.yaxis.grid(True, color=(1,1,1,0.06))
    ax_h.legend(labelcolor="#ddd", facecolor="#1a1f2e", edgecolor="none")
    plt.tight_layout()
    st.pyplot(fig_h); plt.close()

    # ── Keywords + Word Cloud ─────────────────
    if kdf is not None and not kdf.empty:
        st.markdown('<div class="rs-section">🔑 Keywords & Word Cloud</div>',
                    unsafe_allow_html=True)
        col_kw, col_wc = st.columns([3,2])
        with col_kw:
            top15 = kdf.head(15)
            fig_k, ax_k = plt.subplots(figsize=(8,6))
            fig_k.patch.set_facecolor("#0d1120")
            ax_k.set_facecolor("#0d1120")
            bars_k = ax_k.barh(top15["keyword"], top15["frequency"],
                               color="#38c9a4", edgecolor="none")
            ax_k.invert_yaxis()
            ax_k.set_xlabel("Frequency", color="#aaa")
            ax_k.set_title("Top 15 Keywords", color="#ddd")
            ax_k.tick_params(colors="#aaa"); ax_k.spines[:].set_visible(False)
            ax_k.xaxis.grid(True, color=(1,1,1,0.06))
            for b in bars_k:
                ax_k.text(b.get_width()+2, b.get_y()+b.get_height()/2,
                          f"{int(b.get_width()):,}", va="center", color="#ddd", fontsize=9)
            plt.tight_layout()
            st.pyplot(fig_k); plt.close()
        with col_wc:
            wc = WordCloud(
                width=500, height=400, background_color="#0d1120",
                colormap="cool", min_font_size=9
            ).generate_from_frequencies(dict(zip(kdf["keyword"], kdf["frequency"])))
            fig_wc, ax_wc = plt.subplots(figsize=(6,5))
            fig_wc.patch.set_facecolor("#0d1120")
            ax_wc.imshow(wc, interpolation="bilinear")
            ax_wc.axis("off")
            plt.tight_layout()
            st.pyplot(fig_wc); plt.close()

    # ── Raw Data Preview + Download ───────────
    with st.expander("📋 Preview Filtered Data"):
        st.dataframe(fdf.head(20), use_container_width=True)

    st.markdown('<div class="rs-section">💾 Export</div>', unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    col_d1.download_button(
        "⬇️ Download Filtered Reviews (.csv)",
        fdf.to_csv(index=False).encode(),
        "ReviewSense_Filtered.csv", "text/csv", use_container_width=True
    )
    if kdf is not None and not kdf.empty:
        col_d2.download_button(
            "⬇️ Download Keywords (.csv)",
            kdf.to_csv(index=False).encode(),
            "ReviewSense_Keywords.csv", "text/csv", use_container_width=True
        )

    st.success("✅ Dashboard fully loaded. Use the sidebar to slice and dice.")


# ─────────────────────────────────────────────
# 9. CUSTOMER VIEW
# ─────────────────────────────────────────────
def customer_view():
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
         color:#fff;margin-bottom:.2rem;">
        🛍️ Product Reviews
    </div>
    <div style="color:rgba(255,255,255,.4);font-size:.9rem;margin-bottom:1.5rem;">
        Browse customer reviews and see what people think about each product
    </div>
    """, unsafe_allow_html=True)

    # Upload section (customer can also upload)
    upload_section()

    df = st.session_state.pipeline_df
    if df is None:
        st.info("⬆️ Upload a feedback file above to explore reviews.")
        return

    filters = render_sidebar(df, "customer")
    fdf = apply_filters(df, filters)

    if fdf.empty:
        st.warning("No reviews match the current filters.")
        return

    # ── Mini KPIs ─────────────────────────────
    total = len(fdf)
    pos = (fdf["sentiment"]=="positive").sum()
    neg = (fdf["sentiment"]=="negative").sum()

    c1,c2,c3 = st.columns(3)
    for col, label, value, sub in [
        (c1,"Reviews Shown",  f"{total:,}", f"across {fdf['product'].nunique()} products"),
        (c2,"👍 Positive",    f"{pos/total*100:.0f}%", f"{pos:,} happy customers"),
        (c3,"👎 Negative",    f"{neg/total*100:.0f}%", f"{neg:,} unhappy customers"),
    ]:
        col.markdown(f"""
        <div class="rs-metric">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # ── Product Summary Cards ─────────────────
    st.markdown('<div class="rs-section">📦 Product Summary</div>', unsafe_allow_html=True)
    products = sorted(fdf["product"].unique())
    cols = st.columns(min(len(products), 4))
    for i, prod in enumerate(products):
        pdf = fdf[fdf["product"]==prod]
        pos_p = (pdf["sentiment"]=="positive").mean()*100
        badge = "🟢" if pos_p>=60 else ("🔴" if pos_p<40 else "🟡")
        cols[i%4].markdown(f"""
        <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
             border-radius:12px;padding:1rem;text-align:center;margin-bottom:.5rem;">
          <div style="font-size:.75rem;color:rgba(255,255,255,.4);margin-bottom:.3rem;">
            {badge} {len(pdf)} reviews
          </div>
          <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
               color:#fff;margin-bottom:.3rem;">{prod}</div>
          <div style="font-size:1.4rem;font-weight:800;
               color:{'#4CAF50' if pos_p>=60 else '#F44336' if pos_p<40 else '#FFC107'};">
            {pos_p:.0f}%
          </div>
          <div style="font-size:.72rem;color:rgba(255,255,255,.3);">positive</div>
        </div>""", unsafe_allow_html=True)

    # ── Review Feed ───────────────────────────
    st.markdown('<div class="rs-section">💬 Review Feed</div>', unsafe_allow_html=True)

    # Sort options
    sort_by = st.selectbox("Sort by", ["Most Recent","Most Positive","Most Negative"],
                           label_visibility="collapsed")
    if sort_by == "Most Recent":
        fdf_sorted = fdf.sort_values("date", ascending=False)
    elif sort_by == "Most Positive":
        fdf_sorted = fdf.sort_values("confidence_score", ascending=False)
    else:
        fdf_sorted = fdf.sort_values("confidence_score", ascending=True)

    show_n = st.slider("Reviews to show", 5, 50, 15, label_visibility="collapsed")

    for _, row in fdf_sorted.head(show_n).iterrows():
        sent = row.get("sentiment","neutral")
        sc   = row.get("confidence_score",0)
        date = pd.to_datetime(row["date"]).strftime("%b %d, %Y") if pd.notna(row["date"]) else "–"
        st.markdown(f"""
        <div class="review-card">
          <span class="review-sentiment sent-{sent}">{SENT_DISPLAY.get(sent,sent)}</span>
          <span style="font-size:.75rem;color:rgba(255,255,255,.3);margin-left:.6rem;">
            {row['product']} · {date} · score {sc:+.2f}
          </span>
          <div style="color:rgba(255,255,255,.85);margin-top:.5rem;font-size:.92rem;
               line-height:1.55;">
            "{row['feedback']}"
          </div>
          {'<div style="font-size:.75rem;color:rgba(255,255,255,.3);margin-top:.4rem;">— ' + str(row.get("customer_name","Anonymous")) + '</div>' if "customer_name" in row else ""}
        </div>""", unsafe_allow_html=True)

    # ── Download filtered reviews (customer can download too) ──
    st.download_button(
        "⬇️ Download these reviews",
        fdf_sorted.head(show_n).to_csv(index=False).encode(),
        "my_reviews.csv", "text/csv"
    )


# ─────────────────────────────────────────────
# 10. MAIN ROUTER
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    show_login()
    st.stop()

role = st.session_state.role
if role == "admin":
    admin_dashboard()
else:
    customer_view()
