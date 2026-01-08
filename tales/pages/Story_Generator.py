import streamlit as st
import requests
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Story Generator - TinyTales",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and embed the backdrop SVG
svg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assest")
svg_filename = "nightBackDrop.svg"
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

# Get API endpoint from environment variable
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/api/story/generate-agentic")

# Chatbot/Story Generator Page
st.title("🤖 AI Story Generator")
st.markdown("*Create personalized stories with AI assistance*")

st.markdown("---")

st.markdown("### 📝 Create a Story")

# Simple prompt input
prompt = st.text_area(
    "Tell me what story you'd like to create",
    placeholder="e.g., A story about a brave dragon who learns to share, for kids age 6-9",
    height=120,
    help="Describe your story idea - you can include age, characters, moral, setting, etc."
)

# Create story button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    create_button = st.button("✨ Generate Story", width="stretch", type="primary")

# Handle story creation
if create_button:
    if not prompt or not prompt.strip():
        st.error("❌ Please enter a story prompt")
    else:
        # Prepare the request payload
        story_request = {
            "prompt": prompt.strip()
        }
        
        print(f"📝 Story Request: {story_request}")
        
        # Add user request to messages
        st.session_state.messages.append({
            "role": "user",
            "content": prompt.strip()
        })
        
        # Show loading indicator
        with st.spinner("✨ Generating your story with images and audio..."):
            try:
                # Send request to API
                response = requests.post(
                    API_ENDPOINT,
                    json=story_request,
                    timeout=120  # Increased timeout for agentic processing
                )
                
                # Handle API response
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check if it's a clarification question
                        if data.get("type") == "clarification":
                            st.warning(f"🤔 {data.get('question', 'Please provide more details')}")
                            
                            # Add assistant response
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": data.get('question', 'Please provide more details')
                            })
                        
                        # Check if response contains a story
                        elif "pages" in data and isinstance(data.get("pages"), list):
                            # It's a story! Store it and redirect to Read_Story page
                            st.session_state.current_story = data
                            st.session_state.current_page = 0
                            
                            # Add assistant response
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"✨ Story Generated: {data.get('title', 'Untitled')}"
                            })
                            
                            # Redirect to Read_Story page
                            st.switch_page("pages/Read_Story.py")
                        else:
                            st.error("❌ Invalid story format from API")
                    
                    except json.JSONDecodeError:
                        st.error(f"❌ Invalid response format: {response.text}")
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to API at: {API_ENDPOINT}")
            except requests.exceptions.Timeout:
                st.error("❌ API request timed out")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Sidebar
st.sidebar.markdown("### 📌 About")
st.sidebar.info("""
**TinyTales** - AI Story Generator

Create personalized children's stories with:
- Custom characters & settings
- Age-appropriate content
- Moral lessons
- Multiple languages
- Beautiful narratives
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Settings")
clear_chat = st.sidebar.button("Clear Chat History")
if clear_chat:
    st.session_state.messages = []
    st.rerun()
