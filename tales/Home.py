import streamlit as st
import base64
import os
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="TinyTales - Home",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and embed the backdrop SVG
svg_dir = os.path.join(os.path.dirname(__file__), "assest")
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
</style>
""", unsafe_allow_html=True)

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
    
    Click the **"🤖 Story Generator"** page in the sidebar to start creating your first story!
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

st.markdown("---")

# Story Library Section
st.markdown("### 📚 Your Story Library")

# Get path to stories data folder
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
stories_data_dir = os.path.join(backend_dir, "stories", "data")

# Load all stories
if os.path.exists(stories_data_dir):
    story_files = [f for f in os.listdir(stories_data_dir) if f.endswith('.json')]
    
    if story_files:
        st.markdown(f"*Found {len(story_files)} saved {'story' if len(story_files) == 1 else 'stories'}*")
        
        # Display stories in a grid
        cols = st.columns(3)
        
        for idx, story_file in enumerate(story_files):
            story_path = os.path.join(stories_data_dir, story_file)
            
            try:
                with open(story_path, 'r', encoding='utf-8') as f:
                    story_data = json.load(f)
                
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"**📖 {story_data.get('title', 'Untitled')}**")
                        st.caption(f"Age: {story_data.get('age_range', 'N/A')} | Pages: {len(story_data.get('pages', []))}")
                        st.caption(f"Moral: {story_data.get('moral', 'N/A')[:50]}...")
                        
                        if st.button(f"Read Story", key=f"read_{story_file}", width="stretch"):
                            # Load the story into session state
                            st.session_state.current_story = story_data
                            st.session_state.current_page = 0
                            st.switch_page("pages/Read_Story.py")
            except Exception as e:
                st.error(f"Error loading {story_file}: {str(e)}")
    else:
        st.info("📖 No saved stories yet. Create your first story using the Story Generator!")
        if st.button("🤖 Go to Story Generator", width="stretch"):
            st.switch_page("pages/Story_Generator.py")
else:
    st.warning("Stories folder not found!")

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

Navigate to **Story Generator** page to start!
""")
