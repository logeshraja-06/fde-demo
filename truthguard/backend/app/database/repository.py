import json
import logging
from typing import List, Dict, Any, Optional
from app.database.db import get_sqlite_connection, is_pg_active
from app.config import settings

logger = logging.getLogger("truthguard.repository")


def upsert_document(doc_data: Dict[str, Any]) -> None:
    doc_id = doc_data["document_id"]
    filename = doc_data["filename"]
    file_type = doc_data["file_type"]
    file_size_bytes = doc_data["file_size_bytes"]
    version = doc_data.get("version")
    published_at = doc_data.get("published_at")
    effective_date = doc_data.get("effective_date")
    status = doc_data.get("status")
    authority_level = doc_data.get("authority_level")
    meta_json = json.dumps(doc_data)

    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO tg_documents (
                    document_id, filename, file_type, file_size_bytes,
                    version, published_at, effective_date, status, authority_level, metadata_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    version = EXCLUDED.version,
                    published_at = EXCLUDED.published_at,
                    effective_date = EXCLUDED.effective_date,
                    status = EXCLUDED.status,
                    authority_level = EXCLUDED.authority_level,
                    metadata_json = EXCLUDED.metadata_json;
                """, (doc_id, filename, file_type, file_size_bytes, version, published_at, effective_date, status, authority_level, meta_json))
                conn.commit()
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO tg_documents (
            document_id, filename, file_type, file_size_bytes,
            version, published_at, effective_date, status, authority_level, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (document_id) DO UPDATE SET
            filename = excluded.filename,
            version = excluded.version,
            published_at = excluded.published_at,
            effective_date = excluded.effective_date,
            status = excluded.status,
            authority_level = excluded.authority_level,
            metadata_json = excluded.metadata_json;
        """, (doc_id, filename, file_type, file_size_bytes, version, published_at, effective_date, status, authority_level, meta_json))
        conn.commit()
        conn.close()


def upsert_chunks(doc_id: str, chunks: List[Dict[str, Any]]) -> None:
    """
    Saves chunks with embeddings.
    Avoids duplicating chunks when a document is reprocessed.
    """
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # Remove prior chunks for this document
                cur.execute("DELETE FROM tg_chunks WHERE document_id = %s;", (doc_id,))
                for c in chunks:
                    c_id = c["chunk_id"]
                    p_num = c.get("page_number")
                    sec = c.get("section")
                    ver = c.get("version")
                    pub = c.get("published_at")
                    eff = c.get("effective_date")
                    auth = c.get("authority_level")
                    tok = c.get("token_count", 0)
                    txt = c["text"]
                    emb = c.get("embedding", [])
                    meta = json.dumps(c)
                    cur.execute("""
                    INSERT INTO tg_chunks (
                        chunk_id, document_id, page_number, section, version,
                        published_at, effective_date, authority_level, token_count, text, embedding, metadata_json
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (c_id, doc_id, p_num, sec, ver, pub, eff, auth, tok, txt, emb, meta))
                conn.commit()
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tg_chunks WHERE document_id = ?;", (doc_id,))
        for c in chunks:
            c_id = c["chunk_id"]
            p_num = c.get("page_number")
            sec = c.get("section")
            ver = c.get("version")
            pub = c.get("published_at")
            eff = c.get("effective_date")
            auth = c.get("authority_level")
            tok = c.get("token_count", 0)
            txt = c["text"]
            emb_json = json.dumps(c.get("embedding", []))
            meta = json.dumps(c)
            cur.execute("""
            INSERT INTO tg_chunks (
                chunk_id, document_id, page_number, section, version,
                published_at, effective_date, authority_level, token_count, text, embedding_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (c_id, doc_id, p_num, sec, ver, pub, eff, auth, tok, txt, emb_json, meta))
        conn.commit()
        conn.close()


def list_documents() -> List[Dict[str, Any]]:
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT d.document_id, d.filename, d.file_type, d.file_size_bytes, d.version,
                       d.published_at, d.status, d.created_at, COUNT(c.chunk_id) as chunk_count
                FROM tg_documents d
                LEFT JOIN tg_chunks c ON d.document_id = c.document_id
                GROUP BY d.document_id, d.filename, d.file_type, d.file_size_bytes, d.version,
                         d.published_at, d.status, d.created_at
                ORDER BY d.created_at DESC;
                """)
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "document_id": r[0],
                        "filename": r[1],
                        "file_type": r[2],
                        "file_size_bytes": r[3],
                        "version": r[4],
                        "published_at": r[5],
                        "status": r[6],
                        "created_at": str(r[7]),
                        "chunk_count": r[8]
                    })
                return results
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT d.document_id, d.filename, d.file_type, d.file_size_bytes, d.version,
               d.published_at, d.status, d.created_at, COUNT(c.chunk_id) as chunk_count
        FROM tg_documents d
        LEFT JOIN tg_chunks c ON d.document_id = c.document_id
        GROUP BY d.document_id
        ORDER BY d.created_at DESC;
        """)
        rows = cur.fetchall()
        results = [dict(r) for r in rows]
        conn.close()
        return results


