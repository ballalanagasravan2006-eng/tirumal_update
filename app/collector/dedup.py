import hashlib
from app.database.db import get_connection

def calculate_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def is_duplicate_article(source_url: str, content_hash: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM ttd_news WHERE source_url = ? OR content_hash = ?", (source_url, content_hash))
    row = cursor.fetchone()
    conn.close()
    
    return row is not None
