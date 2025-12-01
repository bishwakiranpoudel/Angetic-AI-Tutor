"""Utility functions for the AI Tutor application."""
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters that might break JSON
    text = text.replace('\x00', '')
    return text

def extract_json(text: str) -> dict:
    """Extract JSON from text, handling code blocks."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*\n?', '', text)
    text = re.sub(r'```\s*\n?', '', text)
    text = text.strip()
    
    # Try to find JSON object
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Try parsing the whole text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}

def calculate_streak(dates: List[str]) -> int:
    """Calculate learning streak from list of date strings."""
    if not dates:
        return 0
    
    try:
        sorted_dates = sorted([datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates], reverse=True)
        streak = 1
        current_date = sorted_dates[0].date()
        
        for date in sorted_dates[1:]:
            date_obj = date.date()
            if (current_date - date_obj).days == 1:
                streak += 1
                current_date = date_obj
            elif (current_date - date_obj).days == 0:
                continue
            else:
                break
        
        return streak
    except Exception:
        return 0

def format_time_ago(dt: datetime) -> str:
    """Format datetime as human-readable time ago."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def generate_id(text: str) -> str:
    """Generate a unique ID from text."""
    return hashlib.md5(text.encode()).hexdigest()[:12]

def validate_student_id(student_id: str) -> bool:
    """Validate student ID format."""
    if not student_id or len(student_id) < 3:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', student_id))

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks for processing."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename[:255]  # Limit length

