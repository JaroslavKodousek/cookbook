import sqlite3
import os
import base64
from typing import List, Dict, Any
from .github_service import GitHubService
import streamlit as st

class Database:
    def __init__(self, db_name: str = "cookbook.db"):
        try:
            self.github_service = GitHubService()
            self.use_github = True
            self.db_name = db_name
            self.init_db()
            self.migrate_db()
        except Exception as e:
            st.error(f"GitHub integration is required but not available: {str(e)}")
            raise

    def _get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_name)

    def _sync_db_to_github(self):
        """Sync the database file to GitHub."""
        try:
            # Verify the database is valid before syncing
            conn = self._get_connection()
            c = conn.cursor()
            c.execute("PRAGMA integrity_check")
            result = c.fetchone()
            if result[0] != "ok":
                raise Exception("Database integrity check failed")
            conn.close()

            with open(self.db_name, 'rb') as f:
                db_content = f.read()
            # Convert to base64 for GitHub storage
            db_content_b64 = base64.b64encode(db_content).decode('utf-8')
            self.github_service.upload_file(db_content_b64, self.db_name, "Update database")
        except Exception as e:
            st.error(f"Error syncing database to GitHub: {str(e)}")
            raise

    def _get_db_from_github(self):
        """Get the database file from GitHub."""
        try:
            db_content = self.github_service.get_file_content(self.db_name)
            if db_content:
                # Decode base64 content
                db_bytes = base64.b64decode(db_content)
                with open(self.db_name, 'wb') as f:
                    f.write(db_bytes)
                
                # Verify the database is valid after downloading
                conn = self._get_connection()
                c = conn.cursor()
                c.execute("PRAGMA integrity_check")
                result = c.fetchone()
                conn.close()
                
                if result[0] != "ok":
                    raise Exception("Downloaded database failed integrity check")
                return True
            return False
        except Exception as e:
            st.error(f"Error getting database from GitHub: {str(e)}")
            raise

    def init_db(self):
        # Try to get existing database from GitHub
        try:
            if self._get_db_from_github():
                return
        except Exception as e:
            st.warning(f"Could not retrieve database from GitHub: {str(e)}")
            # If file exists but is invalid, remove it
            if os.path.exists(self.db_name):
                os.remove(self.db_name)
            
        # Create new database
        conn = self._get_connection()
        c = conn.cursor()
        
        try:
            # Start transaction
            c.execute("BEGIN TRANSACTION")
            
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
            
            # Commit transaction
            conn.commit()
            
            # Sync new database to GitHub
            try:
                self._sync_db_to_github()
            except Exception as e:
                st.warning(f"Could not sync database to GitHub: {str(e)}")
        except Exception as e:
            conn.rollback()
            st.error(f"Error initializing database: {str(e)}")
            raise
        finally:
            conn.close()

    def migrate_db(self):
        """Migrate the database to add new columns if they don't exist."""
        conn = self._get_connection()
        c = conn.cursor()
        
        try:
            # Start transaction
            c.execute("BEGIN TRANSACTION")
            
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
            
            # Commit transaction
            conn.commit()
            
            # Sync migrated database to GitHub
            self._sync_db_to_github()
        except Exception as e:
            # Rollback transaction on error
            conn.rollback()
            st.error(f"Error during database migration: {str(e)}")
            raise
        finally:
            conn.close()

    def add_dish(self, name: str, ingredients: str, instructions: str, category: str, type: str, image_data=None) -> bool:
        conn = None
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
            
            # Start transaction
            c.execute("BEGIN TRANSACTION")
            
            c.execute('''
                INSERT INTO dishes (name, ingredients, instructions, category, type, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, ingredients, instructions, category, type, image_path))
            
            # Commit transaction
            conn.commit()
            
            # Sync updated database to GitHub if available
            if self.use_github:
                self._sync_db_to_github()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error adding dish: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    def get_all_dishes(self) -> List[Dict[str, Any]]:
        conn = None
        try:
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
            return dishes
        except Exception as e:
            print(f"Error getting dishes: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    def update_dish(self, dish_id: int, name: str, ingredients: str, instructions: str, category: str, type: str, image_data=None) -> bool:
        conn = None
        try:
            # Get latest database from GitHub if available
            if self.use_github:
                self._get_db_from_github()
            
            conn = self._get_connection()
            c = conn.cursor()
            
            # Start transaction
            c.execute("BEGIN TRANSACTION")
            
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
            
            # Commit transaction
            conn.commit()
            
            # Sync updated database to GitHub if available
            if self.use_github:
                self._sync_db_to_github()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error updating dish: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_dish(self, dish_id: int) -> bool:
        conn = None
        try:
            # Get latest database from GitHub if available
            if self.use_github:
                self._get_db_from_github()
            
            conn = self._get_connection()
            c = conn.cursor()
            
            # Start transaction
            c.execute("BEGIN TRANSACTION")
            
            # Get image path before deleting
            c.execute('SELECT image_path FROM dishes WHERE id = ?', (dish_id,))
            image_path = c.fetchone()[0]
            
            # Delete the dish
            c.execute('DELETE FROM dishes WHERE id = ?', (dish_id,))
            
            # Commit transaction
            conn.commit()
            
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
            if conn:
                conn.rollback()
            print(f"Error deleting dish: {str(e)}")
            return False
        finally:
            if conn:
                conn.close() 