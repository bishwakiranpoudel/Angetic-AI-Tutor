import os 
from dotenv import load_dotenv
import google.generativeai as genai 

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")

genai.configure(api_key=GENAI_API_KEY)
MODEL = genai.GenerativeModel("gemini-1.5-flash")

CHROMADB_PATH = './tutor_memory'