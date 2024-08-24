import logging
import logging.config
import yaml
import os

def setup_logging():
    """Set up logging configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'logging.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): The name of the logger, typically __name__ of the calling module.
    
    Returns:
        logging.Logger: A configured logger instance.
    """
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger(name)
