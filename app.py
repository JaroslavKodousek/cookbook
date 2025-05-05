import streamlit as st
from translations import TRANSLATIONS

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'cs'

# Function to get translation
def t(key):
    return TRANSLATIONS[st.session_state.language][key]

# Set page config
st.set_page_config(
    page_title=t('app_title'),
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language selector in sidebar
with st.sidebar:
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

# Navigation instructions
st.info(t('getting_started')) 