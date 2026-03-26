from agents.base import BaseAgent


class SocialAgent(BaseAgent):
    name = "Minister of Social Affairs"
    icon = "🧑‍🤝‍🧑"
    domain = "Social Stability"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Focus on education and social stability. 2-3 sentences."
        prompt = f"Country: {country}\nGoal: {goal}\nSocial Data: {json.dumps(data)}\nYour assessment?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == "Global"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2]
        }
