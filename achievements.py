"""Achievement and badge system for gamification."""
from datetime import datetime
from typing import Dict, List
from database import Database

db = Database("./tutor_memory")

class AchievementSystem:
    """Manages achievements, badges, and gamification elements."""
    
    ACHIEVEMENTS = {
        "first_question": {
            "name": "First Steps",
            "description": "Asked your first question",
            "icon": "🎯",
            "points": 10
        },
        "questions_10": {
            "name": "Curious Mind",
            "description": "Asked 10 questions",
            "icon": "🤔",
            "points": 50
        },
        "questions_50": {
            "name": "Knowledge Seeker",
            "description": "Asked 50 questions",
            "icon": "🔍",
            "points": 100
        },
        "questions_100": {
            "name": "Master Inquirer",
            "description": "Asked 100 questions",
            "icon": "💡",
            "points": 250
        },
        "streak_3": {
            "name": "Getting Started",
            "description": "3-day learning streak",
            "icon": "🔥",
            "points": 30
        },
        "streak_7": {
            "name": "Week Warrior",
            "description": "7-day learning streak",
            "icon": "⚡",
            "points": 100
        },
        "streak_30": {
            "name": "Dedication Master",
            "description": "30-day learning streak",
            "icon": "🌟",
            "points": 500
        },
        "topics_5": {
            "name": "Explorer",
            "description": "Explored 5 different topics",
            "icon": "🗺️",
            "points": 75
        },
        "topics_10": {
            "name": "Renaissance Learner",
            "description": "Explored 10 different topics",
            "icon": "🌍",
            "points": 200
        },
        "advanced_10": {
            "name": "Advanced Scholar",
            "description": "Answered 10 advanced questions",
            "icon": "🎓",
            "points": 150
        },
        "quiz_perfect": {
            "name": "Perfect Score",
            "description": "Got 100% on a quiz",
            "icon": "🏆",
            "points": 100
        },
        "flashcard_master": {
            "name": "Memory Master",
            "description": "Mastered 50 flashcards",
            "icon": "🧠",
            "points": 200
        }
    }
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.achievements_data = self._load_achievements()
    
    def _load_achievements(self) -> Dict:
        """Load student's achievement data."""
        try:
            data = db.progress_db.get(ids=[f"{self.student_id}_achievements"])
            if data and data.get("documents"):
                import json
                return json.loads(data["documents"][0])
        except Exception:
            pass
        
        return {
            "unlocked": [],
            "points": 0,
            "level": 1,
            "badges": []
        }
    
    def _save_achievements(self):
        """Save achievement data."""
        try:
            import json
            db.progress_db.upsert(
                documents=[json.dumps(self.achievements_data)],
                ids=[f"{self.student_id}_achievements"]
            )
        except Exception as e:
            print(f"Error saving achievements: {e}")
    
    def check_achievements(self, progress_data: Dict) -> List[Dict]:
        """Check and unlock new achievements based on progress."""
        newly_unlocked = []
        
        # Check question count achievements
        total_questions = progress_data.get("total_questions_asked", 0)
        if total_questions >= 1 and "first_question" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("first_question"))
        if total_questions >= 10 and "questions_10" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("questions_10"))
        if total_questions >= 50 and "questions_50" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("questions_50"))
        if total_questions >= 100 and "questions_100" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("questions_100"))
        
        # Check topic count achievements
        topics_count = len(progress_data.get("topics_covered", {}))
        if topics_count >= 5 and "topics_5" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("topics_5"))
        if topics_count >= 10 and "topics_10" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("topics_10"))
        
        # Check advanced questions
        advanced_count = progress_data.get("difficulty_distribution", {}).get("Advanced", 0)
        if advanced_count >= 10 and "advanced_10" not in self.achievements_data["unlocked"]:
            newly_unlocked.append(self._unlock("advanced_10"))
        
        # Check streak achievements (would need streak data)
        # This would be calculated from progress_data
        
        return newly_unlocked
    
    def _unlock(self, achievement_id: str) -> Dict:
        """Unlock an achievement."""
        if achievement_id in self.achievements_data["unlocked"]:
            return None
        
        achievement = self.ACHIEVEMENTS.get(achievement_id, {})
        self.achievements_data["unlocked"].append(achievement_id)
        self.achievements_data["points"] += achievement.get("points", 0)
        self.achievements_data["level"] = self._calculate_level(self.achievements_data["points"])
        
        self._save_achievements()
        
        return {
            "id": achievement_id,
            "name": achievement.get("name", ""),
            "description": achievement.get("description", ""),
            "icon": achievement.get("icon", "🏅"),
            "points": achievement.get("points", 0)
        }
    
    def _calculate_level(self, points: int) -> int:
        """Calculate level based on points."""
        # Level 1: 0-99, Level 2: 100-299, etc.
        if points < 100:
            return 1
        elif points < 300:
            return 2
        elif points < 600:
            return 3
        elif points < 1000:
            return 4
        elif points < 1500:
            return 5
        else:
            return 6 + (points - 1500) // 500
    
    def get_all_achievements(self) -> Dict:
        """Get all achievement information."""
        return {
            "unlocked": [
                {
                    "id": ach_id,
                    **self.ACHIEVEMENTS.get(ach_id, {})
                }
                for ach_id in self.achievements_data["unlocked"]
            ],
            "locked": [
                {
                    "id": ach_id,
                    **ach_data
                }
                for ach_id, ach_data in self.ACHIEVEMENTS.items()
                if ach_id not in self.achievements_data["unlocked"]
            ],
            "points": self.achievements_data["points"],
            "level": self.achievements_data["level"]
        }

