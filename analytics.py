"""Advanced analytics and visualization for student progress."""
import json
from datetime import datetime, timedelta
from typing import Dict, List
from database import Database
from utils import calculate_streak, format_time_ago

db = Database("./tutor_memory")

class AnalyticsDashboard:
    """Generate comprehensive analytics and insights."""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics for the student."""
        progress = self._get_progress()
        conversations = self._get_conversations()
        
        # Calculate various metrics
        stats = {
            "overview": self._get_overview_stats(progress, conversations),
            "learning_trends": self._get_learning_trends(conversations),
            "topic_analysis": self._get_topic_analysis(progress, conversations),
            "performance_metrics": self._get_performance_metrics(progress, conversations),
            "time_analysis": self._get_time_analysis(conversations),
            "recommendations": self._generate_recommendations(progress, conversations)
        }
        
        return stats
    
    def _get_progress(self) -> Dict:
        """Get student progress data."""
        try:
            data = db.get_progress(self.student_id)
            return data if data else {}
        except:
            return {}
    
    def _get_conversations(self) -> List[Dict]:
        """Get all conversations."""
        try:
            return db.get_conversation(self.student_id) or []
        except:
            return []
    
    def _get_overview_stats(self, progress: Dict, conversations: List[Dict]) -> Dict:
        """Get overview statistics."""
        total_questions = progress.get("total_questions_asked", 0)
        topics_count = len(progress.get("topics_covered", {}))
        difficulty_dist = progress.get("difficulty_distribution", {})
        
        # Calculate streak
        dates = [conv.get("timestamp", progress.get("last_active_date", "")) for conv in conversations if conv.get("timestamp")]
        streak = calculate_streak(dates) if dates else 0
        
        return {
            "total_questions": total_questions,
            "topics_explored": topics_count,
            "learning_streak": streak,
            "difficulty_distribution": difficulty_dist,
            "last_active": format_time_ago(datetime.fromisoformat(progress.get("last_active_date", str(datetime.now())).replace('Z', '+00:00'))) if progress.get("last_active_date") else "Never"
        }
    
    def _get_learning_trends(self, conversations: List[Dict]) -> Dict:
        """Analyze learning trends over time."""
        if not conversations:
            return {"daily_activity": [], "weekly_activity": []}
        
        # Group by date
        daily_counts = {}
        for conv in conversations:
            try:
                timestamp = conv.get("timestamp", conv.get("date", ""))
                if timestamp:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    daily_counts[date] = daily_counts.get(date, 0) + 1
            except:
                continue
        
        # Get last 30 days
        today = datetime.now().date()
        daily_activity = []
        for i in range(30):
            date = today - timedelta(days=i)
            daily_activity.append({
                "date": str(date),
                "count": daily_counts.get(date, 0)
            })
        
        daily_activity.reverse()
        
        # Weekly aggregation
        weekly_activity = []
        for i in range(4):
            week_start = today - timedelta(days=(i+1)*7)
            week_end = today - timedelta(days=i*7)
            week_count = sum(daily_counts.get(d, 0) for d in daily_counts.keys() if week_start <= d < week_end)
            weekly_activity.append({
                "week": f"Week {i+1}",
                "count": week_count
            })
        
        weekly_activity.reverse()
        
        return {
            "daily_activity": daily_activity,
            "weekly_activity": weekly_activity,
            "trend": "increasing" if len(daily_activity) > 1 and daily_activity[-1]["count"] > daily_activity[0]["count"] else "stable"
        }
    
    def _get_topic_analysis(self, progress: Dict, conversations: List[Dict]) -> Dict:
        """Analyze topic coverage and distribution."""
        topics_covered = progress.get("topics_covered", {})
        
        topic_stats = []
        for topic, subtopics in topics_covered.items():
            # Count questions per topic
            topic_questions = sum(1 for conv in conversations 
                                if conv.get("topic") == topic or topic.lower() in conv.get("question", "").lower())
            
            topic_stats.append({
                "topic": topic,
                "subtopics_count": len(subtopics),
                "questions_count": topic_questions,
                "subtopics": subtopics
            })
        
        # Sort by question count
        topic_stats.sort(key=lambda x: x["questions_count"], reverse=True)
        
        return {
            "topics": topic_stats,
            "most_studied": topic_stats[0]["topic"] if topic_stats else None,
            "total_topics": len(topic_stats)
        }
    
    def _get_performance_metrics(self, progress: Dict, conversations: List[Dict]) -> Dict:
        """Calculate performance metrics."""
        difficulty_dist = progress.get("difficulty_distribution", {})
        total = sum(difficulty_dist.values())
        
        if total == 0:
            return {
                "average_difficulty": "N/A",
                "improvement_rate": 0,
                "mastery_level": 0
            }
        
        # Calculate weighted average difficulty
        weights = {"Basic": 1, "Intermediate": 2, "Advanced": 3}
        weighted_sum = sum(difficulty_dist.get(level, 0) * weights.get(level, 1) for level in weights.keys())
        avg_difficulty_score = weighted_sum / total
        
        # Determine mastery level (0-100)
        mastery = min(100, (avg_difficulty_score / 3) * 100)
        
        return {
            "average_difficulty": "Advanced" if avg_difficulty_score > 2.5 else "Intermediate" if avg_difficulty_score > 1.5 else "Basic",
            "improvement_rate": self._calculate_improvement_rate(conversations),
            "mastery_level": round(mastery, 1)
        }
    
    def _calculate_improvement_rate(self, conversations: List[Dict]) -> float:
        """Calculate improvement rate based on difficulty progression."""
        if len(conversations) < 2:
            return 0.0
        
        # Get difficulty levels over time (if available)
        difficulties = []
        for conv in conversations[-20:]:  # Last 20 conversations
            diff = conv.get("difficulty", "Basic")
            weights = {"Basic": 1, "Intermediate": 2, "Advanced": 3}
            difficulties.append(weights.get(diff, 1))
        
        if len(difficulties) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(difficulties)
        x_mean = n / 2
        y_mean = sum(difficulties) / n
        
        numerator = sum((i - x_mean) * (difficulties[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return round(slope * 100, 1)  # Convert to percentage
    
    def _get_time_analysis(self, conversations: List[Dict]) -> Dict:
        """Analyze time patterns in learning."""
        if not conversations:
            return {"peak_hours": [], "study_pattern": "No data"}
        
        hour_counts = {}
        for conv in conversations:
            try:
                timestamp = conv.get("timestamp", conv.get("date", ""))
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                continue
        
        if not hour_counts:
            return {"peak_hours": [], "study_pattern": "No data"}
        
        # Find peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, count in sorted_hours[:3]]
        
        # Determine study pattern
        morning = sum(hour_counts.get(h, 0) for h in range(6, 12))
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 18))
        evening = sum(hour_counts.get(h, 0) for h in range(18, 24))
        night = sum(hour_counts.get(h, 0) for h in range(0, 6))
        
        max_period = max(morning, afternoon, evening, night)
        if max_period == morning:
            pattern = "Morning Learner"
        elif max_period == afternoon:
            pattern = "Afternoon Learner"
        elif max_period == evening:
            pattern = "Evening Learner"
        else:
            pattern = "Night Owl"
        
        return {
            "peak_hours": peak_hours,
            "study_pattern": pattern,
            "hourly_distribution": hour_counts
        }
    
    def _generate_recommendations(self, progress: Dict, conversations: List[Dict]) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        total_questions = progress.get("total_questions_asked", 0)
        if total_questions < 5:
            recommendations.append("Keep asking questions! You're just getting started.")
        
        difficulty_dist = progress.get("difficulty_distribution", {})
        if difficulty_dist.get("Advanced", 0) == 0 and total_questions > 10:
            recommendations.append("Try exploring more advanced topics to challenge yourself!")
        
        topics_count = len(progress.get("topics_covered", {}))
        if topics_count < 3:
            recommendations.append("Explore different subjects to broaden your knowledge.")
        
        # Check for learning streak
        dates = [conv.get("timestamp", "") for conv in conversations if conv.get("timestamp")]
        streak = calculate_streak(dates)
        if streak < 3:
            recommendations.append("Build a learning streak by studying daily!")
        elif streak >= 7:
            recommendations.append(f"Great job on your {streak}-day streak! Keep it up!")
        
        if not recommendations:
            recommendations.append("You're doing great! Keep up the excellent work!")
        
        return recommendations

