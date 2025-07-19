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
    page_title="Smart Chat Screenshot Extractor & Analyzer",
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
        genai.configure(api_key=self.api_key) # type: ignore
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17') # type: ignore
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
    
    def generate_extraction_prompt(self) -> str:
        """
        Generate the detailed prompt for conversation extraction.
        
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

    def generate_analysis_prompt(self, conversation_text: str, analysis_type: str, user_context: str = "") -> str:
        """
        Generate analysis prompts based on the selected analysis type.
        
        Args:
            conversation_text: The extracted conversation
            analysis_type: Type of analysis to perform
            user_context: Additional context provided by user
            
        Returns:
            Formatted analysis prompt
        """
        base_context = f"""
CONVERSATION TO ANALYZE:
{conversation_text}

{"USER PROVIDED CONTEXT: " + user_context if user_context.strip() else ""}

ANALYSIS INSTRUCTIONS:
Provide an unbiased, objective analysis of this conversation. Focus on observable patterns, communication styles, and interpersonal dynamics without making assumptions about people's character or intentions beyond what's directly evident in the text.
"""

        prompts = {
            "communication_style": base_context + """
COMMUNICATION STYLE ANALYSIS:
Analyze the communication patterns and styles of each participant:
1. **Formality Level**: How formal or casual is each person's language?
2. **Response Patterns**: Who initiates topics? Who responds more/less?
3. **Message Length**: Are messages typically short/long? Who writes more?
4. **Language Choice**: Any code-switching, emojis, slang usage patterns?
5. **Engagement Style**: Active vs passive participation patterns
6. **Emotional Expression**: How do participants express emotions through text?

Be objective and focus only on observable communication behaviors.""",

            "emotional_tone": base_context + """
EMOTIONAL TONE & SENTIMENT ANALYSIS:
Analyze the emotional undertones and sentiment flow:
1. **Overall Sentiment**: What's the general emotional tone throughout?
2. **Sentiment Progression**: How does the emotional tone change over time?
3. **Individual Emotions**: What emotions can you detect from each participant?
4. **Tension Points**: Are there moments of disagreement, confusion, or tension?
5. **Positive Moments**: Identify moments of connection, humor, or warmth
6. **Subtle Indicators**: Tone shifts, word choices that suggest underlying feelings

