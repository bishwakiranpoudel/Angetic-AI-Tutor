import json
from config import MODEL
from database import Database
from progress_tracker import StudentProgressTracker

db = Database("./tutor_memory")

class TutorAssistant:
    def __init__(self, student_id):
        self.student_id = student_id
        self.progress_tracker = StudentProgressTracker(student_id)

    def tutor_response(self, user_input):
        """Generate a tutor response based on the student's input and progress."""
        topic, subtopic = self.progress_tracker.classify_topic_and_subtopic(user_input)
        difficulty = self.progress_tracker.analyze_difficulty(user_input)
        

        self.progress_tracker.update_progress(topic=topic, subtopic=subtopic, difficulty=difficulty)

        # Retrieve past conversation history
        past_conversation = db.get_conversation(self.student_id) or []
        relevant_interactions = db.retrieve_relevant_interactions(user_input, self.student_id) or []

        # Combine past with relevant
        num_past = min(3, len(past_conversation))
        conversation_history = past_conversation[-num_past:] if past_conversation else []
        conversation_history.extend(relevant_interactions)  # Add relevant interactions

        

        # Prepare context
        formatted_conversation = []
        for entry in conversation_history:
            if "question" in entry and "response" in entry:
                formatted_conversation.append(f"Student: {entry['question']}\nAI Tutor: {entry['response']}")

        context = "\n".join(formatted_conversation)

        prompt = f"{context}\nStudent: {user_input}\nAI Tutor:"
        response = MODEL.generate_content(prompt)

      
        try:
            tutor_reply = response.candidates[0].content.parts[0].text.strip()
        except (AttributeError, IndexError):
            print(f"ERROR: Failed to generate response for input: {user_input}")
            tutor_reply = "I'm sorry, I couldn't generate a response."

        # Update conversation history
        db.store_conversation(self.student_id, {"question": user_input, "response": tutor_reply})

        return tutor_reply
