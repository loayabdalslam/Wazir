import httpx
import json
from typing import Optional


class CountryDataScraper:

    async def scrape_country(self, country: str, goal: str = "") -> dict:
        data = {
            "country": country,
            "timestamp": "",
            "economy": {},
            "military": {},
            "demographics": {},
            "energy": {},
            "trade": {},
            "political": {},
            "agriculture": {},
            "social": {},
            "diplomacy": {},
            "raw_sources": [],
            "live_context": ""
        }

        import asyncio
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            results = await asyncio.gather(
                self._get_economic_data(client, country),
                self._get_military_data(client, country, goal),
                self._get_demographics(client, country),
                self._get_energy_data(client, country, goal),
                self._get_political_data(client, country, goal),
                self._get_social_data(client, country),
                self._get_live_context(country, goal)
            )

        data["economy"] = results[0]
        data["military"] = results[1][0]
        data["demographics"] = results[2]
        data["energy"] = results[3][0]
        data["political"] = results[4][0]
        data["social"] = results[5]
        data["live_context"] = results[6][0]
        
        # Aggregate sources
        data["raw_sources"] = results[1][1] + results[3][1] + results[4][1] + results[6][1]

        from datetime import datetime, timezone
        data["timestamp"] = datetime.now(timezone.utc).isoformat()

        return data

    async def _get_economic_data(self, client: httpx.AsyncClient, country: str) -> dict:
        try:
            url = f"https://api.worldbank.org/v2/country/{country}/indicator/NY.GDP.MKTP.CD?format=json&per_page=5"
            resp = await client.get(url)
            if resp.status_code == 200:
                j = resp.json()
                if len(j) > 1 and j[1]:
                    gdp_series = [r for r in j[1] if r.get("value")]
                    if gdp_series:
                        return {
                            "gdp_usd": gdp_series[0]["value"],
                            "gdp_year": gdp_series[0]["date"],
                            "source": "World Bank"
                        }
        except Exception:
            pass

        return {
            "gdp_usd": "N/A",
            "gdp_year": "N/A",
            "source": "fallback",
            "note": "Live data unavailable - using simulation defaults"
        }

    async def _get_intelligent_domain_data(self, country: str, domain: str, goal: str = "") -> tuple[dict, list]:
        import asyncio
        from ddgs import DDGS
        
        def do_search():
            if domain == "military":
                query = f"{country} military capabilities defense budget 2024"
                if goal: query += f" impact on {goal}"
            elif domain == "energy":
                query = f"{country} energy grid production 2024 sources"
                if goal: query += f" {goal} infrastructure"
            elif domain == "political":
                query = f"{country} political stability leadership 2024"
                if goal: query += f" {goal} policy support"
            else:
                query = f"{country} {domain} status 2024"
                if goal: query += f" {goal}"
                
            sources = []
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=4))
                    summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                    sources = [{"title": r['title'], "url": r['href'], "domain": domain} for r in results]
                    return {
                        "domain": domain,
                        "intelligent_summary": summary,
                        "source": "Deep Web Intelligence Scan"
                    }, sources
            except Exception as e:
                return {"source": "fallback", "note": str(e)}, []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, do_search)

    async def _get_military_data(self, client: httpx.AsyncClient, country: str, goal: str = "") -> tuple[dict, list]:
        return await self._get_intelligent_domain_data(country, "military", goal)

    async def _get_demographics(self, client: httpx.AsyncClient, country: str) -> dict:
        try:
            url = f"https://api.worldbank.org/v2/country/{country}/indicator/SP.POP.TOTL?format=json&per_page=3"
            resp = await client.get(url)
            if resp.status_code == 200:
                j = resp.json()
                if len(j) > 1 and j[1]:
                    pop_series = [r for r in j[1] if r.get("value")]
                    if pop_series:
                        return {
                            "population": pop_series[0]["value"],
                            "year": pop_series[0]["date"],
                            "source": "World Bank"
                        }
        except Exception:
            pass
        return {"source": "fallback"}

    async def _get_energy_data(self, client: httpx.AsyncClient, country: str, goal: str = "") -> tuple[dict, list]:
        return await self._get_intelligent_domain_data(country, "energy", goal)

    async def _get_political_data(self, client: httpx.AsyncClient, country: str, goal: str = "") -> tuple[dict, list]:
        return await self._get_intelligent_domain_data(country, "political", goal)

    async def _get_social_data(self, client: httpx.AsyncClient, country: str) -> dict:
        try:
            url = f"https://api.worldbank.org/v2/country/{country}/indicator/SE.XPD.TOTL.GD.ZS?format=json&per_page=3"
            resp = await client.get(url)
            if resp.status_code == 200:
                j = resp.json()
                if len(j) > 1 and j[1]:
                    edu_series = [r for r in j[1] if r.get("value")]
                    if edu_series:
                        return {
                            "education_spend_pct_gdp": edu_series[0]["value"],
                            "year": edu_series[0]["date"],
                            "source": "World Bank"
                        }
        except Exception:
            pass
        return {"source": "fallback"}

    async def _get_live_context(self, country: str, goal: str) -> tuple[str, list]:
        import asyncio
        from ddgs import DDGS
        
        def do_search():
            try:
                queries = [
                    f"{country} news 2024",
                    f"{country} {goal} feasibility analysis",
                    f"{country} current challenges {goal}"
                ]
                all_results = []
                sources = []
                with DDGS() as ddgs:
                    for q in queries:
                        results = list(ddgs.text(q, max_results=2))
                        all_results.extend(results)
                        sources.extend([{"title": r['title'], "url": r['href'], "domain": "Global"} for r in results])
                
                return "\n".join([f"- {r['title']}: {r['body']}" for r in all_results]), sources
            except Exception as e:
                return f"Live search failed: {e}", []
                
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, do_search)
