#!/usr/bin/env python3
"""
RECALL MEMORY - Retrieve important context from memory system
"""

import json
import sys
from datetime import datetime

def recall_memory(query=None):
    """Recall memories based on query"""
    memory_file = "trading_data/memory.json"
    
    try:
        with open(memory_file, 'r') as f:
            memories = json.load(f)
        
        print("="*70)
        print("🧠 RECALLING MEMORIES")
        print("="*70)
        
        if query:
            # Search for query
            results = []
            query_lower = query.lower()
            
            for memory in memories:
                if (query_lower in memory['title'].lower() or 
                    query_lower in memory['content'].lower() or
                    any(query_lower in tag.lower() for tag in memory['tags'])):
                    results.append(memory)
            
            if results:
                print(f"🔍 Found {len(results)} memories for '{query}':")
                for memory in results[:5]:  # Show first 5
                    print(f"\n📌 {memory['title']} [{memory['category']}]")
                    print(f"   Priority: {memory['priority'].upper()}")
                    print(f"   Tags: {', '.join(memory['tags'])}")
                    print(f"   {memory['content'][:200]}...")
            else:
                print(f"❌ No memories found for '{query}'")
                print("\n📋 Available categories:")
                categories = set(m['category'] for m in memories)
                for cat in sorted(categories):
                    count = sum(1 for m in memories if m['category'] == cat)
                    print(f"  • {cat}: {count} memories")
        
        else:
            # Show summary
            print("📋 MEMORY SYSTEM SUMMARY:")
            print(f"Total memories: {len(memories)}")
            
            # Group by category
            categories = {}
            for memory in memories:
                cat = memory['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(memory)
            
            print("\n📁 BY CATEGORY:")
            for cat, mems in sorted(categories.items()):
                print(f"  {cat}: {len(mems)} memories")
                
                # Show high priority items
                high_priority = [m for m in mems if m['priority'] in ['critical', 'high']]
                if high_priority:
                    for mem in high_priority[:2]:  # Show first 2 high priority
                        print(f"    • {mem['title']} [{mem['priority']}]")
            
            # Show critical memories
            critical = [m for m in memories if m['priority'] == 'critical']
            if critical:
                print("\n🚨 CRITICAL MEMORIES:")
                for mem in critical:
                    print(f"  • {mem['title']} ({mem['category']})")
        
        print("\n" + "="*70)
        print("💡 USAGE: python3 recall_memory.py [query]")
        print("   Examples: python3 recall_memory.py pnl")
        print("             python3 recall_memory.py dashboard")
        print("             python3 recall_memory.py gemini")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error reading memory: {e}")
        print("Try running: python3 memory_system.py to initialize")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else None
    recall_memory(query)