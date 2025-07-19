# Smart Chat Screenshot Extractor Setup

## 📋 File Structure
```
chat_extractor/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── .env.example          # Example environment file
└── README.md             # This file
```

## 🚀 Installation & Setup

### 1. Clone or Create Project Directory
```bash
mkdir chat_extractor
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

### 4. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini
3. Copy the API key

### 5. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your API key
GEMINI_API_KEY=your_actual_api_key_here
```

### 6. Run the Application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 🎯 How to Use

1. **Upload Screenshots**: Select multiple chat screenshots in chronological order
2. **Preview Images**: Review the uploaded images and their processing order
3. **Extract Conversation**: Click the extract button to process with Gemini AI
4. **Download/Copy Results**: Get your structured conversation as text or markdown

## 📁 Supported File Formats
- PNG
- JPG/JPEG

## 🔧 Features

✅ **Smart Image Ordering**: Automatically sorts images by filename
✅ **Thumbnail Previews**: See your uploaded images before processing  
✅ **Real-time Processing**: Live spinner and progress indication
✅ **Multiple Download Options**: TXT and MD formats
✅ **Copy to Clipboard**: One-click copy functionality
✅ **Processing Statistics**: See extraction metrics
✅ **Error Handling**: Comprehensive error messages and validation
✅ **Responsive UI**: Works on desktop and mobile
✅ **Multilingual Support**: Handles mixed languages naturally

## 🛠️ Troubleshooting

### Common Issues:

**"GEMINI_API_KEY not found"**
- Make sure you created the `.env` file
- Check that the API key is correctly added without quotes
- Ensure the file is in the same directory as `app.py`

**"Failed to initialize Gemini model"**
- Verify your API key is valid
- Check your internet connection
- Ensure you have sufficient API quota

**"No valid images found"**
- Check image file formats (PNG, JPG, JPEG only)
- Ensure images aren't corrupted
- Verify file sizes aren't too large

**Images not in correct order**
- Rename files sequentially (e.g., `01_chat.png`, `02_chat.png`)
- Files are sorted alphabetically by filename

## 🔒 Security Notes

- Keep your `.env` file private and never commit it to version control
- Add `.env` to your `.gitignore` file if using Git
- Your API key is only used to call Gemini API and isn't stored anywhere

## 📱 Tips for Best Results

1. **Image Quality**: Ensure text is clearly readable
2. **Complete Messages**: Don't cut off message bubbles
3. **Sequential Naming**: Use numbered filenames for proper order
4. **Good Lighting**: Screenshots should be well-lit and clear
5. **Avoid Overlays**: Remove any screen overlays or notifications

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all requirements are installed
3. Ensure your Gemini API key is valid
4. Check the Streamlit logs for detailed error messages

## 📄 License

This project is open source and available under the MIT License.
