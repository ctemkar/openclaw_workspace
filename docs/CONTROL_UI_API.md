# Control UI API Documentation

## 🎯 REAL-TIME BOT STATUS ENDPOINTS

### **Base URL:** `http://localhost:5022`

### **1. Get All Bots Summary**
**Endpoint:** `GET /api/bots/summary`
**Description:** Returns a summary of all bots for the control UI list view
**Response:**
```json
[
  {
    "id": "forex",
    "name": "💰 FOREX Arbitration Bot",
    "status": "✅ RUNNING",
    "pid": "60261",
    "activity": "Idle"
  },
  {
    "id": "arbitrage",
    "name": "Auto Arbitrage Bot",
    "status": "✅ RUNNING",
    "pid": "61457",
    "activity": "Scanning"
  }
]
```

### **2. Get Bot Real-Time Status**
**Endpoint:** `GET /api/bot/{bot_id}/status`
**Description:** Returns detailed real-time status for a specific bot (use when clicking on a bot)
**Parameters:** `bot_id` - One of: `forex`, `arbitrage`, `practical_profit`, `multi_llm`
**Response:**
```json
{
  "id": "forex",
  "name": "💰 FOREX Arbitration Bot",
  "status": "✅ RUNNING",
  "pid": "60261",
  "activity": "Idle",
  "last_action": "Unknown",
  "real_time": true,
  "timestamp": "2026-04-04T04:37:53.756437"
}
```

### **3. Get All Bot Activities (Detailed)**
**Endpoint:** `GET /api/all_activity`
**Description:** Returns full detailed information for all bots
**Response:** Full bot objects with all metrics

### **4. Get Specific Bot Activity**
**Endpoint:** `GET /api/activity/{bot_id}`
**Description:** Returns full detailed information for a specific bot
**Parameters:** `bot_id` - One of: `forex`, `arbitrage`, `practical_profit`, `multi_llm`

## 🖱️ **HOW TO IMPLEMENT IN CONTROL UI:**

### **1. Bot List View:**
```javascript
// Fetch all bots summary
fetch('http://localhost:5022/api/bots/summary')
  .then(response => response.json())
  .then(bots => {
    // Display bots in list
    bots.forEach(bot => {
      console.log(`${bot.name}: ${bot.status} - ${bot.activity}`);
    });
  });
```

### **2. Click Handler for Bot Details:**
```javascript
// When user clicks on a bot
function showBotDetails(botId) {
  fetch(`http://localhost:5022/api/bot/${botId}/status`)
    .then(response => response.json())
    .then(botStatus => {
      // Show real-time status
      console.log(`Real-time status for ${botStatus.name}:`);
      console.log(`- Status: ${botStatus.status}`);
      console.log(`- PID: ${botStatus.pid}`);
      console.log(`- Activity: ${botStatus.activity}`);
      console.log(`- Last action: ${botStatus.last_action}`);
      console.log(`- Updated: ${botStatus.timestamp}`);
    });
}
```

### **3. Auto-Refresh (Every 30 seconds):**
```javascript
// Auto-refresh bot status
setInterval(() => {
  fetch('http://localhost:5022/api/bots/summary')
    .then(response => response.json())
    .then(bots => {
      // Update UI with fresh data
      updateBotList(bots);
    });
}, 30000); // 30 seconds
```

## 🚀 **CURRENT BOT IDs:**

| Bot ID | Name | Description |
|--------|------|-------------|
| `forex` | 💰 FOREX Arbitration Bot | Forex trading with Schwab account |
| `arbitrage` | Auto Arbitrage Bot | Crypto arbitrage between exchanges |
| `practical_profit` | Practical Profit Bot | Practical crypto trading (making $5.08 profit) |
| `multi_llm` | Multi-LLM Trading Bot | AI-powered trading with multiple LLMs |

## ✅ **STATUS INDICATORS:**

- **✅ RUNNING**: Bot is actively running
- **❌ NOT RUNNING**: Bot is stopped
- **⚠️ ERROR**: Error checking bot status

## 📊 **ACTIVITY EXAMPLES:**

- `Idle`: Bot is running but not currently active
- `Scanning`: Bot is scanning for opportunities
- `📉 SELLING 50.00 MANA...`: Executing a trade
- `Analyzing`: LLM bot analyzing market data
- `🌏 Asia hours: Next scan in 40 seconds...`: Waiting for next scan

## 🔧 **TROUBLESHOOTING:**

1. **If endpoints return 404:** Make sure live_activity_dashboard.py is running on port 5022
2. **If no data:** Check if bot log files exist (active_forex_trading.log, etc.)
3. **If status shows "NOT RUNNING":** Bot process may have stopped
4. **For real-time updates:** Use the `/api/bot/{id}/status` endpoint which includes timestamp

## 🎯 **EXAMPLE IMPLEMENTATION:**

```html
<div id="bot-list">
  <!-- Bots will be populated here -->
</div>

<script>
// Load bots on page load
document.addEventListener('DOMContentLoaded', function() {
  loadBots();
  
  // Auto-refresh every 30 seconds
  setInterval(loadBots, 30000);
});

function loadBots() {
  fetch('http://localhost:5022/api/bots/summary')
    .then(response => response.json())
    .then(bots => {
      const botList = document.getElementById('bot-list');
      botList.innerHTML = '';
      
      bots.forEach(bot => {
        const botElement = document.createElement('div');
        botElement.className = 'bot-item';
        botElement.innerHTML = `
          <h3 onclick="showBotDetails('${bot.id}')">${bot.name}</h3>
          <p>Status: ${bot.status}</p>
          <p>Activity: ${bot.activity}</p>
          <p>PID: ${bot.pid}</p>
        `;
        botList.appendChild(botElement);
      });
    });
}

function showBotDetails(botId) {
  fetch(`http://localhost:5022/api/bot/${botId}/status`)
    .then(response => response.json())
    .then(bot => {
      alert(`
        Real-time Status for ${bot.name}:
        -------------------------------
        Status: ${bot.status}
        PID: ${bot.pid}
        Activity: ${bot.activity}
        Last Action: ${bot.last_action}
        Updated: ${new Date(bot.timestamp).toLocaleTimeString()}
      `);
    });
}
</script>
```