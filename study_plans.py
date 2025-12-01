"""Study plans and learning path generation."""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import MODEL
from database import Database

db = Database("./tutor_memory")

class StudyPlanGenerator:
    """Generate personalized study plans and learning paths."""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
    
    def generate_study_plan(self, topic: str, duration_days: int = 7, hours_per_day: float = 1.0) -> Dict:
        """Generate a personalized study plan for a topic."""
        system_prompt = """You are an expert educational planner. Create structured, achievable study plans that help students learn effectively."""
        
        prompt = f"""Create a {duration_days}-day study plan for learning {topic}.

The student can study for approximately {hours_per_day} hours per day.

Return JSON in this format:
{{
    "topic": "{topic}",
    "duration_days": {duration_days},
    "hours_per_day": {hours_per_day},
    "daily_plans": [
        {{
            "day": 1,
            "date": "YYYY-MM-DD",
            "topics": ["topic1", "topic2"],
            "activities": ["activity1", "activity2"],
            "estimated_time": 1.0,
            "resources": ["resource1", "resource2"]
        }}
    ],
    "learning_objectives": ["objective1", "objective2"],
    "milestones": ["milestone1", "milestone2"]
}}

Make the plan progressive, starting with basics and building to advanced concepts."""
        
        try:
            response = MODEL.generate_content(prompt, system_prompt=system_prompt)
            if isinstance(response, str):
                from utils import extract_json
                plan = extract_json(response)
                
                # Add dates
                start_date = datetime.now()
                if "daily_plans" in plan:
                    for i, day_plan in enumerate(plan["daily_plans"]):
                        day_plan["date"] = str((start_date + timedelta(days=i)).date())
                
                plan["created_at"] = str(datetime.now())
                plan["student_id"] = self.student_id
                plan["completed_days"] = []
                plan["progress"] = 0.0
                
                # Save plan
                self._save_study_plan(plan)
                
                return plan
        except Exception as e:
            print(f"Error generating study plan: {e}")
        
        return self._get_default_plan(topic, duration_days, hours_per_day)
    
    def _get_default_plan(self, topic: str, duration_days: int, hours_per_day: float) -> Dict:
        """Return a default study plan."""
        start_date = datetime.now()
        daily_plans = []
        
        for i in range(duration_days):
            daily_plans.append({
                "day": i + 1,
                "date": str((start_date + timedelta(days=i)).date()),
                "topics": [f"{topic} - Day {i+1}"],
                "activities": ["Study", "Practice", "Review"],
                "estimated_time": hours_per_day,
                "resources": []
            })
        
        return {
            "topic": topic,
            "duration_days": duration_days,
            "hours_per_day": hours_per_day,
            "daily_plans": daily_plans,
            "learning_objectives": [f"Learn {topic}"],
            "milestones": ["Complete study plan"],
            "created_at": str(datetime.now()),
            "student_id": self.student_id,
            "completed_days": [],
            "progress": 0.0
        }
    
    def _save_study_plan(self, plan: Dict):
        """Save study plan to database."""
        try:
            plans = self._load_all_plans()
            plan_id = plan.get("id", f"{self.student_id}_{datetime.now().timestamp()}")
            plan["id"] = plan_id
            plans[plan_id] = plan
            
            db.progress_db.upsert(
                documents=[json.dumps(plans)],
                ids=[f"{self.student_id}_study_plans"]
            )
        except Exception as e:
            print(f"Error saving study plan: {e}")
    
    def _load_all_plans(self) -> Dict:
        """Load all study plans for student."""
        try:
            data = db.progress_db.get(ids=[f"{self.student_id}_study_plans"])
            if data and data.get("documents"):
                return json.loads(data["documents"][0])
        except Exception:
            pass
        return {}
    
    def get_active_plans(self) -> List[Dict]:
        """Get all active study plans."""
        plans = self._load_all_plans()
        active = []
        
        for plan_id, plan in plans.items():
            if plan.get("progress", 0) < 1.0:
                active.append(plan)
        
        return sorted(active, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def mark_day_complete(self, plan_id: str, day: int):
        """Mark a day as complete in a study plan."""
        plans = self._load_all_plans()
        if plan_id in plans:
            plan = plans[plan_id]
            completed = plan.get("completed_days", [])
            if day not in completed:
                completed.append(day)
                plan["completed_days"] = completed
                plan["progress"] = len(completed) / plan.get("duration_days", 1)
                self._save_study_plan(plan)

