import streamlit as st
import json
from datetime import datetime
try:
    import plotly.graph_objects as go
except ImportError:
    go = None
from tutor import TutorAssistant
from progress_tracker import StudentProgressTracker
from achievements import AchievementSystem
from exercises import ExerciseGenerator
from flashcards import FlashcardSystem
from study_plans import StudyPlanGenerator
from analytics import AnalyticsDashboard
from multimodal import MultimodalProcessor

# Page configuration
st.set_page_config(
    page_title="AI Tutor - Advanced Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .achievement-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'student_id' not in st.session_state:
        st.session_state.student_id = None
    if 'tutor' not in st.session_state:
        st.session_state.tutor = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Chat"
    if 'exercise_generator' not in st.session_state:
        st.session_state.exercise_generator = None
    if 'flashcard_system' not in st.session_state:
        st.session_state.flashcard_system = None

def login_page():
    """Display login/registration page."""
    st.markdown('<div class="main-header">🎓 AI Tutor - Advanced Learning Platform</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Welcome! 👋")
        st.markdown("Enter your student ID to begin your learning journey.")
        
        student_id = st.text_input(
            "Student ID:",
            placeholder="Enter a unique ID (e.g., student123)",
            key="login_input"
        )
        
        if st.button("Start Learning", type="primary", use_container_width=True):
            if student_id and len(student_id) >= 3:
                from utils import validate_student_id
                if validate_student_id(student_id):
                    st.session_state.student_id = student_id
                    st.session_state.tutor = TutorAssistant(student_id)
                    st.session_state.progress_tracker = StudentProgressTracker(student_id)
                    st.session_state.achievement_system = AchievementSystem(student_id)
                    st.session_state.exercise_generator = ExerciseGenerator(student_id)
                    st.session_state.flashcard_system = FlashcardSystem(student_id)
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Invalid student ID. Use only letters, numbers, hyphens, and underscores.")
            else:
                st.error("Please enter a valid student ID (at least 3 characters).")

def sidebar_navigation():
    """Display sidebar navigation."""
    with st.sidebar:
        st.markdown("## 🎓 Navigation")
        
        pages = {
            "💬 Chat": "Chat",
            "📊 Analytics": "Analytics",
            "📚 Study Plans": "Study Plans",
            "🎯 Exercises": "Exercises",
            "🃏 Flashcards": "Flashcards",
            "🏆 Achievements": "Achievements",
            "📈 Progress": "Progress",
            "📥 Export": "Export"
        }
        
        selected = st.radio("Go to:", list(pages.keys()))
        st.session_state.current_page = pages[selected]
        
        st.markdown("---")
        
        # Student info
        if st.session_state.student_id:
            st.markdown(f"**Student ID:** {st.session_state.student_id}")
            
            # Quick stats
            progress = st.session_state.progress_tracker.progress
            st.metric("Questions Asked", progress.get("total_questions_asked", 0))
            st.metric("Topics Explored", len(progress.get("topics_covered", {})))
            
            # Achievement level
            achievements = st.session_state.achievement_system.get_all_achievements()
            st.metric("Level", achievements["level"])
            st.metric("Points", achievements["points"])
        
        st.markdown("---")
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def chat_page():
    """Main chat interface."""
    st.markdown("## 💬 Chat with Your AI Tutor")
    
    # File uploaders
    col1, col2 = st.columns(2)
    with col1:
        uploaded_image = st.file_uploader("📷 Upload Image", type=["png", "jpg", "jpeg"], help="Ask questions about images!")
    with col2:
        uploaded_doc = st.file_uploader("📄 Upload Document", type=["pdf", "txt", "md"], help="Get help with documents!")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "metadata" in message:
                with st.expander("📊 Question Details"):
                    st.json(message["metadata"])
    
    # Chat input
    prompt = st.chat_input("Ask me anything or type 'help' for commands...")
    
    if prompt or uploaded_image or uploaded_doc:
        # Process the input
        image_file = uploaded_image if uploaded_image else None
        document_file = uploaded_doc if uploaded_doc else None
        document_type = uploaded_doc.type.split('/')[-1] if uploaded_doc else None
        
        if prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Handle special commands
            if prompt.lower() == "help":
                help_text = """
**Available Commands:**
- `progress` - View your learning progress
- `analytics` - View detailed analytics
- `exercise [topic]` - Generate an exercise
- `quiz [topic]` - Generate a quiz
- `flashcards [topic]` - Generate flashcards
- `study plan [topic]` - Create a study plan
- `achievements` - View your achievements
- `export` - Export your data
                """
                st.session_state.messages.append({"role": "assistant", "content": help_text})
            elif prompt.lower() == "progress":
                show_progress_page()
            elif prompt.lower().startswith("exercise"):
                topic = prompt.split("exercise", 1)[1].strip() if len(prompt.split("exercise")) > 1 else "General"
                generate_exercise_interface(topic)
            elif prompt.lower().startswith("quiz"):
                topic = prompt.split("quiz", 1)[1].strip() if len(prompt.split("quiz")) > 1 else "General"
                generate_quiz_interface(topic)
            elif prompt.lower().startswith("flashcards"):
                topic = prompt.split("flashcards", 1)[1].strip() if len(prompt.split("flashcards")) > 1 else "General"
                generate_flashcards_interface(topic)
            elif prompt.lower().startswith("study plan"):
                topic = prompt.split("study plan", 1)[1].strip() if len(prompt.split("study plan")) > 1 else "General"
                create_study_plan_interface(topic)
            elif prompt.lower() == "achievements":
                show_achievements_page()
            elif prompt.lower() == "export":
                show_export_page()
            else:
                # Get tutor response
                with st.spinner("Thinking..."):
                    result = st.session_state.tutor.tutor_response(
                        prompt, 
                        image_file=image_file,
                        document_file=document_file,
                        document_type=document_type
                    )
                    
                    response = result["response"]
                    metadata = {
                        "topic": result.get("topic"),
                        "subtopic": result.get("subtopic"),
                        "difficulty": result.get("difficulty")
                    }
                    
                    # Show new achievements if any
                    new_achievements = result.get("new_achievements", [])
                    if new_achievements:
                        achievement_text = "\n\n🎉 **New Achievement Unlocked!**\n\n"
                        for ach in new_achievements:
                            achievement_text += f"{ach.get('icon', '🏅')} **{ach.get('name', '')}** - {ach.get('description', '')}\n"
                        response = achievement_text + "\n\n" + response
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "metadata": metadata
                    })
        
        st.rerun()

