import streamlit as st
from translations import TRANSLATIONS

def setup_page_config(page_title_key=None):
    """Set up the universal page configuration for the entire app.
    
    Args:
        page_title_key (str, optional): Translation key for the page title. If provided,
        it will be combined with the app title.
    """
    title = TRANSLATIONS[st.session_state.language]['app_title']
    if page_title_key:
        page_title = TRANSLATIONS[st.session_state.language][page_title_key]
        title = f"{page_title} - {title}"
        
    st.set_page_config(
        page_title=title,
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    ) 