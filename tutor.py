import json
from datetime import datetime
from typing import Optional, Dict, Any
from config import MODEL
from database import Database
from progress_tracker import StudentProgressTracker
from achievements import AchievementSystem
from multimodal import MultimodalProcessor

db = Database("./tutor_memory")

class TutorAssistant:
    def __init__(self, student_id):
        self.student_id = student_id
        self.progress_tracker = StudentProgressTracker(student_id)
        self.achievement_system = AchievementSystem(student_id)
        self.multimodal_processor = MultimodalProcessor()

    def tutor_response(self, user_input: str, image_file=None, document_file=None, document_type: str = None) -> Dict:
        """Generate a tutor response based on the student's input and progress."""
        # Process multimodal inputs
        image_data = None
        document_text = None
        
        if image_file:
            image_data = self.multimodal_processor.process_image(image_file)
        
        if document_file:
            document_text = self.multimodal_processor.extract_text_from_document(document_file, document_type or "txt")
        
        # Classify topic and difficulty
        topic, subtopic = self.progress_tracker.classify_topic_and_subtopic(user_input)
        difficulty = self.progress_tracker.analyze_difficulty(user_input)
        
        # Update progress
        self.progress_tracker.update_progress(topic=topic, subtopic=subtopic, difficulty=difficulty)
        
        # Check for new achievements
        progress_data = self.progress_tracker.progress
        new_achievements = self.achievement_system.check_achievements(progress_data)
        
        # Retrieve past conversation history
        past_conversation = db.get_conversation(self.student_id) or []
        relevant_interactions = db.retrieve_relevant_interactions(user_input, self.student_id) or []

        # Combine past with relevant
        num_past = min(5, len(past_conversation))
        conversation_history = past_conversation[-num_past:] if past_conversation else []
        conversation_history.extend(relevant_interactions[:3])  # Limit relevant interactions

        # Prepare context with progress information
        progress_summary = f"""
Student Progress Summary:
- Total Questions: {progress_data.get('total_questions_asked', 0)}
- Topics Covered: {len(progress_data.get('topics_covered', {}))}
- Current Topic: {topic} - {subtopic}
- Difficulty Level: {difficulty}
"""
        
        # Prepare conversation context
        formatted_conversation = []
        for entry in conversation_history:
            if isinstance(entry, dict):
                if "question" in entry and "response" in entry:
                    formatted_conversation.append(f"Student: {entry['question']}\nAI Tutor: {entry['response']}")
                elif "user" in entry and "assistant" in entry:
                    formatted_conversation.append(f"Student: {entry['user']}\nAI Tutor: {entry['assistant']}")

        context = "\n".join(formatted_conversation[-3:])  # Last 3 conversations
        
        # Enhanced system prompt
        system_prompt = """You are an expert AI tutor. Your role is to:
1. Provide clear, educational explanations
2. Adapt to the student's level and learning style
3. Encourage critical thinking
4. Use examples and analogies when helpful
5. Ask follow-up questions to deepen understanding
6. Be patient, supportive, and encouraging

Keep responses concise but comprehensive. If the student provides images or documents, reference them in your response."""
        
        # Build enhanced prompt
        if image_data or document_text:
            enhanced_input = self.multimodal_processor.analyze_with_context(
                user_input, image_data, document_text
            )
        else:
            enhanced_input = user_input
        
        prompt = f"""{progress_summary}

Previous conversation context:
{context}

Student: {enhanced_input}
AI Tutor:"""
        
        try:
            response = MODEL.generate_content(prompt, system_prompt=system_prompt)
            
            if isinstance(response, str):
                tutor_reply = response
            else:
                # Handle different response formats
                tutor_reply = str(response)
            
            tutor_reply = tutor_reply.strip()
        except Exception as e:
            print(f"ERROR: Failed to generate response for input: {user_input}: {e}")
            tutor_reply = "I'm sorry, I couldn't generate a response. Please try rephrasing your question."

        # Store conversation with metadata
        conversation_entry = {
            "question": user_input,
            "response": tutor_reply,
            "topic": topic,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "timestamp": str(datetime.now()),
            "has_image": image_data is not None,
            "has_document": document_text is not None
        }
        
        db.store_conversation(self.student_id, conversation_entry)

        return {
            "response": tutor_reply,
            "topic": topic,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "new_achievements": new_achievements
        }
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversations."""
        conversations = db.get_conversation(self.student_id) or []
        if not conversations:
            return "No conversations yet. Start asking questions!"
        
        recent = conversations[-5:]
        summary_parts = [f"Recent topics: {', '.join(set(c.get('topic', 'General') for c in recent))}"]
        
        return "\n".join(summary_parts)
