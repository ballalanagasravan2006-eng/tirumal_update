import os
from dotenv import load_dotenv

load_dotenv()

class AIProvider:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY", "").strip()
        self.model_name = os.getenv("AI_MODEL", "gemini-2.5-flash")
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                print(f"[AI] Initialized Gemini client model={self.model_name}")
            except Exception as e:
                print(f"[AI] Warning: Failed to initialize Gemini client: {e}")

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        if not self.client:
            return ""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"system_instruction": system_instruction} if system_instruction else None
            )
            return response.text if response else ""
        except Exception as e:
            print(f"[AI] Generation error: {e}")
            return ""

ai_provider = AIProvider()
