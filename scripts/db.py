import sqlite3
import os
import base64
from typing import List, Dict, Any
from .github_service import GitHubService

class Database:
    def __init__(self, db_name: str = "cookbook.db"):
        self.db_name = db_name
        self.use_memory = not os.access('.', os.W_OK)  # Check if we can write to disk
        try:
            self.github_service = GitHubService()
            self.use_github = True
        except Exception as e:
            print(f"GitHub integration not available: {str(e)}")
            self.use_github = False
        self.init_db()
        self.migrate_db()

    def _get_connection(self):
        """Get a database connection, using memory if we can't write to disk."""
        if self.use_memory:
            return sqlite3.connect(':memory:')
        return sqlite3.connect(self.db_name)

    def _sync_db_to_github(self):
        """Sync the database file to GitHub."""
        if not self.use_github:
            return
            
        try:
            if self.use_memory:
                # For in-memory database, we need to dump it to a temporary file
                conn = self._get_connection()
                with open(self.db_name, 'wb') as f:
                    for line in conn.iterdump():
                        f.write(f'{line}\n'.encode('utf-8'))
                conn.close()
            
            with open(self.db_name, 'rb') as f:
                db_content = f.read()
            # Convert to base64 for GitHub storage
            db_content_b64 = base64.b64encode(db_content).decode('utf-8')
            self.github_service.upload_file(db_content_b64, self.db_name, "Update database")
        except Exception as e:
            print(f"Error syncing database to GitHub: {str(e)}")

    def _get_db_from_github(self):
        """Get the database file from GitHub."""
        if not self.use_github:
            return False
            
        try:
            db_content = self.github_service.get_file_content(self.db_name)
            if db_content:
                # Decode base64 content
                db_bytes = base64.b64decode(db_content)
                
                if self.use_memory:
                    # For in-memory database, we need to execute the SQL directly
                    conn = self._get_connection()
                    conn.executescript(db_bytes.decode('utf-8'))
                    conn.close()
                else:
                    with open(self.db_name, 'wb') as f:
                        f.write(db_bytes)
                return True
        except Exception as e:
            print(f"Error getting database from GitHub: {str(e)}")
        return False

    def init_db(self):
        # Try to get existing database from GitHub if available
        if self.use_github and self._get_db_from_github():
            return
            
        # If not found or GitHub not available, create new database
        conn = self._get_connection()
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
        # Sync new database to GitHub if available
        if self.use_github:
            self._sync_db_to_github()

    def migrate_db(self):
        """Migrate the database to add new columns if they don't exist."""
        conn = self._get_connection()
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
        # Sync migrated database to GitHub
        self._sync_db_to_github()

    def add_dish(self, name: str, ingredients: str, instructions: str, category: str, type: str, image_data=None) -> bool:
        try:
            image_path = None
            if image_data and self.use_github:
                # Handle different types of image data
                if hasattr(image_data, 'name'):
                    # File upload object
                    filename = f"{name}_{image_data.name}"
                else:
                    # For string data (URL or base64), use a generic name
                    filename = f"{name}_image.png"
                image_path = self.github_service.upload_image(image_data, filename)
            
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO dishes (name, ingredients, instructions, category, type, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, ingredients, instructions, category, type, image_path))
            conn.commit()
            conn.close()
            # Sync updated database to GitHub if available
            if self.use_github:
                self._sync_db_to_github()
            return True
        except Exception as e:
            print(f"Error adding dish: {str(e)}")
            return False

    def get_all_dishes(self) -> List[Dict[str, Any]]:
        # Get latest database from GitHub if available
        if self.use_github:
            self._get_db_from_github()
        
        conn = self._get_connection()
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
            # Get latest database from GitHub if available
            if self.use_github:
                self._get_db_from_github()
            
            conn = self._get_connection()
            c = conn.cursor()
            
            # Get current image path
            c.execute('SELECT image_path FROM dishes WHERE id = ?', (dish_id,))
            current_image_path = c.fetchone()[0]
            
            # Handle image update
            image_path = current_image_path
            if self.use_github:
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
            
            # Update the dish
            c.execute('''
                UPDATE dishes 
                SET name = ?, ingredients = ?, instructions = ?, category = ?, type = ?, image_path = ?
                WHERE id = ?
            ''', (name, ingredients, instructions, category, type, image_path, dish_id))
            
            conn.commit()
            conn.close()
            
            # Sync updated database to GitHub if available
            if self.use_github:
                self._sync_db_to_github()
            return True
        except Exception as e:
            print(f"Error updating dish: {str(e)}")
            return False

    def delete_dish(self, dish_id: int) -> bool:
        try:
            # Get latest database from GitHub if available
            if self.use_github:
                self._get_db_from_github()
            
            conn = self._get_connection()
            c = conn.cursor()
            
            # Get image path before deleting
            c.execute('SELECT image_path FROM dishes WHERE id = ?', (dish_id,))
            image_path = c.fetchone()[0]
            
            # Delete the dish
            c.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
            
            conn.commit()
            conn.close()
            
            # Delete image from GitHub if available
            if self.use_github and image_path:
                try:
                    filename = image_path.split('/')[-1]
                    self.github_service.delete_image(filename)
                except Exception as e:
                    print(f"Warning: Could not delete image: {str(e)}")
            
            # Sync updated database to GitHub if available
            if self.use_github:
                self._sync_db_to_github()
            return True
        except Exception as e:
            print(f"Error deleting dish: {str(e)}")
            return False 