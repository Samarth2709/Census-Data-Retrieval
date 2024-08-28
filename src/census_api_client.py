import aiohttp
import asyncio
from typing import Dict, Any, List, Tuple, Optional, Union
import os, time, json
from utils.logging_config import get_logger
from utils.config_loader import config
from input_parser import InputParser
from url_generator import URLGenerator

logger = get_logger(__name__)

class CensusAPIClient:
    def __init__(self):
        self.max_retries = config.get('error_handling.max_retries', 3)
        self.retry_delay = config.get('error_handling.retry_delay', 5)
        self.concurrent_requests = config.get('performance.concurrent_requests', 5)
        self.request_timeout = config.get('performance.request_timeout', 30)

    async def fetch_data(self, urls: Dict[str, Dict[int, Dict[str, str]]]) -> Dict[str, Dict[int, Optional[Dict[str, Any]]]]:
        """Fetch data for multiple URLs concurrently."""
        logger.info("Starting data fetch process")
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stat_name, year_urls in urls.items():
                for year, url_types in year_urls.items():
                    primary_url = url_types.get('primary')
                    backup_url = url_types.get('backup')
                    task = asyncio.ensure_future(self._fetch_with_retry(session, stat_name, year, primary_url, backup_url))
                    tasks.append(task)

            semaphore = asyncio.Semaphore(self.concurrent_requests)
            results = await asyncio.gather(*[self._bounded_fetch(semaphore, task) for task in tasks])

        organized_results = {}
        for result in results:
            stat_name, year, data = result
            if stat_name not in organized_results:
                organized_results[stat_name] = {}
            # organized_results[stat_name][year] = self.process_response(data) if data else None
            organized_results[stat_name][year] = self.reformat_data(data) if data else None
            # data is [[header1, header2], [VALUE1, value2]]
            # Creae a function to process the response
            # Function should return a list like so[VALUE1, header1]

        logger.info("Data fetch process completed")
        return organized_results

    async def _bounded_fetch(self, semaphore: asyncio.Semaphore, task: asyncio.Future) -> Tuple[str, int, Any]:
        async with semaphore:
            return await task

    async def _fetch_with_retry(self, session: aiohttp.ClientSession, stat_name: str, year: int, primary_url: str, backup_url: Optional[str] = None) -> Tuple[str, int, Optional[List[List[str]]]]:
        for attempt in range(self.max_retries):
            try:
                data = await self._make_request(session, primary_url)
                logger.info(f"Successfully fetched data for {stat_name}, year {year} using primary URL")
                return stat_name, year, data
            except aiohttp.ClientError as e:
                logger.warning(f"Attempt {attempt + 1} failed for {stat_name}, year {year} using primary URL: {str(e)}")
                if backup_url and attempt == self.max_retries - 1:
                    try:
                        data = await self._make_request(session, backup_url)
                        logger.info(f"Successfully fetched data for {stat_name}, year {year} using backup URL")
                        return stat_name, year, data
                    except aiohttp.ClientError as be:
                        logger.error(f"Backup URL fetch failed for {stat_name}, year {year}: {str(be)}")
                elif attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to fetch data for {stat_name}, year {year} after {self.max_retries} attempts")
        return stat_name, year, None

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> List[List[str]]:
        async with session.get(url, timeout=self.request_timeout) as response:
            response.raise_for_status()
            data = await response.json()
            if not isinstance(data, list) or not all(isinstance(row, list) for row in data):
                raise ValueError("Unexpected response format from API")
            return data
    
    def reformat_data(self, data: List[List[str]]) -> Optional[List[Union[float, str]]]:
        """
        Reformats data by getting header1 (key identifier of the stat data) and value1 (value of the stat data) from the input list.
        Input list is the response data from the API.
        Output is a list with header1 and value1 as the first two elements.

        Args:
            data (List[List[str]]): Response from the Census API in the format: [[header1, header2], [value1, value2]]

        Returns:
            List[str]: Reformatted data in the format: [value1, header1]
        """
        logger.debug(f"Reformatting data: {data}")

        # Check if input is valid format, check if there is a value for the first elements of each list
        if len(data) != 2 or len(data[0]) != len(data[1]):
            logger.error("Invalid input data format")
            return None
        elif not data[0][0] or not data[1][0]:
            logger.error(f"No data found as statistic header or value.\nStatistic:{data}")
            return None

        # Extract the headers and values from the input list
        header = data[0][0]
        value = data[1][0]

        # Try to convert value to an float, except error and give warning
        try:
            value = float(value)
        except ValueError as e:
            logger.warning(f"Failed to convert value ({value}) to float: {str(e)}")
        
        # Reformat the data by swapping the positions of the first value and first header
        reformatted_data = [value, header]
        logger.debug(f"Reformatted data: {reformatted_data}")
        return reformatted_data


# Usage example remains the same

# Usage example
async def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the JSON file
    json_path = os.path.join(current_dir, "..", "data", "input", "census_stats_config.json")

    # Parse input
    input_parser = InputParser(json_path)
    statistics = input_parser.get_statistics()

    # Generate URLs
    url_generator = URLGenerator(statistics)
    urls = url_generator.generate_urls()

    # url_generator.print_urls(urls)

    # Fetch data
    client = CensusAPIClient()
    results = await client.fetch_data(urls)

    print(json.dumps(results, indent=2))
if __name__ == "__main__":
    asyncio.run(main())