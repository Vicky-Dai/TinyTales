import streamlit as st
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Read Story - TinyTales",
    page_icon="📖",
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

# Custom CSS styling
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
    
    .story-container {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .story-text {{
        font-size: 1.2em;
        line-height: 1.8;
        color: #333;
        margin: 20px 0;
    }}
    
    .story-image {{
        margin: 20px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }}
    
    .audio-button {{
        margin: 15px 0;
        text-align: center;
    }}
    
    .page-indicator {{
        text-align: center;
        font-size: 0.9em;
        color: #666;
        margin: 15px 0;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize current page
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

# Check if we have a story to display
if "current_story" not in st.session_state or st.session_state.current_story is None:
    st.warning("📚 No story to display!")
    st.markdown("Please go to the **Story Generator** page to create a story first.")
    
    if st.button("🤖 Go to Story Generator"):
        st.switch_page("pages/Story_Generator.py")
    
else:
    story = st.session_state.current_story
    current_page_idx = st.session_state.current_page
    
    # Display story header
    st.title("📖 " + story.get('title', 'Untitled Story'))
    
    # Story metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Age Range:** {story.get('age_range', 'N/A')}")
    with col2:
        st.markdown(f"**Moral:** {story.get('moral', 'N/A')}")
    with col3:
        st.markdown(f"**Language:** {story.get('language', 'en').upper()}")
    
    st.markdown("---")
    
    # Get pages
    pages = story.get('pages', [])
    
    if pages and current_page_idx < len(pages):
        page = pages[current_page_idx]
        
        # Debug: Show what data we have
        with st.expander("🔍 Debug Info (Page Data)"):
            st.json(page)
        
        # Story content container
        st.markdown('<div class="story-container">', unsafe_allow_html=True)
        
        # Page indicator
        st.markdown(f'<div class="page-indicator">Page {current_page_idx + 1} of {len(pages)}</div>', unsafe_allow_html=True)
        
        # Display image above text if available
        image_url = page.get('image_url')
        image_prompt = page.get('image_prompt', '')
        
        if image_url:
            # Use local file path instead of URL
            backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "backend")
            local_image_path = os.path.join(backend_dir, "stories", image_url)
            
            if os.path.exists(local_image_path):
                # Center the image with smaller width
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    st.image(local_image_path, caption=f"Page {current_page_idx + 1}")
            else:
                st.warning(f"Image not found: {local_image_path}")
        elif image_prompt:
            st.info(f"🎨 Illustration: {image_prompt}")
        
        # Story text
        st.markdown(f'<div class="story-text">{page.get("text", "")}</div>', unsafe_allow_html=True)
        
        # Audio player for this page
        audio_url = page.get('audio_url')
        if audio_url:
            # Use local file path instead of URL
            backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "backend")
            local_audio_path = os.path.join(backend_dir, "stories", audio_url)
            
            if os.path.exists(local_audio_path):
                st.markdown('<div class="audio-button">', unsafe_allow_html=True)
                st.audio(local_audio_path, format='audio/wav')
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(f"Audio not found: {local_audio_path}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 2])
        
        with col1:
            if current_page_idx > 0:
                if st.button("⬅️ Previous Page", width="stretch"):
                    st.session_state.current_page -= 1
                    st.rerun()
        
        with col3:
            st.markdown(f'<div style="text-align: center; padding-top: 8px; font-weight: bold;">{current_page_idx + 1} / {len(pages)}</div>', unsafe_allow_html=True)
        
        with col5:
            if current_page_idx < len(pages) - 1:
                if st.button("Next Page ➡️", width="stretch"):
                    st.session_state.current_page += 1
                    st.rerun()
            else:
                if st.button("✨ Create New Story", width="stretch", type="primary"):
                    st.session_state.current_story = None
                    st.session_state.current_page = 0
                    st.switch_page("pages/Story_Generator.py")

# Sidebar
st.sidebar.markdown("### 📖 Story Navigation")

if "current_story" in st.session_state and st.session_state.current_story:
    pages = st.session_state.current_story.get('pages', [])
    
    st.sidebar.markdown("**Jump to Page:**")
    for i in range(len(pages)):
        page_label = f"Page {i + 1}"
        if i == st.session_state.current_page:
            page_label += " 📍"
        
        if st.sidebar.button(page_label, key=f"page_{i}", width="stretch"):
            st.session_state.current_page = i
            st.rerun()
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🏠 Back to Home", width="stretch"):
        st.switch_page("Home.py")
    
    if st.sidebar.button("🤖 Create New Story", width="stretch"):
        st.session_state.current_story = None
        st.session_state.current_page = 0
        st.switch_page("pages/Story_Generator.py")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 About")
st.sidebar.info("""
**TinyTales** - AI Story Generator

Enjoy your personalized children's story with beautiful narratives and illustrations!
""")
