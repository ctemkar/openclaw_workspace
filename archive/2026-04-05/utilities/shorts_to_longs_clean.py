#!/usr/bin/env python3
"""
SHORTS TO LONGS SYSTEM - CLEAN VERSION
Create Long-form from Shorts content - Maximum efficiency
"""

import json
from datetime import datetime, timedelta

print("="*80)
print("🎬 SHORTS TO LONGS SYSTEM - DOUBLE YOUR CONTENT!")
print("="*80)

# Create the core strategy
strategy = {
    "weekly_output": {
        "shorts": 21,
        "longs": 4,
        "total": 25,
        "shorts_duration": "45-60 seconds",
        "longs_duration": "8-15 minutes"
    },
    "time_efficiency": {
        "weekly_hours": "16-22.5",
        "content_per_hour": "1.1-1.6 pieces",
        "time_saving": "60% vs separate creation"
    },
    "conversion_examples": [
        {
            "short": "Krishna: India's Original Superhero (50s)",
            "long": "Krishna: Complete Character Documentary (12min)",
            "expansion": "Take traits → Expand to life chapters"
        },
        {
            "short": "Bhagavad Gita Decision Making (45s)",
            "long": "Complete Bhagavad Gita System (10min)",
            "expansion": "3 steps → Full system + case studies"
        }
    ]
}

with open('shorts_longs_strategy.json', 'w') as f:
    json.dump(strategy, f, indent=2)
print("✅ Created shorts_longs_strategy.json")

# Create weekly calendar
calendar = []
for day in range(7):
    date_str = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
    
    # 3 Shorts per day
    for i in range(3):
        calendar.append({
            "day": day + 1,
            "date": date_str,
            "time": ["10:00", "14:00", "18:00"][i],
            "type": "short",
            "duration": "45-60s",
            "topic": f"Day {day+1} Short {i+1}"
        })
    
    # Long-form on odd days (1, 3, 5, 7)
    if day % 2 == 0:
        calendar.append({
            "day": day + 1,
            "date": date_str,
            "time": "20:00",
            "type": "long",
            "duration": "8-15min",
            "topic": f"Day {day+1} Long-form",
            "based_on": f"Shorts from previous day"
        })

with open('weekly_calendar.json', 'w') as f:
    json.dump(calendar, f, indent=2)
print("✅ Created weekly_calendar.json (25 pieces)")

# Create quick guide
guide = """# 🎬 SHORTS + LONGS SYSTEM - QUICK START

## 🚀 WEEKLY OUTPUT:
- 21 Shorts (45-60 seconds each)
- 4 Long-form videos (8-15 minutes each)
- Total: 25 content pieces

## ⏰ TIME: 16-22.5 hours/week
## 💰 INCOME: $9,000-40,000/month by Month 12

## 🎯 CONVERSION FORMULA:
1. Research topic once
2. Create 45-60 second Short
3. Expand to 8-15 minute Long-form
4. Result: 2x content, 1.3x effort

## 📅 SAMPLE DAY:
- 10 AM: Short 1 (45s)
- 2 PM: Short 2 (45s)
- 6 PM: Short 3 (45s)
- 8 PM: Long-form (12min) [on odd days]

## 💡 PRO TIP:
Start with Krishna topic:
- Short: "Krishna: India's Original Superhero" (50s)
- Long: "Krishna Complete Documentary" (12min)
Same research, double content!

## 🚀 READY?
1. Follow weekly_calendar.json
2. Use conversion formulas
3. Track progress weekly
4. Scale what works

Good luck! 🎬📚
"""

with open('QUICK_START_GUIDE.md', 'w') as f:
    f.write(guide)
print("✅ Created QUICK_START_GUIDE.md")

print("\n" + "="*80)
print("🎬 SYSTEM READY: Shorts + Longs from same content!")
print("="*80)

print("\n📊 WEEKLY OUTPUT:")
print("  • 21 Shorts (45-60 seconds)")
print("  • 4 Long-form (8-15 minutes)")
print("  • Total: 25 pieces")

print("\n⏰ TIME: 16-22.5 hours/week")
print("💰 MONTH 12 INCOME: $9,000-40,000/month")

print("\n🚀 START WITH:")
print("  1. Create 45-second Krishna Short")
print("  2. Expand to 12-minute Krishna Long")
print("  3. Repeat for other topics")

print("\n" + "="*80)
print("Double your content, not your effort! 🎬")
print("="*80)