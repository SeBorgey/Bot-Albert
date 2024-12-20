import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data.json")

class Storage:
    def __init__(self):
        logging.debug("Initializing storage.")
        self.data = {"users": {}}
        if os.path.exists(DB_PATH):
            logging.debug("Loading existing data from file.")
            self.load_data()
        else:
            logging.debug("No data file found, creating new.")
            self.save_data()

    def load_data(self):
        logging.debug("Loading data from file.")
        with open(DB_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save_data(self):
        logging.debug("Saving data to file.")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_user_settings(self, user_id):
        logging.debug(f"Getting user settings for user_id={user_id}.")
        return self.data["users"].get(str(user_id), None)

    def update_user_settings(self, user_id, settings):
        logging.debug(f"Updating user settings for user_id={user_id}.")
        self.data["users"][str(user_id)] = settings
        self.save_data()

    def get_all_users(self):
        logging.debug("Getting all users.")
        return list(self.data["users"].keys())

    def get_user_server_count(self, user_id, server_id):
        # Возвращаем сохраненное количество пользователей для данного пользователя и сервера.
        # Если данных нет, считаем что раньше было 0.
        settings = self.get_user_settings(user_id)
        if not settings:
            return 0
        server_counts = settings.get("server_counts", {})
        return server_counts.get(str(server_id), 0)

    def update_user_server_count(self, user_id, server_id, count):
        # Обновляем сохраненное количество людей для (user, server)
        settings = self.get_user_settings(user_id) or {
            "servers": [],
            "threshold": 0,
            "mode": "total"
        }
        server_counts = settings.get("server_counts", {})
        server_counts[str(server_id)] = count
        settings["server_counts"] = server_counts
        self.update_user_settings(user_id, settings)
