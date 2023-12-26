from vlite.main import VLite
from typing import Any, List
from warnings import warn
import json
import os

class Settings(object):
    """A class to save interface settings and preferences."""
    
    def __init__(self):
        """Initialize the settings object."""
        self.settings_file = os.path.join(os.path.expanduser(os.getenv('LOCALAPPDATA')), "Automacene/EmbravecDB/settings.json").replace("\\", "/")
        self.settings = {}
        self.settings = self.load_settings()

    def load_settings(self):
        """Load the settings from the settings file."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                return json.load(f)
        else:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            return {
                "database_path": self.database_path
            }

    def save_settings(self):
        """Save the settings to the settings file."""
        if not os.path.exists(os.path.dirname(self.settings_file)):
            os.makedirs(os.path.dirname(self.settings_file))
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f)

    def get(self, key):
        """Get a setting."""
        return self.settings.get(key)

    def set(self, key, value):
        """Set a setting."""
        self.settings[key] = value
        self.save_settings()

    def delete(self, key):
        """Delete a setting."""
        del self.settings[key]
        self.save_settings()

    def clear(self):
        """Clear all settings."""
        self.settings = {}
        self.save_settings()

    @property
    def keys(self):
        """Return the settings keys."""
        return self.settings.keys()
    
    @property
    def database_path(self):
        """Return the database path."""
        if self.get("database_path") == None:
            return os.path.join(os.path.expanduser(os.getenv('LOCALAPPDATA')), "Automacene/EmbravecDB/databases").replace("\\", "/")
        return self.get("database_path")
    
    @database_path.setter
    def database_path(self, value):
        """Set the database path."""
        #Make sure path is folder and not file
        if "." in value:
            warn("The database path must be a folder, not a file.")
            return
        #Check if the path exists, create it if it doesn't, and set the database path
        if not os.path.exists(value):
            os.makedirs(value)
        self.set("database_path", value)


def load_md_text(path: str, file: Any = None) -> str:
    """
    Load markdown text from a file.

    parameters:
        path: str
            The path to the markdown file.
    
    returns:
        str
            The markdown text.
    """
    if file != None:
        current_dir = os.path.dirname(file)
        path = os.path.join(current_dir, path)

    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise Exception(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"Error loading file {path.split('/')[-1]}: {e}")
    
def get_databases(path: str) -> (List[str], List[str]):
    """
    Get the databases from the database path.

    parameters:
        path: str
            The path to the databases.

    returns:
        List[str]
            The databases.
        List[str]
            The descriptions of the databases.
    """
    if not os.path.exists(path):
        raise Exception(f"Path does not exist: {path}")
    if not os.path.isdir(path):
        raise Exception(f"Path is not a directory: {path}")

    files = os.listdir(path)
    dbs = [file for file in files if file.endswith(".db")]
    databases = []
    descriptions = []
    for db in dbs:
        loaded_db = VLite(os.path.join(path, db))
        databases.append(db.split(".")[0])
        if "description" in loaded_db.metadata:
            descriptions.append(loaded_db.metadata["description"])
        else:

            descriptions.append("None provided.")
        print("Loaded database:", db)

    return databases, descriptions

def create_new_database(path: str, name: str, description: str, source: str) -> None:
    """
    Create a new database.

    parameters:
        path: str
            The path to the databases.
        name: str
            The name of the database.
        description: str
            The description of the database.
    """
    print("Creating new database..")
    if not os.path.exists(path):
        raise Exception(f"Path does not exist: {path}")
    if not os.path.isdir(path):
        raise Exception(f"Path is not a directory: {path}")
    if not name.endswith(".db"):
        name += ".db"
    if name in os.listdir(path):
        raise Exception(f"Database already exists: {name}")
    
    db_path = os.path.join(path, name)
    db = VLite(db_path)
    db.metadata["description"] = description
    db.metadata["source"] = source
    db.save()
    