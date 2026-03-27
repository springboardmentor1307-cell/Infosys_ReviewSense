# 📊 ReviewSense — Customer Feedback Intelligence Platform

> A multi-role Streamlit dashboard that automatically cleans, analyses sentiment, and extracts keywords from customer feedback data — all in one upload.

---

## 🗂️ Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Milestones](#milestones)
- [Features by Role](#features-by-role)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [How to Use](#how-to-use)
- [Input File Format](#input-file-format)
- [Login Credentials](#login-credentials)
- [Dependencies](#dependencies)
- [Screenshots](#screenshots)

---

## Overview

**ReviewSense** is a customer feedback analysis platform built with Python and Streamlit. It takes raw customer reviews, runs them through a 3-stage NLP pipeline (cleaning → sentiment analysis → keyword extraction), and presents the results as an interactive dark-themed dashboard.

The system supports **two user roles**:
- **Admin** — full analytics dashboard with charts, heatmaps, trends, word clouds, and exports
- **Customer** — simplified review browser with product summaries and a sortable review feed

---

## Project Structure

```
reviewsense/
│
├── app.py                              ← Main app (login + all roles in one file)
│
├── milestone1.py                       ← Standalone: Text cleaning & preprocessing
├── milestone2.py                       ← Standalone: Sentiment analysis (TextBlob)
├── milestone3.py                       ← Standalone: Keyword frequency extraction
│
├── login.py                            ← Standalone login page (legacy)
│
├── ReviewSense_Customer_Feedback_5000.xlsx   ← Sample dataset (5,000 reviews)
│
├── Milestone1_Cleaned_Feedback.csv     ← Output of milestone1.py
├── Milestone2_Sentiment_Results.csv    ← Output of milestone2.py
├── Milestone3_Keyword_Insights.csv     ← Output of milestone3.py
│
├── sentiment_bar_chart.png             ← Chart saved by milestone2.py
│
└── README.md                           ← This file
```

---

## Milestones

The NLP pipeline is split into three stages, each building on the previous:

### Milestone 1 — Data Cleaning & Preprocessing (`milestone1.py`)
- Reads raw feedback from the Excel file
- Converts text to lowercase
- Removes URLs, digits, and punctuation
- Strips common stopwords (the, and, is, etc.)
- Outputs: `Milestone1_Cleaned_Feedback.csv`

### Milestone 2 — Sentiment Analysis (`milestone2.py`)
- Reads cleaned feedback from Milestone 1
- Uses **TextBlob** to compute sentiment polarity (−1.0 to +1.0)
- Labels each review as **positive**, **negative**, or **neutral**
- Generates a sentiment bar chart (`sentiment_bar_chart.png`)
- Outputs: `Milestone2_Sentiment_Results.csv`

### Milestone 3 — Keyword Extraction (`milestone3.py`)
- Reads sentiment-labelled data from Milestone 2
- Counts word frequencies across all cleaned reviews
- Ranks keywords by frequency
- Outputs: `Milestone3_Keyword_Insights.csv`

### Milestone 4 — Interactive Dashboard (`app.py`)
- Combines all three milestones into a live in-memory pipeline
- Upload any CSV/XLSX → pipeline runs automatically in the browser
- Role-based access: Admin dashboard vs Customer review feed
- Full dark-themed UI with filters, charts, and export options

---

## Features by Role

### 🔐 Admin
| Feature | Details |
|---|---|
| CSV / XLSX Upload | Triggers full M1→M2→M3 pipeline automatically |
| KPI Cards | Total reviews, Positive %, Negative %, Neutral %, Avg score |
| Sentiment Bar + Pie Chart | Visual breakdown of positive / negative / neutral |
| Product Sentiment Table | Per-product counts with colour-coded Positive % |
| Product Heatmap | Seaborn heatmap across all products |
| Monthly Trend Chart | Line chart of sentiment over time |
| Confidence Score Histogram | Distribution of polarity scores (−1 to +1) |
| Top Keywords Bar Chart | Horizontal bar of top 15 most frequent words |
| Word Cloud | Visual word cloud from all keywords |
| Sidebar Filters | Filter by sentiment, product, date range, keyword search |
| Export | Download filtered reviews CSV + keywords CSV |
| Raw Data Preview | Expandable table showing first 20 rows |

### 🛍️ Customer
| Feature | Details |
|---|---|
| CSV / XLSX Upload | Same pipeline, simpler results view |
| Mini KPI Cards | Reviews shown, Positive %, Negative % |
| Product Summary Cards | Per-product positive % with colour indicators |
| Review Feed | Paginated reviews with sentiment badge, score, date |
| Sort Options | Most Recent / Most Positive / Most Negative |
| Slider | Control how many reviews to display (5–50) |
| Export | Download visible reviews as CSV |

---

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/yourname/reviewsense.git
cd reviewsense
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install manually:

```bash
pip install streamlit pandas numpy matplotlib seaborn textblob wordcloud openpyxl
python -m textblob.download_corpora
```

---

## How to Run

### Run the full app (recommended)

```bash
streamlit run app.py
```

Then open your browser at: **http://localhost:8501**

### Run individual milestone scripts

```bash
python milestone1.py   # Cleans raw Excel → CSV
python milestone2.py   # Sentiment analysis → CSV + chart
python milestone3.py   # Keyword extraction → CSV
```

> ⚠️ Standalone scripts expect the Excel file and previous CSVs to be in the **same folder**.

---

## How to Use

1. **Open the app** — `streamlit run app.py`
2. **Log in** with admin or customer credentials (see below)
3. **Upload your feedback file** — `.csv` or `.xlsx` with the required columns
4. The pipeline runs automatically in 3 stages (Milestone 1 → 2 → 3)
5. **Explore the dashboard** — use the sidebar to filter by sentiment, product, or date
6. **Export results** — download filtered reviews or keyword lists as CSV

---

## Input File Format

Your uploaded file **must contain these three columns** (exact names, case-insensitive):

| Column | Type | Example |
|---|---|---|
| `feedback` | Text | "Great product, fast delivery!" |
| `date` | Date | 2025-03-15 |
| `product` | Text | Laptop |

Additional columns (like `customer_name`, `feedback_id`) are preserved and displayed.

**Supported formats:** `.csv`, `.xlsx`

**Example row:**
```
feedback_id, customer_name, feedback,              date,       product
1,           Priya,         Great service!,         2025-01-10, Mobile
```

---

## Login Credentials

| Role | Username | Password | Access |
|---|---|---|---|
| Admin | `admin` | `admin123` | Full dashboard, all charts, keyword analysis, exports |
| Customer | `customer` | `customer123` | Review feed, product summaries, basic export |

> 💡 To add more users, edit the `USERS` dictionary in `app.py` and add a new entry with a SHA-256 hashed password.

```python
import hashlib
print(hashlib.sha256("yournewpassword".encode()).hexdigest())
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | Data loading, cleaning, filtering |
| `numpy` | Numerical operations |
| `matplotlib` | Charts and plots |
| `seaborn` | Heatmap visualisation |
| `textblob` | Sentiment analysis (polarity scoring) |
| `wordcloud` | Word cloud generation |
| `openpyxl` | Reading `.xlsx` Excel files |
| `hashlib` | Password hashing (built-in) |
| `collections` | Keyword frequency counting (built-in) |

Install all at once:

```bash
pip install streamlit pandas numpy matplotlib seaborn textblob wordcloud openpyxl
python -m textblob.download_corpora
```

---

## Screenshots

| Screen | Description |
|---|---|
| Login Page | Dark-themed login with role-based routing |
| Admin Dashboard | Full analytics with KPI cards, charts, heatmap, word cloud |
| Customer View | Product summary cards + sortable review feed |

---

## Notes

- The pipeline runs **in-memory** — no files are written to disk when using the upload feature in `app.py`
- TextBlob sentiment is rule-based and works best on English text
- For large files (10,000+ rows), sentiment analysis may take 10–30 seconds
- The app uses Streamlit's `@st.cache_data` pattern — re-uploading the same file won't re-run the pipeline unless the file changes

---

## Author

Built as part of a customer feedback analysis project using Python, Streamlit, and NLP.

---

*ReviewSense — Turn reviews into insights.*
