def build_sql_generation_prompt(schema_str: str, question: str, max_rows: int) -> str:
    """Builds the strict prompt that forces the LLM to output pure SQL."""
    return f"""You are an expert PostgreSQL developer.
Given the following database schema:
{schema_str}

Write a strictly valid PostgreSQL query to answer this user question: "{question}"
- Output NOTHING BUT the raw SQL query. Do not wrap it in markdown or ```sql.
- Only use tables and columns that exist in the schema.
- Limit results to {max_rows} rows unless the user specifically asks for less.
- Never write destructive queries like DROP, DELETE, or UPDATE.
"""

def build_human_answer_prompt(question: str, sql_query: str, data_snippet: str) -> str:
    """Builds the prompt that tells the LLM to explain the returned data humanely."""
    return f"""You are an AI assistant answering a user's question about their database.
User Question: "{question}"
SQL Query Executed: {sql_query}
Data Returned (first 5 rows): {data_snippet}

Provide a short, friendly response.
1. Answer the user's question directly based on the data.
2. In a new paragraph starting with "Explanation:", explain in 1 simple sentence what the SQL query did.
"""
