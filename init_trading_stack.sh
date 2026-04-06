export REASONING_MODEL="gpt-oss-120b"
export TOOL_MODEL="llama-4-scout"
export VISION_MODEL="llama-4-scout"
export STT_MODEL="whisper-large-v3-turbo"
export TTS_MODEL="orpheus-english"
printf "{\n  \"models\": {\n    \"analysis\": \"$REASONING_MODEL\",\n    \"execution\": \"$TOOL_MODEL\",\n    \"voice_control\": \"$STT_MODEL\"\n  },\n  \"endpoints\": {\n    \"schwab\": \"https://api.schwab.com/v1\",\n    \"gemini\": \"https://api.gemini.com/v1\"\n  }\n}" > bot_settings.json
chmod +x init_trading_stack.sh
./init_trading_stack.sh
printf "Trading stack initialized with bot_settings.json configuration\n"
