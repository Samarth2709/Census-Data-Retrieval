import logging
import logging.config
import yaml
import os

def setup_logging():
    """Set up logging configuration"""
    # Get the path to the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    config_path = os.path.join(project_root, 'config', 'logging.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f.read())
    
    # Set the log file path
    log_file_path = os.path.join(project_root, 'data', 'census_data_tool.log')
    config['handlers']['file']['filename'] = log_file_path
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
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
# Usage example:
# from utils.logging_config import get_logger
# 
# # In your module (e.g., census_api_client.py):
# logger = get_logger(__name__)
# 
# def some_function():
#     logger.debug("This is a debug message")
#     logger.info("This is an info message")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")
#     try:
#         # Some operation that might raise an exception
#         raise ValueError("Example exception")
#     except Exception as e:
#         logger.exception("An error occurred: %s", str(e))
