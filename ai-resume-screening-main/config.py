# ============================================================
# config.py — Configuration and environment validation
# Loads API keys from .env and exposes settings to the app.
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------- OpenAI ----------------------
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL        = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE  = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))

# ---------------------- LangSmith ----------------------
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_ENDPOINT   = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
LANGCHAIN_API_KEY    = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT    = os.getenv("LANGCHAIN_PROJECT", "ai-resume-screening")


def validate_config() -> bool:
    """
    Check that all required API keys are present.
    Returns True if valid, False otherwise.
    """
    errors = []

    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is missing in .env")
    if not LANGCHAIN_API_KEY:
        errors.append("LANGCHAIN_API_KEY is missing in .env")

    if errors:
        print("\n" + "=" * 50)
        print("❌ CONFIGURATION ERRORS:")
        print("=" * 50)
        for err in errors:
            print(f"  • {err}")
        print("=" * 50)
        print("Add the missing keys to your .env file and retry.\n")
        return False

    # Ensure LangSmith env vars are actually set in the process,
    # so LangChain picks them up automatically.
    os.environ.setdefault("LANGCHAIN_TRACING_V2", LANGCHAIN_TRACING_V2)
    os.environ.setdefault("LANGCHAIN_ENDPOINT",   LANGCHAIN_ENDPOINT)
    os.environ.setdefault("LANGCHAIN_API_KEY",    LANGCHAIN_API_KEY)
    os.environ.setdefault("LANGCHAIN_PROJECT",    LANGCHAIN_PROJECT)

    print("✅ Configuration OK")
    print(f"   Model:           {OPENAI_MODEL}")
    print(f"   LangSmith project: {LANGCHAIN_PROJECT}")
    print(f"   Tracing:          {LANGCHAIN_TRACING_V2}")
    return True