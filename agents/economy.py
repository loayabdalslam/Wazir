from agents.base import BaseAgent


class EconomyAgent(BaseAgent):
    name = "Minister of Economy"
    icon = "💰"
    domain = "Economy"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> dict:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}, focusing on {self.domain}. Keep your analysis concise (2-4 sentences). Do not use markdown headers."
        prompt = f"Country: {country}\nObjective: {goal}\nData: {json.dumps(data)}\n"
        if context:
            prompt += f"Colleagues' insights:\n{json.dumps(context)}\n"
        prompt += "\nBased on this, what is your specific advice or assessment?"
        
        brief = await client.generate(prompt=prompt, system=system_prompt)
        
        # Filter sources that this agent focused on
        all_sources = data.get("raw_sources", [])
        my_sources = [s for s in all_sources if s.get("domain") == self.domain or s.get("domain") == "Economy"]
        
        return {
            "brief": brief,
            "sources": my_sources[:2] # Limit to top 2 for brevity
        }
