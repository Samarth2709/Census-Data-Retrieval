import re
from typing import List, Optional
from datetime import datetime
from utils.logging_config import get_logger
from utils.config_loader import config

logger = get_logger(__name__)

def validate_url(url: str) -> bool:
    """
    Validate if the given URL is a valid Census API URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    if not url or not url.strip():
        logger.error("Empty or whitespace-only URL provided")
        return False
    
    pattern = r'^https://api\.census\.gov/data/\d{4}/.*$'
    is_valid = bool(re.match(pattern, url))
    if not is_valid:
        logger.error(f"Invalid URL format: {url}")
    return is_valid

def validate_years(years: List[int]) -> bool:
    """
    Validate if the given years are valid for Census API queries.

    Args:
        years (List[int]): List of years to validate.

    Returns:
        bool: True if all years are valid, False otherwise.
    """
    # Check if years is empty or None
    if years is None or len(years) == 0:
        logger.warn("No years provided to validate.") 
    
    current_year = datetime.now().year
    min_year = config.get('data_retrieval.min_year', 1790)
    is_valid = all(min_year <= year <= current_year for year in years)
    if not is_valid:
        logger.error(f"Invalid years: {years}. Years must be between {min_year} and {current_year}")
    return is_valid

# Get year from URL
def get_year_from_url(base_url: str) -> int:
    """
    Extract the year from the given URL.

    Args:
        base_url (str): The URL to extract the year from.

    Returns:
        int: The extracted year.
    """
    # Extract the year from the base URL
    base_year_match = re.search(r'/data/(\d{4})/', base_url)
    if not base_year_match:
        logger.error(f"Could not extract year from base URL: {base_url}")
        raise ValueError("Could not extract year from base URL")
    base_year = base_year_match.group(1)
    return int(base_year)

def generate_urls(base_url: str, years: Optional[List[int]] = None) -> List[str]:
    """
    Generate URLs for the given years based on the base URL.
    If no years are provided, return the base URL as is.
    If the number of years exceeds the maximum allowed, use only the most recent years up to the maximum.

    Args:
        base_url (str): The base URL to use as a template.
        years (Optional[List[int]]): List of years to generate URLs for. Defaults to None.

    Returns:
        List[str]: List of generated URLs.
    """
    logger.info(f"Generating URLs for base_url: {base_url} and years: {years}")
    
    if not validate_url(base_url):
        logger.error(f"Invalid base URL provided: {base_url}")
        raise ValueError("Invalid base URL provided")

    if years is None or len(years) == 0:
        logger.info("No years provided. Returning base URL.")
        return [base_url]

    if not validate_years(years):
        logger.error(f"Invalid years provided: {years}")
        raise ValueError("Invalid years provided")
    
    # Limit the number of years to the maximum allowed
    max_years = config.get('data_retrieval.max_years_per_query', 3) # Maximum number of years allowed per query, if not specified in config use default value (3)
    if len(years) > max_years:
        logger.warning(f"Number of years ({len(years)}) exceeds maximum allowed ({max_years}). Using only the most recent {max_years} years.")
        years = sorted(years, reverse=True)[:max_years]

    base_year = get_year_from_url(base_url)

    # Generate new URLs by replacing the year
    urls = []
    for year in years:
        new_url = base_url.replace(f"/data/{base_year}/", f"/data/{year}/")
        urls.append(new_url)

    logger.info(f"Generated {len(urls)} URLs")
    return urls

# Example usage
if __name__ == "__main__":
    # Example usage for validate_url function
    print("Testing validate_url function:")
    test_urls = [
        "https://api.census.gov/data/2022/acs/acs5/subject?get=group(S2503)&ucgid=1600000US1743250",
        "https://api.census.gov/data/2023/acs/acs5/subject?get=group(S2503)&ucgid=1600000US1743250",
        "https://api.census.gov/data/invalid/acs/acs5/subject?get=group(S2503)&ucgid=1600000US1743250",
        "https://example.com/invalid-url"
    ]
    for url in test_urls:
        print(f"URL: {url}")
        print(f"Is valid: {validate_url(url)}")
        print()

    # Example usage for validate_years function
    print("Testing validate_years function:")
    test_year_sets = [
        [2020, 2021, 2022],
        [1900, 1950, 2000],
        [2022, 2023, 2024],
        [1700, 1800, 1900]
    ]
    for years in test_year_sets:
        print(f"Years: {years}")
        print(f"Are valid: {validate_years(years)}")
        print()

    # Example usage for generate_urls function
    base_url = "https://api.census.gov/data/2022/acs/acs5/subject?get=group(S2503)&ucgid=1600000US1743250"
    
    # Test with years provided (within max limit)
    years = [2020, 2021, 2022]
    try:
        generated_urls = generate_urls(base_url, years)
        logger.info("Generated URLs with years (within max limit):")
        for url in generated_urls:
            logger.info(url)
    except ValueError as e:
        logger.error(f"Error generating URLs: {str(e)}")

    # Test with years provided (exceeding max limit)
    years = [2018, 2019, 2020, 2021, 2022]
    try:
        generated_urls = generate_urls(base_url, years)
        logger.info("Generated URLs with years (exceeding max limit):")
        for url in generated_urls:
            logger.info(url)
    except ValueError as e:
        logger.error(f"Error generating URLs: {str(e)}")

    # Test without years provided
    try:
        generated_urls = generate_urls(base_url)
        logger.info("Generated URLs without years:")
        for url in generated_urls:
            logger.info(url)
    except ValueError as e:
        logger.error(f"Error generating URLs: {str(e)}")