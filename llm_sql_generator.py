"""
llm_sql_generator.py
--------------------
Converts a natural-language question into a valid SQLite SQL query using
Google Gemini via LangChain.

Handles free-tier 429 RESOURCE_EXHAUSTED errors with:
  • Exponential backoff retry (up to 3 attempts per model)
  • Model fallback chain: gemini-2.0-flash → gemini-1.5-flash → gemini-1.0-pro
"""

import os
import re
import time
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Model fallback chain (tried in order on quota exhaustion) ──────────────────
_MODEL_FALLBACK_CHAIN = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
]

# ── Retry settings ─────────────────────────────────────────────────────────────
_MAX_RETRIES = 3          # attempts per model before moving to the next
_INITIAL_WAIT = 5         # seconds before first retry
_BACKOFF_FACTOR = 2       # each retry doubles the wait

# ── Prompt Template ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert SQLite SQL query generator.

You will be given a database schema and a natural-language question.
Your task is to convert the question into a single, valid SQLite SQL SELECT query.

Rules:
1. Return ONLY the raw SQL query — no markdown, no code fences, no explanation.
2. Use only the tables and columns defined in the schema below.
3. For date filtering, use SQLite date functions (e.g. strftime, date()).
4. Always use proper SQL syntax compatible with SQLite 3.
5. Do NOT add a trailing semicolon.
6. If the question cannot be answered with the given schema, return:
   SELECT 'Unable to generate query for this question' AS message

Database Schema:
{schema}
"""

HUMAN_PROMPT = "Question: {question}"

_prompt_template = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", HUMAN_PROMPT)]
)


def _is_quota_error(exc: Exception) -> bool:
    """Return True if the exception is a 429 / RESOURCE_EXHAUSTED quota error."""
    msg = str(exc).upper()
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg or "QUOTA" in msg


def _build_llm(model: str) -> ChatGoogleGenerativeAI:
    """Instantiate a Gemini chat model for the given *model* name."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. "
            "Please add it to your .env file. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        )
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0,
        google_api_key=api_key,
    )


def _clean_sql(raw: str) -> str:
    """Strip markdown code fences and extra whitespace from the LLM response."""
    cleaned = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    cleaned = cleaned.rstrip(";").strip()
    return cleaned


def generate_sql(question: str, schema: str) -> str:
    """
    Convert a natural-language *question* into a SQL query.

    Retries with exponential backoff and falls back through the model chain
    when a free-tier quota (429) error is encountered.

    Parameters
    ----------
    question : str
        The user's question in plain English.
    schema : str
        The table schema description to include in the prompt.

    Returns
    -------
    str
        A SQL SELECT query string.

    Raises
    ------
    RuntimeError
        If all models in the fallback chain are exhausted.
    """
    # Honour an explicit override in .env; otherwise use the fallback chain
    env_model = os.getenv("GEMINI_MODEL")
    models_to_try = [env_model] if env_model else _MODEL_FALLBACK_CHAIN

    last_exc: Exception | None = None

    for model in models_to_try:
        wait = _INITIAL_WAIT
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                logger.info("Calling model '%s' (attempt %d/%d)", model, attempt, _MAX_RETRIES)
                llm = _build_llm(model)
                chain = _prompt_template | llm
                response = chain.invoke({"schema": schema, "question": question})
                raw_sql = response.content if hasattr(response, "content") else str(response)
                return _clean_sql(raw_sql)

            except Exception as exc:
                last_exc = exc
                if _is_quota_error(exc):
                    if attempt < _MAX_RETRIES:
                        logger.warning(
                            "Quota error on model '%s' (attempt %d). "
                            "Retrying in %ds…",
                            model, attempt, wait,
                        )
                        time.sleep(wait)
                        wait *= _BACKOFF_FACTOR
                    else:
                        logger.warning(
                            "Model '%s' exhausted after %d attempts. "
                            "Trying next model…",
                            model, _MAX_RETRIES,
                        )
                else:
                    # Non-quota error — propagate immediately
                    raise

    raise RuntimeError(
        "All Gemini models in the fallback chain are quota-exhausted. "
        "Please wait a few minutes, upgrade your Google AI plan, or use a "
        "different API key.\n"
        f"Last error: {last_exc}"
    )
