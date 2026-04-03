    def _generate_wisdom_bite(self, short_info: Dict) -> Dict:
        """Generate wisdom bite short"""
        wisdoms = [
            {
                'problem': 'Struggling with decisions?',
                'wisdom': 'Do your duty without attachment to results - Bhagavad Gita',
                'application': 'Focus on action, not outcomes',
                'action': 'Try this today: Do one thing without worrying about result'
            },
            {
                'problem': 'Feeling angry or upset?',
                'wisdom': 'When meditation is mastered, the mind is unwavering like flame in windless place',
                'application': 'Practice mindfulness daily',
                'action': 'Try: 5-minute meditation when upset'
            },
            {
                'problem': 'Dealing with difficult people?',
                'wisdom': 'See same Self in all beings and all beings in Self',
                'application': 'Practice empathy and understanding',
                'action': 'Today: See from other person\'s perspective'
            },
            {
                'problem': 'Wanting material success?',
                'wisdom': 'Set thy heart upon thy work, but never on its reward',
                'application': 'Excel at work, detach from rewards',
                'action': 'Focus on doing excellent work today'
            },
            {
                'problem': 'Facing fear or anxiety?',
                'wisdom': 'The soul is never born nor dies',
                'application': 'Remember what\'s temporary vs eternal',
                'action': 'Write down: What am I truly afraid of?'
            }
        ]
        
        wisdom = random.choice(wisdoms)
        hook = f"Ancient wisdom for modern problem: {wisdom['problem']}"
        wisdom_text = f"{wisdom['wisdom']}"
        application = f"Modern application: {wisdom['application']}"
        action = f"Action step: {wisdom['action']}"
        cta = random.choice(random.choice([cta for cta in self.cta_templates if cta['type'] == 'save_share'])['templates'])
        
        script = f"{hook}\n\n{wisdom_text}\n\n{application}\n\n{action}\n\n{cta}"
        
        return {
            'type': 'wisdom_bite',
            'title': f"Mahabharata Wisdom: {wisdom['problem']}",
            'script': script,
            'duration': short_info['duration'],
            'problem': wisdom['problem'],
            'wisdom': wisdom['wisdom'],
            'application': wisdom['application'],
            'action_step': wisdom['action'],
            'cta': cta,
            'visuals': [
                'Modern problem scene',
                'Ancient text animation',
                'Action step highlight',
                'Calming background'
            ],
            'hashtags': ['#Wisdom', '#Mahabharata', #LifeAdvice', #Shorts', #AncientWisdom'],
            'algorithm_tips': [
                'High save/share potential',
                'Use problem-solution structure',
                'Actionable advice increases value'
            ]
        }
    
    def _generate_krishnavatara_hook(self, short_info: Dict) -> Dict:
        """Generate Krishnavatara hook short"""
        books = [
            {
                'book': 1,
                'title': 'The Magic Flute',
                'insight': 'Shows Krishna\'s human childhood with divine protection',
                'difference': 'Not just miracles - psychological growth',
                'hook': 'Where epic meets novel'
            },
            {
                'book': 2,
                'title': 'The Wrath of an Emperor',
                'insight': 'Political intrigue in ancient India',
                'difference': 'Kamsa as complex villain, not just evil',
                'hook': 'Historical fiction at its best'
            },
            {
                'book': 3,
                'title': 'The Five Brothers',
                'insight': 'Pandavas as real people with flaws',
                'difference': 'Psychological depth over mythological perfection',
                'hook': 'Characters you can relate to'
            },
            {
                'book': 4,
                'title': 'The Book of Bhima',
                'insight': 'Bhima as protector, not just strongman',
                'difference': 'Emotional depth in "simple" character',
                'hook': 'Strength with purpose'
            },
            {
                'book': 7,
                'title': 'The Book of Draupadi',
                'insight': 'Draupadi as central character with agency',
                'difference': 'Feminist perspective in ancient epic',
                'hook': 'Women\'s stories finally told'
            }
        ]
        
        book = random.choice(books)
        hook = f"Book lovers: Discover K.M. Munshi\'s Krishnavatara!"
        insight = f"Book {book['book']}: '{book['title']}'\n\n{book['insight']}"
        difference = f"Why different: {book['difference']}"
        read_more = f"Hook: {book['hook']}"
        cta = "Want more novel insights? Follow!"
        
        script = f"{hook}\n\n{insight}\n\n{difference}\n\n{read_more}\n\n{cta}"
        
        return {
            'type': 'krishnavatara_hook',
            'title': f"Krishnavatara Book {book['book']}: {book['title']}",
            'script': script,
            'duration': short_info['duration'],
            'book': book['book'],
            'book_title': book['title'],
            'insight': book['insight'],
            'difference': book['difference'],
            'hook': book['hook'],
            'cta': cta,
            'visuals': [
                'Book cover image',
                'K.M. Munshi portrait',
                'Novel scene (AI art)',
                'Text comparison: Epic vs Novel'
            ],
            'hashtags': ['#Krishnavatara', '#KMunshi', '#HistoricalFiction', #BookRecommendation', #Shorts'],
            'algorithm_tips': [
                'Niche but engaged audience',
                'Unique content angle',
                'Book lovers are high-value audience'
            ],
            'affiliate_link': f"Amazon link for Krishnavatara Book {book['book']}"
        }
    
    def _generate_quiz_question(self, short_info: Dict) -> Dict:
        """Generate quiz question short"""
        quizzes = [
            {
                'question': 'Which Mahabharata character never told a lie?',
                'options': ['Krishna', 'Yudhishthira', 'Arjuna', 'Bhima'],
                'answer': 'Yudhishthira',
                'hint': 'His name means "steadfast in battle"',
                'fun_fact': 'His chariot floated due to truthfulness!'
            },
            {
                'question': 'How many days did the Mahabharata war last?',
                'options': ['7 days', '18 days', '100 days', '1 year'],
                'answer': '18 days',
                'hint': 'The number of chapters in Bhagavad Gita',
                'fun_fact': 'Billions died in just 18 days!'
            },
            {
                'question': 'Which weapon did Arjuna receive from Indra?',
                'options': ['Brahmastra', 'Pasupatastra', 'Vajra', 'Sudarshana Chakra'],
                'answer': 'Pasupatastra',
                'hint': 'It was Shiva\'s personal weapon',
                'fun_fact': 'Could destroy entire universe!'
            },
            {
                'question': 'Who was Karna\'s biological mother?',
                'options': ['Kunti', 'Gandhari', 'Madri', 'Draupadi'],
                'answer': 'Kunti',
                'hint': 'Same as Pandavas\' mother',
                'fun_fact': 'She abandoned him at birth!'
            },
            {
                'question': 'What was Draupadi\'s other name?',
                'options': ['Satyabhama', 'Subhadra', 'Krishnaa', 'Rukmini'],
                'answer': 'Krishnaa',
                'hint': 'Means "dark" or "black"',
                'fun_fact': 'Born from fire with dark complexion!'
            }
        ]
        
        quiz = random.choice(quizzes)
        hook = f"Quick quiz: {quiz['question']}"
        options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(quiz['options'])])
        hint = f"Hint: {quiz['hint']}"
        answer = f"Answer: {quiz['answer']}"
        fun_fact = f"Fun fact: {quiz['fun_fact']}"
        cta = random.choice(random.choice([cta for cta in self.cta_templates if cta['type'] == 'comment'])['templates'])
        
        # Script with timing markers
        script = f"{hook}\n\n{options}\n\n{hint}\n\n{answer}\n\n{fun_fact}\n\n{cta}"
        
        return {
            'type': 'quiz_question',
            'title': f"Mahabharata Quiz: {quiz['question'][:30]}...",
            'script': script,
            'duration': short_info['duration'],
            'question': quiz['question'],
            'options': quiz['options'],
            'answer': quiz['answer'],
            'hint': quiz['hint'],
            'fun_fact': quiz['fun_fact'],
            'cta': cta,
            'visuals': [
                'Quiz question text',
                'Options with numbers (1, 2, 3, 4)',
                'Countdown timer animation',
                'Answer reveal with celebration'
            ],
            'hashtags': ['#Quiz', '#Mahabharata', #Trivia', #Shorts', #TestYourKnowledge'],
            'algorithm_tips': [
                'High comment engagement',
                'Use polls in community tab too',
                'Reveal answer after pause'
            ]
        }
    
    def _generate_comparison(self, short_info: Dict) -> Dict:
        """Generate comparison short"""
        comparisons = [
            {
                'title': 'Krishna vs. Superman',
                'item1': 'Krishna',
                'item2': 'Superman',
                'points': ['8 powers vs. many powers', 'Divine vs. alien', '5000 years older', 'Philosophy teacher'],
                'winner': 'Krishna',
                'why': 'Older, wiser, actually existed in culture'
            },
            {
                'title': 'Mahabharata vs. Game of Thrones',
                'item1': 'Mahabharata',
                'item2': 'Game of Thrones',
                'points': ['18-day war vs. many seasons', 'Real cultural impact vs. fiction', '5000 years older', 'Spiritual depth'],
                'winner': 'Mahabharata',
                'why': 'Original epic that inspired many'
            },
            {
                'title': 'Draupadi vs. Wonder Woman',
                'item1': 'Draupadi',
                'item2': 'Wonder Woman',
                'points': ['Born from fire vs. clay', 'Queen of 5 vs. princess', '2000+ years older', 'Real cultural icon'],
                'winner': 'Draupadi',
                'why': 'Older, more complex, historical basis'
            },
            {
                'title': 'Traditional vs. Krishnavatara',
                'item1': 'Traditional Epic',
                'item2': 'Krishnavatara Novel',
                'points': ['Mythological vs. historical fiction', 'Divine focus vs. human focus', 'Ancient vs. modern retelling', 'Religious vs. literary'],
                'winner': 'Both',
                'why': 'Different experiences, both valuable'
            }
        ]
        
        comp = random.choice(comparisons)
        hook = f"{comp['title']} - Who wins?"
        points = "\n".join([f"• {point}" for point in comp['points'][:3]])
        winner = f"Winner: {comp['winner']}"
        why = f"Why: {comp['why']}"
        cta = f"Agree? Comment your take! {random.choice(['👑', '⚔️', '🕉️', '🎯'])}"
        
        script = f"{hook}\n\n{points}\n\n{winner}\n\n{why}\n\n{cta}"
        
        return {
            'type': 'comparison',
            'title': comp['title'],
            'script': script,
            'duration': short_info['duration'],
            'item1': comp['item1'],
            'item2': comp['item2'],
            'points': comp['points'],
            'winner': comp['winner'],
            'why': comp['why'],
            'cta': cta,
            'visuals': [
                'Split screen comparison',
                'Animated points list',
                'Winner highlight',
                'Debate question text'
            ],
            'hashtags': ['#Comparison', '#Mahabharata', #Debate', #Shorts', #Vs'],
            'algorithm_tips': [
                'Creates debate in comments',
                'Use controversial comparisons',
                'Ask for opinions at end'
            ]
        }
    
    def generate_daily_batch(self, count: int = 3) -> List[Dict]:
        """Generate daily batch of Shorts"""
        ideas = []
        
        # Mix of content types for daily batch
        types_for_day = []
        if count >= 3:
            types_for_day = ['quick_fact', 'character_intro', 'wisdom_bite']
        elif count == 2:
            types_for_day = ['quick_fact', 'story_teaser']
        else:
            types_for_day = [random.choice([st['type'] for st in self.shorts_types])]
        
        for i, short_type in enumerate(types_for_day[:count]):
            idea = self.generate_short(short_type)
            idea['id'] = f"MS{datetime.now().strftime('%Y%m%d')}{i+1:02d}"
            idea['batch_date'] = datetime.now().strftime('%Y-%m-%d')
            idea['upload_order'] = i + 1
            idea['status'] = 'pending'
            
            ideas.append(idea)
            self.content_ideas.append(idea)
        
        self.shorts_created += len(ideas)
        self.save_data()
        
        logger.info(f"✅ Generated {len(ideas)} Shorts for today")
        return ideas
    
    def generate_7_day_plan(self) -> List[Dict]:
        """Generate 7-day Shorts plan (21 Shorts)"""
        plan = []
        start_date = datetime.now()
        
        # Content mix for week
        daily_mixes = [
            ['quick_fact', 'character_intro', 'wisdom_bite'],  # Day 1
            ['story_teaser', 'quiz_question', 'quick_fact'],   # Day 2
            ['krishnavatara_hook', 'comparison', 'wisdom_bite'], # Day 3
            ['character_intro', 'quick_fact', 'story_teaser'], # Day 4
            ['wisdom_bite', 'quiz_question', 'comparison'],    # Day 5
            ['krishnavatara_hook', 'character_intro', 'quick_fact'], # Day 6
            ['story_teaser', 'wisdom_bite', 'quiz_question']   # Day 7
        ]
        
        for day in range(7):
            video_date = start_date + timedelta(days=day)
            day_mix = daily_mixes[day]
            
            for i, short_type in enumerate(day_mix):
                idea = self.generate_short(short_type)
                
                plan_entry = {
                    'day': day + 1,
                    'date': video_date.strftime('%Y-%m-%d'),
                    'upload_time': f"{10 + i}:00 AM",  # 10 AM, 11 AM, 12 PM
                    'type': short_type,
                    'title': idea['title'],
                    'duration': idea['duration'],
                    'focus': self._get_short_focus(idea),
                    'status': 'planned'
                }
                
                plan.append(plan_entry)
        
        # Save plan
        with open('7_day_shorts_plan.json', 'w') as f:
            json.dump(plan, f, indent=2)
        
        logger.info("✅ Generated 7-day Shorts plan (21 Shorts)")
        return plan
    
    def _get_short_focus(self, idea: Dict) -> str:
        """Get focus description for Short"""
        if idea['type'] == 'character_intro':
            return f"Character: {idea.get('character', 'Unknown')}"
        elif idea['type'] == 'story_teaser':
            return f"Story: {idea.get('story_title', 'Unknown')}"
        elif idea['type'] == 'krishnavatara_hook':
            return f"Book: {idea.get('book_title', 'Unknown')}"
        elif idea['type'] == 'quiz_question':
            return f"Quiz: {idea.get('question', 'Unknown')[:30]}..."
        else:
            return idea.get('title', 'General')[:40]
    
    def generate_production_guide(self) -> Dict:
        """Generate Shorts production guide"""
        guide = {
            'shorts_specs': {
                'duration': '25-45 seconds',
                'resolution': '1080x1920 (9:16)',
                'fps': 30,
                'max_size': '1GB',
                'format': 'MP4'
            },
            'algorithm_optimization': {
                'hook_first_3_seconds': 'Critical for retention',
                'vertical_format': 'Required for Shorts shelf',
                'engaging_cta': 'Increases comments/shares',
                'consistent_posting': 'Algorithm rewards consistency',
                'trending_sounds': 'Use trending audio when relevant'
            },
            'daily_workflow': {
                'script_writing': '15 mins (3 Shorts)',
                'visual_creation': '30 mins (AI art + text)',
                'video