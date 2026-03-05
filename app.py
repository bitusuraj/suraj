"""
app.py
------
Main controller: accepts a natural-language question, generates SQL via the
LLM, executes it against the SQLite database, and returns both the SQL and
the result DataFrame.
"""

import sys
import os

# Allow imports from the backend directory when running directly
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from database import init_db, get_table_schema
from llm_sql_generator import generate_sql
from query_executor import execute_query, QueryExecutionError


def answer_question(question: str) -> dict:
    """
    End-to-end pipeline: Natural Language → SQL → DataFrame.

    Parameters
    ----------
    question : str
        Plain-English question about the sales data.

    Returns
    -------
    dict with keys:
        - "sql"     : str            – the generated SQL query
        - "result"  : pd.DataFrame   – query result (may be empty)
        - "error"   : str | None     – error message if something went wrong
    """
    sql = ""
    try:
        # Step 1: Retrieve table schema for prompt context
        schema = get_table_schema()

        # Step 2: Generate SQL from natural language
        sql = generate_sql(question, schema)

        # Step 3: Execute the SQL query
        result_df = execute_query(sql)

        return {"sql": sql, "result": result_df, "error": None}

    except QueryExecutionError as exc:
        return {"sql": sql, "result": pd.DataFrame(), "error": str(exc)}
    except Exception as exc:
        return {"sql": sql, "result": pd.DataFrame(), "error": f"Unexpected error: {exc}"}


def main():
    """CLI entry point for quick testing without the Streamlit frontend."""
    init_db()

    print("\n🤖  AI Database Chatbot — CLI Mode")
    print("=" * 50)

    sample_questions = [
        "What were the top 5 selling products overall?",
        "What is the total sales by region?",
        "Which product had the highest sales in the North region?",
    ]

    for question in sample_questions:
        print(f"\n❓ Question: {question}")
        output = answer_question(question)

        print(f"📝 Generated SQL:\n{output['sql']}")
        if output["error"]:
            print(f"❌ Error: {output['error']}")
        else:
            print(f"📊 Result:\n{output['result'].to_string(index=False)}")
        print("-" * 50)


if __name__ == "__main__":
    main()
