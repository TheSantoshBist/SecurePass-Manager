import bcrypt
import json
import os
from datetime import datetime, timedelta

class Auth:
    def __init__(self):
        self.last_activity = datetime.now()
        self.session_timeout = timedelta(minutes=5)
        self.config_file = 'config.json'
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_file):
            self._create_default_config()
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def _create_default_config(self):
        default_config = {
            'master_hash': None,
            'salt': None
        }
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f)
        self.config = default_config

    def set_master_password(self, password: str) -> bool:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        self.config['master_hash'] = password_hash.decode()
        self.config['salt'] = salt.decode()

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        return True

    def verify_password(self, password: str) -> bool:
        if not self.config['master_hash']:
            return False

        return bcrypt.checkpw(
            password.encode(),
            self.config['master_hash'].encode()
        )

    def update_activity(self):
        self.last_activity = datetime.now()

    def is_session_valid(self) -> bool:
        return datetime.now() - self.last_activity < self.session_timeout

    def has_master_password(self) -> bool:
        return bool(self.config.get('master_hash'))

    def reset_master_password(self) -> bool:
        """Clear master password without deleting config file."""
        try:
            with open('config.json', 'w') as f:
                json.dump({"master_hash": None, "salt": None}, f)
            return True
        except Exception as e:
            print(f"Error resetting master password: {e}")
            return False