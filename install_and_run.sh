#!/bin/bash

# Wazir V.3.3.0 - Intelligent National Simulation
# GitHub: https://github.com/loayabdalslam/Wazir

echo "🚀 Launching Wazir: Autonomous National Intelligence (V.3.3.0)"

# 1. Environment Check
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required."
    exit 1
fi

# 2. Dependency Installation
echo "📦 Synchronizing dependencies..."
pip install -r requirements.txt || pip install ddgs fastapi uvicorn websockets httpx pydantic

# 3. Model Verification 
echo "🧠 Verifying Intelligence Backend (Ollama)..."
if ! curl -s http://localhost:11434/api/tags | grep -q "mistral\|llama3"; then
    echo "⚠️  Ollama is required at http://localhost:11434"
    echo "💡 Please install Ollama and run: ollama pull mistral"
fi

# 4. Start Application
echo "🌐 Environment Ready. Starting Wazir..."
python -m main
