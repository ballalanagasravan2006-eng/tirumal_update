import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(news_id: str, title: str, category: str, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    width, height = 1080, 1920
    # Create dark devotional background with subtle gold gradient feel
    image = Image.new("RGB", (width, height), color="#0f141c")
    draw = ImageDraw.Draw(image)

    # Decorative top header strip
    draw.rectangle([0, 0, width, 180], fill="#1b2028")
    draw.rectangle([0, 175, width, 180], fill="#eec14b")

    # Font setup
    try:
        font_title = ImageFont.truetype("arial.ttf", 52)
        font_badge = ImageFont.truetype("arial.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font_title = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw Brand Title
    draw.text((60, 60), "TIRUMALA DAILY", fill="#eec14b", font=font_title)
    draw.text((60, 125), "OFFICIAL DEVOTIONAL BULLETIN", fill="#9a907c", font=font_sub)

    # Category Pill Badge
    badge_text = category.upper() if category else "TTD ANNOUNCEMENT"
    draw.rectangle([60, 240, 500, 310], fill="#7f2830")
    draw.text((80, 255), badge_text, fill="#ffdad9", font=font_badge)

    # News Title Card
    draw.rectangle([60, 360, 1020, 1200], fill="#171c24", outline="#4e4635", width=3)
    
    # Word wrap main headline
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) * 22 < 880:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y_offset = 420
    for line in lines[:8]:
        draw.text((100, y_offset), line, fill="#dee2ee", font=font_title)
        y_offset += 75

    # Devotional Footer
    draw.rectangle([60, 1650, 1020, 1800], fill="#1b2028", outline="#eec14b", width=2)
    draw.text((100, 1690), "GOVINDA GOVINDA!", fill="#eec14b", font=font_title)
    draw.text((100, 1750), "Source: news.tirumala.org", fill="#d1c5af", font=font_sub)

    image.save(output_path, quality=95)
    try:
        print(f"[Assets] Generated thumbnail asset: {output_path}")
    except Exception:
        print(f"[Assets] Generated thumbnail asset: {output_path.encode('ascii', 'ignore').decode('ascii')}")
    return output_path

if __name__ == "__main__":
    generate_thumbnail("test", "TTD Annual Brahmotsavam Procession Schedule Released", "Festivals", "data/test_thumb.jpg")
