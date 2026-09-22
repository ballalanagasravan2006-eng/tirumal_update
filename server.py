import os
import sqlite3
import json
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from app.database.db import get_connection, init_db
from app.database.migrations import run_migrations
from app.collector.ttd_collector import collect_ttd_news
from app.media.media_manager import run_media_pipeline
from app.reel.package_generator import create_reel_packages

app = FastAPI(title="Tirumala Daily Devotional Dashboard", version="2.0.0")

# Ensure static and data paths exist
Path("static").mkdir(exist_ok=True)
Path("data/reels").mkdir(parents=True, exist_ok=True)

# Mount data directory to serve generated thumbnails, posters, and media files directly
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    init_db()
    run_migrations()

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_path = Path("static/index.html")
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Tirumala Daily App Starting...</h1>")

@app.get("/api/status")
def get_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM ttd_news")
    total_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_news WHERE processing_status = 'READY'")
    ready_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_media")
    total_media = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reel_packages")
    total_reels = cursor.fetchone()[0]

    conn.close()

    return {
        "success": True,
        "stats": {
            "total_news": total_news,
            "ready_news": ready_news,
            "total_media": total_media,
            "total_reels": total_reels
        }
    }

@app.get("/api/news")
def get_news_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ttd_news ORDER BY published_date DESC, collected_at DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    news_list = []
    for r in rows:
        news_list.append({
            "id": r["id"],
            "title": r["title"],
            "title_te": r["title_te"],
            "category": r["category"] or "TTD Announcements",
            "published_date": r["published_date"],
            "source_url": r["source_url"],
            "summary": r["summary"] or r["article_text"][:200] if r["article_text"] else r["title"],
            "verification_status": r["verification_status"] or "VERIFIED",
            "processing_status": r["processing_status"]
        })
    return {"success": True, "news": news_list}

@app.get("/api/reels")
def get_reels_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.*, n.title, n.title_te, n.category, n.source_url, n.published_date 
    FROM reel_packages r 
    JOIN ttd_news n ON r.news_id = n.id 
    ORDER BY r.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    reels = []
    for r in rows:
        pkg_path = Path(r["package_path"])
        meta_file = pkg_path / "metadata.json"
        meta_data = {}
        if meta_file.exists():
            try:
                meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        telugu_script = ""
        hindi_script = ""
        english_script = ""

        te_file = pkg_path / "scripts/telugu.txt"
        hi_file = pkg_path / "scripts/hindi.txt"
        en_file = pkg_path / "scripts/english.txt"

        if te_file.exists(): telugu_script = te_file.read_text(encoding="utf-8")
        if hi_file.exists(): hindi_script = hi_file.read_text(encoding="utf-8")
        if en_file.exists(): english_script = en_file.read_text(encoding="utf-8")

        # Build clean web relative URLs for assets
        rel_path = str(pkg_path).replace("\\", "/")
        thumb_url = f"/{rel_path}/thumbnail.jpg" if (pkg_path / "thumbnail.jpg").exists() else ""
        poster_url = f"/{rel_path}/poster.jpg" if (pkg_path / "poster.jpg").exists() else ""

        reels.append({
            "id": r["id"],
            "news_id": r["news_id"],
            "title": r["title"],
            "category": r["category"] or "Festivals",
            "source_url": r["source_url"],
            "package_path": rel_path,
            "thumb_url": thumb_url,
            "poster_url": poster_url,
            "telugu_script": telugu_script,
            "hindi_script": hindi_script,
            "english_script": english_script,
            "created_at": r["created_at"],
            "metadata": meta_data
        })

    return {"success": True, "reels": reels}

@app.post("/api/run-automation")
def run_automation():
    try:
        c_res = collect_ttd_news(max_articles=5)
        m_res = run_media_pipeline()
        r_res = create_reel_packages()

        return {
            "success": True,
            "message": "Automation pipeline completed successfully!",
            "summary": {
                "new_articles": c_res.get("new", 0),
                "reels_created": r_res.get("packages_created", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