def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT metadata_json FROM tg_documents WHERE document_id = %s;", (doc_id,))
                row = cur.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
                return None
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("SELECT metadata_json FROM tg_documents WHERE document_id = ?;", (doc_id,))
        row = cur.fetchone()
        conn.close()
        if row and row["metadata_json"]:
            return json.loads(row["metadata_json"])
        return None


def get_document_chunks(doc_id: str) -> List[Dict[str, Any]]:
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT chunk_id, document_id, page_number, section, version,
                       published_at, token_count, text, metadata_json
                FROM tg_chunks
                WHERE document_id = %s
                ORDER BY chunk_id ASC;
                """, (doc_id,))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    meta = json.loads(r[8]) if r[8] else {}
                    results.append({
                        "chunk_id": r[0],
                        "document_id": r[1],
                        "filename": meta.get("filename", ""),
                        "page_number": r[2],
                        "section": r[3],
                        "version": r[4],
                        "published_at": r[5],
                        "token_count": r[6],
                        "text": r[7]
                    })
                return results
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT chunk_id, document_id, page_number, section, version,
               published_at, token_count, text, metadata_json
        FROM tg_chunks
        WHERE document_id = ?
        ORDER BY chunk_id ASC;
        """, (doc_id,))
        rows = cur.fetchall()
        results = []
        for r in rows:
            meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            results.append({
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "filename": meta.get("filename", ""),
                "page_number": r["page_number"],
                "section": r["section"],
                "version": r["version"],
                "published_at": r["published_at"],
                "token_count": r["token_count"],
                "text": r["text"]
            })
        conn.close()
        return results


def get_all_chunks_with_embeddings() -> List[Dict[str, Any]]:
    """Returns all chunks with their embeddings for similarity search."""
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT chunk_id, document_id, page_number, section, version,
                       published_at, effective_date, authority_level, token_count, text,
                       embedding::text, metadata_json
                FROM tg_chunks;
                """)
                rows = cur.fetchall()
                results = []
                for r in rows:
                    emb = []
                    if r[10]:
                        try:
                            # pgvector string e.g. "[0.1, 0.2, ...]"
                            emb = json.loads(r[10])
                        except Exception:
                            emb = []
                    meta = json.loads(r[11]) if r[11] else {}
                    results.append({
                        "chunk_id": r[0],
                        "document_id": r[1],
                        "filename": meta.get("filename", ""),
                        "page_number": r[2],
                        "section": r[3],
                        "version": r[4],
                        "published_at": r[5],
                        "effective_date": r[6],
                        "authority_level": r[7],
                        "token_count": r[8],
                        "text": r[9],
                        "embedding": emb,
                        "metadata": meta
                    })
                return results
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT chunk_id, document_id, page_number, section, version,
               published_at, effective_date, authority_level, token_count, text,
               embedding_json, metadata_json
        FROM tg_chunks;
        """)
        rows = cur.fetchall()
        results = []
        for r in rows:
            emb = json.loads(r["embedding_json"]) if r["embedding_json"] else []
            meta = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
            results.append({
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "filename": meta.get("filename", ""),
                "page_number": r["page_number"],
                "section": r["section"],
                "version": r["version"],
                "published_at": r["published_at"],
                "effective_date": r["effective_date"],
                "authority_level": r["authority_level"],
                "token_count": r["token_count"],
                "text": r["text"],
                "embedding": emb,
                "metadata": meta
            })
        conn.close()
        return results


def save_report(query_id: str, question: str, final_answer: str, conflict_status: str, report_dict: Dict[str, Any]) -> None:
    rep_json = json.dumps(report_dict)
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO tg_reports (query_id, question, final_answer, conflict_status, report_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (query_id) DO UPDATE SET
                    final_answer = EXCLUDED.final_answer,
                    conflict_status = EXCLUDED.conflict_status,
                    report_json = EXCLUDED.report_json;
                """, (query_id, question, final_answer, conflict_status, rep_json))
                conn.commit()
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO tg_reports (query_id, question, final_answer, conflict_status, report_json)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (query_id) DO UPDATE SET
            final_answer = excluded.final_answer,
            conflict_status = excluded.conflict_status,
            report_json = excluded.report_json;
        """, (query_id, question, final_answer, conflict_status, rep_json))
        conn.commit()
        conn.close()


def get_report(query_id: str) -> Optional[Dict[str, Any]]:
    if is_pg_active():
        import psycopg  # type: ignore
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT report_json FROM tg_reports WHERE query_id = %s;", (query_id,))
                row = cur.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
                return None
    else:
        conn = get_sqlite_connection()
        cur = conn.cursor()
        cur.execute("SELECT report_json FROM tg_reports WHERE query_id = ?;", (query_id,))
        row = cur.fetchone()
        conn.close()
        if row and row["report_json"]:
            return json.loads(row["report_json"])
        return None
