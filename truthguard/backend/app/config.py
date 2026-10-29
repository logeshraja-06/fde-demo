import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env from backend root, truthguard root, or server root
base_dir = Path(__file__).resolve().parent.parent
env_paths = [
    base_dir / ".env",
    base_dir.parent / ".env",
    base_dir.parent.parent / "enterprise-ai-assistant" / "server" / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(p, override=False)


class Settings(BaseSettings):
    APP_NAME: str = "TruthGuard Adversarial Document Verification"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Gemini Configuration (loaded securely from environment or .env)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")

    # OpenAI configuration (optional fallback)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION: int = 1536

    # Database configuration (PostgreSQL + pgvector)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://truthguard:truthguard@localhost:5432/truthguard"
    )
    # Local fallback sqlite vector file when postgres is unavailable
    LOCAL_FALLBACK_DB_PATH: str = os.getenv(
        "LOCAL_FALLBACK_DB_PATH",
        str(base_dir / "data" / "truthguard_local.db")
    )
    ALLOW_LOCAL_FALLBACK: bool = True

    # Chunking configuration
    TARGET_CHUNK_TOKENS: int = 600
    CHUNK_OVERLAP_TOKENS: int = 100

    # Upload configuration
    MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: set = {"pdf", "docx", "txt"}
    UPLOAD_DIR: str = str(base_dir / "data" / "uploads")

    # Workflow parameters
    MAX_RETRIEVAL_RETRIES: int = 2
    RAG_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.45

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )


settings = Settings()

# Ensure data directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(Path(settings.LOCAL_FALLBACK_DB_PATH).parent, exist_ok=True)
