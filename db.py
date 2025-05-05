import sqlite3
import os
from typing import List, Dict, Any

class Database:
    def __init__(self, db_name: str = "cookbook.db"):
        self.db_name = db_name
        self.images_dir = "images"
        self.init_db()
        self.migrate_db()
        self.ensure_images_dir()

    def ensure_images_dir(self):
        """Create images directory if it doesn't exist."""
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

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

    def add_dish(self, name: str, ingredients: str, instructions: str, category: str, type: str, image_path: str = None) -> bool:
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''
                INSERT INTO dishes (name, ingredients, instructions, category, type, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, ingredients, instructions, category, type, image_path))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
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

    def update_dish(self, dish_id: int, name: str, ingredients: str, instructions: str, category: str, type: str, image_path: str = None) -> bool:
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''
                UPDATE dishes
                SET name = ?, ingredients = ?, instructions = ?, category = ?, type = ?, image_path = ?
                WHERE id = ?
            ''', (name, ingredients, instructions, category, type, image_path, dish_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def delete_dish(self, dish_id: int) -> bool:
        try:
            # First get the image path
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('SELECT image_path FROM dishes WHERE id = ?', (dish_id,))
            result = c.fetchone()
            
            # Delete the dish
            c.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
            conn.commit()
            conn.close()
            
            # Delete the image file if it exists
            if result and result[0]:
                image_path = result[0]
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            return True
        except sqlite3.Error:
            return False 