from agents.base import BaseAgent


class EnergyAgent(BaseAgent):
    name = "Minister of Energy"
    icon = "🛢️"
    domain = "Energy"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Focus on infrastructure and sustainability. 2-3 sentences."
        prompt = f"Country: {country}\nGoal: {goal}\nEnergy Data: {json.dumps(data)}\nYour plan?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == "energy"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2]
        }
