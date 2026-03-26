from agents.base import BaseAgent


class IntelligenceAgent(BaseAgent):
    name = "Chief of Intelligence"
    icon = "🔒"
    domain = "Intelligence & Security"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Focus on stability and external threats. 2-3 sentences."
        prompt = f"Country: {country}\nGoal: {goal}\nPolitical Data: {json.dumps(data)}\n"
        if context:
            prompt += f"Colleagues' insights:\n{json.dumps(context)}\n"
        prompt += "Insights?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == "political"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2]
        }