Focus on what's directly observable in the language used.""",

            "relationship_dynamics": base_context + """
RELATIONSHIP DYNAMICS ANALYSIS:
Examine the interpersonal dynamics and relationship patterns:
1. **Power Balance**: Is the conversation equal or does someone lead/follow?
2. **Intimacy Level**: How close/distant do the participants seem?
3. **Conversational Roles**: Who asks questions, gives advice, shares personal info?
4. **Conflict Resolution**: How do they handle disagreements or misunderstandings?
5. **Support Patterns**: How do they offer/receive emotional support?
6. **Boundaries**: Are there topics avoided or boundaries respected/crossed?

Base analysis only on interaction patterns visible in the conversation.""",

            "hidden_meanings": base_context + """
SUBTEXT & HIDDEN MEANINGS ANALYSIS:
Look for underlying messages and unspoken communication:
1. **Subtext**: What might be implied but not directly stated?
2. **Avoidance Patterns**: Topics that seem to be skirted around?
3. **Passive Communication**: Indirect ways of expressing needs/concerns?
4. **Reading Between Lines**: Suggestions, hints, or coded messages?
5. **Unresolved Issues**: Tensions or topics that remain unaddressed?
6. **Context Clues**: References to shared experiences or inside knowledge?

Be careful to distinguish between reasonable inferences and speculation.""",

            "conversation_flow": base_context + """
CONVERSATION FLOW & STRUCTURE ANALYSIS:
Analyze how the conversation develops and flows:
1. **Topic Progression**: How do topics evolve and connect?
2. **Transition Points**: How smoothly do participants change subjects?
3. **Interruption Patterns**: Who interrupts or redirects conversations?
4. **Question-Answer Dynamics**: How are questions posed and answered?
5. **Storytelling Elements**: How do participants share experiences or information?
6. **Conversation Closure**: How do topics or the overall chat conclude?

Focus on the structural and flow aspects of the communication.""",

            "cultural_context": base_context + """
CULTURAL & LINGUISTIC CONTEXT ANALYSIS:
Examine cultural and language elements in the conversation:
1. **Language Mixing**: How multiple languages are used and why?
2. **Cultural References**: Mentions of cultural practices, events, or concepts?
3. **Formality Levels**: Cultural politeness markers or informal expressions?
4. **Generation Indicators**: Language that might indicate age or generational differences?
5. **Regional Elements**: Location-specific references or language patterns?
6. **Social Context**: References to social situations, family, work, etc.?

Analyze without stereotyping or making broad cultural generalizations.""",

            "comprehensive": base_context + """
COMPREHENSIVE CONVERSATION ANALYSIS:
Provide a thorough, multi-dimensional analysis covering:

**COMMUNICATION OVERVIEW:**
- Overall conversation purpose and outcome
- Key themes and topics discussed
- Communication effectiveness

**PARTICIPANT ANALYSIS:**
- Individual communication styles
- Emotional states and expressions
- Role each person plays in the conversation

**DYNAMICS & PATTERNS:**
- Power balance and relationship dynamics  
- Conversation flow and topic management
- Conflict/agreement patterns

**EMOTIONAL LANDSCAPE:**
- Sentiment progression throughout
- Emotional support and connection moments
- Areas of tension or misunderstanding

**DEEPER INSIGHTS:**
- Possible subtext or unspoken elements
- Cultural/linguistic context
- What the conversation reveals about the relationship

Keep analysis balanced, evidence-based, and avoid over-interpretation."""
        }
        
        return prompts.get(analysis_type, prompts["comprehensive"])
    
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
            prompt = self.generate_extraction_prompt()
            
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

    def analyze_conversation(self, conversation_text: str, analysis_type: str, user_context: str = "") -> Optional[str]:
        """
        Analyze the extracted conversation using Gemini API.
        
        Args:
            conversation_text: The conversation to analyze
            analysis_type: Type of analysis to perform
            user_context: Additional context from user
            
        Returns:
            Analysis result or None if failed
        """
        if not conversation_text:
            return None
            
        try:
            # Generate analysis prompt
            prompt = self.generate_analysis_prompt(conversation_text, analysis_type, user_context)
            
            # Generate analysis using Gemini
            response = self.model.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                return response.text.strip()
            else:
                st.error("❌ No response received from Gemini API for analysis")
                return None
                
        except Exception as e:
            st.error(f"❌ Error during conversation analysis: {str(e)}")
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

def get_analysis_descriptions():
    """Return descriptions for each analysis type."""
    return {
        "communication_style": "📝 **Communication Style**: Analyzes how each person communicates - formality, response patterns, message length, and language choices.",
        "emotional_tone": "💭 **Emotional Tone**: Examines the emotional undertones, sentiment flow, and feeling progression throughout the conversation.",
        "relationship_dynamics": "🤝 **Relationship Dynamics**: Looks at power balance, intimacy level, conversational roles, and interaction patterns.",
        "hidden_meanings": "🔍 **Hidden Meanings**: Identifies potential subtext, implications, avoidance patterns, and things that might be 'read between the lines'.",
        "conversation_flow": "🌊 **Conversation Flow**: Analyzes how topics progress, transition points, and the structural development of the discussion.",
        "cultural_context": "🌍 **Cultural Context**: Examines language mixing, cultural references, and social/regional elements in the conversation.",
        "comprehensive": "📊 **Comprehensive Analysis**: A thorough multi-dimensional analysis covering all aspects - communication, emotions, dynamics, and insights."
    }

