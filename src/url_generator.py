import re
import json
import urllib.parse
from typing import Dict, List, Any
from utils.logging_config import get_logger
from utils.config_loader import config

logger = get_logger(__name__)

class URLGenerator:
    def __init__(self, parsed_data: List[Dict[str, Any]]):
        self.parsed_data = parsed_data
        logger.info("Initializing URLGenerator")

    def generate_urls(self) -> Dict[str, Dict[str, Dict[int, str]]]:
        """
        Generate primary and backup URLs for each statistic and year.
        
        Returns:
            A dictionary with statistic names as keys, containing nested dictionaries
            with 'primary' and 'backup' keys, each containing a dictionary of years and URLs.
        """
        urls = {}
        logger.info("Generating URLs for all statistics and years")
        for stat in self.parsed_data:
            stat_name = stat['name']
            urls[stat_name] = {} 
            for year in stat['years']:
                urls[stat_name][year] = {}
                try:
                    primary_url = self._generate_single_url(stat['api_url'], year)
                    urls[stat_name][year]['primary'] = primary_url
                    logger.debug(f"Generated primary URL for {stat_name}, year {year}: {primary_url}")

                    if 'cell_number' in stat:
                        backup_url = self._generate_backup_url(stat['api_url'], year, stat['cell_number'])
                        urls[stat_name][year]['backup'] = backup_url
                        logger.debug(f"Generated backup URL for {stat_name}, year {year}: {backup_url}")
                except Exception as e:
                    logger.error(f"Error generating URL for {stat_name}, year {year}: {str(e)}")
                    urls[stat_name][year]['primary'] = None
                    ValueError(f"Error generating URL for {stat_name}, year {year}: {str(e)}")
        
        """
        A backup url is not guaranteed structure of urls:
        {
            "statistic1": {
                2010: {"primary": "https://api.example.com/2010?key=API_KEY", 
                    "backup": "https://api.example.com/2010?key=API_KEYbackup},
                2011: {"primary": "https://api.example.com/2011?key=API_KEY", 
                    "backup": "https://api.example.com/2011?key=API_KEYbackup},
                2012: {"primary": "https://api.example.com/2012?key=API_KEY"}
                ...
            },
            "statistic2": {
                2010: {"primary": "https://api.example.com/2010?key=API_KEY", 
                    "backup": "https://api.example.com/2010?key=API_KEYbackup},
                2011: {"primary": "https://api.example.com/2011?key=API_KEY"},
                2012: {"primary": "https://api.example.com/2012?key=API_KEY",
                    "backup": "https://api.example.com/2012?key=API_KEYbackup}
                }
                ...
            },
        """
        
        return urls

    def _generate_single_url(self, api_url: str, year: int) -> str:
        """
        Generate a single URL by replacing the [year] placeholder and adding the API key.
        
        Args:
            api_url: The API URL template from the input data.
            year: The year to be inserted into the URL.
        
        Returns:
            The generated URL as a string.
        """
        url = api_url.replace('[year]', str(year))
        api_key = config.get('api.key')
        if not api_key:
            logger.warning("API key not found in configuration. URL will not contain an API key.")
            return url
        
        url += f"&key={urllib.parse.quote(api_key)}"
        return url

    def _generate_backup_url(self, api_url: str, year: int, cell_number: str) -> str:
        """
        Generate a backup URL by replacing the [year] placeholder, the value after 'get=',
        and adding the API key.
        
        Args:
            api_url: The API URL template from the input data.
            year: The year to be inserted into the URL.
            cell_number: The cell number to be used in place of the original 'get=' value.
        
        Returns:
            The generated backup URL as a string.
        """
        url = api_url.replace('[year]', str(year))
        
        url = re.sub(r"(?<=get=)[^&]+", cell_number, url)
        
        api_key = config.get('api.key')
        if not api_key:
            logger.warning("API key not found in configuration. Backup URL will not contain an API key.")
            return url
        
        url += f"&key={urllib.parse.quote(api_key)}"
        return url

    def encode_url(self, url: str) -> str:
        """
        Encode the URL to ensure all characters are properly escaped.
        
        Args:
            url: The URL to be encoded.
        
        Returns:
            The encoded URL as a string.
        """
        return urllib.parse.quote(url, safe=':/?&=')

    def print_urls(self, urls: Dict[str, Dict[str, Dict[int, str]]]) -> None:
        """
        Print each URL along with its statistic name, year, and type (primary/backup).

        Args:
            urls: A dictionary with statistic names as keys, containing nested dictionaries
                  with years as keys, each containing a dictionary with 'primary' and optionally 'backup' URLs.
        """
        print(json.dumps(urls, indent=2))
        print("\n" * 5)
        for stat_name, years in urls.items():
            print(f"\n{stat_name}:")
            for year, url_types in years.items():
                for url_type, url in url_types.items():
                    print(f"  {url_type.capitalize()} {year}: {url}")

# Usage example
if __name__ == "__main__":
    from input_parser import InputParser
    import os

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the JSON file
    json_path = os.path.join(current_dir, "..", "data", "input", "census_stats_config.json")

    # Create an instance of InputParser and get the statistics
    input_parser = InputParser(json_path)
    statistics = input_parser.get_statistics()

    # Create an instance of URLGenerator
    url_generator = URLGenerator(statistics)

    # Generate URLs
    generated_urls = url_generator.generate_urls()
    print(generated_urls)

    # Print generated URLs using the print_urls function
    print("\nGenerated URLs:")
    url_generator.print_urls(generated_urls)

    # Example of URL encoding
    if generated_urls:
        # Get the first generated URL (assuming there's at least one)
        first_stat = next(iter(generated_urls))
        first_year = next(iter(generated_urls[first_stat]))
        first_url = generated_urls[first_stat][first_year]['primary']

        print("\nExample of URL encoding:")
        print(f"Original URL: {first_url}")
        encoded_url = url_generator.encode_url(first_url)
        print(f"Encoded URL: {encoded_url}")