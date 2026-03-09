# ⚡ QueryMind: Natural Language to SQL Agent

QueryMind is a highly optimized, AI-powered agent that translates natural language questions into executable SQL queries. It allows anyone, regardless of technical expertise, to converse with their database, extract insights, and auto-generate visualizations—all through a modern, responsive web interface.

Built focusing on performance and reliability, QueryMind uses a bespoke two-shot prompting pipeline powered by Google's Gemini models to ensure incredibly fast latency, deterministic SQL extraction, and minimal API footprint.

---

## ✨ Core Features

- **Schema-Aware SQL Generation**: Dynamically inspects your database schema, tables, and relationships to construct highly accurate PostgreSQL or SQLite queries.
- **Lightning Fast 2-Shot Architecture**: Abandons heavy agent-loop frameworks (like ReAct) in favor of a strict 2-call deterministic pipeline (Schema → SQL → Local Execution → Natural Language Answer), reducing API calls by over 70% per query.
- **Auto Data Visualization**: Automatically detects result structures to render appropriate Bar, Line, or Scatter charts using Plotly.
- **Enterprise-Grade UI**: A beautiful, custom dark-themed Streamlit interface inspired by modern developer tools, featuring a query console, metrics, history, and a schema explorer.
- **Data Safety First**: Implements read-only enforcement at the engine level, query timeouts, and strict `LIMIT` injection to ensure your production database is never mutated or overwhelmed.
- **Bundled Demo Mode**: Includes an offline, ready-to-test SQLite e-commerce database (`sample.db`) so you can test the AI securely without providing real database credentials.

---

## 📁 System Architecture

The codebase handles UI rendering, SQL extraction, execution, and LLM communication through cleanly separated modules:

```text
nl2sql/
├── app/
│   ├── agents/
│   │   ├── nl2sql_agent.py      # Core optimized 2-shot pipeline logic
│   │   └── prompts.py           # Decoupled LLM system prompts
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy engine + read-only session management
│   │   └── schema_inspector.py  # DDL / Metadata extraction for prompt context
│   ├── ui/
│   │   ├── streamlit_app.py     # Streamlit entry point & orchestration
│   │   ├── main_content.py      # Query console, DataFrame, and Chart layouts
│   │   ├── sidebar.py           # DB connection and history state
│   │   └── styles.py            # Global custom CSS and theme definitions
│   └── utils/
│       ├── query_history.py     # Local JSON history persistence
│       └── chart_renderer.py    # Heuristic-based auto chart generation
├── sample.db                    # Bundled SQLite database for safe demo testing
├── .env                         # Environment variables configuration
└── README.md
```

---

## 🚀 Getting Started

### 1. Requirements & Installation

We use Python 3.12+ and recommend using a virtual environment (`venv` or `uv`).

```bash
# Clone the repository
git clone https://github.com/yourusername/nl2sql.git
cd nl2sql

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your API keys.

```bash
cp .env.example .env
```

Open `.env` and add your Google Gemini API key:
```ini
GEMINI_API_KEY="AIzaSyYourSecretKeyHere..."
# Optional: Set a default database URL
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
```

### 3. Running the Application

Start the Streamlit web server:

```bash
streamlit run app/ui/streamlit_app.py
```

The application will launch on **http://localhost:8501**. 

### 4. Trying the Demo Mode (No Setup Required)
If you don't have a PostgreSQL database ready, simply toggle the **"Use bundled Demo DB"** switch in the sidebar to securely experiment with the pre-loaded `sample.db` e-commerce dataset.

---

## ☁️ Deployment (Streamlit Community Cloud)

QueryMind is designed to be instantly deployable on platforms like Streamlit Community Cloud for free.

1. Push your repository to GitHub (the `sample.db` is safe to commit if you want a public demo).
2. Log into [share.streamlit.io](https://share.streamlit.io/).
3. Click **New app**, select your repository, and set the Main file path to `app/ui/streamlit_app.py`.
4. Under **Advanced settings**, inject your API keys into the Secrets manager:
   ```toml
   GEMINI_API_KEY="your-gemini-key"
   ```
5. Deploy and share the URL. Users can leverage the *Demo DB feature* without needing any database credentials.

---

## 💡 Example Queries

If you're using the built-in Demo database, try asking these natural language questions:

- *"Show me the top 10 products by total revenue."*
- *"Which products have the highest return rate?"*
- *"What is the monthly sales trend for 2024?"*
- *"List all customers located in the South region who have purchased Electronics."*
- *"What is the total quantity sold for each product category?"*

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **LLM Engine** | Google Gemini (2.0 Flash) via `langchain-google-genai` |
| **Frontend Framework** | Streamlit |
| **Data Engine** | Pandas & SQLAlchemy |
| **Visualizations** | Plotly |
| **Supported Databases** | PostgreSQL, SQLite |

---

## 📄 License
MIT License. See `LICENSE` for more information.
