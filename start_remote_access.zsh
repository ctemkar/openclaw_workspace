printf "Installing InstaTunnel: The 2026 ngrok-killer...\n"
npm install -g instatunnel --quiet

printf "Opening a 24-hour persistent tunnel for your dashboard...\n"
printf "Your dashboard will be live at: https://ctemkar-bot.instatunnel.my\n"

instatunnel 8501 --subdomain ctemkar-bot
