from app.ai.provider import ai_provider

SYSTEM_PROMPT = """
You are the Tirumala Daily Script Generator.
Rules:
1. Scripts must be factual, reverent, dignified, and natural for 20-45 second Instagram Reels.
2. Structure: HOOK -> MAIN FACT -> IMPORTANT DETAIL -> ENDING / SOURCE REFERENCE.
3. Keep proper nouns intact: Tirumala, Tirupati, TTD, Srivari, Brahmotsavam, etc.
4. Do NOT invent information, fake dates, or exaggerated claims.
5. End Telugu scripts with "గోవిందా గోవింద!" and Hindi scripts with "गोविंदा गोविंदा!".
"""

def generate_reel_scripts(title: str, text: str, facts: dict, source_url: str) -> dict:
    prompt = f"""
Based ONLY on these facts from official TTD News:
Title: {title}
Article Text: {text}
Source URL: {source_url}

Generate short (20-45s) Instagram Reel scripts in Telugu, Hindi, and English.
Return JSON format:
{{
  "telugu": "Full Telugu script string...",
  "hindi": "Full Hindi script string...",
  "english": "Full English script/caption string..."
}}
"""

    response_text = ai_provider.generate_text(prompt, system_instruction=SYSTEM_PROMPT)

    if response_text:
        try:
            import json, re
            cleaned = re.sub(r"```json|```", "", response_text).strip()
            parsed = json.loads(cleaned)
            if "telugu" in parsed and "hindi" in parsed and "english" in parsed:
                return parsed
        except Exception:
            pass

    # Fallback script generation if AI API is unconfigured or failed
    telugu_fallback = (
        f"ఓం నమో వేంకటేశాయ!\n\n"
        f"తిరుమలలో ఇవాళ్టి ముఖ్యమైన అప్డేట్: {title}\n\n"
        f"మరిన్ని వివరాల కోసం టీటీడీ అధికారిక వెబ్‌సైట్ {source_url} ను సందర్శించండి.\n\n"
        f"మరిన్ని రోజూవారీ తిరుమల తాజా సమాచారం కోసం తిరుమల డైలీని ఫాలో అవ్వండి. గోవిందా గోవింద!"
    )

    hindi_fallback = (
        f"ओम नमो वेंकटेशाय!\n\n"
        f"तिरुपति बालाजी आज का मुख्य अपडेट: {title}\n\n"
        f"अधिक जानकारी के लिए टीटीडी आधिकारिक वेबसाइट {source_url} देखें।\n\n"
        f"प्रतिदिन तिरुमाला के ताज़ा अपडेट के लिए तिरुमाला डेली को फ़ॉलो करें। गोविंदा गोविंदा!"
    )

    english_fallback = (
        f"✨ {title}\n\n"
        f"Official update from Tirumala Tirupati Devasthanams (TTD).\n\n"
        f"🔗 Source: {source_url}\n\n"
        f"📌 Share this update with fellow devotees. Follow @TirumalaDaily for authentic everyday updates! 🔔 #TirumalaDaily #TTD #Tirumala"
    )

    return {
        "telugu": telugu_fallback,
        "hindi": hindi_fallback,
        "english": english_fallback
    }
