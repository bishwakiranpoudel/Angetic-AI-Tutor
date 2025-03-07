import chromadb
import json

class Database:
    def __init__(self, path):
        self.client = chromadb.PersistentClient(path=path)
        self.conversation_db = self.client.get_or_create_collection("student_conversation")
        self.progress_db = self.client.get_or_create_collection("student_progress")

    def get_progress(self, student_id):
        """Retrieve stored progress data for a student."""
        try:
            data = self.progress_db.get(ids=[student_id])
            
            return json.loads(data["documents"][0]) if data and data.get("documents") else None
        except Exception as e:
            print(f"Error retrieving progress for {student_id}: {e}")
            return None

    def update_progress(self, student_id, progress_data):
        """Update or add student progress."""
        
        try:
            existing_data = self.get_progress(student_id)
            if existing_data:
                self.progress_db.update(documents=[json.dumps(progress_data)], ids=[student_id])
                print(f"Updated progress for student {student_id}")
            else:
                self.progress_db.add(documents=[json.dumps(progress_data)], ids=[student_id])
                print(f"Added new progress entry for student {student_id}")
        except Exception as e:
            print(f"Error updating progress for {student_id}: {e}")

    def store_conversation(self, student_id, conversation_history):
        """Store conversation history, appending new interactions."""
        try:
            existing_conversations = self.get_conversation(student_id)

            if existing_conversations:
                existing_conversations.append(conversation_history)
                self.conversation_db.update(documents=[json.dumps(existing_conversations)], ids=[student_id])
                print(f"Updated conversation history for student {student_id}")
            else:
                self.conversation_db.add(documents=[json.dumps([conversation_history])], ids=[student_id])
                print(f"Added new conversation entry for student {student_id}")
        except Exception as e:
            print(f"Error storing conversation for {student_id}: {e}")

    def get_conversation(self, student_id):
        """Retrieve stored conversation history."""
        try:
            data = self.conversation_db.get(ids=[student_id])
            return json.loads(data["documents"][0]) if data and data.get("documents") else []
        except Exception as e:
            print(f"Error retrieving conversation history for {student_id}: {e}")
            return []

    def retrieve_relevant_interactions(self, query_text, student_id, num_results=3):
        """Retrieve relevant past interactions specific to the student."""
        try:
            result = self.conversation_db.query(query_texts=[query_text], n_results=num_results)

            # return only related to student 
            interactions = []
            for docs, ids in zip(result.get("documents", [[]]), result.get("ids", [[]])):
                for doc, doc_id in zip(docs, ids):
                    if doc and doc_id == student_id:
                        interactions.append(json.loads(doc))

            return interactions
        except Exception as e:
            print(f"Error retrieving past interactions for {student_id}: {e}")
            return []
