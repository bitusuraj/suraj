# 🤖 AI Chatbot for Database Analytics

> Ask questions in plain English — get instant SQL-powered answers from your sales database.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-1C3C3C?logo=chainlink)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Project Overview

**AI SQL Chatbot** is a production-ready conversational data analytics tool. It bridges natural language and structured data by:

1. Accepting a plain-English question from the user
2. Using an LLM (OpenAI via LangChain) to generate a valid SQL query
3. Executing the query against a local SQLite database
4. Displaying the SQL and the results in a clean Streamlit UI

---

## 🏗️ Architecture

```
User Question (natural language)
        │
        ▼
┌─────────────────────┐
│  Streamlit Frontend │  ← streamlit_app.py
└────────┬────────────┘
         │  calls
         ▼
┌─────────────────────┐
│   app.py Controller │  ← orchestration layer
└──┬──────────────┬───┘
   │              │
   ▼              ▼
┌──────────┐  ┌──────────────────┐
│ LangChain│  │  query_executor  │
│  + OpenAI│  │  (pandas + SQLA) │
└──────────┘  └────────┬─────────┘
                       │
                       ▼
               ┌───────────────┐
               │  SQLite DB    │
               │  (sales.db)   │
               └───────────────┘
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🧠 Natural Language to SQL | Converts plain-English questions into SQLite queries |
| 🛡️ Read-only Safety Guard | Blocks INSERT / UPDATE / DELETE / DROP at the executor level |
| 📊 Interactive Results | Paginated table with CSV download |
| 💬 Conversation History | Keeps a session-level history of Q&A |
| 🎛️ Sidebar Quick Questions | One-click example queries |
| 🌙 Dark Glassmorphism UI | Premium, modern Streamlit design |
| 🔌 Configurable Model | Switch between `gpt-4o-mini`, `gpt-4o`, etc. via `.env` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Orchestration | LangChain `langchain-openai` |
| Frontend | Streamlit |
| Database | SQLite via SQLAlchemy |
| Data Processing | pandas |
| Config | python-dotenv |

---

## 📁 Folder Structure

```
ai-sql-chatbot/
│
├── backend/
│   ├── app.py                  # Main controller / pipeline
│   ├── database.py             # DB init, schema, seeding
│   ├── llm_sql_generator.py    # NL → SQL via LangChain + OpenAI
│   └── query_executor.py       # Safe SQL execution → DataFrame
│
├── frontend/
│   └── streamlit_app.py        # Streamlit UI
│
├── data/
│   ├── sample_sales_data.csv   # Seed data (100+ rows)
│   └── sales.db                # Auto-generated SQLite database
│
├── .env.example                # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 💡 Example Usage

**Question:** *"What were the top selling products last month?"*

**Generated SQL:**
```sql
SELECT product_name, SUM(sales) AS total_sales
FROM sales
WHERE strftime('%Y-%m', date) = strftime('%Y-%m', date('now', '-1 month'))
GROUP BY product_name
ORDER BY total_sales DESC
LIMIT 5
```

**Result:**

| product_name | total_sales |
|---|---|
| Standing Desk | 16,800 |
| Laptop Pro | 14,300 |
| Gaming Chair | 11,500 |
| Monitor 27" | 9,900 |
| Wireless Headphones | 8,100 |

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-sql-chatbot.git
cd ai-sql-chatbot

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

---

## ▶️ How to Run

```bash
# From the project root directory
streamlit run frontend/streamlit_app.py
```

The app will open automatically at **http://localhost:8501**.

> **First run:** The SQLite database (`data/sales.db`) is created and seeded automatically from `data/sample_sales_data.csv`.

### CLI Mode (optional, no UI)
```bash
cd backend
python app.py
```

---

## 🔮 Future Improvements

- [ ] **Multi-table support** — Join across multiple tables (e.g., customers, orders)
- [ ] **Chart visualisations** — Auto-generate bar / line charts with Plotly for numeric results
- [ ] **Query explanation** — Add a natural-language explanation of what the SQL does
- [ ] **Authentication** — User login / API key management UI
- [ ] **Query history persistence** — Store past Q&A in the database
- [ ] **Schema auto-discovery** — Introspect any SQLite/PostgreSQL database automatically
- [ ] **Few-shot prompt examples** — Include domain-specific SQL examples for better accuracy
- [ ] **Export to Excel** — Add XLSX download alongside CSV

---

## 📄 License

MIT © 2025 — see [LICENSE](LICENSE) for details.
