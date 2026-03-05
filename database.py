"""
database.py
-----------
Handles SQLite database creation, schema definition, and CSV data loading.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"
CSV_PATH = BASE_DIR / "data" / "sample_sales_data.csv"

DATABASE_URL = f"sqlite:///{DB_PATH}"


# ── Schema ─────────────────────────────────────────────────────────────────────
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sales (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT    NOT NULL,
    region       TEXT    NOT NULL,
    sales        INTEGER NOT NULL,
    date         DATE    NOT NULL
);
"""

TABLE_SCHEMA = """
Table: sales
Columns:
  - id           INTEGER  PRIMARY KEY, auto-incremented unique row identifier
  - product_name TEXT     Name of the product sold (e.g. 'Laptop Pro', 'Wireless Mouse')
  - region       TEXT     Sales region: 'North', 'South', 'East', or 'West'
  - sales        INTEGER  Total sales amount in USD for that row
  - date         DATE     Date of the sale in YYYY-MM-DD format
"""


def get_engine():
    """Return a SQLAlchemy engine connected to the SQLite sales database."""
    return create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Initialise the database:
      1. Create the sales table if it does not exist.
      2. Seed it from the CSV file if the table is empty.
    """
    os.makedirs(DB_PATH.parent, exist_ok=True)
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        conn.commit()

        row_count = conn.execute(text("SELECT COUNT(*) FROM sales")).scalar()

    if row_count == 0:
        _seed_from_csv(engine)
        print(f"[database] Seeded sales table from {CSV_PATH}")
    else:
        print(f"[database] sales table already contains {row_count} rows – skipping seed.")


def _seed_from_csv(engine) -> None:
    """Load the sample CSV into the sales table."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Sample data file not found: {CSV_PATH}\n"
            "Please ensure data/sample_sales_data.csv exists."
        )
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_sql("sales", con=engine, if_exists="append", index=False)


def get_table_schema() -> str:
    """Return the human-readable schema string used in LLM prompts."""
    return TABLE_SCHEMA
