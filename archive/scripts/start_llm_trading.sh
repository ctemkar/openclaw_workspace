#!/bin/bash
# Start LLM Trading Bot

echo "🚀 STARTING LLM TRADING BOT"
echo "=============================="

# Check if Ollama is running
if ! ollama list > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Check available models
echo "🔍 Available LLM models:"
ollama list

# Start trading bot with DeepSeek R1
echo ""
echo "🤖 Starting trading bot with DeepSeek R1..."
echo "📊 Dashboard: http://localhost:5009/"
echo "📈 Trading logs will appear below..."
echo "=============================="
echo ""

# Run the trading bot
python3 llm_trading_bot.py