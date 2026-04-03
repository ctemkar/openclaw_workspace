            'moral': story['moral'],
            'cliffhanger': story['cliffhanger'],
            'cta': cta,
            'visuals': [
                'Story scene animation',
                'Key moment highlights',
                'Moral text overlay',
                'Cliffhanger suspense build'
            ],
            'hashtags': [f"#{story['title'].replace(' ', '')}", '#StoryTime', #Mahabharata', #60SecondStory', #EpicTales'],
            'algorithm_tips': [
                '60-second narratives show storytelling skill',
                'Cliffhangers increase series retention',
                'Moral lessons add educational value'
            ]
        }
    
    def _generate_wisdom_application(self, short_info: Dict) -> Dict:
        """Generate wisdom application short (45-50 seconds)"""
        wisdoms = [
            {
                'problem': 'Decision paralysis in modern life',
                'wisdom': 'Do your duty without attachment to results - Bhagavad Gita 2.47',
                'steps': '1. Identify your duty\n2. Take action\n3. Release attachment to outcome',
                'results': 'Reduced anxiety, increased productivity, peace of mind'
            },
            {
                'problem': 'Anger management issues',
                'wisdom': 'When meditation is mastered, mind is unwavering like flame in windless place - Bhagavad Gita 6.19',
                'steps': '1. 5-minute daily meditation\n2. Observe anger without reacting\n3. Respond instead of react',
                'results': 'Better emotional control, improved relationships'
            },
            {
                'problem': 'Work-life balance struggle',
                'wisdom': 'Set thy heart upon thy work, but never on its reward - Bhagavad Gita 2.47',
                'steps': '1. Focus on work quality\n2. Detach from promotions/rewards\n3. Find joy in the process',
                'results': 'Reduced stress, increased satisfaction, better performance'
            }
        ]
        
        wisdom = random.choice(wisdoms)
        hook = f"Ancient solution to modern problem: {wisdom['problem']}"
        
        script = f"{hook}\n\nAncient wisdom: {wisdom['wisdom']}\n\nStep-by-step application:\n{wisdom['steps']}\n\nExpected results: {wisdom['results']}"
        
        cta = random.choice(random.choice([cta for cta in self.cta_templates if cta['type'] == 'save_study'])['templates'])
        script += f"\n\n{cta}"
        
        return {
            'type': 'wisdom_application',
            'title': f"Wisdom: {wisdom['problem']}",
            'script': script,
            'duration': short_info['duration'],
            'problem': wisdom['problem'],
            'wisdom': wisdom['wisdom'],
            'steps': wisdom['steps'],
            'results': wisdom['results'],
            'cta': cta,
            'visuals': [
                'Modern problem scene',
                'Ancient text animation',
                'Step-by-step visualization',
                'Results comparison'
            ],
            'hashtags': ['#AncientWisdom', #ModernProblems', #BhagavadGita', #60SecondSolution', #LifeAdvice'],
            'algorithm_tips': [
                'Actionable content gets saved',
                'Problem-solution structure works well',
                '45+ seconds shows practical value'
            ]
        }
    
    def _generate_book_breakdown(self, short_info: Dict) -> Dict:
        """Generate book breakdown short (55-60 seconds)"""
        books = [
            {
                'book': 1,
                'title': 'The Magic Flute',
                'insight': 'Shows Krishna\'s human childhood with divine protection',
                'uniqueness': 'Psychological depth over mythological miracles',
                'audience': 'Readers who want humanized gods',
                'affiliate': 'Krishnavatara Book 1 on Amazon'
            },
            {
                'book': 2,
                'title': 'The Wrath of an Emperor',
                'insight': 'Political intrigue in ancient India',
                'uniqueness': 'Kamsa as complex villain with motivations',
                'audience': 'Political thriller fans',
                'affiliate': 'Krishnavatara Book 2 on Amazon'
            },
            {
                'book': 7,
                'title': 'The Book of Draupadi',
                'insight': 'Draupadi as central character with agency',
                'uniqueness': 'Feminist perspective in ancient epic',
                'audience': 'Readers interested in women\'s stories',
                'affiliate': 'Krishnavatara Book 7 on Amazon'
            }
        ]
        
        book = random.choice(books)
        hook = f"60-second book breakdown: K.M. Munshi's Krishnavatara"
        
        script = f"{hook}\n\nBook {book['book']}: '{book['title']}'\n\nKey insight: {book['insight']}\n\nWhy it's unique: {book['uniqueness']}\n\nWho should read: {book['audience']}"
        
        cta = f"Link in bio for {book['affiliate']}"
        script += f"\n\n{cta}"
        
        return {
            'type': 'book_breakdown',
            'title': f"Book: {book['title']}",
            'script': script,
            'duration': short_info['duration'],
            'book': book['book'],
            'book_title': book['title'],
            'insight': book['insight'],
            'uniqueness': book['uniqueness'],
            'audience': book['audience'],
            'affiliate': book['affiliate'],
            'cta': cta,
            'visuals': [
                'Book cover image',
                'K.M. Munshi portrait',
                'Key insight text',
                'Audience targeting graphic'
            ],
            'hashtags': ['#Krishnavatara', '#KMunshi', #BookReview', #60SecondBreakdown', #HistoricalFiction'],
            'algorithm_tips': [
                '60-second reviews establish authority',
                'Book content appeals to educated audience',
                'Affiliate potential in description'
            ]
        }
    
    def generate_daily_batch(self, count: int = 3) -> List[Dict]:
        """Generate daily batch of 45-60 second Shorts"""
        ideas = []
        
        # Mix for daily batch
        types_for_day = []
        if count >= 3:
            types_for_day = ['deep_fact', 'character_study', 'wisdom_application']
        elif count == 2:
            types_for_day = ['story_digest', 'book_breakdown']
        else:
            types_for_day = [random.choice([st['type'] for st in self.shorts_types])]
        
        for i, short_type in enumerate(types_for_day[:count]):
            idea = self.generate_60s_short(short_type)
            idea['id'] = f"M60{datetime.now().strftime('%Y%m%d')}{i+1:02d}"
            idea['batch_date'] = datetime.now().strftime('%Y-%m-%d')
            idea['upload_order'] = i + 1
            idea['status'] = 'pending'
            
            ideas.append(idea)
            self.content_ideas.append(idea)
        
        self.shorts_created += len(ideas)
        self.save_data()
        
        logger.info(f"✅ Generated {len(ideas)} 45-60s Shorts for today")
        return ideas
    
    def generate_7_day_plan(self) -> List[Dict]:
        """Generate 7-day plan (21 Shorts, 45-60 seconds each)"""
        plan = []
        start_date = datetime.now()
        
        daily_mixes = [
            ['deep_fact', 'character_study', 'wisdom_application'],
            ['story_digest', 'book_breakdown', 'deep_fact'],
            ['interactive_quiz', 'comparative_analysis', 'character_study'],
            ['wisdom_application', 'story_digest', 'book_breakdown'],
            ['deep_fact', 'interactive_quiz', 'comparative_analysis'],
            ['character_study', 'wisdom_application', 'story_digest'],
            ['book_breakdown', 'deep_fact', 'interactive_quiz']
        ]
        
        for day in range(7):
            video_date = start_date + timedelta(days=day)
            day_mix = daily_mixes[day]
            
            for i, short_type in enumerate(day_mix):
                idea = self.generate_60s_short(short_type)
                
                plan_entry = {
                    'day': day + 1,
                    'date': video_date.strftime('%Y-%m-%d'),
                    'upload_time': f"{10 + i}:00 AM",
                    'type': short_type,
                    'title': idea['title'],
                    'duration': idea['duration'],
                    'focus': self._get_short_focus(idea),
                    'status': 'planned'
                }
                
                plan.append(plan_entry)
        
        with open('7_day_60s_plan.json', 'w') as f:
            json.dump(plan, f, indent=2)
        
        logger.info("✅ Generated 7-day 45-60s Shorts plan (21 Shorts)")
        return plan
    
    def _get_short_focus(self, idea: Dict) -> str:
        """Get focus description"""
        if idea['type'] == 'character_study':
            return f"Character: {idea.get('character', 'Unknown')}"
        elif idea['type'] == 'story_digest':
            return f"Story: {idea.get('story_title', 'Unknown')}"
        elif idea['type'] == 'book_breakdown':
            return f"Book: {idea.get('book_title', 'Unknown')}"
        else:
            return idea.get('title', 'General')[:40]
    
    def print_sample(self):
        """Print sample 60-second Short"""
        print("\n" + "="*80)
        print("🎬 SAMPLE 60-SECOND MAHABHARATA SHORT")
        print("="*80)
        
        sample = self.generate_60s_short()
        
        print(f"\n📝 TYPE: {sample['type'].upper()}")
        print(f"⏱️ DURATION: {sample['duration']}")
        print(f"🎯 TITLE: {sample['title']}")
        print(f"\n📜 SCRIPT:")
        print("-"*40)
        print(sample['script'])
        print("-"*40)
        
        print(f"\n🖼️ VISUALS: {', '.join(sample['visuals'][:3])}...")
        print(f"🏷️ HASHTAGS: {', '.join(sample['hashtags'][:3])}...")
        print(f"🤖 ALGORITHM TIPS: {sample['algorithm_tips'][0]}")
        
        print("\n" + "="*80)
        print("✅ Perfect for YouTube Shorts algorithm - 45-60 seconds!")
        print("="*80)

# Main execution
if __name__ == "__main__":
    generator = Mahabharata60sShorts()
    
    print("\n" + "="*80)
    print("🕉️ MAHABHARATA 45-60 SECOND SHORTS GENERATOR")
    print("="*80)
    
    # Generate sample
    generator.print_sample()
    
    # Generate today's batch
    print("\n📅 GENERATING TODAY'S BATCH (3 Shorts)...")
    today_batch = generator.generate_daily_batch(3)
    
    print(f"\n✅ Generated {len(today_batch)} Shorts:")
    for i, short in enumerate(today_batch, 1):
        print(f"  {i}. {short['title']} ({short['duration']})")
    
    # Generate 7-day plan
    print("\n📋 GENERATING 7-DAY PLAN (21 Shorts)...")
    plan = generator.generate_7_day_plan()
    
    print(f"\n✅ 7-day plan created with {len(plan)} Shorts")
    print("   Saved to: 7_day_60s_plan.json")
    
    print("\n" + "="*80)
    print("🎬 Your 45-60 second Mahabharata Shorts are ready!")
    print("="*80)
    print("\n💡 TIPS FOR SUCCESS:")
    print("  • Keep videos 45-60 seconds for algorithm favor")
    print("  • Hook viewers in first 3 seconds")
    print("  • Add depth with historical context")
    print("  • Include actionable wisdom")
    print("  • Use trending audio when relevant")
    
    print("\n🚀 READY TO LAUNCH:")
    print("  Run: python3 mahabharata_shorts_60s.py")
    print("  Plan: 7_day_60s_plan.json")
    print("  Logs: mahabharata_shorts_60s.log")