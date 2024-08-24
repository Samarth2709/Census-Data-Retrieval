import re
from datetime import datetime
from typing import List, Tuple
from urllib.parse import urlparse, parse_qs

from utils.config_loader import config
from utils.logging_config import get_logger

logger = get_logger(__name__)

class InputValidationError(Exception):
    """Custom exception for input validation errors."""
    pass

def validate_api_url(url: str) -> bool:
    """
    Validate the Census API URL format.
    
    Args:
        url (str): The API URL to validate.
    
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    pattern = r'^https://api\.census\.gov/data/\d{4}/.*$'
    return bool(re.match(pattern, url))

def parse_api_url(url: str) -> dict:
    """
    Parse the Census API URL and extract key components.
    
    Args:
        url (str): The API URL to parse.
    
    Returns:
        dict: A dictionary containing the parsed components.
    """
    parsed_url = urlparse(url)
    path_components = parsed_url.path.split('/')
    query_params = parse_qs(parsed_url.query)
    
    return {
        'year': path_components[3],
        'dataset': '/'.join(path_components[4:]),
        'variables': query_params.get('get', []),
        'geography': query_params.get('for', [])
    }

def validate_year_range(start_year: int, end_year: int) -> Tuple[int, int]:
    """
    Validate the provided year range.
    
    Args:
        start_year (int): The start year.
        end_year (int): The end year.
    
    Returns:
        Tuple[int, int]: The validated start and end years.
    
    Raises:
        InputValidationError: If the year range is invalid.
    """
    current_year = datetime.now().year
    max_years = config.get('data_retrieval.max_years_per_query', 3)
    
    if start_year > end_year:
        raise InputValidationError("Start year must be less than or equal to end year.")
    
    if end_year > current_year:
        raise InputValidationError(f"End year cannot be in the future. Current year: {current_year}")
    
    if end_year - start_year + 1 > max_years:
        raise InputValidationError(f"Year range cannot exceed {max_years} years.")
    
    return start_year, end_year

def generate_urls(base_url: str, start_year: int, end_year: int) -> List[str]:
    """
    Generate URLs for different years based on the parsed components.
    
    Args:
        base_url (str): The base API URL.
        start_year (int): The start year.
        end_year (int): The end year.
    
    Returns:
        List[str]: A list of generated URLs for each year in the range.
    """
    parsed_components = parse_api_url(base_url)
    urls = []
    
    for year in range(start_year, end_year + 1):
        new_url = f"https://api.census.gov/data/{year}/{parsed_components['dataset']}?get={','.join(parsed_components['variables'])}&for={','.join(parsed_components['geography'])}"
        urls.append(new_url)
    
    return urls

def process_user_input(api_url: str, start_year: int, end_year: int) -> List[str]:
    """
    Process and validate user input, then generate appropriate URLs.
    
    Args:
        api_url (str): The Census API URL provided by the user.
        start_year (int): The start year for data retrieval.
        end_year (int): The end year for data retrieval.
    
    Returns:
        List[str]: A list of generated URLs for each year in the validated range.
    
    Raises:
        InputValidationError: If any input validation fails.
    """
    if not validate_api_url(api_url):
        raise InputValidationError("Invalid Census API URL format.")
    
    start_year, end_year = validate_year_range(start_year, end_year)
    
    urls = generate_urls(api_url, start_year, end_year)
    
    logger.info(f"Generated {len(urls)} URLs for years {start_year}-{end_year}")
    return urls

# Usage examples:

# Example URL
example_url = "https://api.census.gov/data/2022/acs/acs5/subject?get=group(S1901)&ucgid=1600000US1743250"

# 1. Validate API URL
print(f"Is URL valid? {validate_api_url(example_url)}")  # Should print: Is URL valid? True

# 2. Parse API URL
parsed_url = parse_api_url(example_url)
print("Parsed URL components:")
print(f"Year: {parsed_url['year']}")
print(f"Dataset: {parsed_url['dataset']}")
print(f"Variables: {parsed_url['variables']}")
print(f"Geography: {parsed_url['geography']}")

# 3. Validate year range
try:
    validated_years = validate_year_range(2020, 2022)
    print(f"Validated year range: {validated_years}")
except InputValidationError as e:
    print(f"Year validation error: {str(e)}")

# 4. Generate URLs
generated_urls = generate_urls(example_url, 2020, 2022)
print("Generated URLs:")
for url in generated_urls:
    print(url)

# 5. Process user input (main function)
try:
    final_urls = process_user_input(example_url, 2020, 2022)
    print("Final processed URLs:")
    for url in final_urls:
        print(url)
except InputValidationError as e:
    print(f"Input processing error: {str(e)}")

# 6. Error handling examples
print("\nError handling examples:")

# Invalid URL
try:
    process_user_input("https://invalid-url.com", 2020, 2022)
except InputValidationError as e:
    print(f"Invalid URL error: {str(e)}")

# Invalid year range
try:
    process_user_input(example_url, 2022, 2020)
except InputValidationError as e:
    print(f"Invalid year range error: {str(e)}")

# Year range exceeding maximum
try:
    process_user_input(example_url, 2018, 2022)
except InputValidationError as e:
    print(f"Excessive year range error: {str(e)}")

# Future year
current_year = datetime.now().year
try:
    process_user_input(example_url, current_year, current_year + 1)
except InputValidationError as e:
    print(f"Future year error: {str(e)}")
