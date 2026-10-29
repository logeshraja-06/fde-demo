import logging
import sqlite3
from app.config import settings

logger = logging.getLogger("truthguard.db")

_pg_available = False
_engine = None
_session_maker = None


def init_db():
    """
    Initializes database storage:
    Tries PostgreSQL + pgvector first.
    If PostgreSQL is unreachable, transparently falls back to local SQLite with vector indexing.
    """
    global _pg_available, _engine, _session_maker

    # Try PostgreSQL first
    try:
        import psycopg  # type: ignore
        conn = psycopg.connect(settings.DATABASE_URL, connect_timeout=2)
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS tg_documents (
                document_id VARCHAR(100) PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                file_size_bytes BIGINT NOT NULL,
                version VARCHAR(50),
                published_at VARCHAR(100),
                effective_date VARCHAR(100),
                status VARCHAR(100),
                authority_level VARCHAR(100),
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS tg_chunks (
                chunk_id VARCHAR(120) PRIMARY KEY,
                document_id VARCHAR(100) REFERENCES tg_documents(document_id) ON DELETE CASCADE,
                page_number INT,
                section VARCHAR(255),
                version VARCHAR(50),
                published_at VARCHAR(100),
                effective_date VARCHAR(100),
                authority_level VARCHAR(100),
                token_count INT,
                text TEXT NOT NULL,
                embedding vector(1536),
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS tg_reports (
                query_id VARCHAR(100) PRIMARY KEY,
                question TEXT NOT NULL,
                final_answer TEXT NOT NULL,
                conflict_status VARCHAR(50) NOT NULL,
                report_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()
        conn.close()
        _pg_available = True
        logger.info("Successfully connected and initialized PostgreSQL + pgvector.")
        return
    except Exception as exc:
        logger.info(f"PostgreSQL + pgvector connection not active ({exc}). Initializing local SQLite fallback vector store at {settings.LOCAL_FALLBACK_DB_PATH}...")

    # Fallback to SQLite
    conn = sqlite3.connect(settings.LOCAL_FALLBACK_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tg_documents (
        document_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        version TEXT,
        published_at TEXT,
        effective_date TEXT,
        status TEXT,
        authority_level TEXT,
        metadata_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tg_chunks (
        chunk_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        page_number INTEGER,
        section TEXT,
        version TEXT,
        published_at TEXT,
        effective_date TEXT,
        authority_level TEXT,
        token_count INTEGER,
        text TEXT NOT NULL,
        embedding_json TEXT,
        metadata_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES tg_documents (document_id) ON DELETE CASCADE
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tg_reports (
        query_id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        final_answer TEXT NOT NULL,
        conflict_status TEXT NOT NULL,
        report_json TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    logger.info("Local SQLite storage initialized successfully.")


def get_sqlite_connection():
    conn = sqlite3.connect(settings.LOCAL_FALLBACK_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_pg_active() -> bool:
    return _pg_available
