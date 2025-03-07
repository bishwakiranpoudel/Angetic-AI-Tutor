import json
from datetime import datetime
from config import MODEL
from database import Database
import re

db = Database("./tutor_memory")

class StudentProgressTracker:
    def __init__(self, student_id):
        self.student_id = student_id
        self.progress = self.get_progress()

    def get_progress(self):
        """Retrieve or initialize student progress."""
        progress_data = db.get_progress(self.student_id)
        if progress_data:
            return progress_data 
        return {
            "student_id": self.student_id,
            "total_questions_asked": 0,
            "topics_covered": {},
            "last_active_date": str(datetime.now()),
            "performance_feedback": {},
            "difficulty_distribution": {"Basic": 0, "Intermediate": 0, "Advanced": 0},
        }



    def classify_topic_and_subtopic(self, user_input):
        """Use AI model to classify the question into a precise topic and subtopic."""
        past_conversation = db.get_conversation(self.student_id) or []
        relevant_interactions = db.retrieve_relevant_interactions(user_input, self.student_id) or []

        # Combine past and relevent
        num_past = min(3, len(past_conversation))
        conversation_history = past_conversation[-num_past:] if past_conversation else []
        conversation_history.extend(relevant_interactions) 

        

        # Prepare context
        formatted_conversation = []
        for entry in conversation_history:
            if "question" in entry and "response" in entry:
                formatted_conversation.append(f"Student: {entry['question']}\nAI Tutor: {entry['response']}")

        context = "\n".join(formatted_conversation)

        prompt = f"""Classify the following question into a specific subject or broader area (topic) and exact field within the subject (subtopic). 
        Return a JSON object with the keys 'topic' and 'subtopic'.The previous conversation context is provided to help with understanding the subject. However, if the new question is about a different topic, classify it separately.
    Context: 
    {context}
    
        
        Example input: "What are the symptoms of diabetes?"
        Example output: {{"topic": "Health", "subtopic": "Diabetes"}}
        
        Example input: "How does a transformer model work?"
        Example output: {{"topic": "Artificial Intelligence", "subtopic": "Deep Learning"}}
        
        Now classify this input:
        "{user_input}"
        
        Ensure the topic and subtopic are as specific as possible.
        """

        try:
            response = MODEL.generate_content(prompt)

            # Debugging: Print the full raw response
            print("Raw model response:", response)

            if not response or not response.candidates:
                raise ValueError("No response from model.")

            # Extract the text content and remove the code block markers
            content = response.candidates[0].content.parts[0].text.strip() if response.candidates[0].content.parts else ""
            
            # Clean the content 
            cleaned_content = re.sub(r'```json\n|\n```', '', content).strip()

            if not cleaned_content:
                raise ValueError("Empty AI response")

            # Debugging: Print cleaned content before parsing JSON
            print("Cleaned content:", cleaned_content)

            classification = json.loads(cleaned_content)

            topic = classification.get("topic", "").strip()
            subtopic = classification.get("subtopic", "").strip()
            
            if not topic or not subtopic:
                raise ValueError("Empty classification result.")

            return topic, subtopic

        except (json.JSONDecodeError, AttributeError, IndexError, ValueError) as e:
            print(f"Error in topic classification: {e} | Input: {user_input}")
            return "General", "General"


    def analyze_difficulty(self, user_input):
        """Classify question difficulty as Basic, Intermediate, or Advanced."""
        
        prompt = f"""Classify the difficulty level of the following question. 
        The difficulty must be one of: "Basic", "Intermediate", or "Advanced".
        
        Example input: "What is 2 + 2?"
        Example output: "Basic"
        
        Example input: "Explain the time complexity of quicksort."
        Example output: "Intermediate"
        
        Example input: "Derive the equations for General Relativity."
        Example output: "Advanced"
        
        Now classify this input:
        "{user_input}"
        
        Strictly return only one of these options: "Basic", "Intermediate", or "Advanced".
        """

        response = MODEL.generate_content(prompt)

        try:
            difficulty = response.candidates[0].content.parts[0].text.strip()
            return difficulty if difficulty in {"Basic", "Intermediate", "Advanced"} else "Basic" 

        except (AttributeError, IndexError) as e:
            print(f"Error in difficulty classification: {e} | Input: {user_input}")
            return "Basic"


    def update_progress(self, topic, subtopic, difficulty):
        """Update student progress based on the latest question asked."""
        valid_difficulties = {"Basic", "Intermediate", "Advanced"}
        difficulty = difficulty if difficulty in valid_difficulties else "Basic"

        self.progress["total_questions_asked"] += 1
        self.progress["last_active_date"] = str(datetime.now())

        if topic not in self.progress["topics_covered"]:
            self.progress["topics_covered"][topic] = []

        if subtopic and subtopic not in self.progress["topics_covered"][topic]:
            self.progress["topics_covered"][topic].append(subtopic)

        self.progress["difficulty_distribution"][difficulty] += 1 

        db.update_progress(self.student_id, self.progress)  
        
        

    def generate_recommendations(self):
        """Generate topic recommendations based on student progress."""
        prompt = f"Suggest 3 topics based on:\n{json.dumps(self.progress)}"
        response = MODEL.generate_content(prompt)

        try:
            return response.candidates[0].content.parts[0].text.strip() if response.candidates else "No recommendations available."
        except (AttributeError, IndexError):
            print(f"Error generating recommendations for student {self.student_id}")
            return "No recommendations available."
