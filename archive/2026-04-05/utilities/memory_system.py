#!/usr/bin/env python3
"""
MEMORY SYSTEM - Store and retrieve important context
"""

import json
import os
from datetime import datetime
import hashlib

class MemorySystem:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        self.memories = self.load_memories()
    
    def load_memories(self):
        """Load existing memories from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_memories(self):
        """Save memories to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def add_memory(self, category, title, content, tags=None, priority="medium"):
        """Add a new memory"""
        memory = {
            'id': hashlib.md5(f"{datetime.now().isoformat()}{title}".encode()).hexdigest()[:8],
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'title': title,
            'content': content,
            'tags': tags or [],
            'priority': priority,
            'accessed': 0
        }
        
        self.memories.append(memory)
        self.save_memories()
        return memory['id']
    
    def get_memories(self, category=None, tag=None, limit=10):
        """Get memories with optional filters"""
        filtered = self.memories
        
        if category:
            filtered = [m for m in filtered if m['category'] == category]
        
        if tag:
            filtered = [m for m in filtered if tag in m['tags']]
        
        # Sort by priority and timestamp
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        filtered.sort(key=lambda x: (priority_order.get(x['priority'], 4), x['timestamp']))
        
        return filtered[:limit]
    
    def search_memories(self, query):
        """Search memories by content"""
        results = []
        query_lower = query.lower()
        
        for memory in self.memories:
            if (query_lower in memory['title'].lower() or 
                query_lower in memory['content'].lower() or
                any(query_lower in tag.lower() for tag in memory['tags'])):
                results.append(memory)
        
        return results
    
    def update_memory(self, memory_id, updates):
        """Update an existing memory"""
        for i, memory in enumerate(self.memories):
            if memory['id'] == memory_id:
                self.memories[i].update(updates)
                self.memories[i]['accessed'] += 1
                self.save_memories()
                return True
        return False
    
    def delete_memory(self, memory_id):
        """Delete a memory"""
        self.memories = [m for m in self.memories if m['id'] != memory_id]
        self.save_memories()

# Create memory categories
MEMORY_CATEGORIES = {
    'system_state': 'Current system status and configuration',
    'trading_positions': 'Open positions and P&L',
    'issues_fixed': 'Problems that were resolved',
    'user_preferences': 'User preferences and instructions',
    'bot_config': 'Trading bot configuration',
    'dashboard_status': 'Dashboard states and issues',
    'api_keys': 'API configuration notes',
    'git_commits': 'Important git commit messages',
    'lessons_learned': 'Important lessons from mistakes',
    'next_actions': 'Pending actions and tasks'
}