def show_progress_page():
    """Display progress information."""
    progress = st.session_state.progress_tracker.progress
    recommendations = st.session_state.progress_tracker.generate_recommendations()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Questions", progress.get("total_questions_asked", 0))
    with col2:
        st.metric("Topics Covered", len(progress.get("topics_covered", {})))
    with col3:
        st.metric("Last Active", progress.get("last_active_date", "Never")[:10])
    
    st.markdown("### Topics Covered")
    topics_covered = progress.get("topics_covered", {})
    for topic, subtopics in topics_covered.items():
        with st.expander(f"📚 {topic}"):
            st.write(", ".join(subtopics) if subtopics else "No subtopics yet")
    
    st.markdown("### Recommendations")
    st.info(recommendations)

def show_analytics_page():
    """Display comprehensive analytics dashboard."""
    st.markdown("## 📊 Analytics Dashboard")
    
    analytics = AnalyticsDashboard(st.session_state.student_id)
    stats = analytics.get_comprehensive_stats()
    
    # Overview metrics
    overview = stats["overview"]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Questions", overview["total_questions"])
    with col2:
        st.metric("Topics Explored", overview["topics_explored"])
    with col3:
        st.metric("Learning Streak", f"{overview['learning_streak']} days")
    with col4:
        st.metric("Last Active", overview["last_active"])
    
    # Learning trends chart
    st.markdown("### 📈 Learning Trends")
    trends = stats["learning_trends"]
    if trends.get("daily_activity") and len(trends["daily_activity"]) > 0:
        try:
            if go:
                daily_data = trends["daily_activity"]
                dates = [d["date"] for d in daily_data]
                counts = [d["count"] for d in daily_data]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=counts, mode='lines+markers', name='Daily Activity', line=dict(color='#1f77b4')))
                fig.update_layout(
                    title="Daily Learning Activity (Last 30 Days)",
                    xaxis_title="Date",
                    yaxis_title="Questions Asked",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback to simple text display
                daily_data = trends["daily_activity"]
                st.write("Daily Activity (Last 7 Days):")
                for day in daily_data[-7:]:
                    st.write(f"{day['date']}: {day['count']} questions")
        except Exception as e:
            st.info("Chart data available but visualization error occurred.")
    
    # Topic analysis
    st.markdown("### 📚 Topic Analysis")
    topic_analysis = stats["topic_analysis"]
    if topic_analysis.get("topics"):
        for topic_stat in topic_analysis["topics"][:5]:
            st.write(f"**{topic_stat['topic']}** - {topic_stat['questions_count']} questions, {topic_stat['subtopics_count']} subtopics")
    
    # Performance metrics
    st.markdown("### 🎯 Performance Metrics")
    performance = stats["performance_metrics"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Difficulty", performance["average_difficulty"])
    with col2:
        st.metric("Improvement Rate", f"{performance['improvement_rate']}%")
    with col3:
        st.metric("Mastery Level", f"{performance['mastery_level']}%")
    
    # Recommendations
    st.markdown("### 💡 Personalized Recommendations")
    for rec in stats["recommendations"]:
        st.info(rec)

def generate_exercise_interface(topic: str):
    """Interface for generating and solving exercises."""
    st.markdown(f"### 🎯 Exercise: {topic}")
    
    if st.button("Generate New Exercise"):
        with st.spinner("Generating exercise..."):
            exercise = st.session_state.exercise_generator.generate_exercise(
                topic, "General", "Intermediate", "multiple_choice"
            )
            st.session_state.current_exercise = exercise
    
    if "current_exercise" in st.session_state:
        exercise = st.session_state.current_exercise
        st.markdown(f"**Question:** {exercise.get('question', '')}")
        
        if exercise.get("type") == "multiple_choice":
            options = exercise.get("options", [])
            selected = st.radio("Select your answer:", options, key="exercise_answer")
            
            if st.button("Check Answer"):
                result = st.session_state.exercise_generator.check_answer(exercise, options.index(selected))
                if result["correct"]:
                    st.success("✅ Correct! " + result["explanation"])
                else:
                    st.error("❌ Incorrect. " + result["explanation"])

def generate_quiz_interface(topic: str):
    """Interface for taking quizzes."""
    st.markdown(f"### 📝 Quiz: {topic}")
    
    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            quiz = st.session_state.exercise_generator.generate_quiz(topic, 5)
            st.session_state.current_quiz = quiz
            st.session_state.quiz_answers = {}
    
    if "current_quiz" in st.session_state:
        quiz = st.session_state.current_quiz
        for i, question in enumerate(quiz):
            st.markdown(f"**Question {i+1}:** {question.get('question', '')}")
            options = question.get("options", [])
            answer = st.radio(f"Answer {i+1}:", options, key=f"quiz_q{i}")
            st.session_state.quiz_answers[i] = options.index(answer) if answer in options else 0
        
        if st.button("Submit Quiz"):
            score = 0
            for i, question in enumerate(quiz):
                user_answer = st.session_state.quiz_answers.get(i, 0)
                result = st.session_state.exercise_generator.check_answer(question, user_answer)
                if result["correct"]:
                    score += 1
            
            st.success(f"Quiz Complete! Score: {score}/{len(quiz)} ({score/len(quiz)*100:.1f}%)")

def generate_flashcards_interface(topic: str):
    """Interface for flashcards."""
    st.markdown(f"### 🃏 Flashcards: {topic}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate New Flashcards"):
            with st.spinner("Generating flashcards..."):
                cards = st.session_state.flashcard_system.generate_flashcards(topic, "General", 10)
                st.success(f"Generated {len(cards)} flashcards!")
    
    with col2:
        if st.button("Review Due Cards"):
            due_cards = st.session_state.flashcard_system.get_due_cards(10)
            if due_cards:
                st.session_state.current_flashcard = due_cards[0]
                st.session_state.flashcard_index = 0
            else:
                st.info("No cards due for review!")
    
    if "current_flashcard" in st.session_state:
        card = st.session_state.current_flashcard
        st.markdown(f"**Front:** {card.get('front', '')}")
        
        if st.button("Show Answer"):
            st.markdown(f"**Back:** {card.get('back', '')}")
            
            st.markdown("**How well did you know this?**")
            quality = st.slider("Quality (0-5)", 0, 5, 3, key="flashcard_quality")
            
            if st.button("Submit Review"):
                st.session_state.flashcard_system.review_card(card["id"], quality)
                st.success("Card reviewed! Next review scheduled.")
                del st.session_state.current_flashcard
    
    # Statistics
    stats = st.session_state.flashcard_system.get_statistics()
    st.metric("Total Cards", stats["total_cards"])
    st.metric("Mastered", stats["mastered"])
    st.metric("Due for Review", stats["due_for_review"])

def create_study_plan_interface(topic: str):
    """Interface for creating study plans."""
    st.markdown(f"### 📚 Study Plan: {topic}")
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Duration (days)", 1, 30, 7)
    with col2:
        hours_per_day = st.number_input("Hours per day", 0.5, 8.0, 1.0, 0.5)
    
    if st.button("Generate Study Plan"):
        generator = StudyPlanGenerator(st.session_state.student_id)
        with st.spinner("Creating your personalized study plan..."):
            plan = generator.generate_study_plan(topic, duration, hours_per_day)
            st.session_state.current_study_plan = plan
    
    if "current_study_plan" in st.session_state:
        plan = st.session_state.current_study_plan
        st.markdown(f"**Topic:** {plan.get('topic', '')}")
        st.markdown(f"**Duration:** {plan.get('duration_days', 0)} days")
        
        st.markdown("### Daily Plan")
        for day_plan in plan.get("daily_plans", []):
            with st.expander(f"Day {day_plan.get('day', 0)} - {day_plan.get('date', '')}"):
                st.write(f"**Topics:** {', '.join(day_plan.get('topics', []))}")
                st.write(f"**Activities:** {', '.join(day_plan.get('activities', []))}")
                st.write(f"**Estimated Time:** {day_plan.get('estimated_time', 0)} hours")
                
                if st.button(f"Mark Day {day_plan.get('day', 0)} Complete", key=f"complete_{day_plan.get('day', 0)}"):
                    generator = StudyPlanGenerator(st.session_state.student_id)
                    generator.mark_day_complete(plan.get("id", ""), day_plan.get("day", 0))
                    st.success("Day marked as complete!")

def show_achievements_page():
    """Display achievements and badges."""
    st.markdown("## 🏆 Achievements")
    
    achievements = st.session_state.achievement_system.get_all_achievements()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Level", achievements["level"])
    with col2:
        st.metric("Total Points", achievements["points"])
    
    st.markdown("### Unlocked Achievements")
    unlocked = achievements.get("unlocked", [])
    if unlocked:
        cols = st.columns(3)
        for i, ach in enumerate(unlocked):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="achievement-badge">
                    {ach.get('icon', '🏅')} {ach.get('name', '')}
                </div>
                """, unsafe_allow_html=True)
                st.caption(ach.get('description', ''))
    else:
        st.info("No achievements unlocked yet. Keep learning!")
    
    st.markdown("### Locked Achievements")
    locked = achievements.get("locked", [])
    if locked:
        for ach in locked[:5]:  # Show first 5
            st.write(f"🔒 {ach.get('name', '')} - {ach.get('description', '')}")

def show_export_page():
    """Display export options."""
    st.markdown("## 📥 Export Your Data")
    
    exporter = DataExporter(st.session_state.student_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Conversation History")
        export_format = st.selectbox("Format", ["JSON", "TXT"], key="conv_format")
        if st.button("Export Conversations"):
            data = exporter.export_conversation_history(export_format.lower())
            st.download_button(
                label="Download",
                data=data,
                file_name=f"conversations_{st.session_state.student_id}_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
                mime="application/json" if export_format == "JSON" else "text/plain"
            )
    
    with col2:
        st.markdown("### Progress Report")
        report_format = st.selectbox("Format", ["JSON", "TXT"], key="report_format")
        if st.button("Export Report"):
            data = exporter.export_progress_report(report_format.lower())
            st.download_button(
                label="Download",
                data=data,
                file_name=f"progress_report_{st.session_state.student_id}_{datetime.now().strftime('%Y%m%d')}.{report_format.lower()}",
                mime="application/json" if report_format == "JSON" else "text/plain"
            )
    
    if st.button("Export All Data"):
        all_data = exporter.export_all_data()
        data_str = json.dumps(all_data, indent=2)
        st.download_button(
            label="Download All Data",
            data=data_str,
            file_name=f"all_data_{st.session_state.student_id}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

def show_export_page():
    """Display export options."""
    st.markdown("## 📥 Export Your Data")
    
    exporter = DataExporter(st.session_state.student_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Conversation History")
        export_format = st.selectbox("Format", ["JSON", "TXT"], key="conv_format")
        if st.button("Export Conversations"):
            data = exporter.export_conversation_history(export_format.lower())
            st.download_button(
                label="Download",
                data=data,
                file_name=f"conversations_{st.session_state.student_id}_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
                mime="application/json" if export_format == "JSON" else "text/plain"
            )
    
    with col2:
        st.markdown("### Progress Report")
        report_format = st.selectbox("Format", ["JSON", "TXT"], key="report_format")
        if st.button("Export Report"):
            data = exporter.export_progress_report(report_format.lower())
            st.download_button(
                label="Download",
                data=data,
                file_name=f"progress_report_{st.session_state.student_id}_{datetime.now().strftime('%Y%m%d')}.{report_format.lower()}",
                mime="application/json" if report_format == "JSON" else "text/plain"
            )
    
    if st.button("Export All Data"):
        all_data = exporter.export_all_data()
        data_str = json.dumps(all_data, indent=2)
        st.download_button(
            label="Download All Data",
            data=data_str,
            file_name=f"all_data_{st.session_state.student_id}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

def main():
    """Main application entry point."""
    initialize_session_state()
    
    if st.session_state.student_id is None:
        login_page()
    else:
        sidebar_navigation()
        
        # Route to appropriate page
        if st.session_state.current_page == "Chat":
            chat_page()
        elif st.session_state.current_page == "Analytics":
            show_analytics_page()
        elif st.session_state.current_page == "Study Plans":
            create_study_plan_interface("General")
        elif st.session_state.current_page == "Exercises":
            generate_exercise_interface("General")
        elif st.session_state.current_page == "Flashcards":
            generate_flashcards_interface("General")
        elif st.session_state.current_page == "Achievements":
            show_achievements_page()
        elif st.session_state.current_page == "Progress":
            show_progress_page()
        elif st.session_state.current_page == "Export":
            show_export_page()

if __name__ == "__main__":
    main()
