# My Cookbook - Personal Recipe Manager

A bilingual (English/Czech) Streamlit application for managing your personal recipe collection. The app allows you to add, edit, delete, and search through your recipes with support for images and multiple categories.

## Features

- 🌍 Bilingual interface (English/Czech)
- 🔍 Search recipes by name or ingredients
- 📚 Browse your complete recipe collection
- ✏️ Add, edit, and delete recipes
- 🖼️ Upload and manage recipe images
- 🏷️ Multiple categories per recipe
- 📱 Responsive design

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cookbook.git
cd cookbook
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py` - Main application file
- `pages/` - Streamlit pages
  - `1_🔍_Find_Recipes.py` - Search functionality
  - `2_📚_Browse_Collection.py` - Recipe collection browser
  - `3_✏️_Manage_Recipes.py` - Recipe management
- `db.py` - Database operations
- `translations.py` - Language translations
- `requirements.txt` - Project dependencies

## Technologies Used

- Streamlit
- SQLite
- Python

## License

MIT License 