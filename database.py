import chromadb
import json
from typing import Optional, List, Dict

class Database:
    def __init__(self, path):
        self.client = chromadb.PersistentClient(path=path)
        self.conversation_db = self.client.get_or_create_collection("student_conversation")
        self.progress_db = self.client.get_or_create_collection("student_progress")
        # Add metadata collection for better organization
        self.metadata_db = self.client.get_or_create_collection("metadata")

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
            # Get all conversations for this student first
            all_data = self.conversation_db.get(ids=[student_id])
            if not all_data or not all_data.get("documents"):
                return []
            
            # Parse conversations
            conversations = json.loads(all_data["documents"][0]) if all_data["documents"] else []
            
            # Simple keyword-based relevance (can be enhanced with embeddings)
            query_lower = query_text.lower()
            relevant = []
            
            for conv in conversations:
                question = conv.get("question", "").lower()
                response = conv.get("response", "").lower()
                # Check if query keywords appear in question or response
                if any(word in question or word in response for word in query_lower.split() if len(word) > 3):
                    relevant.append(conv)
            
            # Return most recent relevant interactions
            return relevant[-num_results:] if len(relevant) > num_results else relevant
            
        except Exception as e:
            print(f"Error retrieving past interactions for {student_id}: {e}")
            return []
    
    def upsert(self, collection_name: str, documents: List[str], ids: List[str], metadatas: Optional[List[Dict]] = None):
        """Generic upsert method for any collection."""
        try:
            collection = getattr(self, collection_name, None)
            if not collection:
                collection = self.client.get_or_create_collection(collection_name)
            
            if metadatas:
                collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
            else:
                collection.upsert(documents=documents, ids=ids)
        except Exception as e:
            print(f"Error in upsert operation: {e}")
