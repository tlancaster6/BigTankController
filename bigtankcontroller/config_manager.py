"""code for reading and writing project parameters"""

import yaml
from types import SimpleNamespace
import logging
import pathlib
from bigtankcontroller.utils import generate_logging_decorator

logger = logging.getLogger(__name__)
logging_decorator = generate_logging_decorator(logger)

class ConfigManager:

    @logging_decorator
    def __init__(self, config_path: pathlib.Path):
        """
        class for reading and writing  configuration files
        :param config_path: path to config file
        """
        self.config_path = config_path
        if self.config_exists():
            self.load_config()
        else:
            self.config = None

    @logging_decorator
    def config_exists(self):
        if not self.config_path or not self.config_path.exists():
            return False
        return True

    @logging_decorator
    def load_config(self):
        with open(str(self.config_path), 'r') as f:
            self.config = yaml.load(f, yaml.FullLoader)

    @logging_decorator
    def write_config(self):
        self.config_path.parent.mkdir(exist_ok=True, parents=True)
        with open(str(self.config_path), 'w') as f:
            yaml.dump(self.config, f)

    @logging_decorator
    def generate_new_config(self):
        config = {
            'cloud_data_dir': None,   # cloud path, including the rclone remote, where the projects will upload
            'cam_serials': None,
            'start_hour': 7,
            'stop_hour': 19
            }
        self.config = config
        self.write_config()

    @logging_decorator
    def config_as_namespace(self):
        return SimpleNamespace(**self.config)
