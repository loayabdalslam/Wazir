from agents.base import BaseAgent


class IndustryAgent(BaseAgent):
    name = "Minister of Industry & Trade"
    icon = "🏭"
    domain = "Industry & Trade"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Focus on manufacturing and commerce. 2-3 sentences."
        prompt = f"Country: {country}\nGoal: {goal}\nIndustry Data: {json.dumps(data)}\nYour advice?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == "energy" or s.get("domain") == "Global"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2]
        }
