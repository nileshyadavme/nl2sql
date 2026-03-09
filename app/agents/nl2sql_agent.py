import logging
import re
from typing import Optional
from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI

from app.database.connection import DatabaseConnection
from app.database.schema_inspector import SchemaInspector
from app.agents.prompts import build_sql_generation_prompt, build_human_answer_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Structured result from the NL2SQL agent."""
    question: str
    sql_query: str
    answer: str
    explanation: str
    columns: list = field(default_factory=list)
    rows: list = field(default_factory=list)
    error: Optional[str] = None
    success: bool = True


SYSTEM_PREFIX = """You are an expert SQL agent that helps users query a PostgreSQL database.

Your job:
1. Understand the user's natural language question
2. Generate the correct SQL query for the given schema
3. Execute the query
4. Return a clear, helpful answer based on the results

Rules you MUST follow:
- ALWAYS look at the schema first using the sql_db_schema tool before writing any SQL
- ONLY use tables and columns that actually exist in the schema
- Use LIMIT to cap results (default: 100 rows unless user asks for more)
- Write clean, readable SQL with proper aliases
- If a query fails, analyze the error and try a corrected version automatically
- NEVER make up data — only use what the database returns
- If the question is ambiguous, make a reasonable assumption and state it

After getting results, always:
- Give a direct answer to the user's question
- Briefly explain what the SQL query does in simple terms
"""


class NL2SQLAgent:
    """
    Lightweight, highly-optimized agent that converts natural language to SQL.

    Pipeline (2 API Calls ONLY):
      1. Schema + Question → LLM → SQL Generation
      2. App executes SQL locally.
      3. SQL + Data → LLM → Answer & Explanation
    """

    def __init__(self, db: DatabaseConnection, gemini_api_key: str, model: str = "gemini-2.5-flash-lite"):
        self.db = db
        self.schema_inspector = SchemaInspector(db)

        # Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=gemini_api_key,
        )

        logger.info(f"NL2SQLAgent initialised with direct prompting pipeline (model={model})")

    def run(self, question: str, max_rows: int = 500) -> AgentResult:
        """
        Run the full NL2SQL pipeline efficiently with minimal API calls.
        """
        logger.info(f"Processing question: '{question}'")

        try:
            # 1. Fetch schema locally (0 API calls)
            schema_str = self.schema_inspector.get_schema_prompt()

            # 2. Generate SQL (API Call 1)
            sql_prompt = build_sql_generation_prompt(schema_str, question, max_rows)
            sql_response = self.llm.invoke(sql_prompt)
            sql_query = sql_response.content.strip()
            # Clean up just in case the LLM ignores instructions and adds markdown
            sql_query = re.sub(r"^```(sql)?\s*|```\s*$", "", sql_query, flags=re.IGNORECASE).strip()

            if not sql_query:
                raise ValueError("LLM failed to generate a SQL query.")

            # 3. Execute locally (0 API calls)
            columns, rows = [], []
            answer = ""
            explanation = ""
            try:
                columns, rows = self.db.execute_query(sql_query, max_rows=max_rows)
                
                # 4. Generate Answer and Explanation (API Call 2)
                # Send the question, the SQL, and a snippet of the data back to get a nice answer
                data_snippet = str(rows[:5])
                answer_prompt = build_human_answer_prompt(question, sql_query, data_snippet)
                final_response = self.llm.invoke(answer_prompt)
                final_text = final_response.content.strip()
                
                # Split the answer and explanation
                if "Explanation:" in final_text:
                    parts = final_text.split("Explanation:")
                    answer = parts[0].strip()
                    explanation = parts[1].strip()
                else:
                    answer = final_text
                    explanation = "This query selects data to answer your question."

            except Exception as exec_err:
                logger.warning(f"Direct execution failed: {exec_err}")
                answer = f"I generated the SQL, but there was an error running it: {exec_err}"

            return AgentResult(
                question=question,
                sql_query=sql_query,
                answer=answer,
                explanation=explanation,
                columns=columns,
                rows=rows,
                success=True,
            )

        except PermissionError as e:
            return AgentResult(
                question=question,
                sql_query="",
                answer=str(e),
                explanation="",
                error=str(e),
                success=False,
            )
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return AgentResult(
                question=question,
                sql_query="",
                answer=f"I encountered an error: {str(e)}",
                explanation="",
                error=str(e),
                success=False,
            )

    def get_schema_summary(self) -> str:
        """Return the schema as a formatted string."""
        return self.schema_inspector.get_schema_prompt()

    def get_table_stats(self) -> dict:
        """Return row counts per table."""
        return self.schema_inspector.get_table_row_counts()
