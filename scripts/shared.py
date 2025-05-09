import streamlit as st
import base64
from io import BytesIO
from PIL import Image
from scripts.translations import TRANSLATIONS

def navigation(t):
    with st.sidebar:
        st.title(t('app_title'))
        
        # Navigation links
        st.page_link("app.py", label=t('welcome_title'), icon="👨‍🍳")
        st.page_link("pages/Find_Recipes.py", label=t('find_recipes'), icon="🔍")
        st.page_link("pages/Browse_Collection.py", label=t('browse_collection'), icon="📚")
        st.page_link("pages/Manage_Recipes.py", label=t('manage_recipes'), icon="✏️")

        st.divider()

        # Language selector
        st.write("🌍 Language / Jazyk")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇬🇧 English", use_container_width=True, 
                        type="primary" if st.session_state.language == 'en' else "secondary"):
                st.session_state.language = 'en'
                st.rerun()
        with col2:
            if st.button("🇨🇿 Čeština", use_container_width=True,
                        type="primary" if st.session_state.language == 'cs' else "secondary"):
                st.session_state.language = 'cs'
                st.rerun()

def display_image(image_path, caption=None):
    """
    Display an image from either a base64 string or a file path.
    
    Args:
        image_path: Can be a base64 string (with or without data URL prefix) or a file path
        caption: Optional caption for the image
    """
    try:
        if not image_path:
            return
            
        if image_path.startswith('data:image'):
            # Handle base64 image data with data URL prefix
            image_data = image_path.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption=caption)
        elif image_path.startswith('http'):
            # Handle regular image URLs
            st.image(image_path, caption=caption)
        elif image_path.startswith('iVBORw0KGgoAAAANSUhEUg'):  # Common base64 PNG header
            # Handle raw base64 string without data URL prefix
            try:
                image_bytes = base64.b64decode(image_path)
                image = Image.open(BytesIO(image_bytes))
                st.image(image, caption=caption)
            except Exception as e:
                st.warning(f"Could not decode base64 image: {str(e)}")
                # Try to display as raw base64 with data URL prefix
                try:
                    st.image(f"data:image/png;base64,{image_path}", caption=caption)
                except:
                    st.error("Failed to display image in any format")
        else:
            # Handle regular file paths
            st.image(image_path, caption=caption)
    except Exception as e:
        st.warning(f"Could not display image: {str(e)}")