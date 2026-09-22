import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_poster(news_id: str, title: str, category: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    width, height = 1080, 1920
    image = Image.new("RGB", (width, height), color="#090e16")
    draw = ImageDraw.Draw(image)

    # Top & Bottom UI Safe Area Scrims
    draw.rectangle([0, 0, width, 220], fill="#0f141c")
    draw.rectangle([0, 1600, width, 1920], fill="#0f141c")

    try:
        font_main = ImageFont.truetype("arial.ttf", 48)
        font_sub = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Poster Header
    draw.text((60, 70), "TIRUMALA DAILY • REEL POSTER", fill="#eec14b", font=font_sub)
    draw.text((60, 120), category.upper(), fill="#ff989b", font=font_sub)

    # Hero Poster Graphic Frame
    draw.rectangle([60, 260, 1020, 1100], fill="#171c24", outline="#eec14b", width=3)
    draw.text((360, 650), "SRIVARI TEMPLE BULLETIN", fill="#9a907c", font=font_sub)

    # Headline Area
    draw.rectangle([60, 1150, 1020, 1550], fill="#1b2028")
    
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) * 20 < 880:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y_offset = 1180
    for line in lines[:5]:
        draw.text((90, y_offset), line, fill="#dee2ee", font=font_main)
        y_offset += 65

    draw.text((60, 1650), "Official Reference: https://news.tirumala.org", fill="#7bd9ad", font=font_sub)
    draw.text((60, 1720), "Verified & Prepared for Devotional Instagram Distribution", fill="#9a907c", font=font_sub)

    image.save(output_path, quality=95)
    try:
        print(f"[Assets] Generated poster asset: {output_path}")
    except Exception:
        print(f"[Assets] Generated poster asset: {output_path.encode('ascii', 'ignore').decode('ascii')}")
    return output_path

if __name__ == "__main__":
    generate_poster("test", "TTD Annual Brahmotsavam Procession Schedule Released", "Festivals", "data/test_poster.jpg")
