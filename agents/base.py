from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name: str = "Base"
    icon: str = "🤖"
    domain: str = "General"
    
    # We optionally can pass the ollama_client here, or instantiate it inside each agent.
    # To keep it simple, we'll let each subclass handle its generation or pass it in.

    @abstractmethod
    async def analyze(self, country: str, goal: str, data: dict, context: dict = None) -> str:
        ...
