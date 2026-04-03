#!/usr/bin/env python3
"""
MAHABHARATA YOUTUBE SHORTS GENERATOR
Optimized for YouTube Shorts algorithm - 30-45 second videos
"""

import json
import random
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mahabharata_shorts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MahabharataShortsGenerator:
    def __init__(self):
        self.shorts_types = self.load_shorts_types()
        self.hook_templates = self.load_hook_templates()
        self.cta_templates = self.load_cta_templates()
        self.content_ideas = []
        self.shorts_created = 0
        
        # Load existing data
        self.load_data()
    
    def load_shorts_types(self) -> List[Dict]:
        """Load Shorts-optimized content types"""
        return [
            {
                'type': 'quick_fact',
                'name': 'Quick Fact',
                'duration': '25-30 seconds',
                'structure': 'Hook (3s) → Fact (15s) → Surprise (7s) → CTA (5s)',
                'algorithm_tip': 'High retention - facts keep viewers watching',
                'viral_potential': 'High (shareable facts)'
            },
            {
                'type': 'character_intro',
                'name': 'Character Intro',
                'duration': '30-35 seconds',
                'structure': 'Who is this? (3s) → Key traits (15s) → Cool fact (7s) → Follow for more (5s)',
                'algorithm_tip': 'Builds character series - encourages binge watching',
                'viral_potential': 'Medium (character fans share)'
            },
            {
                'type': 'story_teaser',
                'name': 'Story Teaser',
                'duration': '35-40 seconds',
                'structure': 'Set up (5s) → Story (20s) → Cliffhanger (5s) → "Part 2?" (5s)',
                'algorithm_tip': 'Creates series - increases watch time across multiple Shorts',
                'viral_potential': 'High (curiosity gap)'
            },
            {
                'type': 'wisdom_bite',
                'name': 'Wisdom Bite',
                'duration': '25-30 seconds',
                'structure': 'Problem (3s) → Ancient wisdom (15s) → Modern application (7s) → Save/share (5s)',
                'algorithm_tip': 'High saves/shares - algorithm loves this',
                'viral_potential': 'Very High (inspirational content)'
            },
            {
                'type': 'krishnavatara_hook',
                'name': 'Krishnavatara Hook',
                'duration': '40-45 seconds',
                'structure': 'Book intro (5s) → Novel insight (20s) → Why different (10s) → Read more (5s)',
                'algorithm_tip': 'Unique angle - less competition',
                'viral_potential': 'Medium (niche but engaged)'
            },
            {
                'type': 'quiz_question',
                'name': 'Quiz Question',
                'duration': '30-35 seconds',
                'structure': 'Question (5s) → Options (10s) → Hint (5s) → Answer reveal (10s) → Comment answer (5s)',
                'algorithm_tip': 'High comments - algorithm loves engagement',
                'viral_potential': 'High (interactive)'
            },
            {
                'type': 'comparison',
                'name': 'Quick Comparison',
                'duration': '30-35 seconds',
                'structure': 'Two things (5s) → Compare (15s) → Winner (5s) → Why (5s) → Your take? (5s)',
                'algorithm_tip': 'Creates debate in comments',
                'viral_potential': 'High (debate drives engagement)'
            }
        ]
    
    def load_hook_templates(self) -> List[str]:
        """Load hook templates for first 3 seconds"""
        return [
            "Did you know this about Mahabharata?",
            "This Mahabharata fact will surprise you!",
            "Wait until you hear this...",
            "You won't believe what happened in Mahabharata!",
            "This changed how I see Mahabharata forever...",
            "Mahabharata secret most people don't know:",
            "Ancient wisdom that still works today:",
            "The untold story of...",
            "Why everyone gets this Mahabharata story wrong:",
            "This Mahabharata character was actually...",
            "K.M. Munshi's Krishnavatara reveals...",
            "Book lovers: This novel changed Mahabharata for me...",
            "Quick quiz: Which Mahabharata character are you?",
            "Mahabharata vs. Modern life - who wins?",
            "This 30-second story will change your perspective..."
        ]
    
    def load_cta_templates(self) -> List[Dict]:
        """Load call-to-action templates"""
        return [
            {
                'type': 'follow',
                'templates': [
                    "Follow for more Mahabharata shorts!",
                    "Want more? Follow @MahabharataShorts",
                    "Daily Mahabharata content - follow!",
                    "Follow for ancient wisdom daily!"
                ]
            },
            {
                'type': 'comment',
                'templates': [
                    "Comment your answer below!",
                    "What do you think? Comment!",
                    "Tag someone who needs to know this!",
                    "Comment which character you want next!",
                    "Did this surprise you? Comment!"
                ]
            },
            {
                'type': 'save_share',
                'templates': [
                    "Save this for later!",
                    "Share with a friend who loves stories!",
                    "Save & share if you learned something!",
                    "Bookmark this wisdom!"
                ]
            },
            {
                'type': 'series',
                'templates': [
                    "Part 2 tomorrow - follow!",
                    "Next in series dropping soon!",
                    "This is part 1 - stay tuned!",
                    "Series continues tomorrow!"
                ]
            }
        ]
    
    def load_data(self):
        """Load existing data"""
        try:
            if os.path.exists('shorts_content.json'):
                with open('shorts_content.json', 'r') as f:
                    data = json.load(f)
                    self.content_ideas = data.get('content_ideas', [])
                    self.shorts_created = data.get('shorts_created', 0)
                    logger.info(f"✅ Loaded data: {len(self.content_ideas)} shorts ideas, {self.shorts_created} shorts")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save data"""
        try:
            data = {
                'content_ideas': self.content_ideas,
                'shorts_created': self.shorts_created,
                'last_updated': datetime.now().isoformat()
            }
            
            with open('shorts_content.json', 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("✅ Shorts data saved")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def generate_short(self, short_type: str = None) -> Dict:
        """Generate a YouTube Short idea"""
        if not short_type:
            short_type = random.choice([st['type'] for st in self.shorts_types])
        
        short_info = next((st for st in self.shorts_types if st['type'] == short_type), self.shorts_types[0])
        
        if short_type == 'quick_fact':
            return self._generate_quick_fact(short_info)
        elif short_type == 'character_intro':
            return self._generate_character_intro(short_info)
        elif short_type == 'story_teaser':
            return self._generate_story_teaser(short_info)
        elif short_type == 'wisdom_bite':
            return self._generate_wisdom_bite(short_info)
        elif short_type == 'krishnavatara_hook':
            return self._generate_krishnavatara_hook(short_info)
        elif short_type == 'quiz_question':
            return self._generate_quiz_question(short_info)
        elif short_type == 'comparison':
            return self._generate_comparison(short_info)
        else:
            return self._generate_quick_fact(short_info)
    
    def _generate_quick_fact(self, short_info: Dict) -> Dict:
        """Generate quick fact short"""
        facts = [
            "Krishna had 8 principal wives and 16,100 other wives he rescued from demon Narakasura!",
            "The Mahabharata war lasted exactly 18 days but resulted in billions of deaths!",
            "Draupadi was born from fire and had 5 husbands - the Pandava brothers!",
            "Karna was born with golden armor and earrings that made him invincible!",
            "Bhishma lay on a bed of arrows for 58 days before choosing his time of death!",
            "The Bhagavad Gita conversation happened on a battlefield before war started!",
            "Yudhishthira's chariot always floated 4 inches above ground due to his truthfulness!",
            "Arjuna could shoot arrows in complete darkness by listening to sound alone!",
            "The palace of illusions (Maya Sabha) was built by a demon architect!",
            "Krishna lifted Govardhan hill on his little finger for 7 days straight!"
        ]
        
        hook = random.choice(self.hook_templates)
        fact = random.choice(facts)
        cta = random.choice(random.choice([cta for cta in self.cta_templates if cta['type'] in ['follow', 'save_share']])['templates'])
        
        script = f"{hook}\n\n{fact}\n\n{cta}"
        
        return {
            'type': 'quick_fact',
            'title': f"Mahabharata Fact: {fact[:40]}...",
            'script': script,
            'duration': short_info['duration'],
            'hook': hook,
            'main_content': fact,
            'cta': cta,
            'visuals': [
                'Surprised reaction face (AI)',
                'Animated text for fact',
                'Related scene image',
                'Eye-catching background'
            ],
            'hashtags': ['#Mahabharata', '#Fact', #DidYouKnow', #Shorts', #IndianMythology'],
            'algorithm_tips': [
                'High retention expected',
                'Encourage saves/shares',
                'Use curiosity gap in hook'
            ]
        }
    
    def _generate_character_intro(self, short_info: Dict) -> Dict:
        """Generate character introduction short"""
        characters = [
            {
                'name': 'Krishna',
                'traits': ['8th avatar of Vishnu', 'Master strategist', 'Flute player', 'Butter lover'],
                'cool_fact': 'Spoke Bhagavad Gita at age 89!',
                'emoji': '🕉️'
            },
            {
                'name': 'Draupadi',
                'traits': ['Born from fire', 'Queen of 5 kings', 'Unmatched beauty', 'Fierce intelligence'],
                'cool_fact': 'Swore not to tie her hair until washed with enemy blood!',
                'emoji': '👑'
            },
            {
                'name': 'Arjuna',
                'traits': ['World\'s greatest archer', 'Student of Krishna', 'Won Draupadi', 'Meditated for weapons'],
                'cool_fact': 'Could shoot 10 arrows per second!',
                'emoji': '🎯'
            },
            {
                'name': 'Karna',
                'traits': ['Son of sun god', 'Most generous man', 'Loyal friend', 'Tragic hero'],
                'cool_fact': 'Gave away his invincible armor before battle!',
                'emoji': '☀️'
            },
            {
                'name': 'Bhima',
                'traits': ['Strongest Pandava', 'Protector of family', 'Enemy of Kauravas', 'Great cook'],
                'cool_fact': 'Killed all 100 Kaurava brothers!',
                'emoji': '💪'
            },
            {
                'name': 'Yudhishthira',
                'traits': ['King of righteousness', 'Never told lie', 'Skilled dice player', 'Wise ruler'],
                'cool_fact': 'His chariot floated due to truthfulness!',
                'emoji': '⚖️'
            }
        ]
        
        char = random.choice(characters)
        hook = f"Meet {char['name']} {char['emoji']} - Mahabharata's {random.choice(['most interesting', 'most powerful', 'most tragic', 'most wise'])} character!"
        traits = f"Key traits: {', '.join(char['traits'][:2])}"
        fact = f"Cool fact: {char['cool_fact']}"
        cta = random.choice(random.choice([cta for cta in self.cta_templates if cta['type'] == 'follow'])['templates'])
        
        script = f"{hook}\n\n{traits}\n\n{fact}\n\n{cta}"
        
        return {
            'type': 'character_intro',
            'title': f"Meet {char['name']} from Mahabharata",
            'character': char['name'],
            'script': script,
            'duration': short_info['duration'],
            'hook': hook,
            'traits': char['traits'],
            'cool_fact': char['cool_fact'],
            'cta': cta,
            'visuals': [
                f"{char['name']} portrait (AI art)",
                'Animated traits list',
                'Cool fact highlight',
                f"{char['emoji']} emoji animation'
            ],
            'hashtags': [f"#{char['name']}", '#Mahabharata', '#CharacterIntro', '#Shorts', '#IndianEpic'],
            'algorithm_tips': [
                'Start character series',
                'Encourage follows for more characters',
                'Use emojis in captions'
            ]
        }
    
    def _generate_story_teaser(self, short_info: Dict) -> Dict:
        """Generate story teaser short"""
        stories = [
            {
                'title': 'The Dice Game',
                'setup': 'A king gambles away everything...',
                'story': 'Yudhishthira loses kingdom, brothers, and wife in dice game',
                'cliffhanger': 'Draupadi is dragged to court and...',
                'part': 1
            },
            {
                'title': 'Krishna\'s Childhood',
                'setup': 'A divine child with deadly uncle...',
                'story': 'Krishna performs miracles while uncle Kamsa tries to kill him',
                'cliffhanger': 'Kamsa sends demon after demon but...',
                'part': 1
            },
            {
                'title': 'Draupadi\'s Swayamvar',
                'setup': 'Archery contest to win a queen...',
                'story': 'Archers try to hit fish eye while looking at reflection',
                'cliffhanger': 'Karna steps up but Draupadi says...',
                'part': 1
            },
            {
                'title': 'Karna\'s Secret',
                'setup': 'A warrior doesn\'t know his true identity...',
                'story': 'Karna fights against his own brothers unknowingly',
                'cliffhanger': 'His mother reveals the truth but...',
                'part': 1
            },
            {
                'title': 'Bhishma\'s Vow',
                'setup': 'A prince gives up everything for father...',
                'story': 'Bhishma takes vow of lifelong celibacy so father can marry',
                'cliffhanger': 'This vow leads to...',
                'part': 1
            }
        ]
        
        story = random.choice(stories)
        hook = f"Story time: {story['title']} from Mahabharata"
        story_text = f"{story['setup']}\n\n{story['story']}"
        cliffhanger = f"{story['cliffhanger']}"
        cta = f"Part {story['part'] + 1} tomorrow - follow!"
        
        script = f"{hook}\n\n{story_text}\n\n{cliffhanger}\n\n{cta}"
        
        return {
            'type': 'story_teaser',
            'title': f"{story['title']} - Part {story['part']}",
            'story_title': story['title'],
            'script': script,
            'duration': short_info['duration'],
            'hook': hook,
            'story': story['story'],
            'cliffhanger': story['cliffhanger'],
            'part': story['part'],
            'cta': cta,
            'visuals': [
                'Story scene (AI art)',
                'Suspenseful text animation',
                'Cliffhanger text highlight',
                '"To be continued" graphic'
            ],
            'hashtags': [f"#{story['title'].replace(' ', '')}", '#Mahabharata', '#Storytime', '#Shorts', '#EpicTales'],
            'algorithm_tips': [
                'Create series for binge watching',
                'End with cliffhanger for retention',
                'Schedule part 2 for next day'
            ]
        }
    
    def _generate_wisdom