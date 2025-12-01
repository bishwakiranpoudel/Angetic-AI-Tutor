# 🎓 AI Tutor - Advanced Learning Platform

A comprehensive AI-powered tutoring system with advanced features for personalized learning, progress tracking, and interactive exercises.

## ✨ Features

### Core Features
- **Intelligent AI Tutoring**: Powered by multiple AI providers (Hugging Face, Ollama, Google Gemini)
- **Multi-modal Support**: Upload images, PDFs, and documents for context-aware learning
- **Progress Tracking**: Comprehensive tracking of learning progress, topics, and difficulty levels
- **Achievement System**: Gamified learning with badges, points, and levels

### Interactive Learning
- **Exercises & Quizzes**: Generate and solve interactive exercises
- **Flashcards**: Spaced repetition system for effective memorization
- **Study Plans**: Personalized learning paths and schedules
- **Code Execution**: Run and test code (Python support)

### Analytics & Insights
- **Analytics Dashboard**: Detailed learning analytics with visualizations
- **Learning Trends**: Track daily and weekly learning patterns
- **Performance Metrics**: Mastery level, improvement rate, and difficulty analysis
- **Personalized Recommendations**: AI-generated learning suggestions

### Additional Features
- **Export Capabilities**: Export conversations, progress reports, and data
- **Modern UI**: Beautiful, responsive interface with sidebar navigation
- **Voice Support Ready**: Architecture ready for voice input/output
- **Adaptive Learning**: Personalized learning paths based on performance

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Angetic-AI-Tutor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```env
# Choose AI provider: "huggingface", "ollama", or "google"
AI_PROVIDER=huggingface

# Hugging Face (Free tier)
HUGGINGFACE_API_KEY=your_huggingface_api_key
HUGGINGFACE_MODEL=meta-llama/Llama-3.2-3B-Instruct

# Ollama (Local - completely free)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Google Gemini (fallback)
GENAI_API_KEY=your_google_api_key
```

4. Run the application:
```bash
streamlit run main.py
```

## 📖 Usage

### Starting a Session
1. Enter your student ID (or create a new one)
2. Start asking questions in the chat interface
3. Upload images or documents for context-aware help

### Available Commands
- `help` - Show all available commands
- `progress` - View your learning progress
- `analytics` - View detailed analytics
- `exercise [topic]` - Generate an exercise
- `quiz [topic]` - Generate a quiz
- `flashcards [topic]` - Generate flashcards
- `study plan [topic]` - Create a study plan
- `achievements` - View your achievements
- `export` - Export your data

### Navigation
Use the sidebar to navigate between:
- **Chat**: Main tutoring interface
- **Analytics**: Comprehensive analytics dashboard
- **Study Plans**: Create and manage study plans
- **Exercises**: Practice with interactive exercises
- **Flashcards**: Review flashcards with spaced repetition
- **Achievements**: View unlocked achievements
- **Progress**: Detailed progress tracking
- **Export**: Export your data

## 🎯 AI Models Supported

### Hugging Face (Recommended - Free)
- Supports multiple free models
- Default: Llama-3.2-3B-Instruct
- No local installation required

### Ollama (Local - Completely Free)
- Run models locally
- No API keys needed
- Default: llama3.2
- Requires Ollama installation: https://ollama.ai

### Google Gemini (Fallback)
- Requires API key
- Good performance
- Fallback option

## 📁 Project Structure

```
Angetic-AI-Tutor/
├── main.py                 # Main Streamlit application
├── tutor.py                # Core tutoring logic
├── config.py               # AI model configuration
├── database.py              # ChromaDB database operations
├── progress_tracker.py      # Progress tracking system
├── achievements.py          # Achievement and gamification
├── exercises.py             # Exercise and quiz generation
├── flashcards.py            # Flashcard system with spaced repetition
├── study_plans.py           # Study plan generation
├── analytics.py             # Analytics and insights
├── multimodal.py            # Multi-modal processing
├── code_executor.py         # Code execution for programming
├── export.py                # Data export functionality
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### AI Provider Selection
Edit `.env` file to choose your preferred AI provider:
- `AI_PROVIDER=huggingface` - Use Hugging Face (recommended for free tier)
- `AI_PROVIDER=ollama` - Use local Ollama
- Defaults to Google Gemini if others fail

### Database
Data is stored locally in `./tutor_memory/` using ChromaDB. No external database setup required.

## 🎨 Features in Detail

### Multi-modal Learning
- Upload images to ask questions about visual content
- Upload PDFs and documents for context-aware tutoring
- Automatic text extraction and summarization

### Spaced Repetition
- SM-2 algorithm for optimal flashcard review scheduling
- Automatic difficulty adjustment
- Mastery tracking

### Analytics
- Daily and weekly learning trends
- Topic coverage analysis
- Performance metrics and improvement tracking
- Peak learning hours identification

### Gamification
- Achievement system with badges
- Points and leveling system
- Learning streaks
- Progress milestones

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Streamlit
- Powered by ChromaDB for vector storage
- AI models from Hugging Face, Ollama, and Google

## 🐛 Troubleshooting

### Model Not Responding
- Check your API keys in `.env`
- Try switching AI providers
- For Ollama, ensure the service is running: `ollama serve`

### Database Issues
- Delete `./tutor_memory/` folder to reset
- Ensure write permissions in the directory

### Import Errors
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+)

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Happy Learning! 🎓**

