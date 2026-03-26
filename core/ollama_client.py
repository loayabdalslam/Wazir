import httpx
import json

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = None

    async def get_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    if models:
                        # Prefers deepseek or gemma, else just the first one
                        for preferred in ["deepseek", "gemma3", "minimax"]:
                            for m in models:
                                if preferred in m:
                                    self.default_model = m
                                    return models
                        self.default_model = models[0]
                    return models
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
        return []

    async def generate(self, prompt: str, system: str = "", model: str = None) -> str:
        if not model:
            if not self.default_model:
                await self.get_models()
            model = self.default_model
            
        if not model:
            return "Ollama unavailable or no models found."

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False
                }
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    return resp.json().get("response", "")
                else:
                    return f"Ollama generation error: {resp.status_code} - {resp.text}"
        except Exception as e:
            return f"Ollama connection error: {e}"
