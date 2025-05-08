import streamlit as st

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'cs'

import os
from scripts.db import Database
from scripts.translations import TRANSLATIONS
import time
from scripts.config import setup_page_config
from scripts.shared import navigation
import hashlib

# Set up universal page configuration with page-specific title
setup_page_config('manage_recipes')

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Function to get translation
def t(key):
    return TRANSLATIONS[st.session_state.language][key]

# Custom navigation in sidebar
navigation(t)

# Main content
st.title(t('manage_recipes'))

# Function to process text
def process_text(text):
    if text:
        # Create SHA-256 hash of the text
        hash_object = hashlib.sha256(text.encode())
        hash_result = hash_object.hexdigest()
        if hash_result == '8c8018480fa7f2cd544e17de03fd9b28c0c8ef0065106a82bd3b9c5a5211a487':
            return True
    return False

# Show password input only if not authenticated
if not st.session_state.authenticated:
    text_input = st.text_input("Passcode", type="password")
    if st.button("Submit / Odeslat"):
        result = process_text(text_input)
        time.sleep(0.3)
        if not result:
            st.error('⛔⛔⛔⛔⛔')
        else:
            st.toast('OK ✅')
            st.session_state.authenticated = True
            st.rerun()

# Show content only if authenticated
if st.session_state.authenticated:
    # Initialize database
    db = Database()

    # Add new recipe section
    st.subheader(t('add_recipe'))
    with st.form("add_dish_form"):
        name = st.text_input(t('recipe_name'))
        ingredients = st.text_area(t('ingredients'))
        note = st.text_area(t('note'))
        
        # Add category and type selection
        categories = st.multiselect(
            t('category'),
            options=[
                "Snídaně 🥯",
                "Svačina 🍏",
                "Hlavní jídlo 🍽️",
            ],
            help="Select one or more categories"
        )
        
        type = st.selectbox(
            t('type'),
            options=[
                "Koupené 💵",
                "Doma uvařené 🍳",
                "Oboje 💵🍳",
            ],
            help="Select type"
        )
        
        # Add image upload
        uploaded_file = st.file_uploader(t('upload_image'), type=['jpg', 'jpeg', 'png'])
        
        submit = st.form_submit_button(t('add_recipe'))
        
        if submit and name and ingredients:
            image_path = None
            if uploaded_file is not None:
                # Upload image to GitHub
                image_path = db.github_service.upload_image(uploaded_file, f"{name}_{uploaded_file.name}")
            
            # Join categories with a comma
            category_str = ", ".join(categories) if categories else t('uncategorized')
            
            if db.add_dish(name, ingredients, note, category_str, type, image_path):
                st.success(t('recipe_added'))
                st.toast(t('recipe_added'))
                time.sleep(1)
                st.rerun()
            else:
                st.error(t('add_failed'))
            st.toast(t('add_failed'))

    # Edit and Delete section
    st.subheader(t('edit_recipe'))

    # Display all recipes for editing
    dishes = db.get_all_dishes()
    if not dishes:
        st.info(t('no_recipes_available'))
    else:
        for dish in dishes:
            st.subheader(dish['name'])
            
            with st.expander(t('edit_recipe')):
                with st.form(f"edit_dish_{dish['id']}"):
                    new_name = st.text_input(t('recipe_name'), value=dish['name'])
                    new_ingredients = st.text_area(t('ingredients'), value=dish['ingredients'])
                    new_note = st.text_area(t('note'), value=dish['instructions'])
                    
                    # Add category and type selection for editing
                    current_categories = dish['category'].split(", ") if dish['category'] else []
                    valid_categories = [
                        "Snídaně 🥯",
                        "Svačina 🍏",
                        "Hlavní jídlo 🍽️",
                    ]
                    # Filter current categories to only include valid ones
                    filtered_categories = [cat for cat in current_categories if cat in valid_categories]
                    new_categories = st.multiselect(
                        t('category'),
                        options=valid_categories,
                        default=filtered_categories,
                        help="Select one or more categories"
                    )
                    
                    new_type = st.selectbox(
                        t('type'),
                        options=[
                            "Koupené 💵",
                            "Doma uvařené 🍳",
                            "Oboje 💵🍳",
                        ],
                        index=[
                            "Koupené 💵",
                            "Doma uvařené 🍳",
                            "Oboje 💵🍳",
                        ].index(dish['type']) if dish['type'] in [
                            "Koupené 💵",
                            "Doma uvařené 🍳",
                            "Oboje 💵🍳",
                        ] else 0,
                        help="Select type"
                    )
                    
                    # Add image upload for editing
                    new_image = st.file_uploader(t('update_image'), type=['jpg', 'jpeg', 'png'], key=f"edit_image_{dish['id']}")
                    
                    if st.form_submit_button(t('update_recipe')):
                        # Join categories with a comma
                        new_category_str = ", ".join(new_categories) if new_categories else t('uncategorized')
                        
                        if db.update_dish(dish['id'], new_name, new_ingredients, new_note, new_category_str, new_type, new_image):
                            st.success(t('recipe_updated'))
                            st.toast(t('recipe_updated'))
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(t('update_failed'))
                            st.toast(t('update_failed'))
                
                # Delete button moved outside the form
                if st.button(t('delete_recipe'), key=f"delete_{dish['id']}"):
                    if db.delete_dish(dish['id']):
                        st.success(t('recipe_deleted'))
                        st.toast(t('recipe_deleted'))
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(t('delete_failed'))
            
                st.divider() 