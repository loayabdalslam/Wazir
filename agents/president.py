from agents.base import BaseAgent


class PresidentAgent(BaseAgent):
    name = "The President"
    icon = "🏛️"
    domain = "Strategic Synthesis"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Synthesize your ministers' reports and set the final direction. Professional, 3-4 sentences."
        prompt = f"Country: {country}\nGoal: {goal}\nCabinet Reports:\n{json.dumps(context or {})}\nYour Final Verdict?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == "Global"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2]
        }
