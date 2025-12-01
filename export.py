"""Export functionality for reports and data."""
import json
from datetime import datetime
from typing import Dict, List
from database import Database
from progress_tracker import StudentProgressTracker
from analytics import AnalyticsDashboard

class DataExporter:
    """Export student data and reports."""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.db = Database("./tutor_memory")
        self.progress_tracker = StudentProgressTracker(student_id)
        self.analytics = AnalyticsDashboard(student_id)
    
    def export_conversation_history(self, format: str = "json") -> str:
        """Export conversation history."""
        conversations = self.db.get_conversation(self.student_id) or []
        
        if format.lower() == "json":
            return json.dumps(conversations, indent=2)
        elif format.lower() == "txt":
            lines = []
            lines.append(f"Conversation History for Student: {self.student_id}")
            lines.append(f"Generated: {datetime.now()}")
            lines.append("=" * 80)
            lines.append("")
            
            for i, conv in enumerate(conversations, 1):
                lines.append(f"Conversation {i}")
                lines.append(f"Date: {conv.get('timestamp', 'Unknown')}")
                lines.append(f"Topic: {conv.get('topic', 'General')}")
                lines.append(f"Question: {conv.get('question', '')}")
                lines.append(f"Answer: {conv.get('response', '')}")
                lines.append("-" * 80)
                lines.append("")
            
            return "\n".join(lines)
        else:
            return json.dumps(conversations, indent=2)
    
    def export_progress_report(self, format: str = "json") -> str:
        """Export comprehensive progress report."""
        progress = self.progress_tracker.progress
        stats = self.analytics.get_comprehensive_stats()
        
        report = {
            "student_id": self.student_id,
            "generated_at": str(datetime.now()),
            "progress": progress,
            "analytics": stats,
            "summary": {
                "total_questions": progress.get("total_questions_asked", 0),
                "topics_covered": len(progress.get("topics_covered", {})),
                "learning_streak": stats["overview"].get("learning_streak", 0),
                "mastery_level": stats["performance_metrics"].get("mastery_level", 0)
            }
        }
        
        if format.lower() == "json":
            return json.dumps(report, indent=2)
        elif format.lower() == "txt":
            lines = []
            lines.append("=" * 80)
            lines.append(f"PROGRESS REPORT - {self.student_id}")
            lines.append(f"Generated: {datetime.now()}")
            lines.append("=" * 80)
            lines.append("")
            
            summary = report["summary"]
            lines.append("SUMMARY")
            lines.append("-" * 80)
            lines.append(f"Total Questions Asked: {summary['total_questions']}")
            lines.append(f"Topics Explored: {summary['topics_covered']}")
            lines.append(f"Learning Streak: {summary['learning_streak']} days")
            lines.append(f"Mastery Level: {summary['mastery_level']}%")
            lines.append("")
            
            lines.append("TOPICS COVERED")
            lines.append("-" * 80)
            topics = progress.get("topics_covered", {})
            for topic, subtopics in topics.items():
                lines.append(f"{topic}: {', '.join(subtopics) if subtopics else 'None'}")
            lines.append("")
            
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 80)
            for rec in stats.get("recommendations", []):
                lines.append(f"- {rec}")
            
            return "\n".join(lines)
        else:
            return json.dumps(report, indent=2)
    
    def export_all_data(self) -> Dict:
        """Export all student data."""
        return {
            "student_id": self.student_id,
            "exported_at": str(datetime.now()),
            "conversations": self.db.get_conversation(self.student_id) or [],
            "progress": self.progress_tracker.progress,
            "analytics": self.analytics.get_comprehensive_stats()
        }

