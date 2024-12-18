import json
import os
from config import DB_PATH

class Storage:
    def __init__(self):
        self.data = {"users": {}}
        if os.path.exists(DB_PATH):
            self.load_data()
        else:
            self.save_data()

    def load_data(self):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save_data(self):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_user_settings(self, user_id):
        return self.data["users"].get(str(user_id), None)

    def update_user_settings(self, user_id, settings):
        self.data["users"][str(user_id)] = settings
        self.save_data()

    def get_all_users(self):
        return list(self.data["users"].keys())
