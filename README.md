# 🗄️ Talk to Your Database — NL2SQL Agent

A natural language to SQL agent that lets anyone query a PostgreSQL database using plain English. Powered by LangChain Agents, OpenAI GPT-4, SQLAlchemy, and a Streamlit UI.

---

## ✨ Features

- **Natural language → SQL** with schema awareness
- **Auto error-correction** — agent retries on SQL errors automatically
- **Query explanation** — explains what the SQL does in plain English
- **Visual results** — table + bar/line chart rendering
- **Query history** — browse and re-run past queries
- **Safe execution** — read-only mode, query timeout, row limits
- **Sample database** — comes with a demo e-commerce DB to try immediately

---

## 📁 Project Structure

```
nl2sql/
├── app/
│   ├── agents/
│   │   └── nl2sql_agent.py      # LangChain SQL agent core
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy engine + session
│   │   └── schema_inspector.py  # Extract schema for prompt context
│   ├── ui/
│   │   └── streamlit_app.py     # Full Streamlit frontend
│   └── utils/
│       ├── query_history.py     # Save/load query history
│       └── chart_renderer.py    # Auto chart generation from results
├── tests/
│   └── test_agent.py
├── sample_data/
│   └── seed.sql                 # Demo e-commerce database
├── docs/
│   └── architecture.md
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in OPENAI_API_KEY and DATABASE_URL
```

### 3. Set up PostgreSQL
```bash
# Option A: Use Docker (easiest)
docker run --name nl2sql-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ecommerce \
  -p 5432:5432 -d postgres:15

# Option B: Use your own PostgreSQL instance
# Just update DATABASE_URL in .env

# Seed sample data
psql $DATABASE_URL -f sample_data/seed.sql
```

### 4. Run the app
```bash
streamlit run app/ui/streamlit_app.py
```

App opens at **http://localhost:8501**

---

## 🔑 Environment Variables

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://admin:password@localhost:5432/ecommerce
MAX_ROWS=500
QUERY_TIMEOUT=30
READ_ONLY=true
```

---

## 💬 Example Queries to Try

```
"Show me the top 10 customers by total order value"
"How many orders were placed each month in 2024?"
"Which product category has the highest return rate?"
"List all customers who haven't ordered in the last 90 days"
"What is the average order value by region?"
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | OpenAI GPT-4o |
| Agent Framework | LangChain SQL Agent |
| Database | PostgreSQL |
| ORM / DB Toolkit | SQLAlchemy |
| Frontend | Streamlit |
| Charts | Plotly |

---

## 📄 License
MIT
