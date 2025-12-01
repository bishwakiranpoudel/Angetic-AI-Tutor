"""Multi-modal support for images, documents, and video."""
import base64
import io
from typing import Optional, Dict, Any
from PIL import Image
import PyPDF2
from config import MODEL

class MultimodalProcessor:
    """Process images, documents, PDFs, and video for the AI tutor."""
    
    @staticmethod
    def process_image(image_file) -> Optional[str]:
        """Process and encode image for AI model."""
        try:
            if isinstance(image_file, bytes):
                image = Image.open(io.BytesIO(image_file))
            else:
                image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 1024px on longest side)
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return img_str
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """Extract text from PDF file."""
        try:
            if isinstance(pdf_file, bytes):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            else:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_document(file, file_type: str) -> str:
        """Extract text from various document types."""
        if file_type == "pdf":
            return MultimodalProcessor.extract_text_from_pdf(file)
        elif file_type in ["txt", "md"]:
            try:
                if isinstance(file, bytes):
                    return file.decode('utf-8')
                else:
                    return file.read().decode('utf-8')
            except Exception as e:
                print(f"Error reading text file: {e}")
                return ""
        else:
            return ""
    
    @staticmethod
    def analyze_with_context(text: str, image_data: Optional[str] = None, 
                            document_text: Optional[str] = None) -> str:
        """Analyze user query with image/document context."""
        context_parts = []
        
        if document_text:
            # Summarize document if too long
            if len(document_text) > 2000:
                summary_prompt = f"Summarize the key points from this document:\n\n{document_text[:2000]}..."
                try:
                    summary = MODEL.generate_content(summary_prompt)
                    if isinstance(summary, str):
                        document_text = summary
                except:
                    document_text = document_text[:2000] + "..."
            
            context_parts.append(f"Document context:\n{document_text}")
        
        if image_data:
            context_parts.append("The user has provided an image related to their question.")
        
        context = "\n\n".join(context_parts)
        
        if context:
            enhanced_prompt = f"{context}\n\nUser question: {text}\n\nPlease provide a helpful answer considering the context provided."
        else:
            enhanced_prompt = text
        
        try:
            response = MODEL.generate_content(enhanced_prompt)
            if isinstance(response, str):
                return response
            return str(response)
        except Exception as e:
            print(f"Error in multimodal analysis: {e}")
            return "I'm sorry, I couldn't process your request with the provided context."