def initialize_memory_system():
    """Initialize and populate memory system with current state"""
    memory = MemorySystem("trading_data/memory.json")
    
    print("="*70)
    print("🧠 INITIALIZING MEMORY SYSTEM")
    print("="*70)
    
    # Add current system state
    memory.add_memory(
        category='system_state',
        title='Current Trading System State',
        content='''System reset to reality on 2026-04-02 after dashboard showed fictional data.
        
ACTUAL STATE:
- Gemini: $563.08 USD cash + 0.137152 ETH + 0.460077 SOL
- Binance: $70.15 USDT total, $72.62 free (no positions)
- P&L: -$14.29 total (ETH -$12.31, SOL -$1.98)
- Gemini-only bot running with $563 cash
- All 4 dashboards running with accurate data''',
        tags=['reality', 'reset', 'current_state'],
        priority='critical'
    )
    
    # Add trading positions memory
    memory.add_memory(
        category='trading_positions',
        title='Current Gemini Positions with Real P&L',
        content='''ETH/USD:
- Amount: 0.137152
- Entry: $2,126.63 (weighted average)
- Current: $2,036.88
- P&L: -$12.31 (-4.22%)
- Value: $291.67

SOL/USD:
- Amount: 0.460077
- Entry: $83.09 (weighted average)
- Current: $78.79
- P&L: -$1.98 (-5.18%)
- Value: $38.23

TOTAL P&L: -$14.29''',
        tags=['gemini', 'positions', 'pnl', 'eth', 'sol'],
        priority='high'
    )
    
    # Add issues fixed memory
    memory.add_memory(
        category='issues_fixed',
        title='Critical Dashboard Bug - Fictional Data',
        content='''PROBLEM: Dashboard showed 85 fictional trades with wrong P&L
- ETH prices were $80-85 off (4% error)
- Dashboard showed profits when actual was losses
- Positions didn't match reality

SOLUTION:
1. Reset dashboard to show only actual positions
2. Restored real entry prices from backup trades
3. Calculated real P&L based on actual entry vs current prices
4. Fixed trades dashboard to show P&L correctly

LESSON: Always verify dashboard data against exchange APIs''',
        tags=['dashboard_bug', 'data_accuracy', 'critical_fix'],
        priority='critical'
    )
    
    # Add user preferences memory
    memory.add_memory(
        category='user_preferences',
        title='User Instructions - Critical Requirements',
        content='''USER PREFERENCES:
1. P&L is the MOST IMPORTANT part of the system
2. Store important memories on git for context retention
3. Be proactive, don't wait for explicit instructions
4. Verify data accuracy before displaying
5. Use APIs to check reality, don't ask user to check UIs
6. Trading with real money requires 100% real data
7. NO hardcoded values in real trading systems
8. NO simulations or mock data - always use real data''',
        tags=['user_prefs', 'critical', 'instructions'],
        priority='critical'
    )
    
    # Add bot configuration memory
    memory.add_memory(
        category='bot_config',
        title='Gemini-Only Trading Bot Configuration',
        content='''CURRENT BOT: gemini_only_trader.py
- Strategy: Gemini-only (no Binance due to geographic restrictions)
- Capital: $563.08 USD available
- Threshold: 1.5% price drop for LONG entries
- Position size: Conservative (not specified)
- Scan interval: Every 5 minutes
- Status: RUNNING

REASON: Binance API blocked in Thailand, using Gemini only''',
        tags=['trading_bot', 'gemini', 'configuration', 'running'],
        priority='high'
    )
    
    # Add dashboard status memory
    memory.add_memory(
        category='dashboard_status',
        title='Dashboard Status and Ports',
        content='''ALL 4 DASHBOARDS RUNNING:
1. Port 5007: Main dashboard with LLM reports
2. Port 5011: Trades dashboard (shows P&L)
3. Port 5013: Grouped exchange totals
4. Port 5014: Real-time prices (critical fix)

ACCESS:
- http://localhost:5007
- http://localhost:5011
- http://localhost:5013  
- http://localhost:5014

STATUS: All showing accurate data with real P&L''',
        tags=['dashboards', 'ports', 'status', 'working'],
        priority='medium'
    )
    
    # Add git commit guidance
    memory.add_memory(
        category='git_commits',
        title='Git Commit Strategy for Memory',
        content='''GIT COMMIT RULES:
1. Commit after every significant change
2. Include context in commit messages
3. Tag important fixes with [CRITICAL], [FIX], [FEATURE]
4. Include timestamps and reasoning
5. Store memory.json in git for persistence
6. Use descriptive commit messages that explain WHY

EXAMPLE: "Fixed dashboard P&L calculation - was using current price as entry price, now uses actual entry prices from backup"''',
        tags=['git', 'version_control', 'memory', 'best_practices'],
        priority='high'
    )
    
    # Add lessons learned
    memory.add_memory(
        category='lessons_learned',
        title='Critical Lessons from Dashboard Bug',
        content='''LESSONS LEARNED:
1. Dashboard data MUST be verified against exchange APIs
2. P&L calculations require ACTUAL entry prices, not current prices
3. Historical trade data should be preserved for entry price lookup
4. System resets should backup old data before clearing
5. User wants proactive problem identification and fixing
6. Memory retention is critical - store context in git
7. Real trading systems require 100% data accuracy
8. Never assume dashboard data is correct - always verify''',
        tags=['lessons', 'dashboard', 'data_accuracy', 'critical'],
        priority='high'
    )
    
    print(f"✅ Memory system initialized with {len(memory.memories)} memories")
    print(f"📁 Memory file: trading_data/memory.json")
    
    # Show memory summary
    print("\n📋 MEMORY SUMMARY BY CATEGORY:")
    for category in MEMORY_CATEGORIES:
        count = len(memory.get_memories(category=category, limit=100))
        if count > 0:
            print(f"  {category}: {count} memories")
    
    return memory

if __name__ == "__main__":
    memory = initialize_memory_system()
    
    print("\n" + "="*70)
    print("💡 MEMORY SYSTEM READY")
    print("="*70)
    print("1. Memories stored in trading_data/memory.json")
    print("2. Will be included in git commits")
    print("3. Can be searched and updated")
    print("4. Critical context preserved across sessions")
    print("="*70)