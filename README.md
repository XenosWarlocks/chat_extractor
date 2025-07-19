# Smart Chat Screenshot Extractor Setup

## 📋 File Structure
```
chat_extractor/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env (optional)       # Environment variables (for local development)
├── .env.example          # Example environment file
└── README.md             # This file
```

## 🚀 Installation & Setup

### 1. Clone or Create Project Directory
```bash
git clone https://github.com/XenosWarlocks/chat_extractor/edit/XenosWarlocks-New_Feature-1
cd chat_extractor
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 🔑 API Key Setup

### Option 1: Enter API Key in the App (Recommended for public deployment)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini
3. Enter the API key directly in the app's sidebar
4. Start using the app immediately!

### Option 2: Environment File (For local development)
```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your API key
GEMINI_API_KEY=your_actual_api_key_here
```

## 🎯 How to Use

1. **Enter API Key**: Input your Gemini API key in the sidebar
2. **Upload Screenshots**: Select multiple chat screenshots in chronological order
3. **Preview Images**: Review the uploaded images and their processing order
4. **Extract Conversation**: Click the extract button to process with Gemini AI
5. **Download/Copy Results**: Get your structured conversation as text or markdown

## 📁 Supported File Formats
- PNG
- JPG/JPEG

## 🔧 Features

✅ **Easy API Key Input**: Enter your API key directly in the web interface
✅ **Smart Image Ordering**: Automatically sorts images by filename
✅ **Thumbnail Previews**: See your uploaded images before processing  
✅ **Real-time Processing**: Live spinner and progress indication
✅ **Multiple Download Options**: TXT and MD formats
✅ **Copy to Clipboard**: One-click copy functionality
✅ **Processing Statistics**: See extraction metrics
✅ **Error Handling**: Comprehensive error messages and validation
✅ **Responsive UI**: Works on desktop and mobile
✅ **Multilingual Support**: Handles mixed languages naturally
✅ **Secure**: API keys are never stored permanently

## 🌐 Deployment Options

### Deploy to Streamlit Cloud (Free)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy instantly!

### Deploy to Heroku
```bash
# Add to requirements.txt
echo "streamlit" >> requirements.txt

# Create Procfile
echo "web: sh setup.sh && streamlit run app.py" > Procfile
```

### Deploy to Railway/Render/Vercel
- Most platforms support Streamlit apps out of the box
- Just push your code and they handle the rest!

## 🛠️ Troubleshooting

### Common Issues:

**"API Error: Failed to initialize Gemini model"**
- Verify your API key is valid and correctly entered
- Check your internet connection
- Ensure you have sufficient API quota
- Make sure the API key has the correct permissions

**"API key seems too short"**
- Gemini API keys are typically 39+ characters long
- Make sure you copied the complete key
- Check for extra spaces or hidden characters

**"No valid images found"**
- Check image file formats (PNG, JPG, JPEG only)
- Ensure images aren't corrupted
- Verify file sizes aren't too large (under 10MB recommended)

**Images not in correct order**
- Rename files sequentially (e.g., `01_chat.png`, `02_chat.png`)
- Files are sorted alphabetically by filename

## 🔒 Security & Privacy

- **API keys are never stored**: Your key is only used during the session
- **No server-side storage**: All processing happens in real-time
- **Secure transmission**: All data is encrypted in transit
- **Privacy-first**: Images and conversations are not saved anywhere
- **Open source**: You can audit the code yourself

## 📱 Tips for Best Results

1. **Image Quality**: Ensure text is clearly readable
2. **Complete Messages**: Don't cut off message bubbles
3. **Sequential Naming**: Use numbered filenames for proper order
4. **Good Lighting**: Screenshots should be well-lit and clear
5. **Avoid Overlays**: Remove any screen overlays or notifications

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your API key is correctly entered
3. Ensure all requirements are installed
4. Check the Streamlit logs for detailed error messages

## 📄 License

This project is open source and available under the MIT License.