def main():
    """Main Streamlit application."""
    
    # Title and description
    st.title("💬 Smart Chat Screenshot Extractor & Analyzer")
    st.markdown("**Extract structured conversations from chat screenshots and analyze them with AI-powered insights using Gemini 2.0 Flash API**")
    
    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
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
            2. **Extract conversation** first
            3. **Analyze** with different AI perspectives
            4. **Add context** for better insights
            5. **Download** results and analysis
            """)
            
            st.markdown("---")
            st.markdown("### 🔧 Settings")
            
            # Download format selection
            download_format = st.selectbox(
                "Download Format:",
                ["txt", "md"],
                index=1,
                help="Choose the format for downloading extracted conversation and analysis"
            )
        else:
            download_format = "md"  # Default value
    
    # Early return if no valid API key
    if not api_key_input or not api_key_valid:
        st.info("👆 Please enter your Gemini API key in the sidebar to get started!")
        
        # Show helpful information
        st.header("🤖 About This Enhanced App")
        st.markdown("""
        This app uses Google's **Gemini 2.0 Flash API** to intelligently extract structured conversations 
        from chat screenshots and provide deep AI-powered analysis.
        
        **New Analysis Features:**
        - 📝 **Communication Style Analysis** - How each person communicates
        - 💭 **Emotional Tone Detection** - Sentiment and feeling progression  
        - 🤝 **Relationship Dynamics** - Power balance and interaction patterns
        - 🔍 **Hidden Meanings** - Subtext and implications analysis
        - 🌊 **Conversation Flow** - Topic progression and structure
        - 🌍 **Cultural Context** - Language and cultural elements
        - 📊 **Comprehensive Analysis** - All-in-one detailed insights
        
        **Original Features:**
        - 📸 Process multiple screenshots in order
        - 🌍 Multi-language support (Hindi, English, etc.)
        - 📝 Clean formatting with sender labels
        - 💾 Download as TXT or Markdown
        - 📋 One-click copy to clipboard
        """)
        
        st.header("🔒 Privacy & Security")
        st.markdown("""
        - Your API key is only used for this session and never stored
        - Images are processed through Google's secure API
        - Analysis is objective and unbiased
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
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["📸 Extract Conversation", "🔍 Analyze Conversation"])
    
    # Tab 1: Conversation Extraction
    with tab1:
        st.header("📸 Upload Chat Screenshots")
        uploaded_files = st.file_uploader(
            "Choose screenshot files",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload multiple screenshots in chronological order. Files will be sorted by filename.",
            key="file_uploader"
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
                    # Store in session state
                    st.session_state.conversation = conversation
                    
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
                    
                    st.success("🎉 Ready for analysis! Go to the 'Analyze Conversation' tab to get AI insights.")
                
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
    
    # Tab 2: Conversation Analysis
    with tab2:
        if not st.session_state.conversation:
            st.warning("⚠️ Please extract a conversation first in the 'Extract Conversation' tab before analyzing.")
            st.info("💡 Upload screenshots and click 'Extract Conversation' to get started with analysis.")
            return
        
        st.header("🔍 AI-Powered Conversation Analysis")
        st.success("✅ Conversation ready for analysis!")
        
        # Show conversation preview
        with st.expander("👀 View Extracted Conversation", expanded=False):
            st.text_area(
                "Current Conversation:",
                value=st.session_state.conversation,
                height=200,
                disabled=True
            )
        
        # Analysis type selection
        st.header("🎯 Choose Analysis Type")
        
        analysis_descriptions = get_analysis_descriptions()
        
        # Create a radio button selection with descriptions
        analysis_options = list(analysis_descriptions.keys())
        analysis_labels = [analysis_descriptions[key] for key in analysis_options]
        
        selected_analysis = st.radio(
            "Select the type of analysis you want:",
            options=analysis_options,
            format_func=lambda x: analysis_descriptions[x],
            help="Each analysis type focuses on different aspects of the conversation to provide unique insights."
        )
        
        # Optional user context
        st.header("📝 Additional Context (Optional)")
        user_context = st.text_area(
            "Provide any additional context about the conversation:",
            placeholder="E.g., 'This is a conversation between friends about planning a trip' or 'Context: One person seemed upset earlier that day' or any other relevant background information...",
            height=100,
            help="Adding context helps the AI provide more accurate and relevant analysis. Include background information, relationship details, or situational context."
        )
        
        # Analysis button
        if st.button("🤖 Analyze Conversation", type="primary", use_container_width=True):
            
            with st.spinner(f"🔍 Performing {selected_analysis.replace('_', ' ').title()} Analysis... This may take a moment."):
                start_time = time.time()
                
                # Perform analysis
                analysis_result = extractor.analyze_conversation(
                    st.session_state.conversation, 
                    selected_analysis, 
                    user_context
                )
                
                analysis_time = time.time() - start_time
            
            if analysis_result:
                # Store analysis result
                st.session_state.analysis_results[selected_analysis] = {
                    'result': analysis_result,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'context': user_context,
                    'processing_time': analysis_time
                }
                
                st.success(f"✅ Analysis completed in {analysis_time:.2f} seconds!")
                
                # Display analysis results
                st.header(f"📋 {selected_analysis.replace('_', ' ').title()} Analysis Results")
                
                st.markdown(analysis_result)
                
                # Analysis statistics
                st.header("📊 Analysis Statistics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Analysis Time", f"{analysis_time:.2f}s")
                
                with col2:
                    st.metric("Analysis Length", f"{len(analysis_result.split())} words")
                
                with col3:
                    context_provided = "Yes" if user_context.strip() else "No"
                    st.metric("Context Provided", context_provided)
                
                # Download analysis
                st.header("📥 Download Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    analysis_filename = f"conversation_analysis_{selected_analysis}_{timestamp}"
                    
                    # Create comprehensive download content
                    download_content = f"""# Conversation Analysis Report
**Analysis Type:** {selected_analysis.replace('_', ' ').title()}
**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Processing Time:** {analysis_time:.2f} seconds

## Original Conversation
{st.session_state.conversation}

## User Provided Context
{user_context if user_context.strip() else "No additional context provided"}

## Analysis Results
{analysis_result}

---
*Generated using Smart Chat Screenshot Extractor & Analyzer*
"""
                    
                    download_link = create_download_link(
                        download_content,
                        analysis_filename,
                        download_format
                    )
                    st.markdown(download_link, unsafe_allow_html=True)
                
                with col2:
                    # Copy analysis button
                    analysis_escaped = escape_javascript_string(analysis_result)
                    copy_button = f"""
                    <button onclick="navigator.clipboard.writeText(`{analysis_escaped}`).then(function(){{
                        alert('Analysis copied to clipboard!');
                    }}).catch(function(err){{
                        alert('Failed to copy: ' + err);
                    }});" style="background-color: #FF6B6B; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        📋 Copy Analysis
                    </button>
                    """
                    st.markdown(copy_button, unsafe_allow_html=True)
            
            else:
                st.error("❌ Failed to analyze conversation. Please try again.")
        
        # Show previous analysis results if any
        if st.session_state.analysis_results:
            st.header("📚 Previous Analysis Results")
            
            for analysis_type, data in st.session_state.analysis_results.items():
                with st.expander(f"🔍 {analysis_type.replace('_', ' ').title()} Analysis - {data['timestamp']}", expanded=False):
                    st.markdown(f"**Generated:** {data['timestamp']}")
                    st.markdown(f"**Processing Time:** {data['processing_time']:.2f} seconds")
                    if data['context']:
                        st.markdown(f"**Context Used:** {data['context']}")
                    st.markdown("**Results:**")
                    st.markdown(data['result'])
        
        # Quick tips for analysis
        st.header("💡 Analysis Tips")
        st.markdown("""
        - **Try different analysis types** to get various perspectives on the same conversation
        - **Provide context** for more accurate and relevant insights
        - **Compare results** from different analysis types to get a complete picture
        - **Remember** that analysis is AI-generated and should be considered as one perspective
        - **Use insights** to better understand communication patterns and relationship dynamics
        """)
        
        # Clear analysis history button
        if st.session_state.analysis_results:
            if st.button("🗑️ Clear Analysis History", help="Remove all previous analysis results"):
                st.session_state.analysis_results = {}
                st.rerun()

if __name__ == "__main__":
    main()
