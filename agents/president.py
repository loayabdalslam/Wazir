from agents.base import BaseAgent


class PresidentAgent(BaseAgent):
    name = "The President"
    icon = "🏛️"
    domain = "Strategic Synthesis"

    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> str:
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        system_prompt = f"You are the {self.name}. Synthesize the reports from your ministers to form a final strategic decision. Keep it 3-5 sentences. No markdown headers."
        prompt = f"Country: {country}\nGoal: {goal}\nMinisters' Reports:\n{json.dumps(context)}\n\nPlease provide the final synthesis and decision."
        return await client.generate(prompt=prompt, system=system_prompt)
