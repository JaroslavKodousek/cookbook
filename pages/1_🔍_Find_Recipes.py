import streamlit as st
from db import Database
from translations import TRANSLATIONS

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'cs'

# Initialize database
db = Database()

# Function to get translation
def t(key):
    return TRANSLATIONS[st.session_state.language][key]

# Page config
st.set_page_config(
    page_title=f"{t('find_recipes')} - {t('app_title')}",
    page_icon="🔍",
    layout="wide"
)

# Main content
st.title(t('find_recipes'))

# Search section
search_query = st.text_input(t('search_placeholder'), "")

# Display recipes
dishes = db.get_all_dishes()
if search_query:
    dishes = [dish for dish in dishes if search_query.lower() in dish['name'].lower() 
             or search_query.lower() in dish['ingredients'].lower()]

if not dishes:
    st.info(t('no_recipes_found'))
else:
    # Display dishes in a grid layout
    cols = st.columns(2)
    for idx, dish in enumerate(dishes):
        with cols[idx % 2]:
            st.subheader(f"📝 {dish['name']}")
            
            # Display image if it exists
            if dish['image_path']:
                try:
                    st.image(dish['image_path'], caption=dish['name'], use_column_width=True)
                except:
                    st.warning(t('image_not_found'))
            
            st.write(f"**{t('category')}:** {dish['category']}")
            st.write(f"**{t('type')}:** {dish['type']}")
            st.write(f"**{t('ingredients')}:**")
            st.write(dish['ingredients'])
            if dish['instructions']:
                st.write(f"**{t('note')}:**")
                st.write(dish['instructions'])
            st.divider() 