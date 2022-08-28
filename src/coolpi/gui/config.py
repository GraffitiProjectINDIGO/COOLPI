import json
import os

import coolpi

class ConfigError(Exception):
    pass

class Config:
    __current_dir, _ = os.path.splitext(os.path.abspath(coolpi.__file__)) # __init__
    __current_dir = __current_dir[:-9]

    __config_path = ["gui", "assets", "config", "config.json"]
    __instance = None

    @staticmethod
    def instance():
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        if Config.__instance is None:
            Config.__instance = self

            with open(os.path.join(*[Config.__current_dir, *Config.__config_path])) as json_path:
                self.data = json.loads(json_path.read())

        else:
            raise ConfigError("Not allowed multiple instances for the Config class")