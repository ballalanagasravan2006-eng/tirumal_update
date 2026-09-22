import json
import re
from app.ai.provider import ai_provider

def extract_facts(title: str, text: str, source_url: str) -> dict:
    # Rule 13: Structured factual extraction without inventing facts
    prompt = f"""
Extract structured factual details from this official TTD news article:

Title: {title}
Article Text: {text}
Source URL: {source_url}

Return JSON with structure:
{{
  "title": "{title}",
  "event": "Name of temple event or announcement",
  "dates": ["dates mentioned"],
  "times": ["times mentioned"],
  "locations": ["Tirumala / Tirupati / temple locations"],
  "important_numbers": ["token counts / pilgrim numbers if mentioned"],
  "key_instructions": ["important guidelines for devotees"],
  "source_url": "{source_url}"
}}
    """
    
    system_prompt = "You are a strict factual extraction engine for Tirumala Tirupati Devasthanams (TTD). Extract facts exactly as written in the text. Do NOT invent or extrapolate facts."

    response_text = ai_provider.generate_text(prompt, system_instruction=system_prompt)

    if response_text:
        try:
            cleaned = re.sub(r"```json|```", "", response_text).strip()
            return json.loads(cleaned)
        except Exception:
            pass

    # Deterministic fallback fact extraction
    numbers = re.findall(r"\b\d{1,6}\b", text)
    return {
        "title": title,
        "event": title,
        "dates": [],
        "times": [],
        "locations": ["Tirumala", "Tirupati"],
        "important_numbers": numbers[:5],
        "key_instructions": [title],
        "source_url": source_url
    }
