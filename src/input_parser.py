import json
from typing import Dict, List, Any
import os
from utils.logging_config import get_logger

logger = get_logger(__name__)

class InputParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        logger.info(f"Initializing InputParser with file: {file_path}")
        self.data = self._read_json_file()

    def _read_json_file(self) -> Dict[str, Any]:
        """Read and parse the JSON file."""
        logger.debug(f"Attempting to read JSON file: {self.file_path}")
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            logger.info("Successfully read and parsed JSON file")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in the input file: {e}")
            raise ValueError(f"Invalid JSON format in the input file: {e}")
        except IOError as e:
            logger.error(f"Error reading the input file: {e}")
            raise IOError(f"Error reading the input file: {e}")

    def validate_structure(self) -> None:
        """Validate the structure of the parsed JSON data."""
        logger.info("Validating JSON structure")
        if not isinstance(self.data, dict):
            logger.error("Root element is not a dictionary")
            raise ValueError("Root element must be a dictionary")
        
        if 'statistics' not in self.data:
            logger.error("Missing 'statistics' key in the input data")
            raise ValueError("Missing 'statistics' key in the input data")
        
        if not isinstance(self.data['statistics'], list):
            logger.error("'statistics' is not a list")
            raise ValueError("'statistics' must be a list")
        
        for stat in self.data['statistics']:
            required_keys = ['name', 'description', 'api_url', 'years']
            for key in required_keys:
                if key not in stat:
                    logger.error(f"Missing '{key}' in a statistic entry")
                    raise ValueError(f"Missing '{key}' in a statistic entry")
            
            if not isinstance(stat['years'], list):
                logger.error("'years' is not a list")
                raise ValueError("'years' must be a list of integers")
            
            if not all(isinstance(year, int) for year in stat['years']):
                logger.error("Not all elements in 'years' are integers")
                raise ValueError("All elements in 'years' must be integers")
        
        logger.info("JSON structure validation successful")

    def get_statistics(self) -> List[Dict[str, Any]]:
        """Return the list of statistics."""
        logger.debug("Retrieving all statistics")
        return self.data['statistics']
    
    def get_location(self) -> str:
        """Get the location argument of the config file."""
        logger.debug("Retrieving location")
        try:
            return self.data['location']
        except KeyError:
            logger.warning("No location found in the input data")
        return ""

    def get_statistic_by_name(self, name: str) -> Dict[str, Any]:
        """Return a specific statistic by its name."""
        logger.debug(f"Retrieving statistic with name: {name}")
        for stat in self.data['statistics']:
            if stat['name'] == name:
                logger.info(f"Found statistic: {name}")
                return stat
        logger.warning(f"No statistic found with name: {name}")
        raise ValueError(f"No statistic found with name: {name}")

    def get_all_years(self) -> List[int]:
        """Return a sorted list of all unique years across all statistics."""
        logger.debug("Retrieving all unique years")
        years = set()
        for stat in self.data['statistics']:
            years.update(stat['years'])
        return sorted(list(years))

# Usage example
if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the JSON file
    json_path = os.path.join(current_dir, "..", "data", "input", "census_stats_config.json")
    
    try:
        # Create an instance of InputParser
        parser = InputParser(json_path)
        
        # Validate the structure
        parser.validate_structure()
        logger.info("Input file structure is valid.")
        
        # Example usage of methods
        logger.info(f"All statistics: {parser.get_statistics()}")
        logger.info(f"Years to process: {parser.get_all_years()}")
        logger.info(f"Population statistic: {parser.get_statistic_by_name('Population')}")
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")