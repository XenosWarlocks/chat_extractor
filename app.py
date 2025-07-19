import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
import time
from typing import List, Optional, Tuple, Dict, Any
import base64

# Load environment variables for backward compatibility (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, which is fine for UI-based API key input
    pass

# Configure Streamlit page
st.set_page_config(
    page_title="Smart Chat Screenshot Extractor",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ChatExtractor:
    def __init__(self, api_key: str):
        """Initialize the ChatExtractor with Gemini API configuration."""
        self.api_key = api_key
        
        if not self.api_key or self.api_key.strip() == "":
            raise ValueError("API key cannot be empty")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini model: {str(e)}")
    
    def prepare_images(self, uploaded_files: List) -> Tuple[List[Image.Image], List[Dict[str, Any]]]:
        """
        Convert uploaded files to PIL Images and sort them by filename.
        
        Args:
            uploaded_files: List of uploaded file objects from Streamlit
            
        Returns:
            Tuple of (List of PIL Image objects sorted by filename, List of file data dicts)
        """
        images = []
        file_data = []
        
        for file in uploaded_files:
            try:
                # Read file data
                file_bytes = file.read()
                
                # Create PIL Image
                image = Image.open(io.BytesIO(file_bytes))
                
                # Store file info for sorting
                file_data.append({
                    'name': file.name,
                    'image': image,
                    'size': len(file_bytes)
                })
                
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")
                continue
        
        # Sort by filename to preserve order
        file_data.sort(key=lambda x: x['name'])
        
        # Extract sorted images
        images = [item['image'] for item in file_data]
        
        return images, file_data
    
    def generate_prompt(self) -> str:
        """
        Generate the detailed prompt for Gemini API.
        
        Returns:
            Formatted prompt string
        """
        return """You are an intelligent conversation extractor.

You will receive a list of sequential chat screenshots uploaded by the user in the correct order. Each image contains a portion of an informal conversation between two people via a messaging app (e.g., Instagram, WhatsApp, etc.).

Your task is to extract the entire conversation as coherent text, without losing any context or breaking the emotional or logical flow. Assume that the images were uploaded in order: first screenshot is the beginning of the chat, and the last is the latest.

Instructions:
- Preserve message order across images.
- Use visible names like "Snehal" or "You" to label speakers.
- Group multiline messages if they appear in a single message bubble.
- Handle mixed-language content (e.g., Hindi-English) as-is.
- Remove timestamps, UI elements, icons, or chat noise.
- Output format:
  [Sender]: message  
  [Other]: message  
  ...and so on.
Only return the cleaned conversation text."""
    
    def extract_conversation(self, images: List[Image.Image]) -> Optional[str]:
        """
        Extract conversation from images using Gemini API.
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Extracted conversation text or None if failed
        """
        if not images:
            return None
            
        try:
            # Prepare prompt
            prompt = self.generate_prompt()
            
            # Create content list with prompt and images
            content = [prompt]
            content.extend(images)
            
            # Generate content using Gemini
            response = self.model.generate_content(content)
            
            if response and hasattr(response, 'text'):
                return response.text.strip()
            else:
                st.error("❌ No response received from Gemini API")
                return None
                
        except Exception as e:
            st.error(f"❌ Error calling Gemini API: {str(e)}")
            return None

def create_download_link(text_content: str, filename: str, file_format: str) -> str:
    """
    Create a download link for the extracted conversation.
    
    Args:
        text_content: The conversation text
        filename: Name for the download file
        file_format: File format ('txt' or 'md')
        
    Returns:
        HTML download link
    """
    # Encode content
    b64_content = base64.b64encode(text_content.encode()).decode()
    
    # Create download link
    href = f'<a href="data:text/{file_format};base64,{b64_content}" download="{filename}.{file_format}" style="text-decoration: none;">'
    href += f'<button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">📥 Download as {file_format.upper()}</button>'
    href += '</a>'
    
    return href

def escape_javascript_string(text: str) -> str:
    """
    Safely escape a string for use in JavaScript.
    
    Args:
        text: String to escape
        
    Returns:
        Escaped string safe for JavaScript
    """
    # Replace problematic characters
    text = text.replace('\\', '\\\\')  # Escape backslashes first
    text = text.replace('`', '\\`')    # Escape backticks
    text = text.replace('\n', '\\n')   # Escape newlines
    text = text.replace('\r', '\\r')   # Escape carriage returns
    text = text.replace('"', '\\"')    # Escape double quotes
    text = text.replace("'", "\\'")    # Escape single quotes
    
    return text

def main():
    """Main Streamlit application."""
    
    # Title and description
    st.title("💬 Smart Chat Screenshot Extractor")
    st.markdown("**Extract structured conversations from sequential chat screenshots using Gemini 2.0 Flash API**")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔑 API Configuration")
        
        # API Key input
        api_key_input = st.text_input(
            "Enter your Gemini API Key:",
            type="password",
            placeholder="Enter your API key here...",
            help="Get your free API key from Google AI Studio: https://makersuite.google.com/app/apikey"
        )
        
        # API Key status and validation
        if api_key_input:
            # Validate API key format (basic validation)
            if len(api_key_input.strip()) < 20:
                st.warning("⚠️ API key seems too short. Please check your key.")
                api_key_valid = False
            else:
                st.success("✅ API Key entered")
                # Show only first 10 characters for security
                key_preview = api_key_input[:10] + "..." if len(api_key_input) > 10 else api_key_input
                st.text(f"Key: {key_preview}")
                api_key_valid = True
        else:
            st.info("🔐 Please enter your Gemini API key to get started")
            st.markdown("### How to get API Key:")
            st.markdown("""
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click **"Create API Key"**
            4. Copy and paste it above
            """)
            api_key_valid = False
        
        # Only show the rest of the sidebar if API key is provided
        if api_key_valid:
            st.markdown("---")
            st.markdown("### 📋 Instructions")
            st.markdown("""
            1. **Upload screenshots** in chronological order
            2. Supported formats: PNG, JPG, JPEG
            3. Images will be sorted by filename
            4. Click **Extract Conversation** to process
            5. **Download** or **copy** the result
            """)
            
            st.markdown("---")
            st.markdown("### 🔧 Settings")
            
            # Download format selection
            download_format = st.selectbox(
                "Download Format:",
                ["txt", "md"],
                index=0,
                help="Choose the format for downloading extracted conversation"
            )
        else:
            download_format = "txt"  # Default value
    
    # Early return if no valid API key
    if not api_key_input or not api_key_valid:
        st.info("👆 Please enter your Gemini API key in the sidebar to get started!")
        
        # Show helpful information
        st.header("🤖 About This App")
        st.markdown("""
        This app uses Google's **Gemini 2.0 Flash API** to intelligently extract structured conversations 
        from chat screenshots. It can process multiple images and create clean, readable conversation text.
        
        **Features:**
        - 📸 Process multiple screenshots in order
        - 🤖 AI-powered text extraction
        - 🌍 Multi-language support (Hindi, English, etc.)
        - 📝 Clean formatting with sender labels
        - 💾 Download as TXT or Markdown
        - 📋 One-click copy to clipboard
        """)
        
        st.header("🔒 Privacy & Security")
        st.markdown("""
        - Your API key is only used for this session and never stored
        - Images are processed through Google's secure API
        - No data is saved on our servers
        - All processing happens in real-time
        """)
        
        return
    
    # Initialize extractor with user's API key
    try:
        with st.spinner("🔄 Initializing Gemini API..."):
            extractor = ChatExtractor(api_key_input.strip())
        st.sidebar.success("🤖 Gemini API ready!")
    except Exception as e:
        st.sidebar.error(f"❌ API Error: {str(e)}")
        st.error("Failed to initialize Gemini API. Please check your API key and try again.")
        return
    
    # File upload section
    st.header("📸 Upload Chat Screenshots")
    uploaded_files = st.file_uploader(
        "Choose screenshot files",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Upload multiple screenshots in chronological order. Files will be sorted by filename."
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Process images
        with st.spinner("🔄 Processing images..."):
            try:
                images, file_data = extractor.prepare_images(uploaded_files)
            except Exception as e:
                st.error(f"❌ Error processing images: {str(e)}")
                return
        
        if not images:
            st.error("❌ No valid images found. Please check your files and try again.")
            return
        
        # Display image previews
        st.header("🖼️ Image Previews")
        
        # Create columns for thumbnails
        cols = st.columns(min(len(images), 4))
        
        for idx, (image, data) in enumerate(zip(images, file_data)):
            col_idx = idx % 4
            with cols[col_idx]:
                st.image(
                    image, 
                    caption=f"{idx+1}. {data['name']}",
                    use_container_width=True
                )
                st.text(f"Size: {data['size']:,} bytes")
        
        # Show file order
        st.subheader("📋 Processing Order")
        order_info = [f"{idx+1}. {data['name']}" for idx, data in enumerate(file_data)]
        st.text("\n".join(order_info))
        
        # Extract conversation button
        st.header("🚀 Extract Conversation")
        
        if st.button("🔍 Extract Conversation", type="primary", use_container_width=True):
            
            # Show processing spinner
            with st.spinner("🤖 Processing with Gemini AI... This may take a moment."):
                start_time = time.time()
                
                # Extract conversation
                conversation = extractor.extract_conversation(images)
                
                processing_time = time.time() - start_time
            
            if conversation:
                st.success(f"✅ Conversation extracted successfully in {processing_time:.2f} seconds!")
                
                # Display results
                st.header("💬 Extracted Conversation")
                
                # Show conversation in a text area
                st.text_area(
                    "Conversation Text:",
                    value=conversation,
                    height=400,
                    help="Copy this text or use download buttons below"
                )
                
                # Download options
                st.header("📥 Download Options")
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    # Download as selected format
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"chat_conversation_{timestamp}"
                    
                    download_link = create_download_link(
                        conversation, 
                        filename, 
                        download_format
                    )
                    st.markdown(download_link, unsafe_allow_html=True)
                
                with col2:
                    # Copy to clipboard button (JavaScript) - safely escaped
                    conversation_escaped = escape_javascript_string(conversation)
                    copy_button = f"""
                    <button onclick="navigator.clipboard.writeText(`{conversation_escaped}`).then(function(){{
                        alert('Conversation copied to clipboard!');
                    }}).catch(function(err){{
                        alert('Failed to copy: ' + err);
                    }});" style="background-color: #008CBA; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        📋 Copy Text
                    </button>
                    """
                    st.markdown(copy_button, unsafe_allow_html=True)
                
                with col3:
                    st.info(f"📊 **Stats:** {len(conversation.split())} words, {len(conversation.splitlines())} lines")
                
                # Statistics
                st.header("📊 Extraction Statistics")
                
                stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                
                with stats_col1:
                    st.metric("Images Processed", len(images))
                
                with stats_col2:
                    st.metric("Processing Time", f"{processing_time:.2f}s")
                
                with stats_col3:
                    st.metric("Words Extracted", len(conversation.split()))
                
                with stats_col4:
                    st.metric("Lines", len(conversation.splitlines()))
            
            else:
                st.error("❌ Failed to extract conversation. Please check your images and try again.")
    
    else:
        # Show help when no files uploaded
        st.info("👆 Please upload chat screenshots to get started!")
        
        st.header("💡 Tips for Best Results")
        st.markdown("""
        - **Upload screenshots in chronological order** (oldest first)
        - **Ensure good image quality** - text should be clearly readable
        - **Include complete message bubbles** - avoid cutting off messages
        - **Name files sequentially** (e.g., chat_01.png, chat_02.png) for proper ordering
        - **Use common formats** - PNG, JPG, or JPEG
        """)
        
        # Example section
        st.header("🎯 What This App Does")
        st.markdown("""
        1. **Uploads** your chat screenshots in order
        2. **Processes** them with Gemini 2.0 Flash AI
        3. **Extracts** clean, structured conversation text
        4. **Removes** UI clutter, timestamps, and noise
        5. **Preserves** message order and emotional flow
        6. **Handles** multilingual content naturally
        7. **Provides** easy download and copy options
        """)

if __name__ == "__main__":
    main()
