import streamlit as st

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'cs'

from scripts.db import Database
from scripts.translations import TRANSLATIONS
from scripts.config import setup_page_config
from scripts.shared import navigation, display_image

# Set up universal page configuration with page-specific title
setup_page_config('browse_collection')

# Function to get translation
def t(key):
    return TRANSLATIONS[st.session_state.language][key]

# Custom navigation in sidebar
navigation(t)

# Initialize database
db = Database()

# Main content
st.title(t('browse_collection'))

# Display all recipes
dishes = db.get_all_dishes()

if not dishes:
    st.info(t('no_recipes_available'))
else:
    # Display dishes in a grid layout
    cols = st.columns(2)
    for idx, dish in enumerate(dishes):
        with cols[idx % 2]:
            st.subheader(dish['name'])
            
            # Display image if it exists
            if dish['image_path']:
                display_image(dish['image_path'], caption=dish['name'])
            
            st.write(f"**{t('category')}:** {dish['category']}")
            st.write(f"**{t('type')}:** {dish['type']}")
            st.write(f"**{t('ingredients')}:**")
            st.write(dish['ingredients'])
            if dish['instructions']:
                st.write(f"**{t('note')}:**")
                st.write(dish['instructions'])
            st.divider() 