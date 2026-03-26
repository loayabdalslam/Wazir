from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import json
import uuid
from datetime import datetime

from core.simulation import SimulationEngine
from core.data_scraper import CountryDataScraper

app = FastAPI(title="Wazir", version="3.3.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

simulations: dict[str, SimulationEngine] = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.websocket("/ws/simulate")
async def websocket_simulate(ws: WebSocket):
    await ws.accept()
    sim_id = str(uuid.uuid4())[:8]

    try:
        init_data = await ws.receive_text()
        config = json.loads(init_data)
        country = config.get("country", "")
        goal = config.get("goal", "")

        scraper = CountryDataScraper()
        country_data = await scraper.scrape_country(country, goal)

        engine = SimulationEngine(sim_id, country, goal, country_data)
        simulations[sim_id] = engine

        await ws.send_text(json.dumps({
            "type": "country_data",
            "data": country_data
        }))

        await asyncio.sleep(0.5)

        async for message in engine.run_simulation():
            await ws.send_text(json.dumps(message))
            await asyncio.sleep(0.8)

        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=1.0)
                data = json.loads(msg)
                if data.get("type") == "scenario_select":
                    scenario_idx = data.get("scenario", 0)
                    async for message in engine.run_scenario(scenario_idx):
                        await ws.send_text(json.dumps(message))
                        await asyncio.sleep(0.8)
                elif data.get("type") == "restart":
                    country = data.get("country", country)
                    goal = data.get("goal", goal)
                    country_data = await scraper.scrape_country(country, goal)
                    engine = SimulationEngine(sim_id, country, goal, country_data)
                    simulations[sim_id] = engine
                    await ws.send_text(json.dumps({
                        "type": "country_data",
                        "data": country_data
                    }))
                    await asyncio.sleep(0.5)
                    async for message in engine.run_simulation():
                        await ws.send_text(json.dumps(message))
                        await asyncio.sleep(0.8)
            except asyncio.TimeoutError:
                continue

    except WebSocketDisconnect:
        simulations.pop(sim_id, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
