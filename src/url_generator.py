import urllib.parse
from typing import Dict, List
from utils.logging_config import get_logger
from utils.config_loader import config

logger = get_logger(__name__)

class URLGenerator:
    def __init__(self, parsed_data: List[Dict]):
        self.parsed_data = parsed_data
        logger.info("Initializing URLGenerator")

    def generate_urls(self) -> Dict[str, Dict[int, str]]:
        """
        Generate URLs for each statistic and year. The URLs are generated by replacing the [year] placeholder
        in the API URL template with the actual year and adding the API key. The generated URLs are stored in a
        dictionary with statistic names as keys, containing nested dictionaries with years as keys and URLs as values.
        
        Returns:
            A dictionary with statistic names as keys, containing nested dictionaries
            with years as keys and generated URLs as values.
        """
        urls = {}
        logger.info("Generating URLs for all statistics and years")
        for stat in self.parsed_data:
            stat_name = stat['name']
            urls[stat_name] = {}
            for year in stat['years']:
                url = self._generate_single_url(stat['api_url'], year)
                urls[stat_name][year] = url
                logger.debug(f"Generated URL for {stat_name}, year {year}: {url}")
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

    def encode_url(self, url: str) -> str:
        """
        Encode the URL to ensure all characters are properly escaped.
        
        Args:
            url: The URL to be encoded.
        
        Returns:
            The encoded URL as a string.
        """
        return urllib.parse.quote(url, safe=':/?&=')
    
    def print_urls(self, urls: Dict[str, Dict[int, str]]) -> None:
        """
        Print each URL along with its statistic name and year.
        
        Args:
            urls: A dictionary with statistic names as keys, containing nested dictionaries
                  with years as keys and URLs as values.
        """
        for stat_name, years in urls.items():
            for year, url in years.items():
                print(f"{stat_name} {year}: {url}")

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

    # Print generated URLs
    for stat_name, years in generated_urls.items():
        print(f"\nURLs for {stat_name}:")
        for year, url in years.items():
            print(f"  {year}: {url}")

    # Example of URL encoding
    example_url = generated_urls[list(generated_urls.keys())[0]][list(generated_urls[list(generated_urls.keys())[0]].keys())[0]]
    encoded_url = url_generator.encode_url(example_url)
    print(f"\nExample of encoded URL:\n{encoded_url}")