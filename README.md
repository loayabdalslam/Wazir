## 🛠️ Prerequisites
- **Python 3.9+**
- **Ollama**: You must have [Ollama](https://ollama.com/) installed and running locally.
- **Ollama Models**: Pull at least one capable model. The system actively looks for advanced tags (e.g., `deepseek`, `gemma3`, `minimax`, `llama3`). 
  ```bash
  ollama run deepseek-coder  # or your preferred model
  ```

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Wazir.git
   cd Wazir
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. **Ensure Ollama is running** in the background (default port `11434`).
2. **Start the FastAPI simulation server:**
   ```bash
   python -m main
   # OR
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. **Open the web dashboard** in your browser:  
   👉 `http://localhost:8000`

Enter a country (e.g., "France", "Japan", "Brazil") and an optional goal (e.g., "Triple military defense spending" or "Drastically reduce inflation") and click **SIMULATE** to watch your AI cabinet go to work!

## 📁 System Architecture
- `main.py`: The FastAPI server and WebSocket hub.
- `core/simulation.py`: The async hive-mind engine orchestrating the swarm.
- `core/ollama_client.py`: The interface to your local models.
- `core/data_scraper.py`: Fetches real World Bank and live DuckDuckGo facts.
- `agents/`: Contains the specific prompts and personas of all 10 cabinet ministers.
- `static/css/style.css`: The premium light theme design parameters.

---

*Built for advanced agentic exploration and macro-economic simulation.*
