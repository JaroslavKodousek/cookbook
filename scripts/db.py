import sqlite3
import os
from typing import List, Dict, Any
from .github_service import GitHubService

class Database:
    def __init__(self, db_name: str = "cookbook.db"):
        self.db_name = db_name
        self.github_service = GitHubService()
        self.init_db()
        self.migrate_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Create dishes table
        c.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Hlavní jídlo 🍽️',
                type TEXT NOT NULL DEFAULT 'Doma uvařené 🍳',
                image_path TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def migrate_db(self):
        """Migrate the database to add new columns if they don't exist."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Check if columns exist
        c.execute("PRAGMA table_info(dishes)")
        columns = [column[1] for column in c.fetchall()]
        
        # Add category column if it doesn't exist
        if 'category' not in columns:
            c.execute('ALTER TABLE dishes ADD COLUMN category TEXT NOT NULL DEFAULT "Hlavní jídlo 🍽️"')
        
        # Add type column if it doesn't exist
        if 'type' not in columns:
            c.execute('ALTER TABLE dishes ADD COLUMN type TEXT NOT NULL DEFAULT "Doma uvařené 🍳"')
        
        # Add image_path column if it doesn't exist
        if 'image_path' not in columns:
            c.execute('ALTER TABLE dishes ADD COLUMN image_path TEXT')
        
        conn.commit()
        conn.close()

    def add_dish(self, name: str, ingredients: str, instructions: str, category: str, type: str, image_data=None) -> bool:
        try:
            image_path = None
            if image_data:
                # Handle different types of image data
                if hasattr(image_data, 'name'):
                    # File upload object
                    filename = f"{name}_{image_data.name}"
                else:
                    # For string data (URL or base64), use a generic name
                    filename = f"{name}_image.png"
                image_path = self.github_service.upload_image(image_data, filename)
            
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''
                INSERT INTO dishes (name, ingredients, instructions, category, type, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, ingredients, instructions, category, type, image_path))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding dish: {str(e)}")
            return False

    def get_all_dishes(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT id, name, ingredients, instructions, category, type, image_path FROM dishes')
        dishes = []
        for row in c.fetchall():
            dishes.append({
                'id': row[0],
                'name': row[1],
                'ingredients': row[2],
                'instructions': row[3],
                'category': row[4],
                'type': row[5],
                'image_path': row[6]
            })
        conn.close()
        return dishes

    def update_dish(self, dish_id: int, name: str, ingredients: str, instructions: str, category: str, type: str, image_data=None) -> bool:
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Get current image path
            c.execute('SELECT image_path FROM dishes WHERE id = ?', (dish_id,))
            current_image_path = c.fetchone()[0]
            
            # Handle image update
            image_path = current_image_path
            if image_data is None:  # If image_data is None, we want to delete the image
                if current_image_path:
                    try:
                        filename = current_image_path.split('/')[-1]
                        self.github_service.delete_image(filename)
                        image_path = None  # Set image_path to None since we deleted the image
                    except Exception as e:
                        print(f"Warning: Could not delete image: {str(e)}")
            elif image_data != current_image_path:  # Only update if we have new image data
                # Delete old image if it exists and is different from the new one
                if current_image_path:
                    try:
                        filename = current_image_path.split('/')[-1]
                        self.github_service.delete_image(filename)
                    except Exception as e:
                        print(f"Warning: Could not delete old image: {str(e)}")
                
                # Handle different types of image data
                if hasattr(image_data, 'name'):
                    # File upload object
                    filename = f"{name}_{image_data.name}"
                else:
                    # For string data (URL or base64), use a generic name
                    filename = f"{name}_image.png"
                image_path = self.github_service.upload_image(image_data, filename)
            
            c.execute('''
                UPDATE dishes
                SET name = ?, ingredients = ?, instructions = ?, category = ?, type = ?, image_path = ?
                WHERE id = ?
            ''', (name, ingredients, instructions, category, type, image_path, dish_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating dish: {str(e)}")
            return False

    def delete_dish(self, dish_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Get the image path
            c.execute('SELECT image_path FROM dishes WHERE id = ?', (dish_id,))
            result = c.fetchone()
            
            # Delete the dish
            c.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
            conn.commit()
            conn.close()
            
            # Delete the image from GitHub if it exists
            if result and result[0]:
                filename = result[0].split('/')[-1]
                self.github_service.delete_image(filename)
            
            return True
        except Exception as e:
            print(f"Error deleting dish: {str(e)}")
            return False 