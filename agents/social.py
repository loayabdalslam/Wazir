from agents.base import BaseAgent


class SocialAgent(BaseAgent):
    name = "Minister of Social Affairs"
    icon = "🧑‍🤝‍🧑"
    domain = "Social Stability"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> str:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}, focusing on {self.domain}. Keep your analysis concise (2-4 sentences). Do not use markdown headers."
        prompt = f"Country: {country}\nObjective: {goal}\nData: {json.dumps(data)}\n"
        if context:
            prompt += f"Colleagues' insights:\n{json.dumps(context)}\n"
        prompt += "\nBased on this, what is your specific advice or assessment?"
        return await client.generate(prompt=prompt, system=system_prompt)
