            f"Krishnavatara Book {book['book']}: '{book['title']}' - where Mahabharata meets great literature. Munshi doesn't just retell the epic; he reimagines it with {', '.join(book['key_themes'][:2])}. Perfect for book lovers!"
        ]
        
        return {
            'type': 'krishnavatara',
            'book': book['book'],
            'book_title': book['title'],
            'title': random.choice(angles),
            'script': random.choice(scripts),
            'focus': book['focus'],
            'key_themes': book['key_themes'],
            'munshi_insights': [
                'Historical fiction approach',
                'Psychological character depth',
                'Accessible for modern readers',
                'Literary quality'
            ],
            'visuals': [
                f"Book cover of '{book['title']}'",
                'K.M. Munshi portrait',
                'Scene from the book (AI art)',
                'Key themes text overlay'
            ],
            'hashtags': [
                '#Krishnavatara',
                '#KMunshi',
                '#HistoricalFiction',
                '#IndianLiterature',
                '#BookReview'
            ],
            'affiliate_link': f"Amazon link for Krishnavatara Book {book['book']}"
        }
    
    def _generate_character_study(self) -> Dict:
        """Generate character study content"""
        character = random.choice(self.characters)
        
        angles = [
            f"{character['name']}: Traditional vs. Krishnavatara",
            f"Understanding {character['name']} through Munshi's Eyes",
            f"{character['name']} in Mahabharata: More Than Meets the Eye",
            f"The Real {character['name']}: Krishnavatara's Insight"
        ]
        
        scripts = [
            f"Let's explore {character['name']} - but through two lenses! Traditional: {character['traditional_role']}. Krishnavatara: {character['krishnavatara_aspect']}. Munshi's genius: {random.choice(character['munshi_insights'])}",
            
            f"{character['name']} from Mahabharata - but have you met Munshi's version? Traditional role: {character['traditional_role']}. Krishnavatara adds: {character['krishnavatara_aspect']}. Why this matters: {character['modern_relevance']}",
            
            f"Character deep dive: {character['name']}. In traditional Mahabharata: {character['traditional_role']}. In Krishnavatara: {character['krishnavatara_aspect']}. Key story: {random.choice(character['key_stories'])}. Modern lesson: {character['modern_relevance']}"
        ]
        
        return {
            'type': 'character',
            'character': character['name'],
            'title': random.choice(angles),
            'script': random.choice(scripts),
            'traditional_aspect': character['traditional_role'],
            'krishnavatara_aspect': character['krishnavatara_aspect'],
            'key_stories': character['key_stories'][:2],
            'munshi_insights': character['munshi_insights'],
            'modern_relevance': character['modern_relevance'],
            'visuals': [
                f"Traditional art of {character['name']}",
                f"Krishnavatara-style portrait of {character['name']}",
                'Split screen: traditional vs novel version',
                'Key story scene visualization'
            ],
            'hashtags': [
                f"#{character['name']}",
                '#CharacterStudy',
                '#Mahabharata',
                '#Krishnavatara',
                '#LiteraryAnalysis'
            ]
        }
    
    def _generate_story_summary(self) -> Dict:
        """Generate story summary content"""
        story = random.choice(self.stories)
        
        angles = [
            f"{story['title']}: Mahabharata Story Explained",
            f"The Story of {story['title']} - Simple Version",
            f"{story['title']}: What Really Happened?",
            f"Mahabharata Story: {story['title']} in 60 Seconds"
        ]
        
        scripts = [
            f"Today's Mahabharata story: {story['title']}! Traditional version: {story['traditional']}. Krishnavatara version: {story['krishnavatara']}. Key elements: {', '.join(story['key_elements'][:2])}. Why it matters: {story['modern_angle']}",
            
            f"Story time: {story['title']} from Mahabharata. What happened: {story['traditional']}. But in Krishnavatara, Munshi adds: {random.choice(story['munshi_additions'])}. Modern angle: {story['modern_angle']}",
            
            f"Let's unpack {story['title']} - one of Mahabharata's key stories. Basic plot: {story['traditional']}. Krishnavatara depth: {story['krishnavatara']}. Key elements: {random.choice(story['key_elements'])}. Relevance today: {story['modern_angle']}"
        ]
        
        return {
            'type': 'story',
            'story_title': story['title'],
            'title': random.choice(angles),
            'script': random.choice(scripts),
            'traditional_summary': story['traditional'],
            'krishnavatara_summary': story['krishnavatara'],
            'key_elements': story['key_elements'],
            'munshi_additions': story['munshi_additions'],
            'modern_angle': story['modern_angle'],
            'visuals': [
                f"Scene from {story['title']} (AI art)",
                'Story timeline visualization',
                'Key characters involved',
                'Modern parallel visualization'
            ],
            'hashtags': [
                f"#{story['title'].replace(' ', '')}",
                '#MahabharataStories',
                '#Storytelling',
                '#IndianMythology',
                '#EpicTales'
            ]
        }
    
    def _generate_modern_lesson(self) -> Dict:
        """Generate modern lesson content"""
        lessons = [
            {
                'topic': 'Leadership',
                'example': 'Yudhishthira\'s righteous rule',
                'lesson': 'Lead with ethics, not just efficiency',
                'modern_application': 'Business leadership, team management'
            },
            {
                'topic': 'Decision Making',
                'example': 'Arjuna\'s dilemma in Bhagavad Gita',
                'lesson': 'Clarity comes from understanding purpose',
                'modern_application': 'Career choices, life decisions'
            },
            {
                'topic': 'Resilience',
                'example': 'Draupadi\'s strength during exile',
                'lesson': 'True strength is bouncing back from adversity',
                'modern_application': 'Dealing with failure, personal challenges'
            },
            {
                'topic': 'Ethics',
                'example': 'Krishna\'s guidance in difficult situations',
                'lesson': 'Right action often requires wisdom, not just rules',
                'modern_application': 'Workplace ethics, personal morals'
            },
            {
                'topic': 'Relationships',
                'example': 'Pandavas\' brotherhood',
                'lesson': 'Strong relationships require sacrifice and understanding',
                'modern_application': 'Family, friendships, partnerships'
            }
        ]
        
        lesson = random.choice(lessons)
        
        angles = [
            f"Mahabharata Lesson: {lesson['topic']} for Modern Life",
            f"Ancient Wisdom: {lesson['topic']} from Mahabharata",
            f"{lesson['topic']} Lessons from India\'s Epic",
            f"How Mahabharata Teaches {lesson['topic']}"
        ]
        
        scripts = [
            f"Ancient wisdom for modern life! Today: {lesson['topic']} from Mahabharata. Example: {lesson['example']}. Lesson: {lesson['lesson']}. Modern application: {lesson['modern_application']}",
            
            f"Mahabharata isn't just ancient history - it's practical wisdom! {lesson['topic']} lesson: {lesson['lesson']}. From the story of {lesson['example'].split(\"'\")[0]}. Apply today: {lesson['modern_application']}",
            
            f"Need {lesson['topic'].lower()} advice? Mahabharata has it! Based on {lesson['example']}. Key insight: {lesson['lesson']}. How to use this today: {lesson['modern_application']}"
        ]
        
        return {
            'type': 'lesson',
            'topic': lesson['topic'],
            'title': random.choice(angles),
            'script': random.choice(scripts),
            'example': lesson['example'],
            'lesson': lesson['lesson'],
            'modern_application': lesson['modern_application'],
            'visuals': [
                'Modern workplace/生活 scene',
                'Ancient scene parallel',
                'Key lesson text overlay',
                'Action steps visualization'
            ],
            'hashtags': [
                f"#{lesson['topic']}",
                '#LifeLessons',
                '#AncientWisdom',
                '#PersonalGrowth',
                '#SelfImprovement'
            ]
        }
    
    def _generate_comparison(self) -> Dict:
        """Generate comparison content"""
        comparisons = [
            {
                'aspect': 'Character Portrayal',
                'traditional': 'Idealized, archetypal characters',
                'krishnavatara': 'Psychological depth, human flaws',
                'example': 'Krishna as perfect god vs. Krishna with human struggles'
            },
            {
                'aspect': 'Storytelling Style',
                'traditional': 'Epic, mythological narrative',
                'krishnavatara': 'Historical fiction, novelistic approach',
                'example': 'Divine miracles vs. human drama with divine elements'
            },
            {
                'aspect': 'Accessibility',
                'traditional': 'Requires cultural/religious context',
                'krishnavatara': 'Accessible to global audience',
                'example': 'Assumes knowledge of dharma vs. explains through story'
            },
            {
                'aspect': 'Female Characters',
                'traditional': 'Often peripheral or idealized',
                'krishnavatara': 'Central, complex, with agency',
                'example': 'Draupadi as victim vs. Draupadi as strategist'
            }
        ]
        
        comparison = random.choice(comparisons)
        
        angles = [
            f"Traditional vs. Krishnavatara: {comparison['aspect']}",
            f"How Krishnavatara Changes {comparison['aspect']}",
            f"{comparison['aspect']}: Epic vs. Novel Approach",
            f"Mahabharata Through Two Lenses: {comparison['aspect']}"
        ]
        
        scripts = [
            f"Traditional Mahabharata vs. K.M. Munshi's Krishnavatara: {comparison['aspect']}! Traditional: {comparison['traditional']}. Krishnavatara: {comparison['krishnavatara']}. Example: {comparison['example']}",
            
            f"Two ways to experience Mahabharata! Aspect: {comparison['aspect']}. Epic version: {comparison['traditional']}. Novel version (Krishnavatara): {comparison['krishnavatara']}. Why both matter: they complement each other!",
            
            f"Compare and contrast: {comparison['aspect']} in Mahabharata. Traditional approach: {comparison['traditional']}. Munshi's Krishnavatara: {comparison['krishnavatara']}. Perfect example: {comparison['example']}"
        ]
        
        return {
            'type': 'comparison',
            'aspect': comparison['aspect'],
            'title': random.choice(angles),
            'script': random.choice(scripts),
            'traditional': comparison['traditional'],
            'krishnavatara': comparison['krishnavatara'],
            'example': comparison['example'],
            'visuals': [
                'Split screen: traditional vs novel',
                'Venn diagram of approaches',
                'Example scene comparison',
                'Key differences text overlay'
            ],
            'hashtags': [
                '#LiteraryComparison',
                '#TraditionalVsModern',
                '#Krishnavatara',
                '#Mahabharata',
                '#BookAnalysis'
            ]
        }
    
    def generate_content_batch(self, count: int = 7) -> List[Dict]:
        """Generate a batch of content ideas"""
        ideas = []
        
        # Ensure mix of content types
        content_types = [ct['type'] for ct in self.content_types]
        type_distribution = []
        
        # Distribute types (more introductions and stories for beginners)
        for i in range(count):
            if i == 0:
                type_distribution.append('introduction')
            elif i == 1:
                type_distribution.append('krishnavatara')
            elif i == 2:
                type_distribution.append('character')
            elif i == 3:
                type_distribution.append('story')
            elif i == 4:
                type_distribution.append('lesson')
            elif i == 5:
                type_distribution.append('comparison')
            else:
                type_distribution.append(random.choice(content_types))
        
        for i, content_type in enumerate(type_distribution):
            idea = self.generate_content_idea(content_type)
            idea['id'] = f"MBE{i+1:03d}"
            idea['batch_number'] = len(self.content_ideas) // count + 1
            idea['created'] = datetime.now().isoformat()
            idea['status'] = 'pending'
            
            ideas.append(idea)
            self.content_ideas.append(idea)
        
        self.videos_created += len(ideas)
        self.save_data()
        
        logger.info(f"✅ Generated {len(ideas)} content ideas (Batch {ideas[0]['batch_number']})")
        return ideas
    
    def generate_30_day_calendar(self) -> List[Dict]:
        """Generate 30-day content calendar"""
        calendar = []
        start_date = datetime.now()
        
        # Content type distribution for 30 days
        # Week 1: Heavy on introductions and basics
        # Week 2: More Krishnavatara focus
        # Week 3: Character studies
        # Week 4: Mixed advanced content
        
        for day in range(30):
            video_date = start_date + timedelta(days=day)
            week = day // 7
            
            if week == 0:  # Week 1: Basics
                if day == 0:
                    content_type = 'introduction'
                elif day == 1:
                    content_type = 'story'
                elif day == 2:
                    content_type = 'introduction'
                elif day == 3:
                    content_type = 'character'
                elif day == 4:
                    content_type = 'story'
                elif day == 5:
                    content_type = 'krishnavatara'
                else:
                    content_type = 'lesson'
            
            elif week == 1:  # Week 2: Krishnavatara focus
                content_types = ['krishnavatara', 'comparison', 'character', 'story', 'lesson']
                content_type = content_types[day % 5]
            
            elif week == 2:  # Week 3: Character studies
                if day % 3 == 0:
                    content_type = 'character'
                elif day % 3 == 1:
                    content_type = 'comparison'
                else:
                    content_type = 'lesson'
            
            else:  # Week 4: Mixed advanced
                content_types = ['krishnavatara', 'comparison', 'lesson', 'story', 'character']
                content_type = content_types[day % 5]
            
            idea = self.generate_content_idea(content_type)
            
            calendar_entry = {
                'day': day + 1,
                'date': video_date.strftime('%Y-%m-%d'),
                'content_type': content_type,
                'title': idea['title'],
                'focus': self._get_focus_from_idea(idea),
                'production_time': '30-45 minutes',
                'status': 'planned',
                'notes': f"Week {week + 1}: {self._get_week_theme(week)}"
            }
            
            calendar.append(calendar_entry)
        
        # Save calendar
        with open('30_day_calendar.json', 'w') as f:
            json.dump(calendar, f, indent=2)
        
        logger.info("✅ Generated 30-day content calendar")
        return calendar
    
    def _get_focus_from_idea(self, idea: Dict) -> str:
        """Extract focus from idea"""
        if idea['type'] == 'krishnavatara':
            return f"Krishnavatara Book {idea.get('book', '')}: {idea.get('book_title', '')}"
        elif idea['type'] == 'character':
            return f"Character: {idea.get('character', '')}"
        elif idea['type'] == 'story':
            return f"Story: {idea.get('story_title', '')}"
        else:
            return idea.get('title', 'General')
    
    def _get_week_theme(self, week: int) -> str:
        """Get week theme"""
        themes = [
            'Week 1: Mahabharata Basics & Introductions',
            'Week 2: Krishnavatara Deep Dives',
            'Week 3: Character Studies & Analysis',
            'Week 4: Advanced Topics & Applications'
        ]
        return themes[week] if week < len(themes) else 'Advanced Content'
    
    def generate_production_guide(self) -> Dict:
        """Generate production guide"""
        guide = {
            'channel_name': 'Mahabharata for Everyone',
            'tagline': 'Ancient India\'s greatest story - made accessible for all!',
            'unique_angle': 'Combines traditional Mahabharata with K.M. Munshi\'s Krishnavatara novels',
            'target_audience': [
                'Complete beginners to Mahabharata',
                'Western audience interested in Indian culture',
                'Book lovers and literature enthusiasts',
                'People seeking ancient wisdom for modern life'
            ],
            'content_mix': {
                'introduction': '20% - Basics for beginners',
                'krishnavatara': '25% - Unique novel-based content',
                'character': '20% - Deep