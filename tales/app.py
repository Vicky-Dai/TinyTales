import streamlit as st
import requests
import json
import time
import base64
import os

# Page configuration
st.set_page_config(
    page_title="TinyTales - AI Story Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme toggle in session state (early, before using it)
if "use_dark_theme" not in st.session_state:
    st.session_state.use_dark_theme = True

# Load and embed the appropriate backdrop SVG
svg_dir = os.path.join(os.path.dirname(__file__), "assest")

# Use dark theme by default, but will be updated after sidebar toggle
use_dark = st.session_state.use_dark_theme
svg_filename = "nightBackDrop.svg" if use_dark else "sunbackdrop.svg"
svg_path = os.path.join(svg_dir, svg_filename)

if os.path.exists(svg_path):
    with open(svg_path, "r") as f:
        svg_content = f.read()
    # Encode SVG for use in CSS
    svg_encoded = base64.b64encode(svg_content.encode()).decode()
    background_style = f"url('data:image/svg+xml;base64,{svg_encoded}')"
else:
    # Fallback gradient
    background_style = "linear-gradient(135deg, #001a4d 0%, #003d99 100%)"

# Set theme_mode for display
theme_mode = "dark" if use_dark else "light"

# Custom CSS styling for better UI
st.markdown(f"""
<style>
    /* Background image */
    .stApp {{
        background-image: {background_style};
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    
    .user-message {{
        background-color: #E3F2FD;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        text-align: right;
    }}
    
    .assistant-message {{
        background-color: #F5F5F5;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
    }}
    
    .message-label {{
        font-weight: bold;
        font-size: 12px;
        margin-bottom: 4px;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize current story
if "current_story" not in st.session_state:
    st.session_state.current_story = None

if "current_page" not in st.session_state:
    st.session_state.current_page = 0

# Initialize page selection
if "show_chatbot" not in st.session_state:
    st.session_state.show_chatbot = False

# Main content based on page selection
if not st.session_state.show_chatbot:
    # Introduction Page
    st.title("📚 Welcome to TinyTales")
    st.markdown("### *AI-Powered Personalized Story Generator for Children*")
    
    st.markdown("---")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## ✨ What is TinyTales?
        
        TinyTales is an innovative AI-powered platform that creates **personalized, engaging stories** for children. 
        Each story is uniquely crafted based on your preferences, ensuring a magical reading experience every time.
        
        ### 🎯 Key Features
        
        - **📖 Custom Story Generation** - Create stories tailored to specific age groups (3-5, 5-8, 8-12, 12+)
        - **🌍 Multi-Language Support** - Stories available in English, Spanish, French, German, Chinese, and Japanese
        - **🎭 Diverse Tones** - Choose from adventurous, magical, funny, mysterious, heartwarming, or educational themes
        - **👥 Personalized Characters** - Add your own characters to make stories more relatable
        - **📚 Moral Lessons** - Each story teaches valuable life lessons
        - **🎨 Beautiful Illustrations** - AI-generated image descriptions for each page
        
        ### 💡 How It Works
        
        1. **Choose Your Preferences** - Select age range, language, tone, and number of pages
        2. **Add Story Elements** - Define the moral, setting, and characters
        3. **Generate** - Our AI creates a unique story with illustrations
        4. **Read & Enjoy** - Navigate through beautiful pages with your personalized tale
        
        ### 🚀 Get Started
        
        Click the **"🤖 Open Story Generator"** button in the sidebar to start creating your first story!
        """)
    
    with col2:
        st.markdown("### 🎨 Story Examples")
        st.info("""
        **🌟 Sample Themes:**
        - A brave knight learning courage
        - A magical forest adventure
        - A funny tale about friendship
        - An educational journey through space
        """)
        
        st.markdown("### 🎯 Perfect For")
        st.success("""
        - **Parents** looking for bedtime stories
        - **Teachers** creating educational content
        - **Children** who love unique tales
        - **Anyone** who enjoys creative storytelling
        """)
    
    st.markdown("---")
    
    # Features grid
    st.markdown("### 🌟 Why Choose TinyTales?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🎓 Educational
        Each story includes meaningful lessons and morals that help children learn important values.
        """)
    
    with col2:
        st.markdown("""
        #### 🎨 Creative
        AI-generated stories ensure endless variety and creativity, never the same story twice.
        """)
    
    with col3:
        st.markdown("""
        #### 🌈 Engaging
        Interactive page-by-page reading experience keeps children engaged and excited.
        """)
    
else:
    # Chatbot/Story Generator Page
    st.title("🤖 AI Story Generator")
    st.markdown("*Create personalized stories with AI assistance*")
    
    st.markdown("---")

    # If we have a current story, display it
    if st.session_state.current_story:
        story = st.session_state.current_story
        current_page_idx = st.session_state.current_page
    
    # Display story title and info
    st.markdown(f"### 📖 {story.get('title', 'Untitled Story')}")
    st.markdown(f"*Age Range: {story.get('age_range', 'N/A')} | Moral: {story.get('moral', 'N/A')}*")
    
    # Get current page content
    pages = story.get('pages', [])
    if pages and current_page_idx < len(pages):
        page = pages[current_page_idx]
        
        # Display page number
        st.markdown(f"**Page {page.get('page', current_page_idx + 1)} of {len(pages)}**")
        
        # Display page text
        st.markdown(f"> {page.get('text', '')}")
        
        # Display page image (using image_prompt as description if no actual image)
        image_prompt = page.get('image_prompt', '')
        if image_prompt:
            st.markdown(f"*📸 Illustration: {image_prompt}*")
        
        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_page_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_page -= 1
                    st.rerun()
            else:
                st.markdown("")
        
        with col2:
            st.markdown(f"<div style='text-align: center'>{current_page_idx + 1}/{len(pages)}</div>", unsafe_allow_html=True)
        
        with col3:
            if current_page_idx < len(pages) - 1:
                if st.button("Next ➡️"):
                    st.session_state.current_page += 1
                    st.rerun()
            else:
                if st.button("🏠 Back to Chat"):
                    st.session_state.current_story = None
                    st.session_state.current_page = 0
                    st.rerun()
    
    st.markdown("---")

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'><div class='message-label'>You</div>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-message'><div class='message-label'>🤖 Assistant</div>{message['content']}</div>", unsafe_allow_html=True)

    # Input area - Story creation form
    st.markdown("---")

    if not st.session_state.current_story:
        st.markdown("### 📝 Create a Story")
        
        # Create form columns
        col1, col2 = st.columns(2)
        
        with col1:
            age_range = st.selectbox(
                "Age Range",
                ["3-5", "5-8", "8-12", "12+"],
                help="Target age group for the story"
            )
            
            language = st.selectbox(
                "Language",
                ["en", "es", "fr", "de", "zh", "ja"],
                format_func=lambda x: {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "zh": "Chinese", "ja": "Japanese"}.get(x, x),
                help="Story language"
            )
            
            tone = st.selectbox(
                "Tone",
                ["adventurous", "magical", "funny", "mysterious", "heartwarming", "educational"],
                help="Story atmosphere and mood"
            )
        
        with col2:
            moral = st.text_input(
                "Moral/Lesson",
                placeholder="e.g., bravery and helping others",
                help="The main lesson or moral of the story"
            )
            
            pages = st.slider(
                "Number of Pages",
                min_value=3,
                max_value=10,
                value=6,
                help="How many pages should the story have?"
            )
            
            setting = st.text_input(
                "Setting",
                placeholder="e.g., a magical forest",
                help="Where does the story take place?"
            )
        
        # Characters section
        st.markdown("**Characters**")
        character_cols = st.columns(3)
        characters = []
        
        for i, col in enumerate(character_cols):
            with col:
                char = st.text_input(
                    f"Character {i+1}",
                    placeholder=f"e.g., Emma, a wise owl",
                    key=f"char_{i}"
                )
                if char:
                    characters.append(char)
        
        # Create story button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            create_button = st.button("✨ Generate Story", use_container_width=True, type="primary")
        
        # Handle story creation
        if create_button:
            if not moral or not setting or not characters:
                st.error("❌ Please fill in Moral, Setting, and at least one Character")
            else:
                # Prepare the request payload
                story_request = {
                    "age_range": age_range,
                    "language": language,
                    "moral": moral,
                    "characters": characters,
                    "setting": setting,
                    "tone": tone,
                    "pages": pages
                }
                
                print(f"📝 Story Request: {story_request}")
                
                # Check if API endpoint is configured
                if not st.session_state.get("api_endpoint"):
                    st.error("❌ Please configure the API endpoint in the sidebar first!")
                else:
                    # Add user request to messages
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"Create a story: {moral}"
                    })
                    
                    # Show loading indicator
                    with st.spinner("✨ Generating your story..."):
                        try:
                            # Send request to API
                            response = requests.post(
                                st.session_state.api_endpoint,
                                json=story_request,
                                timeout=30
                            )
                            
                            # Handle API response
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    
                                    # Check if response contains a story
                                    if "pages" in data and isinstance(data.get("pages"), list):
                                        # It's a story! Store it and display it
                                        st.session_state.current_story = data
                                        st.session_state.current_page = 0
                                        
                                        # Add assistant response
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": f"✨ Story Generated: {data.get('title', 'Untitled')}"
                                        })
                                        
                                        st.rerun()
                                    else:
                                        st.error("❌ Invalid story format from API")
                                
                                except json.JSONDecodeError:
                                    st.error(f"❌ Invalid response format: {response.text}")
                            else:
                                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                        
                        except requests.exceptions.ConnectionError:
                            st.error(f"❌ Cannot connect to API at: {st.session_state.api_endpoint}")
                        except requests.exceptions.Timeout:
                            st.error("❌ API request timed out (30 seconds)")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    else:
        # Show a button to create a new story
        if st.button("📝 Create Another Story"):
            st.session_state.current_story = None
            st.session_state.current_page = 0
            st.rerun()

# Sidebar with navigation and configuration
st.sidebar.markdown("### 📚 Navigation")

# Button to toggle between intro and story generator
if st.session_state.show_chatbot:
    if st.sidebar.button("🏠 Back to Home", use_container_width=True):
        st.session_state.show_chatbot = False
        st.rerun()
else:
    if st.sidebar.button("🤖 Open Story Generator", use_container_width=True, type="primary"):
        st.session_state.show_chatbot = True
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ API Configuration")
api_endpoint = st.sidebar.text_input(
    "API Endpoint URL",
    placeholder="http://localhost:5000/chat",
    value=st.session_state.get("api_endpoint", "")
)

if api_endpoint:
    st.session_state.api_endpoint = api_endpoint
    st.sidebar.success("✓ API configured")
else:
    st.sidebar.warning("⚠️ API endpoint not configured")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Theme")

# Create a toggle for theme switching
theme_toggle = st.sidebar.toggle(
    "Dark Mode 🌙",
    value=st.session_state.use_dark_theme,
    help="Toggle between dark and light theme"
)

# Update session state if toggle changed
if theme_toggle != st.session_state.use_dark_theme:
    st.session_state.use_dark_theme = theme_toggle
    st.rerun()

# Display current theme
if st.session_state.use_dark_theme:
    st.sidebar.success("🌙 Dark Mode Active - Night Backdrop")
else:
    st.sidebar.success("☀️ Light Mode Active - Sun Backdrop")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 About")
st.sidebar.info("""
**TinyTales** - AI Story Generator

Create personalized children's stories with:
- Custom characters & settings
- Age-appropriate content
- Moral lessons
- Multiple languages
- Beautiful narratives

Configure the API endpoint above to start generating stories!
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Settings")
if st.session_state.show_chatbot:
    clear_chat = st.sidebar.button("Clear Chat History")
    if clear_chat:
        st.session_state.messages = []
        st.rerun()
