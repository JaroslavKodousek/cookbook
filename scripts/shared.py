import streamlit as st
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