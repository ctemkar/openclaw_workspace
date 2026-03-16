import json
import subprocess
from datetime import datetime, timedelta
import os
import psutil
import signal
import time
import glob

LLM_PROVIDERS = {
    "gemini": {"model": "gemini-pro", "api_key_env": "GEMINI_API_KEY"},
    "claude": {"model": "claude-3-haiku-20240307", "api_key_env": "ANTHROPIC_API_KEY"},
    "openai": {"model": "gpt-4o", "api_key_env": "OPENAI_API_KEY"},
    "deepseek": {"model": "deepseek-coder", "api_key_env": "DEEPSEEK_API_KEY"},
    "qwen": {"model": "qwen-turbo", "api_key_env": "QWEN_API_KEY"}
}

def call_gemini_api(prompt_text):
    try: 
        return {"model": "gemini-pro", "strategy_name": "Gemini_Momentum_Strategy", "description": "Identifies upward momentum and suggests buying dips below a certain threshold.", "symbol": "BTC/USD", "investment_usd": 10.00, "risk_parameters": {"stop_loss_pct": 0.05, "take_profit_pct": 0.10}, "profit_rationale": "Based on historical trends showing strong bounce-backs after minor pullbacks.", "llm_provider": "gemini"}
    except Exception as e: print(f"Error calling Gemini API (placeholder): {e}"); return None

def call_claude_api(prompt_text):
    try: 
        return {"model": "claude-3-haiku-20240307", "strategy_name": "Claude_Sentiment_Strategy", "description": "Analyzes recent news sentiment and suggests trades based on overwhelmingly positive or negative sentiment shifts.", "symbol": "ETH/USD", "investment_usd": 10.00, "risk_parameters": {"stop_loss_pct": 0.07, "take_profit_pct": 0.12}, "profit_rationale": "Positive sentiment historically correlates with short-term price increases.", "llm_provider": "claude"}
    except Exception as e: print(f"Error calling Claude API (placeholder): {e}"); return None

def call_openai_api(prompt_text):
    try: 
        return {"model": "gpt-4o", "strategy_name": "OpenAI_Volatility_Strategy", "description": "Targets short-term volatility by scalping small price movements in highly liquid assets.", "symbol": "SOL/USD", "investment_usd": 10.00, "risk_parameters": {"stop_loss_pct": 0.04, "take_profit_pct": 0.08}, "profit_rationale": "Exploits intraday price fluctuations common in volatile markets.", "llm_provider": "openai"}
    except Exception as e: print(f"Error calling OpenAI API (placeholder): {e}"); return None

def call_deepseek_api(prompt_text):
    try: 
        return {"model": "deepseek-coder", "strategy_name": "DeepSeek_Momentum_Scalp_Strategy", "description": "Focuses on quick, small gains from strong short-term momentum indicators.", "symbol": "BTC/USD", "investment_usd": 10.00, "risk_parameters": {"stop_loss_pct": 0.02, "take_profit_pct": 0.03}, "profit_rationale": "Scalping relies on frequent, small profits to accumulate over time.", "llm_provider": "deepseek"}
    except Exception as e: print(f"Error calling DeepSeek API (placeholder): {e}"); return None

def call_qwen_api(prompt_text):
    try: 
        return {"model": "qwen-turbo", "strategy_name": "Qwen_Trend_Following_Strategy", "description": "Identifies established trends and aims to follow them for larger gains.", "symbol": "ETH/USD", "investment_usd": 10.00, "risk_parameters": {"stop_loss_pct": 0.10, "take_profit_pct": 0.20}, "profit_rationale": "Riding established trends can lead to significant profits, accepting larger drawdowns.", "llm_provider": "qwen"}
    except Exception as e: print(f"Error calling Qwen API (placeholder): {e}"); return None

def get_llm_strategies(num_btc_strategies=5):
    all_strategies = []    
    base_prompt = 'You are an expert AI specializing in cryptocurrency trading strategy development. Provide strategies in JSON format: "model", "strategy_name", "description", "symbol", "investment_usd" (simulated, "$10.00"), "risk_parameters" ({"stop_loss_pct": decimal, "take_profit_pct": decimal}), "profit_rationale". Only output the JSON.'
    btc_prompt = f"Generate {num_btc_strategies} distinct and profitable trading strategies for Bitcoin (BTC/USD). Follow the JSON structure. Consider different approaches. Only output the JSON."
    other_cryptos_prompt = "Generate one strategy for Ethereum (ETH/USD) and one for Solana (SOL/USD). Follow JSON structure. Only output JSON."
    suggested_crypto_prompt = "Identify one promising crypto (not BTC, ETH, SOL) and generate one strategy for it. Follow JSON structure. Only output JSON."

    print("Generating LLM strategies...")

    gemini_btc = call_gemini_api(btc_prompt)
    if gemini_btc: all_strategies.append(gemini_btc)
    deepseek_btc = call_deepseek_api(btc_prompt)
    if deepseek_btc: all_strategies.append(deepseek_btc)
        
    claude_eth = call_claude_api(other_cryptos_prompt)
    if claude_eth: all_strategies.append(claude_eth)
        
    qwen_sol = call_qwen_api(other_cryptos_prompt)
    if qwen_sol: all_strategies.append(qwen_sol)

    openai_suggested = call_openai_api(suggested_crypto_prompt)
    if openai_suggested: all_strategies.append(openai_suggested)

    return all_strategies

if __name__ == "__main__":
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    print("Starting LLM Strategy Generation...")    
    strategies = get_llm_strategies(num_btc_strategies=5)    
    output_filename = f"llm_strategies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(os.path.join(scripts_dir, output_filename), 'w') as f:
            json.dump(strategies, f, indent=4)
        print(f"Generated {len(strategies)} strategies and saved to {output_filename}")
    except IOError as e:
        print(f"Error writing strategies to file {output_filename}: {e}")
        
    print("\\n--- Generated Strategies ---")
    if not strategies:
        print("No strategies were generated. Please check LLM API call placeholders and configurations.")
    else:
        for i, strategy in enumerate(strategies):
            if strategy:
                print(f"\\nStrategy {i+1}:")
                print(f"  LLM Provider: {strategy.get('llm_provider', 'N/A')}")
                print(f"  Model: {strategy.get('model', 'N/A')}")
                print(f"  Name: {strategy.get('strategy_name', 'N/A')}")
                print(f"  Symbol: {strategy.get('symbol', 'N/A')}")
                print(f"  Description: {strategy.get('description', 'N/A')}")
                print(f"  Investment (Simulated): ${strategy.get('investment_usd', 0.00):.2f}")
                risk = strategy.get('risk_parameters', {})
                stop_loss = risk.get('stop_loss_pct', 0.0)
                take_profit = risk.get('take_profit_pct', 0.0)
                print(f"  Risk: Stop Loss {stop_loss*100:.2f}%, Take Profit {take_profit*100:.2f}%")
                print(f"  Rationale: {strategy.get('profit_rationale', 'N/A')}")
        
    print("\\n--- Generation Complete ---")
