import streamlit as st
import json
from tutor import TutorAssistant
from progress_tracker import StudentProgressTracker

def main():
    st.set_page_config(page_title="AI Tutor - Powered by Gemini Flash 1.5", layout="wide")
    st.title("Welcome to AI Tutor - Powered by Gemini Flash 1.5")
    
    # Student ID input
    if 'student_id' not in st.session_state:
        student_id = st.text_input("Enter your student ID:")
        if student_id:
            st.session_state.student_id = student_id
            st.session_state.tutor = TutorAssistant(student_id)
            
            st.session_state.messages = []
            st.rerun()
        else:
            st.stop()
    
    # Chat Interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    prompt = st.chat_input("Ask me a question (or type 'progress' to view progress, 'exit' to quit):")
    
    if prompt:
        if prompt.lower() == "exit":
            st.stop()
        elif prompt.lower() == "progress":
            st.session_state.progress_tracker = StudentProgressTracker(st.session_state.student_id)
            progress = st.session_state.progress_tracker.progress
            recommendations = st.session_state.progress_tracker.generate_recommendations()
            topics_covered = "\n".join(
                [f"- **{subject}:** {', '.join(topics)}" for subject, topics in progress['topics_covered'].items()]
            ).replace("\n", "  \n")

            difficulty_distribution = f"""
            - 🟢 **Basic:** {progress['difficulty_distribution'].get('Basic', 0)}  
            - 🟡 **Intermediate:** {progress['difficulty_distribution'].get('Intermediate', 0)}  
            - 🔴 **Advanced:** {progress['difficulty_distribution'].get('Advanced', 0)}
            """.strip() 

            response = f"""
            ### 📊 **Student Progress Report**  

            **Last Active:** *{progress['last_active_date']}*  

            📌 **Total Questions Asked:** **{progress['total_questions_asked']}**  

            📚 **Topics Covered:**  
            {topics_covered}  

            📈 **Difficulty Distribution:**  
            {difficulty_distribution}  

            📌 **Recommended Topics:**  
            {recommendations}
            """

            st.markdown(response)  # ✅ Fixed formatting


        else:
            response = st.session_state.tutor.tutor_response(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()
