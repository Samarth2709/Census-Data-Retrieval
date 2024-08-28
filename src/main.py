import os
import asyncio
from input_parser import InputParser
from url_generator import URLGenerator
from census_api_client import CensusAPIClient
from markdown_formatter import MarkdownFormatter

async def main():
    try:
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

        # Fetch data
        client = CensusAPIClient()
        results = await client.fetch_data(urls)

        # Generate markdown
        formatter = MarkdownFormatter(results)
        output_path = os.path.join(current_dir, "data", "output", "census_data_report.md")
        formatter.save_markdown(output_path)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())