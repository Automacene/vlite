import json
import os

class Settings(object):
    """A class to save interface settings and preferences."""
    
    def __init__(self):
        """Initialize the settings object."""
        self.settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = self.load_settings()

    def load_settings(self):
        """Load the settings from the settings file."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_settings(self):
        """Save the settings to the settings file."""
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
        return self.get("database_path")
    
    @database_path.setter
    def database_path(self, value):
        """Set the database path."""
        #Check if the path exists, create it if it doesn't, and set the database path
        if not os.path.exists(value):
            os.makedirs(value)
        self.set("database_path", value)

    def __repr__(self):
        """Return a string representation of the settings."""
        return f"Settings({self.settings})"

    def __str__(self):
        """Return a string representation of the settings."""
        return f"Settings({self.settings})"

    def __getitem__(self, key):
        """Get a setting."""
        return self.get(key)

    def __setitem__(self, key, value):
        """Set a setting."""
        self.set(key, value)

    def __delitem__(self, key):
        """Delete a setting."""
        self.delete(key)

    def __contains__(self, key):
        """Check if a setting exists."""
        return key in self.settings

    def __len__(self):
        """Return the number of settings."""
        return len(self.settings)

    def __iter__(self):
        """Iterate over the settings."""
        return iter(self.settings)

    def __reversed__(self):
        """Iterate over the settings in reverse."""
        return reversed(self.settings)

    def __eq__(self, other):
        """Check if the settings are equal."""
        return self.settings == other

    def __ne__(self, other):
        """Check if the settings are not equal."""
        return self.settings != other


def get_settings():
    """Get the settings from the settings file."""
    pass

def set_settings():
    """Set the settings in the settings file."""
    pass