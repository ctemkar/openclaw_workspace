#!/bin/bash
# Auto-save script for trading system with memory updates

echo "="
echo "💾 AUTO-SAVING WITH MEMORY UPDATE"
echo "="

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Update memory with current state
echo "🔄 Updating memory system..."
python3 << 'EOF'
import json
from datetime import datetime

# Load current memory
try:
    with open('trading_data/memory.json', 'r') as f:
        memories = json.load(f)
except:
    memories = []

# Check if system_state memory exists and update it
system_updated = False
for i, memory in enumerate(memories):
    if memory.get('category') == 'system_state' and memory.get('title') == 'Current Trading System State':
        # Update timestamp
        memories[i]['timestamp'] = datetime.now().isoformat()
        memories[i]['accessed'] = memories[i].get('accessed', 0) + 1
        system_updated = True
        break

if not system_updated:
    # Create new system_state memory
    new_memory = {
        'id': 'sys_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
        'timestamp': datetime.now().isoformat(),
        'category': 'system_state',
        'title': 'Current Trading System State',
        'content': f'Auto-save at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        'tags': ['auto_save', 'system_state'],
        'priority': 'medium',
        'accessed': 0
    }
    memories.append(new_memory)

# Save updated memory
with open('trading_data/memory.json', 'w') as f:
    json.dump(memories, f, indent=2)

print(f"✅ Memory updated with {len(memories)} total memories")
EOF

# Add all files
git add .

# Commit with context
git commit -m "[AUTO-SAVE] $TIMESTAMP - Memory system updated

Auto-save includes:
- Current system state memory
- Trading positions and P&L
- Dashboard status
- Bot configuration

Memory preserved for context retention."

# Push to remote
git push origin main

echo ""
echo "✅ Auto-save completed at $TIMESTAMP"
echo "📄 Memory system updated and committed to git"