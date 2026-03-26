from agents.base import BaseAgent


class DefenseAgent(BaseAgent):
    name = "Minister of Defense"
    icon = "⚔️"
    domain = "Military & Defense"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Focus on military, security, and hardware. Keep analysis to 2-3 sentences max."
        
        prompt = f"Country: {country}\nGoal: {goal}\nMilitary Data: {json.dumps(data)}\n"
        if context:
            prompt += f"Colleagues' insights:\n{json.dumps(context)}\n"
        prompt += "Your assessment?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == "military"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2]
        }
