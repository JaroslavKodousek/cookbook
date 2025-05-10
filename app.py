import streamlit as st

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'cs'

from scripts.translations import TRANSLATIONS
from scripts.shared import navigation
from scripts.config import setup_page_config

# Function to get translation
def t(key):
    return TRANSLATIONS[st.session_state.language][key]

# Set up universal page configuration
setup_page_config()

# Custom navigation in sidebar
navigation(t)

# Main content
st.title(t('welcome_title'))
st.write(t('welcome_text'))

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(t('find_recipes'))
    st.write(t('find_recipes_desc'))

with col2:
    st.subheader(t('browse_collection'))
    st.write(t('browse_collection_desc'))

with col3:
    st.subheader(t('manage_recipes'))
    st.write(t('manage_recipes_desc'))

# Add large browse collection button
st.markdown("---")  # Add a separator
if st.button(t('browse_collection'), use_container_width=True, type="primary"):
    st.switch_page("pages/Browse_Collection.py")

# Navigation instructions
st.info(t('getting_started')) 