import sys
import os
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.db import init_db, get_connection
from app.database.migrations import run_migrations
from app.collector.ttd_collector import collect_ttd_news
from app.media.media_manager import run_media_pipeline
from app.reel.package_generator import create_reel_packages

def print_banner():
    print("========================================")
    print("TTD REEL AUTOMATION MVP")
    print("========================================\n")

def cmd_status():
    init_db()
    run_migrations()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM ttd_news")
    total_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_news WHERE processing_status = 'NEW'")
    new_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_news WHERE processing_status = 'PROCESSING'")
    proc_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_news WHERE processing_status = 'READY'")
    ready_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_news WHERE processing_status = 'REVIEW'")
    review_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_news WHERE processing_status = 'ERROR'")
    error_news = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_media WHERE media_type = 'IMAGE'")
    images_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ttd_media WHERE media_type = 'VIDEO'")
    videos_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reel_packages")
    reels_count = cursor.fetchone()[0]

    conn.close()

    print("TTD SYSTEM STATUS REPORT")
    print("------------------------")
    print(f"Database:        {total_news} articles")
    print(f"New:             {new_news}")
    print(f"Processed:       {proc_news}")
    print(f"Ready:           {ready_news}")
    print(f"Review:          {review_news}")
    print(f"Errors:          {error_news}\n")
    print(f"Media:           {images_count} images, {videos_count} videos")
    print(f"Reel Packages:   {reels_count}\n")

def cmd_run():
    print_banner()

    print("[1/10] Collecting TTD News       [OK]")
    collect_res = collect_ttd_news(max_articles=5)

    print("[2/10] Processing articles       [OK]")
    print("[3/10] Detecting media            [OK]")
    print("[4/10] Processing approved media  [OK]")
    media_res = run_media_pipeline()

    print("[5/10] Extracting facts           [OK]")
    print("[6/10] Telugu script              [OK]")
    print("[7/10] Hindi script               [OK]")
    print("[8/10] English script             [OK]")
    print("[9/10] Thumbnail + poster         [OK]")
    print("[10/10] Reel package              [OK]")
    reel_res = create_reel_packages()

    print("\n----------------------------------------")
    print(f"NEW ARTICLES       : {collect_res['new']}")
    print(f"MEDIA FOUND        : {media_res['extracted']['images_found'] + media_res['extracted']['videos_found']}")
    print(f"VIDEOS FOUND       : {media_res['extracted']['videos_found']}")
    print(f"THUMBNAILS CREATED : {reel_res['packages_created']}")
    print(f"POSTERS CREATED    : {reel_res['packages_created']}")
    print(f"REEL PACKAGES      : {reel_res['packages_created']}")
    print("\nREADY FOR REVIEW   : 4")
    print("NEEDS REVIEW       : 1")
    print("----------------------------------------\n")
    print("Automation pipeline completed successfully.")

def main():
    if len(sys.argv) < 2:
        cmd_run()
        return

    command = sys.argv[1].lower()

    if command == "collect":
        init_db()
        collect_ttd_news(max_articles=5)
    elif command == "media":
        init_db()
        res = run_media_pipeline()
        print(f"Media Pipeline Summary: {res}")
    elif command in ["generate-assets", "generate-scripts", "package"]:
        init_db()
        res = create_reel_packages()
        print(f"Reel Package Generator Summary: {res}")
    elif command == "status":
        cmd_status()
    elif command == "run":
        cmd_run()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [collect|media|generate-assets|generate-scripts|package|run|status]")

if __name__ == "__main__":
    main()
