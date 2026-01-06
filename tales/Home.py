import streamlit as st
import base64
import os

# Page configuration
st.set_page_config(
    page_title="TinyTales - Home",
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

# Sidebar
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

Navigate to **Story Generator** page to start!
""")
