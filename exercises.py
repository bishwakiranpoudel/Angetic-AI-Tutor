"""Interactive exercises and quiz system."""
import json
import random
from typing import List, Dict, Any
from config import MODEL
from database import Database

db = Database("./tutor_memory")

class ExerciseGenerator:
    """Generate interactive exercises, quizzes, and practice problems."""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
    
    def generate_exercise(self, topic: str, subtopic: str, difficulty: str, exercise_type: str = "multiple_choice") -> Dict:
        """Generate an exercise based on topic and difficulty."""
        system_prompt = """You are an expert educational content creator. Generate engaging, educational exercises that help students learn effectively."""
        
        prompt = f"""Create a {exercise_type} exercise about {topic} - {subtopic} at {difficulty} difficulty level.

For multiple choice questions, return JSON in this format:
{{
    "question": "The question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": 0,
    "explanation": "Why this answer is correct",
    "hints": ["hint1", "hint2"]
}}

For coding exercises, return:
{{
    "question": "The problem description",
    "starter_code": "def function_name():\n    # Your code here",
    "test_cases": [{{"input": "...", "expected_output": "..."}}],
    "hints": ["hint1", "hint2"],
    "solution": "The complete solution code"
}}

For short answer questions, return:
{{
    "question": "The question text",
    "expected_keywords": ["keyword1", "keyword2"],
    "explanation": "Detailed explanation",
    "hints": ["hint1", "hint2"]
}}

Now generate a {exercise_type} exercise about {topic} - {subtopic} at {difficulty} level:"""
        
        try:
            response = MODEL.generate_content(prompt, system_prompt=system_prompt)
            if isinstance(response, str):
                from utils import extract_json
                exercise = extract_json(response)
                exercise["type"] = exercise_type
                exercise["topic"] = topic
                exercise["subtopic"] = subtopic
                exercise["difficulty"] = difficulty
                return exercise
        except Exception as e:
            print(f"Error generating exercise: {e}")
        
        return self._get_default_exercise(topic, subtopic, difficulty, exercise_type)
    
    def _get_default_exercise(self, topic: str, subtopic: str, difficulty: str, exercise_type: str) -> Dict:
        """Return a default exercise if generation fails."""
        return {
            "type": exercise_type,
            "question": f"Explain {subtopic} in {topic}.",
            "topic": topic,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "This is a placeholder exercise."
        }
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> List[Dict]:
        """Generate a quiz with multiple questions."""
        quiz = []
        for i in range(num_questions):
            exercise = self.generate_exercise(topic, "General", "Intermediate", "multiple_choice")
            exercise["question_number"] = i + 1
            quiz.append(exercise)
        return quiz
    
    def check_answer(self, exercise: Dict, user_answer: Any) -> Dict:
        """Check if user's answer is correct."""
        exercise_type = exercise.get("type", "multiple_choice")
        
        if exercise_type == "multiple_choice":
            correct = user_answer == exercise.get("correct_answer")
        elif exercise_type == "short_answer":
            # Check if answer contains expected keywords
            answer_lower = str(user_answer).lower()
            expected = [kw.lower() for kw in exercise.get("expected_keywords", [])]
            correct = any(kw in answer_lower for kw in expected)
        elif exercise_type == "coding":
            # For coding, would need to execute code (implemented separately)
            correct = False  # Placeholder
        else:
            correct = False
        
        result = {
            "correct": correct,
            "explanation": exercise.get("explanation", ""),
            "user_answer": user_answer,
            "correct_answer": exercise.get("correct_answer") if exercise_type == "multiple_choice" else exercise.get("expected_keywords", [])
        }
        
        # Save quiz attempt
        self._save_quiz_attempt(exercise, user_answer, correct)
        
        return result
    
    def _save_quiz_attempt(self, exercise: Dict, user_answer: Any, correct: bool):
        """Save quiz attempt for progress tracking."""
        try:
            attempt = {
                "exercise": exercise,
                "user_answer": user_answer,
                "correct": correct,
                "timestamp": str(datetime.now())
            }
            
            # Get existing attempts
            try:
                data = db.progress_db.get(ids=[f"{self.student_id}_quiz_attempts"])
                attempts = json.loads(data["documents"][0]) if data and data.get("documents") else []
            except Exception:
                attempts = []
            
            attempts.append(attempt)
            
            # Keep only last 100 attempts
            if len(attempts) > 100:
                attempts = attempts[-100:]
            
            db.progress_db.upsert(
                documents=[json.dumps(attempts)],
                ids=[f"{self.student_id}_quiz_attempts"]
            )
        except Exception as e:
            print(f"Error saving quiz attempt: {e}")

from datetime import datetime

