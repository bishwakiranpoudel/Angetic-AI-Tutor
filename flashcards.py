"""Flashcard system with spaced repetition."""
import json
from datetime import datetime, timedelta
from typing import List, Dict
from database import Database
from config import MODEL

db = Database("./tutor_memory")

class FlashcardSystem:
    """Manages flashcards with spaced repetition algorithm."""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.flashcards = self._load_flashcards()
    
    def _load_flashcards(self) -> List[Dict]:
        """Load student's flashcards."""
        try:
            data = db.progress_db.get(ids=[f"{self.student_id}_flashcards"])
            if data and data.get("documents"):
                return json.loads(data["documents"][0])
        except Exception:
            pass
        return []
    
    def _save_flashcards(self):
        """Save flashcards to database."""
        try:
            db.progress_db.upsert(
                documents=[json.dumps(self.flashcards)],
                ids=[f"{self.student_id}_flashcards"]
            )
        except Exception as e:
            print(f"Error saving flashcards: {e}")
    
    def generate_flashcards(self, topic: str, subtopic: str, num_cards: int = 5) -> List[Dict]:
        """Generate flashcards from a topic."""
        system_prompt = """You are an expert at creating educational flashcards. Create clear, concise flashcards that help with memorization."""
        
        prompt = f"""Generate {num_cards} flashcards about {topic} - {subtopic}.

Return JSON array in this format:
[
    {{
        "front": "Question or term",
        "back": "Answer or definition",
        "topic": "{topic}",
        "subtopic": "{subtopic}"
    }}
]

Make the flashcards clear, concise, and educational. Focus on key concepts, definitions, and important facts."""
        
        try:
            response = MODEL.generate_content(prompt, system_prompt=system_prompt)
            if isinstance(response, str):
                from utils import extract_json
                cards_data = extract_json(response)
                if isinstance(cards_data, list):
                    flashcards = []
                    for card_data in cards_data:
                        flashcard = {
                            "id": self._generate_card_id(),
                            "front": card_data.get("front", ""),
                            "back": card_data.get("back", ""),
                            "topic": card_data.get("topic", topic),
                            "subtopic": card_data.get("subtopic", subtopic),
                            "created_at": str(datetime.now()),
                            "next_review": str(datetime.now()),
                            "interval_days": 1,
                            "ease_factor": 2.5,
                            "repetitions": 0,
                            "last_reviewed": None,
                            "mastered": False
                        }
                        flashcards.append(flashcard)
                        self.flashcards.append(flashcard)
                    
                    self._save_flashcards()
                    return flashcards
        except Exception as e:
            print(f"Error generating flashcards: {e}")
        
        return []
    
    def _generate_card_id(self) -> str:
        """Generate unique card ID."""
        from utils import generate_id
        import time
        return generate_id(f"{self.student_id}_{time.time()}")
    
    def get_due_cards(self, limit: int = 10) -> List[Dict]:
        """Get flashcards that are due for review."""
        now = datetime.now()
        due_cards = []
        
        for card in self.flashcards:
            if card.get("mastered", False):
                continue
            
            next_review_str = card.get("next_review")
            if next_review_str:
                try:
                    next_review = datetime.fromisoformat(next_review_str.replace('Z', '+00:00'))
                    if next_review <= now:
                        due_cards.append(card)
                except:
                    due_cards.append(card)
            else:
                due_cards.append(card)
            
            if len(due_cards) >= limit:
                break
        
        return due_cards
    
    def review_card(self, card_id: str, quality: int):
        """
        Review a flashcard using SM-2 spaced repetition algorithm.
        Quality: 0-5 (0=blackout, 1=incorrect, 2=incorrect but remembered, 3=correct with difficulty, 4=correct, 5=perfect)
        """
        card = next((c for c in self.flashcards if c.get("id") == card_id), None)
        if not card:
            return
        
        # SM-2 Algorithm
        ease_factor = card.get("ease_factor", 2.5)
        interval_days = card.get("interval_days", 1)
        repetitions = card.get("repetitions", 0)
        
        # Update ease factor
        ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        if quality < 3:
            # Reset if answer was incorrect
            repetitions = 0
            interval_days = 1
        else:
            # Increase interval
            if repetitions == 0:
                interval_days = 1
            elif repetitions == 1:
                interval_days = 6
            else:
                interval_days = int(interval_days * ease_factor)
            
            repetitions += 1
        
        # Update card
        card["ease_factor"] = ease_factor
        card["interval_days"] = interval_days
        card["repetitions"] = repetitions
        card["last_reviewed"] = str(datetime.now())
        card["next_review"] = str(datetime.now() + timedelta(days=interval_days))
        card["mastered"] = repetitions >= 5 and interval_days >= 30
        
        self._save_flashcards()
    
    def get_statistics(self) -> Dict:
        """Get flashcard statistics."""
        total = len(self.flashcards)
        mastered = sum(1 for c in self.flashcards if c.get("mastered", False))
        due = len(self.get_due_cards(limit=1000))
        
        return {
            "total_cards": total,
            "mastered": mastered,
            "due_for_review": due,
            "in_progress": total - mastered - due,
            "mastery_percentage": (mastered / total * 100) if total > 0 else 0
        }

