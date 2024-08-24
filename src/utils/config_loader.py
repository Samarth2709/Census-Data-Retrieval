import os
import yaml
from dotenv import load_dotenv
from typing import Any, Dict

class Configuration:
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.load_config()
        self.load_env_variables()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
        with open(config_path, 'r') as config_file:
            self.config = yaml.safe_load(config_file)

    def load_env_variables(self):
        load_dotenv()
        self.config['api']['key'] = os.getenv('CENSUS_API_KEY')

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                return default
        return value

def load_configuration() -> Configuration:
    return Configuration()

# Global configuration instance
config = load_configuration()

# Usage example:
# from utils.config_loader import config
# api_key = config.get('api.key')
# default_year = config.get('data_retrieval.default_year')
# output_directory = config.get('output.directory')
# max_retries = config.get('error_handling.max_retries')
