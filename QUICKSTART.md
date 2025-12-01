# 🚀 Quick Start Guide

## Installation Steps

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your API keys (at least one provider)

3. **Choose Your AI Provider**

   **Option A: Hugging Face (Recommended - Free)**
   - Get API key from: https://huggingface.co/settings/tokens
   - Set in `.env`:
     ```
     AI_PROVIDER=huggingface
     HUGGINGFACE_API_KEY=your_key_here
     ```

   **Option B: Ollama (Local - Completely Free)**
   - Install from: https://ollama.ai
   - Run: `ollama pull llama3.2`
   - Set in `.env`:
     ```
     AI_PROVIDER=ollama
     ```

   **Option C: Google Gemini (Fallback)**
   - Get API key from: https://makersuite.google.com/app/apikey
   - Set in `.env`:
     ```
     AI_PROVIDER=google
     GENAI_API_KEY=your_key_here
     ```

4. **Run the Application**
   ```bash
   streamlit run main.py
   ```

5. **Start Learning!**
   - Enter a student ID
   - Start asking questions
   - Explore all the features!

## Features Overview

### 💬 Chat Interface
- Ask any question
- Upload images for visual questions
- Upload PDFs/documents for context

### 📊 Analytics
- View learning trends
- Track progress over time
- See performance metrics

### 🎯 Exercises
- Generate practice problems
- Take quizzes
- Get instant feedback

### 🃏 Flashcards
- Create flashcards from topics
- Spaced repetition system
- Track mastery

### 📚 Study Plans
- Personalized learning paths
- Daily study schedules
- Progress tracking

### 🏆 Achievements
- Unlock badges
- Earn points
- Level up

### 📥 Export
- Download conversation history
- Export progress reports
- Save all your data

## Tips

1. **Use Commands**: Type `help` in chat to see all commands
2. **Track Progress**: Check Analytics regularly
3. **Practice**: Use Exercises and Flashcards for active learning
4. **Stay Consistent**: Build a learning streak!
5. **Explore**: Try different topics and features

## Troubleshooting

**Model not responding?**
- Check your API keys
- Try a different provider
- For Ollama, ensure it's running: `ollama serve`

**Import errors?**
- Run: `pip install -r requirements.txt`
- Check Python version (3.8+)

**Database issues?**
- Delete `./tutor_memory/` to reset
- Ensure write permissions

## Next Steps

- Explore all features
- Create study plans
- Build your learning streak
- Unlock achievements
- Export your progress

Happy Learning! 🎓

