# 📷📄 Image and Document Upload Guide

## How It Works

### ✅ **Documents (PDF, TXT, MD) - FULLY WORKING**

**How it works:**
1. **Upload**: User uploads a PDF, TXT, or Markdown file via the file uploader
2. **Text Extraction**: 
   - PDFs: Text is extracted from all pages using PyPDF2
   - TXT/MD: Text is read directly from the file
3. **Processing**:
   - If document is >2000 characters, it's automatically summarized first
   - Document text is included in the prompt context
4. **AI Response**: The AI tutor can answer questions about the document content

**Example Usage:**
```
1. Upload a PDF document about "Machine Learning"
2. Ask: "What are the main concepts in this document?"
3. AI will analyze the document and provide answers based on its content
```

**Supported Formats:**
- ✅ PDF (.pdf)
- ✅ Text files (.txt)
- ✅ Markdown (.md)

---

### 🖼️ **Images (PNG, JPG, JPEG) - ENHANCED**

**How it works:**
1. **Upload**: User uploads an image via the file uploader
2. **Processing**:
   - Image is converted to RGB format
   - Resized if too large (max 1024px)
   - Converted to base64 encoding
3. **AI Model Support**:
   - **Google Gemini**: ✅ **FULL VISION SUPPORT** - Images are actually sent to the model
   - **Hugging Face/Ollama**: ⚠️ **Limited** - Text-only models, image context is described in prompt

**Example Usage:**
```
1. Upload an image of a math problem
2. Ask: "Can you solve this problem?"
3. AI will analyze the image and provide the solution
```

**Best Results:**
- Works best with **Google Gemini** (supports vision)
- For other providers, the AI will try to help based on your question context

**Supported Formats:**
- ✅ PNG (.png)
- ✅ JPEG (.jpg, .jpeg)

---

## Technical Details

### Document Processing Flow
```
Upload Document → Extract Text → Summarize (if needed) → Include in Prompt → AI Response
```

### Image Processing Flow (Google Gemini)
```
Upload Image → Process & Encode → Send to Gemini Vision API → AI Response
```

### Image Processing Flow (Other Providers)
```
Upload Image → Process & Encode → Add Context Note → AI Response (text-based)
```

---

## Usage Tips

### For Documents:
1. ✅ Upload PDFs, text files, or markdown documents
2. ✅ Ask specific questions about the content
3. ✅ The AI can summarize, explain, or answer questions about the document
4. ⚠️ Very long documents (>2000 chars) are automatically summarized first

### For Images:
1. ✅ Upload clear, readable images
2. ✅ Works best with Google Gemini provider
3. ✅ Ask specific questions about what's in the image
4. ✅ Good for: math problems, diagrams, charts, code screenshots, etc.

---

## Current Limitations

1. **Image Support**:
   - Full vision only with Google Gemini
   - Other providers use text-based context

2. **Document Size**:
   - Very long documents are summarized
   - Maximum practical size depends on model context window

3. **File Types**:
   - Images: PNG, JPG, JPEG only
   - Documents: PDF, TXT, MD only

---

## How to Use

### Step 1: Upload Files
- Use the file uploaders in the chat interface
- Upload image OR document (or both)

### Step 2: Ask Questions
- Type your question in the chat
- Reference the uploaded content in your question
- Example: "What does this image show?" or "Summarize this document"

### Step 3: Get Answers
- AI will analyze the uploaded content
- Provide answers based on the image/document context

---

## Example Scenarios

### Scenario 1: Math Problem
```
1. Upload image of a math equation
2. Ask: "Solve this equation step by step"
3. AI analyzes image and provides solution
```

### Scenario 2: Document Analysis
```
1. Upload a research paper PDF
2. Ask: "What are the key findings?"
3. AI extracts and summarizes the main points
```

### Scenario 3: Code Help
```
1. Upload screenshot of code
2. Ask: "What does this code do?"
3. AI analyzes the code and explains it
```

---

## Troubleshooting

**Images not working?**
- Check if using Google Gemini (best support)
- Ensure image is clear and readable
- Try re-uploading the image

**Documents not processing?**
- Check file format (PDF, TXT, MD only)
- Ensure file is not corrupted
- Try a smaller document first

**AI not understanding content?**
- Be specific in your questions
- Reference what you want to know about
- For images, describe what you're asking about

---

**Note**: For best image results, use Google Gemini as your AI provider in the `.env` file.

