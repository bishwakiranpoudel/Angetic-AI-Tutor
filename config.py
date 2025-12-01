import os 
from dotenv import load_dotenv
import requests
import json

load_dotenv()

# Support multiple AI providers - prioritize free options
AI_PROVIDER = os.getenv("AI_PROVIDER", "huggingface")  # huggingface, ollama, or google

# Hugging Face (Free tier - better models)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-3B-Instruct")  # Free and powerful

# Ollama (Local - completely free)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Google Gemini (fallback)
GENAI_API_KEY = os.getenv("GENAI_API_KEY", "")

CHROMADB_PATH = './tutor_memory'

class AIModel:
    """Unified AI model interface supporting multiple providers."""
    
    def __init__(self):
        self.provider = AI_PROVIDER
        self.setup_model()
    
    def setup_model(self):
        """Initialize the appropriate AI model based on provider."""
        if self.provider == "huggingface" and HUGGINGFACE_API_KEY:
            self.model_type = "huggingface"
        elif self.provider == "ollama":
            self.model_type = "ollama"
        elif GENAI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=GENAI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.model_type = "google"
        else:
            self.model_type = "huggingface"  # Default to Hugging Face
    
    def generate_content(self, prompt, system_prompt=None, max_tokens=2048, temperature=0.7, image_data=None):
        """Generate content using the configured AI provider."""
        if self.model_type == "huggingface":
            return self._huggingface_generate(prompt, system_prompt, max_tokens, temperature, image_data)
        elif self.model_type == "ollama":
            return self._ollama_generate(prompt, system_prompt, max_tokens, temperature, image_data)
        else:
            return self._google_generate(prompt, system_prompt, image_data)
    
    def _huggingface_generate(self, prompt, system_prompt, max_tokens, temperature, image_data=None):
        """Generate using Hugging Face Inference API."""
        try:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # If image is provided, add note to prompt (Hugging Face text models don't support images directly)
            if image_data:
                full_prompt = f"[Note: User has provided an image with their question. Please respond as if you can see the image and describe what might be in it based on the question context.]\n\n{full_prompt}"
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
            else:
                # Fallback to Google if Hugging Face fails
                return self._google_generate(prompt, system_prompt, image_data)
        except Exception as e:
            print(f"Hugging Face error: {e}, falling back to Google")
            return self._google_generate(prompt, system_prompt, image_data)
    
    def _ollama_generate(self, prompt, system_prompt, max_tokens, temperature, image_data=None):
        """Generate using local Ollama."""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # If image is provided, add note to prompt (Ollama text models don't support images directly)
            if image_data:
                full_prompt = f"[Note: User has provided an image with their question. Please respond as if you can see the image and describe what might be in it based on the question context.]\n\n{full_prompt}"
            
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                return self._google_generate(prompt, system_prompt, image_data)
        except Exception as e:
            print(f"Ollama error: {e}, falling back to Google")
            return self._google_generate(prompt, system_prompt, image_data)
    
    def _google_generate(self, prompt, system_prompt, image_data=None):
        """Generate using Google Gemini (supports images)."""
        try:
            import google.generativeai as genai
            if not hasattr(self, 'model'):
                genai.configure(api_key=GENAI_API_KEY)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # If image is provided, send it to Gemini (which supports vision)
            if image_data:
                import base64
                import io
                from PIL import Image
                
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Send both image and text to Gemini
                response = self.model.generate_content([image, full_prompt])
            else:
                # Text only
                response = self.model.generate_content(full_prompt)
            
            return response.candidates[0].content.parts[0].text.strip()
        except Exception as e:
            print(f"Google Gemini error: {e}")
            return "I'm sorry, I couldn't generate a response. Please check your API configuration."

# Create global model instance
MODEL = AIModel()