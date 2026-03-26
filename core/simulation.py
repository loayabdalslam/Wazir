from agents.base import BaseAgent
from agents.president import PresidentAgent
from agents.economy import EconomyAgent
from agents.defense import DefenseAgent
from agents.agriculture import AgricultureAgent
from agents.industry import IndustryAgent
from agents.social import SocialAgent
from agents.energy import EnergyAgent
from agents.foreign import ForeignAgent
from agents.intelligence import IntelligenceAgent
from agents.chief_economist import ChiefEconomistAgent


class SimulationEngine:

    def __init__(self, sim_id: str, country: str, goal: str, country_data: dict):
        self.sim_id = sim_id
        self.country = country
        self.goal = goal
        self.data = country_data

        self.agents: list[BaseAgent] = [
            PresidentAgent(),
            EconomyAgent(),
            DefenseAgent(),
            AgricultureAgent(),
            IndustryAgent(),
            SocialAgent(),
            EnergyAgent(),
            ForeignAgent(),
            IntelligenceAgent(),
            ChiefEconomistAgent(),
        ]

        self.dashboard = {}
        self.scenarios = []
        self.projections = {}
        self.wildcards = []
        self.step = 0

    async def run_simulation(self):
        yield {
            "type": "status",
            "message": f"Initializing swarm for {self.country}...",
            "progress": 5
        }

        yield {
            "type": "status",
            "message": f"{len(self.agents)} agents activated",
            "progress": 10
        }

        await self._build_dashboard()
        yield {"type": "dashboard", "data": self.dashboard, "progress": 25}

        # Initialize shared context for swarm intelligence
        shared_context = {}

        # The president should run LAST to synthesize
        president_idx = next(i for i, a in enumerate(self.agents) if a.name == "The President")
        president_agent = self.agents.pop(president_idx)
        self.agents.append(president_agent)

        for i, agent in enumerate(self.agents):
            await self._step(f"Agent {agent.name} analyzing...", 25 + int(i * 45 / len(self.agents)))
            
            # President gets the full context of other ministers
            if agent.name == "The President":
                brief = await agent.analyze(self.country, self.goal, self.data, context=shared_context)
            else:
                brief = await agent.analyze(self.country, self.goal, self.data)
                shared_context[agent.domain] = brief

            yield {
                "type": "agent_brief",
                "agent": agent.name,
                "icon": agent.icon,
                "domain": agent.domain,
                "brief": brief,
                "progress": 25 + int((i+1) * 45 / len(self.agents))
            }
            await self._delay()

        yield {"type": "status", "message": "Generating decision scenarios...", "progress": 70}
        await self._generate_scenarios(shared_context)
        yield {"type": "scenarios", "data": self.scenarios, "progress": 80}

        yield {"type": "status", "message": "Scanning for wild cards...", "progress": 85}
        await self._generate_wildcards(shared_context)
        yield {"type": "wildcards", "data": self.wildcards, "progress": 95}

        yield {"type": "complete", "message": "Simulation complete"}

    async def run_scenario(self, idx: int):
        if idx < len(self.scenarios):
            scenario = self.scenarios[idx]
            
            from core.ollama_client import OllamaClient
            import json
            client = OllamaClient()
            
            # Follow-up actions
            f_prompt = f"Scenario: {scenario['name']}. Goal: {self.goal}. Country: {self.country}. Generate 4 specific, actionable next steps for a government task force. Return ONLY a JSON list of strings."
            f_resp = await client.generate(f_prompt, system="Output ONLY raw JSON list of strings.")
            try: follow_up = json.loads(f_resp)
            except: follow_up = ["Initiate internal review", "Allocate contingency funds"]

            # Scenario Projections
            p_prompt = (
                f"Scenario: {scenario['name']}\n"
                f"Project the impact on GDP Growth, Inflation, and Approval Rating. Return ONLY valid JSON:\n"
                "{\"gdp_growth\": {\"min\": 1.1, \"base\": 2.5, \"max\": 4.0}, \"inflation\": {...}, \"approval_rating\": {...}}"
            )
            p_resp = await client.generate(p_prompt, system="Output ONLY raw JSON.")
            try: proj = json.loads(p_resp)
            except: proj = {}

            yield {
                "type": "scenario_detail",
                "scenario": scenario,
                "follow_up": follow_up,
                "projections": proj
            }

    async def _build_dashboard(self):
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()

        prompt = (
            f"Country: {self.country}, Goal: {self.goal}\n"
            f"Raw Data Snippet: {json.dumps(self.data)[:2000]}\n"
            "Analyze the state of these 8 domains: Economy, Military, Food Security, Social Stability, Diplomacy, Energy, Industry & Trade, Intelligence.\n"
            "For each, provide: icon, status (short), risk (Low/Medium/High), and trend (↗, ↘, →).\n"
            "Return ONLY valid JSON matching this schema:\n"
            "{\"domains\": [{\"name\": \"Economy\", \"icon\": \"💰\", \"status\": \"...\", \"risk\": \"...\", \"trend\": \"...\"}, ...]}"
        )
        
        response = await client.generate(prompt, system="You are a data-driven intelligence analyst. Output ONLY raw JSON.")
        try:
            parsed = json.loads(response)
            self.dashboard = {
                "country": self.country,
                "goal": self.goal or "General Assessment",
                "domains": parsed.get("domains", []),
                "metrics": self._extract_metrics(),
                "sources": self.data.get("raw_sources", [])
            }
        except:
            # Minimal fallback
            self.dashboard = {"country": self.country, "goal": self.goal, "domains": [], "metrics": [], "sources": []}

    def _extract_metrics(self) -> list:
        econ = self.data.get("economy", {})
        demo = self.data.get("demographics", {})
        social = self.data.get("social", {})
        
        metrics = []
        if econ.get("gdp_usd") and econ["gdp_usd"] != "N/A":
            val = econ["gdp_usd"]
            if val > 1e12:
                metrics.append({"label": "GDP (Total)", "value": f"${val/1e12:.2f}T", "icon": "📈"})
            else:
                metrics.append({"label": "GDP (Total)", "value": f"${val/1e9:.1f}B", "icon": "📈"})
                
        if demo.get("population") and demo["population"] != "N/A":
            val = demo["population"]
            if val > 1e6:
                metrics.append({"label": "Population", "value": f"{val/1e6:.1f}M", "icon": "👥"})
            else:
                metrics.append({"label": "Population", "value": f"{val:,}", "icon": "👥"})

        if social.get("education_spend_pct_gdp"):
            metrics.append({"label": "Edu Spend", "value": f"{social['education_spend_pct_gdp']}%", "icon": "🎓"})

        return metrics

    async def _generate_scenarios(self, shared_context: dict = None):
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        prompt = (
            f"Based on this country: {self.country}, goal: {self.goal}\n"
            f"Data: {json.dumps(self.data)}\n"
            f"Context from ministers: {json.dumps(shared_context)}\n"
            "Generate 3 potential strategic scenarios. Return ONLY valid JSON matching this schema exactly:\n"
            "[\n"
            "  {\n"
            "    \"name\": \"...\",\n"
            "    \"icon\": \"emoji\",\n"
            "    \"summary\": \"...\",\n"
            "    \"short_term\": \"...\",\n"
            "    \"long_term\": \"...\",\n"
            "    \"risks\": [\"...\", \"...\"],\n"
            "    \"agents_for\": [\"...\"],\n"
            "    \"agents_against\": [\"...\"]\n"
            "  }\n"
            "]"
        )
        response = await client.generate(prompt=prompt, system="You are a strategic scenario generator. Output ONLY raw JSON. No markdown code blocks, no explanations.")
        try:
            self.scenarios = json.loads(response)
        except:
            self.scenarios = [{"name": "Error Generating", "icon": "⚠️", "summary": "Failed to parse JSON", "short_term": "", "long_term": "", "risks": [], "agents_for": [], "agents_against": []}]



    async def _generate_wildcards(self, shared_context: dict = None):
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        prompt = (
            f"Country: {self.country}\n"
            "Generate 3 wildcards/unexpected events. Return ONLY valid JSON matching this schema exactly:\n"
            "[\n"
            "  {\n"
            "    \"agent\": \"🔒 Intelligence\",\n"
            "    \"event\": \"...\",\n"
            "    \"probability\": 35,\n"
            "    \"impact\": \"High\"\n"
            "  }\n"
            "]"
        )
        response = await client.generate(prompt=prompt, system="You output ONLY valid JSON, no markdown.")
        try:
            self.wildcards = json.loads(response)
        except:
            self.wildcards = [{"agent": "System", "event": "Error parsing JSON", "probability": 0, "impact": "None"}]

    async def _step(self, msg: str, progress: int):
        pass

    async def _delay(self):
        import asyncio
        await asyncio.sleep(0.3)
