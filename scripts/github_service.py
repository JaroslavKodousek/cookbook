import os
import base64
import streamlit as st
from github import Github

class GitHubService:
    def __init__(self):
        # Get secrets from Streamlit
        self.github_token = st.secrets["github"]["token"]
        self.repo_name = st.secrets["github"]["repo"]
        self.owner = st.secrets["github"]["owner"]
        
        if not all([self.github_token, self.repo_name, self.owner]):
            raise ValueError("Missing GitHub configuration. Please set github.token, github.repo, and github.owner in Streamlit secrets")
        
        self.github = Github(self.github_token)
        self.repo = self.github.get_user(self.owner).get_repo(self.repo_name)
        
    def upload_image(self, image_data, filename):
        try:
            # Handle file-like objects (e.g., from st.file_uploader)
            if hasattr(image_data, 'read'):
                content = image_data.read()
            # Handle bytes objects
            elif isinstance(image_data, bytes):
                content = image_data
            # Handle string inputs
            elif isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    # Base64 image data with data URL prefix
                    content = base64.b64decode(image_data.split(',')[1])
                elif image_data.startswith('http'):
                    # If it's a URL, return it directly
                    return image_data
                elif image_data.startswith('iVBORw0KGgoAAAANSUhEUg'):  # Common base64 PNG header
                    # Raw base64 string without data URL prefix
                    content = base64.b64decode(image_data)
                else:
                    # Try to decode as base64
                    try:
                        content = base64.b64decode(image_data)
                    except:
                        raise ValueError("Invalid image data format")
            else:
                raise ValueError("Unsupported image data type. Please provide a file, bytes, or string.")

            # Create path in images directory for GitHub
            path = f"images/{filename}"

            try:
                # Try to get existing file to get its SHA
                contents = self.repo.get_contents(path)
                # Update existing file
                self.repo.update_file(
                    path=path,
                    message=f"Update image: {filename}",
                    content=content,  # <-- Pass bytes, NOT base64 string
                    sha=contents.sha,
                    branch="main"
                )
            except Exception:
                # File doesn't exist, create new file
                self.repo.create_file(
                    path=path,
                    message=f"Add image: {filename}",
                    content=content,  # <-- Pass bytes, NOT base64 string
                    branch="main"
                )

            # Return the raw URL for the image
            return f"https://raw.githubusercontent.com/{self.owner}/{self.repo_name}/main/{path}"

        except Exception as e:
            st.error(f"Error uploading image to GitHub: {str(e)}")
            raise

    def delete_image(self, filename):
        """Delete an image from GitHub repository."""
        try:
            path = f"images/{filename}"
            contents = self.repo.get_contents(path)
            self.repo.delete_file(
                path=path,
                message=f"Delete image: {filename}",
                sha=contents.sha,
                branch="main"
            )
            return True
        except Exception as e:
            st.error(f"Error deleting image from GitHub: {str(e)}")
            return False
            
    def get_image_url(self, filename):
        """Get the raw URL for an image."""
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo_name}/main/images/{filename}"

    def upload_file(self, content, filename, message="Update file"):
        """Upload a file to GitHub repository.
        
        Args:
            content: The content to upload (base64 encoded string)
            filename: The name to save the file as
            message: Commit message
        """
        try:
            # Create path in root directory
            path = filename
            
            try:
                # Try to get existing file to get its SHA
                contents = self.repo.get_contents(path)
                # Update existing file
                self.repo.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=contents.sha,
                    branch="main"
                )
            except Exception as e:
                if "Not Found" in str(e):
                    # File doesn't exist, create new file
                    self.repo.create_file(
                        path=path,
                        message=message,
                        content=content,
                        branch="main"
                    )
                else:
                    # Re-raise if it's a different error
                    raise
            
            return True
            
        except Exception as e:
            st.error(f"Error uploading file to GitHub: {str(e)}")
            raise

    def get_file_content(self, filename):
        """Get the content of a file from GitHub repository.
        
        Args:
            filename: The name of the file to get
        """
        try:
            path = filename
            contents = self.repo.get_contents(path)
            return contents.decoded_content.decode('utf-8')
        except Exception as e:
            if "Not Found" in str(e):
                return None
            st.error(f"Error getting file from GitHub: {str(e)}")
            raise 