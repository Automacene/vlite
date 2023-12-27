from typing import Any, List, Dict
from vlite.main import VLite
from warnings import warn
import json
import uuid
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

def load_database(path: str, name: str) -> VLite:
    """
    Load a database.

    parameters:
        path: str
            The path to the databases.
        name: str
            The name of the database.

    returns:
        VLite
            The database.
    """
    if not os.path.exists(path):
        raise Exception(f"Path does not exist: {path}")
    if not os.path.isdir(path):
        raise Exception(f"Path is not a directory: {path}")
    if not name.endswith(".db"):
        name += ".db"
    if name not in os.listdir(path):
        raise Exception(f"Database does not exist: {name}")

    db_path = os.path.join(path, name)
    db = VLite(db_path)
    return db

def create_entry(db: VLite, data: str, id: str = None, metadata: Dict[str, Any] = None) -> None:
    """
    Create an entry in a database.

    parameters:
        db: VLite
            The database.
        data: str
            The data to store in the database.
        id: str
    """
    if id == None or id == "":
        id = str(uuid.uuid4().hex)
    if metadata == None:
        metadata = {
            "id": id,
            "source": "EmbravecDB Interface",
            "description": "None provided."
        }
    
    #Check if id already exists
    if id in db._vector_key_store:
        raise Exception(f"Entry already exists with id '{id}'.")
    #Check if metadata has all required keys
    if "id" not in metadata:
        warn("Metadata does not contain an id. Adding one.")
        metadata["id"] = id
    elif metadata["id"] == None:
        warn("Metadata does not contain an id. Adding one.")
        metadata["id"] = id

    if "source" not in metadata:
        warn("Metadata does not contain a source. Adding one.")
        metadata["source"] = "EmbravecDB Interface"
    elif metadata["source"] == None:
        warn("Metadata does not contain a source. Adding one.")
        metadata["source"] = "EmbravecDB Interface"

    if "description" not in metadata:
        warn("Metadata does not contain a description. Adding one.")
        metadata["description"] = "None provided."
    elif metadata["description"] == None:
        warn("Metadata does not contain a description. Adding one.")
        metadata["description"] = "None provided."
    
    db.memorize(data, id=id, metadata=metadata)
    print(db.remember(id=id))

def retrieve_entries_by_id(db: VLite, ids: List[str]=None) -> List[Dict[str, Any]]:
    """
    Retrieve entries from a database.

    parameters:
        db: VLite
            The database.
        ids: List[str]
            The ids of the entries to retrieve.

    returns:
        List[Dict[str, Any]]
            The entries.
    """
    if ids == None:
        ids = db._vector_key_store
    entries = []
    for id in ids:
        entry_data, entry_metadata, _ = db.remember(id=id)
        entry = {
            "id": id,
            "data": entry_data,
        }
        entries.append(entry)
    return entries

def retrieve_entries_by_query(db: VLite, query: str, count:int=5) -> List[Dict[str, Any]]:
    """
    Retrieve entries from a database.

    parameters:
        db: VLite
            The database.
        query: str
            The query to use to retrieve entries.

    returns:
        List[Dict[str, Any]]
            The entries.
    """
    data, metadata, _ = db.remember(text=query, top_k=count)
    entries = []
    for i in range(len(data)):
        entry = {
            "id": metadata[i]["id"],
            "data": data[i],
        }
        entries.append(entry)
    return entries