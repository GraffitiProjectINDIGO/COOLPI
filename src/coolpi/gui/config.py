from curses import get_tabsize
import json
import os

class ConfigError(Exception):
    pass

class Config:

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
            Config.coolpi_dir = self.get_abs_path_coolpi()
            with open(os.path.join(Config.coolpi_dir, *Config.__config_path)) as json_path:
                self.data = json.loads(json_path.read())
            self.data["coolpi_dir"] = Config.coolpi_dir
        else:
            raise ConfigError("Not allowed multiple instances for the Config class")

    def get_abs_path_coolpi(self):
        from coolpi import __file__ as current_dir
        coolpy_path = os.path.abspath(current_dir)
        return coolpy_path[:-12]