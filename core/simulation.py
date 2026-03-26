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

        yield {"type": "status", "message": "Running quantitative projections...", "progress": 85}
        await self._generate_projections(shared_context)
        yield {"type": "projections", "data": self.projections, "progress": 90}

        yield {"type": "status", "message": "Scanning for wild cards...", "progress": 95}
        await self._generate_wildcards(shared_context)
        yield {"type": "wildcards", "data": self.wildcards, "progress": 98}

        score = self._calculate_feasibility()
        yield {"type": "feasibility", "score": score, "progress": 100}

        yield {"type": "complete", "message": "Simulation complete"}

    async def run_scenario(self, idx: int):
        if idx < len(self.scenarios):
            scenario = self.scenarios[idx]
            yield {
                "type": "scenario_detail",
                "scenario": scenario,
                "follow_up": self._generate_follow_up(idx),
                "projections": self._project_scenario(idx)
            }

    async def _build_dashboard(self):
        e = self.data.get("economy", {})
        d = self.data.get("demographics", {})

        self.dashboard = {
            "country": self.country,
            "goal": self.goal or "General Assessment",
            "domains": [
                {
                    "name": "Economy",
                    "icon": "💰",
                    "status": self._economy_status(e),
                    "risk": self._economy_risk(e),
                    "trend": "→"
                },
                {
                    "name": "Military",
                    "icon": "⚔️",
                    "status": "Active",
                    "risk": "Medium",
                    "trend": "→"
                },
                {
                    "name": "Food Security",
                    "icon": "🌾",
                    "status": "Monitoring",
                    "risk": "Medium",
                    "trend": "→"
                },
                {
                    "name": "Social Stability",
                    "icon": "🧑‍🤝‍🧑",
                    "status": "Stable",
                    "risk": "Low",
                    "trend": "→"
                },
                {
                    "name": "Diplomacy",
                    "icon": "🌍",
                    "status": "Active",
                    "risk": "Medium",
                    "trend": "↗"
                },
                {
                    "name": "Energy",
                    "icon": "🛢️",
                    "status": "Monitoring",
                    "risk": "Medium",
                    "trend": "↗"
                },
                {
                    "name": "Industry & Trade",
                    "icon": "🏭",
                    "status": "Active",
                    "risk": "Medium",
                    "trend": "↗"
                },
                {
                    "name": "Intelligence",
                    "icon": "🔒",
                    "status": "Clear",
                    "risk": "Low",
                    "trend": "→"
                }
            ],
            "metrics": self._extract_metrics()
        }

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

        # Add intelligence-derived metrics if available
        for domain in ["military", "energy", "political"]:
            d_data = self.data.get(domain, {})
            if d_data.get("intelligent_summary"):
                # We could try to extract numbers here, but for now we'll just flag they exist
                pass

        return metrics

    def _economy_status(self, e: dict) -> str:
        if e.get("gdp_usd") and e["gdp_usd"] != "N/A":
            gdp = e["gdp_usd"]
            if isinstance(gdp, (int, float)):
                if gdp > 1e12:
                    return f"${gdp/1e12:.1f}T GDP"
                elif gdp > 1e9:
                    return f"${gdp/1e9:.1f}B GDP"
            return str(gdp)
        return "Data Pending"

    def _economy_risk(self, e: dict) -> str:
        return "Medium"

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

    async def _generate_projections(self, shared_context: dict = None):
        from core.ollama_client import OllamaClient
        import json
        client = OllamaClient()
        
        econ = self.data.get("economy", {})
        demo = self.data.get("demographics", {})
        gdp_val = econ.get("gdp_usd", "Unknown")
        pop_val = demo.get("population", "Unknown")

        prompt = (
            f"Country: {self.country}, Goal: {self.goal}\n"
            f"Real Baseline Data to ground your projections: GDP=${gdp_val}, Population={pop_val}.\n"
            "Using this baseline, calculate realistic projections for this country's future. For example, if it's a developed nation, GDP growth should be around 1-3%. Return ONLY valid JSON matching this schema exactly:\n"
            "{\n"
            "  \"gdp_growth\": {\"min\": 1.5, \"base\": 3.2, \"max\": 5.8, \"unit\": \"%\"},\n"
            "  \"inflation\": {\"min\": 2.1, \"base\": 4.5, \"max\": 7.2, \"unit\": \"%\"},\n"
            "  \"unemployment\": {\"min\": 4.0, \"base\": 6.5, \"max\": 9.0, \"unit\": \"%\"},\n"
            "  \"approval_rating\": {\"min\": 38, \"base\": 52, \"max\": 65, \"unit\": \"%\"},\n"
            "  \"fdi_billion\": {\"min\": 2.1, \"base\": 5.5, \"max\": 12.0, \"unit\": \"$B\"},\n"
            "  \"military_readiness\": {\"min\": 65, \"base\": 78, \"max\": 88, \"unit\": \"/100\"}\n"
            "}"
        )
        response = await client.generate(prompt=prompt, system="You output ONLY valid JSON, no markdown. Use realistic math based on the given baselines.")
        try:
            parsed = json.loads(response)
            self.projections = parsed
        except:
            self.projections = {
                "gdp_growth": {"min": 0, "base": 0, "max": 0, "unit": "%"}
            }

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

    def _calculate_feasibility(self) -> int:
        if not self.goal:
            return 0
        return 67

    def _generate_follow_up(self, idx: int) -> list:
        return [
            "Assemble a transition task force with clear 90-day milestones",
            "Prepare contingency budget allocation for implementation risks",
            "Schedule quarterly review checkpoints with all agents",
            "Begin diplomatic groundwork for external dependencies"
        ]

    def _project_scenario(self, idx: int) -> dict:
        multipliers = [0.7, 1.3, 1.0]
        m = multipliers[idx]
        return {
            "gdp_growth": {"min": round(1.5*m,1), "base": round(3.2*m,1), "max": round(5.8*m,1)},
            "inflation": {"min": round(2.1/m,1), "base": round(4.5/m,1), "max": round(7.2/m,1)},
            "approval_rating": {"min": max(20, round(38*m)), "base": round(52*m), "max": min(95, round(65*m))},
        }

    async def _step(self, msg: str, progress: int):
        pass

    async def _delay(self):
        import asyncio
        await asyncio.sleep(0.3)
