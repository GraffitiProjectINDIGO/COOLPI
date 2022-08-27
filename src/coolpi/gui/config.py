import json
import os

class ConfigError(Exception):
    pass

class Config:
    __config_path = ["coolpi", "gui", "assets", "config", "config.json"]
    __instance = None

    @staticmethod
    def instance():
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        if Config.__instance is None:
            Config.__instance = self

            with open(os.path.join(*Config.__config_path)) as json_path:
                self.data = json.loads(json_path.read())

        else:
            raise ConfigError("Not allowed multiple instances for the Config class")