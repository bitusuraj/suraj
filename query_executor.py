"""
query_executor.py
-----------------
Safely executes a SQL query against the SQLite database and returns the
result as a pandas DataFrame.
"""

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import get_engine


class QueryExecutionError(Exception):
    """Raised when a SQL query fails to execute."""


def execute_query(sql: str) -> pd.DataFrame:
    """
    Execute *sql* against the sales database.

    Parameters
    ----------
    sql : str
        A valid SQL SELECT statement.

    Returns
    -------
    pd.DataFrame
        Query results as a DataFrame. Returns an empty DataFrame if the
        query produces no rows.

    Raises
    ------
    QueryExecutionError
        If the query contains a forbidden statement or a database error occurs.
    """
    _validate_query(sql)

    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

        if not rows:
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(rows, columns=columns)

    except SQLAlchemyError as exc:
        raise QueryExecutionError(
            f"Database error while executing query:\n{sql}\n\nDetail: {exc}"
        ) from exc
    except Exception as exc:
        raise QueryExecutionError(
            f"Unexpected error while executing query:\n{sql}\n\nDetail: {exc}"
        ) from exc


def _validate_query(sql: str) -> None:
    """
    Lightweight guard: reject any SQL that tries to mutate the database.
    Only SELECT statements are allowed.
    """
    forbidden_keywords = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"}
    upper_sql = sql.strip().upper()

    for keyword in forbidden_keywords:
        # Check that the statement doesn't *start* with or *contain* a forbidden keyword
        if upper_sql.startswith(keyword) or f" {keyword} " in upper_sql:
            raise QueryExecutionError(
                f"Forbidden SQL operation detected: '{keyword}'. "
                "Only SELECT queries are permitted."
            )

    if not upper_sql.startswith("SELECT"):
        raise QueryExecutionError(
            "Only SELECT queries are permitted. "
            f"Received query starting with: '{sql.split()[0]}'"
        )
