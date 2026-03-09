import logging
import re
from typing import Optional
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.prompts import PromptTemplate

from app.database.connection import DatabaseConnection
from app.database.schema_inspector import SchemaInspector

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
    LangChain-powered agent that converts natural language to SQL.

    Pipeline:
      Question → LangChain SQL Agent → Schema Lookup → SQL Generation
               → SQL Execution → Auto-Retry on Error → Answer + Explanation
    """

    def __init__(self, db: DatabaseConnection, openai_api_key: str, model: str = "gpt-4o"):
        self.db = db
        self.schema_inspector = SchemaInspector(db)

        # LangChain SQLDatabase wrapper (used by the agent tools)
        self.sql_db = SQLDatabase(
            engine=db.get_engine(),
            sample_rows_in_table_info=3,   # show 3 sample rows per table in prompt
        )

        # GPT-4o LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            openai_api_key=openai_api_key,
        )

        # Build the LangChain SQL agent
        self.agent = create_sql_agent(
            llm=self.llm,
            db=self.sql_db,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            prefix=SYSTEM_PREFIX,
            verbose=True,
            max_iterations=10,          # max tool calls before giving up
            handle_parsing_errors=True,
        )

        logger.info(f"NL2SQLAgent initialised with model={model}")

    def run(self, question: str, max_rows: int = 500) -> AgentResult:
        """
        Run the full NL2SQL pipeline for a given natural language question.
        Returns a structured AgentResult with SQL, answer, and data.
        """
        logger.info(f"Processing question: '{question}'")

        try:
            # Run the agent — it will loop: schema → sql → execute → maybe retry
            response = self.agent.invoke({"input": question})
            agent_output = response.get("output", "")

            # Extract SQL from agent's intermediate steps
            sql_query = self._extract_sql(response)

            # If we got SQL, execute it ourselves to get structured data
            columns, rows = [], []
            if sql_query:
                try:
                    columns, rows = self.db.execute_query(sql_query, max_rows=max_rows)
                except Exception as exec_err:
                    logger.warning(f"Direct execution failed: {exec_err}")

            # Generate a plain-English explanation of the SQL
            explanation = self._explain_sql(sql_query) if sql_query else ""

            return AgentResult(
                question=question,
                sql_query=sql_query or "Could not extract SQL",
                answer=agent_output,
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

    def _extract_sql(self, agent_response: dict) -> str:
        """
        Extract the SQL query from the agent's intermediate steps.
        The agent logs tool calls — we look for the SQLQuery tool call.
        """
        try:
            steps = agent_response.get("intermediate_steps", [])
            for step in steps:
                if isinstance(step, tuple) and len(step) == 2:
                    action = step[0]
                    if hasattr(action, "tool") and "sql" in action.tool.lower():
                        query = action.tool_input
                        if isinstance(query, dict):
                            query = query.get("query", "")
                        if query:
                            return query.strip()

            # Fallback: regex extract from output text
            output = agent_response.get("output", "")
            match = re.search(r"```sql\s*(.*?)\s*```", output, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        except Exception as e:
            logger.warning(f"SQL extraction failed: {e}")

        return ""

    def _explain_sql(self, sql: str) -> str:
        """Ask the LLM to explain the SQL in plain English."""
        if not sql or len(sql) < 10:
            return ""
        try:
            response = self.llm.invoke(
                f"Explain this SQL query in 1-2 simple sentences a non-technical person would understand:\n\n{sql}"
            )
            return response.content
        except Exception:
            return ""

    def get_schema_summary(self) -> str:
        """Return the schema as a formatted string."""
        return self.schema_inspector.get_schema_prompt()

    def get_table_stats(self) -> dict:
        """Return row counts per table."""
        return self.schema_inspector.get_table_row_counts()
