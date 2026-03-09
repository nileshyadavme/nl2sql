# Architecture — NL2SQL Agent

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ Question Box │  │ SQL Viewer    │  │ Results + Chart  │ │
│  │ + History    │  │ + Explanation │  │ (Plotly / Table) │ │
│  └──────┬───────┘  └───────────────┘  └──────────────────┘ │
└─────────┼───────────────────────────────────────────────────┘
          │ question
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    NL2SQLAgent                              │
│                                                             │
│  1. Receives natural language question                      │
│  2. LangChain SQL Agent runs with these tools:             │
│     - sql_db_schema  → reads table/column definitions      │
│     - sql_db_query   → executes SQL against PostgreSQL     │
│     - sql_db_list_tables → lists available tables          │
│  3. GPT-4o writes SQL, agent executes it                   │
│  4. If SQL fails → agent auto-retries with error message   │
│  5. Returns: answer + SQL + columns + rows                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌──────────────┐  ┌─────────────────┐  ┌────────────┐
│  PostgreSQL  │  │   OpenAI API    │  │  Pinecone  │
│  (via SQLAl  │  │  GPT-4o         │  │  (not used │
│   chemy)     │  │  text-emb-3     │  │  here)     │
└──────────────┘  └─────────────────┘  └────────────┘
```

## LangChain Agent Loop

```
Question received
      │
      ▼
  Agent thinks:
  "I need to see the schema first"
      │
      ▼
  Tool: sql_db_list_tables → ["customers", "orders", "products"...]
      │
      ▼
  Tool: sql_db_schema → full column/type info for relevant tables
      │
      ▼
  GPT-4o generates SQL:
    SELECT c.name, SUM(o.total_amount)
    FROM customers c JOIN orders o ON o.customer_id = c.id
    GROUP BY c.name ORDER BY 2 DESC LIMIT 10
      │
      ▼
  Tool: sql_db_query → executes SQL, returns rows
      │
  ┌───┴───────────────────────┐
  │ SQL error?                │ No → format final answer
  │ Yes → agent reads error   │
  │ rewrites SQL and retries  │
  └───────────────────────────┘
```

## Key Design Decisions

### Schema injection
The `SchemaInspector` extracts full table/column/FK info and injects it into the LangChain agent's tool context. This is what makes the agent schema-aware — it doesn't guess table names.

### Read-only safety
`DatabaseConnection.execute_query()` checks the first keyword of every SQL statement. INSERT, UPDATE, DELETE, DROP, etc. raise `PermissionError` before ever reaching the database.

### Auto-retry
LangChain's `handle_parsing_errors=True` + `max_iterations=10` means the agent will automatically retry failed SQL up to 10 times, each time reading the error message and correcting the query.

### Sample rows in prompt
`SQLDatabase(sample_rows_in_table_info=3)` includes 3 sample rows per table in the tool context. This helps GPT-4o understand data formats (e.g. date formats, enum values) without extra prompting.
