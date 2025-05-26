# config/settings.py
import os
import json
from pathlib import Path

class Settings:
    def __init__(self):
        self.config_dir = Path.home() / ".sigmatoolkit"
        self.config_file = self.config_dir / "settings.json"
        self.default_settings = {
            "debug_mode": False,
            "default_ping_count": 4,
            "default_timeout": 30,
            "max_port_scan_range": 1000,
            "theme": "dark",
            "window_geometry": {
                "width": 1200,
                "height": 800,
                "x": 100,
                "y": 100
            },
            "last_used_hosts": [],
            "favorite_hosts": [
                {"name": "Google DNS", "host": "8.8.8.8"},
                {"name": "Cloudflare DNS", "host": "1.1.1.1"},
                {"name": "Quad9 DNS", "host": "9.9.9.9"}
            ]
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load settings from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
            else:
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
            
    def save_settings(self, settings=None):
        """Save settings to file"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            if settings is None:
                settings = self.settings
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self.save_settings()