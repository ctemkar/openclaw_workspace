        script_templates = [
            f"Today's Mahabharata wisdom: {lesson}. This {category.lower()} lesson comes from ancient India's greatest epic. How to apply: {self._generate_application(lesson)}. Modern relevance: {self._generate_relevance(lesson)}",
            
            f"Mahabharata teaches us about {category.lower()}. Key lesson: {lesson}. Which character demonstrated this? {random.choice(self.characters)['name']}. How this applies today: {self._generate_modern_application(lesson)}",
            
            f"60-second wisdom from Mahabharata: {lesson}. Category: {category}. Why it matters: {self._generate_importance(lesson)}. Action step: {self._generate_action_step(lesson)}"
        ]
        
        return {
            'type': 'lesson',
            'category': category,
            'lesson': lesson,
            'title': random.choice(title_templates),
            'script': random.choice(script_templates),
            'duration': '40-55 seconds',
            'visuals': [
                "Wisdom text overlay with elegant fonts",
                "AI art of relevant Mahabharata scene",
                "Animated bullet points",
                "Modern life comparison visuals"
            ],
            'hashtags': [
                f"#{category}",
                "#LifeLessons",
                "#AncientWisdom",
                "#Mahabharata",
                "#SpiritualGrowth",
                "#PersonalDevelopment"
            ],
            'target_audience': ['Self-improvement seekers', 'Students', 'Professionals', 'Spiritual practitioners']
        }
    
    def _generate_quote_idea(self, character: Dict, quote: str) -> Dict:
        """Generate quote-based content idea"""
        title_templates = [
            f"{character['name']}'s Wisdom: \"{quote[:30]}...\"",
            f"Powerful Quote from {character['name']}",
            f"{character['name']} Said: {quote[:40]}...",
            f"Mahabharata Quote That Will Change Your Perspective",
            f"{character['name']}'s Timeless Message"
        ]
        
        script_templates = [
            f"\"{quote}\" - {character['name']}. This powerful quote from Mahabharata's {character['role']} teaches us about {random.choice(['life', 'duty', 'wisdom', 'courage'])}. Context: {self._generate_quote_context(character, quote)}. Modern interpretation: {self._generate_quote_interpretation(quote)}",
            
            f"Today's Mahabharata quote: \"{quote}\" by {character['name']}. Meaning: {self._explain_quote(quote)}. When was this said? {random.choice(['During war', 'In counsel', 'To a student', 'In reflection'])}. How to apply this wisdom today?",
            
            f"60-second quote reflection: \"{quote}\" - {character['name']}. Who was {character['name']}? {character['role']}. Why this quote matters: {self._quote_significance(quote)}. Personal takeaway: {self._personal_takeaway(quote)}"
        ]
        
        return {
            'type': 'quote',
            'character': character['name'],
            'quote': quote,
            'title': random.choice(title_templates),
            'script': random.choice(script_templates),
            'duration': '35-50 seconds',
            'visuals': [
                "Quote text with beautiful typography",
                f"Portrait of {character['name']}",
                "Animated background with Indian patterns",
                "Context scene visualization"
            ],
            'hashtags': [
                f"#{character['name'].replace(' ', '')}",
                "#Quotes",
                "#WisdomQuotes",
                "#Mahabharata",
                "#SpiritualQuotes",
                "#IndianWisdom"
            ],
            'target_audience': ['Quote lovers', 'Motivation seekers', 'Content creators', 'Philosophy enthusiasts']
        }
    
    def _generate_modern_idea(self, character: Dict) -> Dict:
        """Generate modern interpretation idea"""
        modern_topics = [
            'leadership', 'management', 'relationships', 'ethics', 
            'decision-making', 'conflict resolution', 'personal growth'
        ]
        
        topic = random.choice(modern_topics)
        
        title_templates = [
            f"What {character['name']} Teaches About Modern {topic.title()}",
            f"{character['name']} in 2024: {topic.title()} Lessons",
            f"Ancient {topic.title()} Wisdom from {character['name']}",
            f"How {character['name']} Would Handle Modern {topic.title()}",
            f"{topic.title()} Tips from Mahabharata's {character['name']}"
        ]
        
        script_templates = [
            f"What can {character['name']} from 5000 years ago teach us about modern {topic}? As {character['role']}, {character['name']} demonstrated {random.choice(character['virtues'])}. Modern application: {self._modern_application(character, topic)}. Actionable tip: {self._modern_tip(character, topic)}",
            
            f"Mahabharata's {character['name']} for modern {topic}. Key quality: {random.choice(character['virtues'])}. How this applies to {topic} today: {self._apply_to_topic(character, topic)}. Example from {character['name']}'s life: {random.choice(character['key_stories'])}",
            
            f"60-second modern wisdom: {character['name']} on {topic}. {character['name']} was {character['role']} known for {random.choice(character['virtues'])}. Modern {topic} lesson: {self._modern_lesson(character, topic)}. Try this today: {self._try_today(character, topic)}"
        ]
        
        return {
            'type': 'modern',
            'character': character['name'],
            'modern_topic': topic,
            'title': random.choice(title_templates),
            'script': random.choice(script_templates),
            'duration': '50-60 seconds',
            'visuals': [
                f"{character['name']} in modern context (AI art)",
                "Split screen: ancient vs modern",
                "Bullet points of applications",
                "Modern workplace/relationship scenes"
            ],
            'hashtags': [
                f"#{topic}",
                "#ModernWisdom",
                "#Mahabharata",
                f"#{character['name'].replace(' ', '')}",
                "#LifeSkills",
                "#PersonalDevelopment"
            ],
            'target_audience': ['Professionals', 'Managers', 'Students', 'Modern seekers']
        }
    
    # Helper methods for content generation
    def _generate_application(self, lesson: str) -> str:
        applications = [
            "Practice this in daily decisions",
            "Apply in relationships and work",
            "Use as guiding principle",
            "Implement in goal setting",
            "Apply during challenges"
        ]
        return random.choice(applications)
    
    def _generate_relevance(self, lesson: str) -> str:
        relevances = [
            "More relevant today than ever",
            "Essential for modern life",
            "Key to happiness and success",
            "Solution to modern problems",
            "Timeless truth for all ages"
        ]
        return random.choice(relevances)
    
    def _generate_modern_application(self, lesson: str) -> str:
        applications = [
            "Apply in digital age challenges",
            "Use in modern relationships",
            "Implement in career growth",
            "Apply to social media interactions",
            "Use in financial decisions"
        ]
        return random.choice(applications)
    
    def _generate_importance(self, lesson: str) -> str:
        importances = [
            "Prevents common mistakes",
            "Leads to inner peace",
            "Improves decision making",
            "Builds strong character",
            "Creates meaningful life"
        ]
        return random.choice(importances)
    
    def _generate_action_step(self, lesson: str) -> str:
        steps = [
            "Reflect on this daily",
            "Share with someone today",
            "Apply in next decision",
            "Journal about it",
            "Teach it to others"
        ]
        return random.choice(steps)
    
    def _generate_quote_context(self, character: Dict, quote: str) -> str:
        contexts = [
            f"Said during {random.choice(character['key_stories'])}",
            "Spoken as advice to a disciple",
            "Part of a larger teaching",
            "Response to a challenging situation",
            "Shared wisdom with followers"
        ]
        return random.choice(contexts)
    
    def _generate_quote_interpretation(self, quote: str) -> str:
        interpretations = [
            "About doing duty without attachment",
            "Teaching detachment from results",
            "Emphasizing righteous action",
            "About the eternal nature of soul",
            "Teaching surrender to divine will"
        ]
        return random.choice(interpretations)
    
    def _explain_quote(self, quote: str) -> str:
        explanations = [
            "Focus on action, not outcomes",
            "Truth is foundation of everything",
            "Duty comes before personal desire",
            "Wisdom overcomes confusion",
            "Right action at right time"
        ]
        return random.choice(explanations)
    
    def _quote_significance(self, quote: str) -> str:
        significances = [
            "Changes perspective on life",
            "Provides clarity in confusion",
            "Offers comfort in difficulty",
            "Guides ethical decisions",
            "Inspires righteous action"
        ]
        return random.choice(significances)
    
    def _personal_takeaway(self, quote: str) -> str:
        takeaways = [
            "Focus on what you can control",
            "Let go of attachment to results",
            "Act with integrity always",
            "Seek wisdom over wealth",
            "Serve others selflessly"
        ]
        return random.choice(takeaways)
    
    def _modern_application(self, character: Dict, topic: str) -> str:
        applications = {
            'leadership': f"Lead like {character['name']} - with {random.choice(character['virtues'])}",
            'management': f"Manage teams with {character['name']}'s {random.choice(character['virtues'])}",
            'relationships': f"Build relationships with {character['name']}'s wisdom",
            'ethics': f"Make ethical decisions like {character['name']}",
            'decision-making': f"Decide with {character['name']}'s clarity"
        }
        return applications.get(topic, f"Apply {character['name']}'s wisdom to {topic}")
    
    def _modern_tip(self, character: Dict, topic: str) -> str:
        tips = {
            'leadership': "Lead by example, not just words",
            'management': "Understand team members individually",
            'relationships': "Communicate with honesty and compassion",
            'ethics': "Choose right over easy",
            'decision-making': "Consider long-term consequences"
        }
        return tips.get(topic, f"Apply ancient wisdom to modern {topic}")
    
    def _apply_to_topic(self, character: Dict, topic: str) -> str:
        applications = {
            'leadership': f"{character['name']}'s leadership was based on {random.choice(character['virtues'])}",
            'management': f"Manage with {character['name']}'s {random.choice(['patience', 'wisdom', 'fairness'])}",
            'relationships': f"Build trust like {character['name']} did",
            'ethics': f"Ethical framework from {character['name']}'s life",
            'decision-making': f"Decision process of {character['name']}"
        }
        return applications.get(topic, f"{character['name']}'s approach to {topic}")
    
    def _modern_lesson(self, character: Dict, topic: str) -> str:
        lessons = {
            'leadership': "True leadership serves others",
            'management': "Good management empowers team",
            'relationships': "Strong relationships need trust",
            'ethics': "Ethics build lasting success",
            'decision-making': "Wise decisions consider all"
        }
        return lessons.get(topic, f"Ancient wisdom for modern {topic}")
    
    def _try_today(self, character: Dict, topic: str) -> str:
        actions = {
            'leadership': "Lead one meeting with complete presence",
            'management': "Listen to one team member without interrupting",
            'relationships': "Express gratitude to someone today",
            'ethics': "Make one ethical choice consciously",
            'decision-making': "Consider three options before deciding"
        }
        return actions.get(topic, f"Apply one lesson from {character['name']} today")
    
    def generate_production_plan(self, idea: Dict) -> Dict:
        """Generate production plan for a content idea"""
        production_steps = [
            {
                'step': 1,
                'task': 'Script Finalization',
                'duration': '10 minutes',
                'tools': ['ChatGPT for refinement', 'Grammarly for editing'],
                'output': 'Final script with timing'
            },
            {
                'step': 2,
                'task': 'Visual Creation',
                'duration': '15 minutes',
                'tools': ['Midjourney/DALL-E for AI art', 'Canva for graphics'],
                'output': '5-7 visual assets'
            },
            {
                'step': 3,
                'task': 'Voiceover Recording',
                'duration': '5 minutes',
                'tools': ['ElevenLabs for AI voice', 'Audacity for editing'],
                'output': 'Audio file with proper pacing'
            },
            {
                'step': 4,
                'task': 'Video Editing',
                'duration': '10 minutes',
                'tools': ['CapCut/InShot', 'Premiere Rush'],
                'output': 'Final 60-second video'
            },
            {
                'step': 5,
                'task': 'Thumbnail Creation',
                'duration': '5 minutes',
                'tools': ['Canva', 'Photoshop'],
                'output': 'Clickable thumbnail'
            }
        ]
        
        total_time = sum([int(step['duration'].split()[0]) for step in production_steps])
        
        return {
            'idea_id': idea.get('id', 'Unknown'),
            'title': idea['title'],
            'total_production_time': f"{total_time} minutes",
            'steps': production_steps,
            'tools_needed': list(set([tool for step in production_steps for tool in step['tools']])),
            'output_files': [
                f"{idea.get('id', 'video')}_script.txt",
                f"{idea.get('id', 'video')}_audio.mp3",
                f"{idea.get('id', 'video')}_video.mp4",
                f"{idea.get('id', 'video')}_thumbnail.jpg"
            ]
        }
    
    def calculate_earnings_potential(self, videos_per_month: int = 30) -> Dict:
        """Calculate potential earnings"""
        # YouTube RPM for this niche: $8-15 (religious/educational content)
        low_rpm = 8
        high_rpm = 15
        
        # View estimates per video (conservative to optimistic)
        low_views = 10000
        medium_views = 50000
        high_views = 200000
        
        scenarios = {}
        
        # Conservative scenario
        monthly_views = videos_per_month * low_views
        low_earnings = (monthly_views / 1000) * low_rpm
        high_earnings = (monthly_views / 1000) * high_rpm
        
        scenarios['conservative'] = {
            'videos_per_month': videos_per_month,
            'views_per_video': low_views,
            'monthly_views': monthly_views,
            'low_earnings': round(low_earnings, 2),
            'high_earnings': round(high_earnings, 2),
            'estimated': round((low_earnings + high_earnings) / 2, 2)
        }
        
        # Medium scenario
        monthly_views = videos_per_month * medium_views
        low_earnings = (monthly_views / 1000) * low_rpm
        high_earnings = (monthly_views / 1000) * high_rpm
        
        scenarios['medium'] = {
            'videos_per_month': videos_per_month,
            'views_per_video': medium_views,
            'monthly_views': monthly_views,
            'low_earnings': round(low_earnings, 2),
            'high_earnings': round(high_earnings, 2),
            'estimated': round((low_earnings + high_earnings) / 2, 2)
        }
        
        # Optimistic scenario
        monthly_views = videos_per_month * high_views
        low_earnings = (monthly_views / 1000) * low_rpm
        high_earnings = (monthly_views / 1000) * high_rpm
        
        scenarios['optimistic'] = {
            'videos_per_month': videos_per_month,
            'views_per_video': high_views,
            'monthly_views': monthly_views,
            'low_earnings': round(low_earnings, 2),
            'high_earnings': round(high_earnings, 2),
            'estimated': round((low_earnings + high_earnings) / 2, 2)
        }
        
        # Additional income streams
        additional = {
            'affiliate_marketing': 2000,
            'sponsorships': 3000,
            'digital_products': 5000,
            'consulting': 4000
        }
        
        total_additional = sum(additional.values())
        
        # Save to file
        with open('earnings_potential.json', 'w') as f:
            json.dump({
                'scenarios': scenarios,
                'additional_income': additional,
                'total_potential': {
                    'conservative': scenarios['conservative']['estimated'] + total_additional * 0.3,
                    'medium': scenarios['medium']['estimated'] + total_additional * 0.6,
                    'optimistic': scenarios['optim