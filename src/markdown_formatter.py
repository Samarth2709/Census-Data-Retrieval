import json
from typing import Dict, Any, List
import os
import asyncio
from utils.logging_config import get_logger
from input_parser import InputParser
from url_generator import URLGenerator
from census_api_client import CensusAPIClient


logger = get_logger(__name__)

class MarkdownFormatter:
    def __init__(self, data: Dict[str, Dict[int, List[Any]]]):
        """
        Initialize the MarkdownFormatter with census data.
        
        :param data: A nested dictionary containing census data organized by statistic and year.
        """
        self.data = data
        logger.info("MarkdownFormatter initialized with data")

    def generate_markdown(self, show_variable_key) -> str:
        """
        Generate the complete markdown content including table of contents,
        list format, and table format representations of the census data.
        
        :return: A string containing the formatted markdown content.
        """
        logger.info("Generating markdown content")
        try:
            markdown = "# Census Data Report\n\n"
            markdown += self._generate_toc()
            markdown += self._generate_list_format(show_variable_key)
            markdown += self._generate_table_format(show_variable_key)
            logger.info("Markdown content generated successfully")
            return markdown
        except Exception as e:
            logger.error(f"Error generating markdown content: {str(e)}")
            raise

    def _generate_toc(self) -> str:
        """
        Generate the table of contents for the markdown report.
        
        :return: A string containing the formatted table of contents.
        """
        logger.debug("Generating table of contents")
        toc = "## Table of Contents\n\n"
        toc += "1. [List Format](#list-format)\n"
        toc += "2. [Table Format](#table-format)\n"
        for statistic in self.data.keys():
            toc += f"   - [{statistic}](###{statistic.lower().replace(' ', '-')})\n"
        return toc + "\n"

    def _generate_list_format(self, show_variable_key) -> str:
        """
        Generate a list format representation of the census data.
        
        :return: A string containing the census data in list format.
        """

        logger.debug("Generating list format")
        list_format = "## List Format\n\n"
        for statistic, years_data in self.data.items():
            list_format += f"### {statistic}\n\n"
            for year, data in years_data.items():
                if show_variable_key:
                    list_format += f"- {year}: {data[0]} ({data[1]})\n"
                else:
                    list_format += f"- {year}: {data[0]}\n"
            list_format += "\n"
        return list_format

    def _generate_table_format(self, show_variable_key) -> str:
        """
        Generate a table format representation of the census data.
        
        :return: A string containing the census data in table format.
        """
        logger.debug("Generating table format")
        table_format = "## Table Format\n\n"
        for statistic, years_data in self.data.items():
            table_format += f"### {statistic}\n\n"
            if show_variable_key:
                table_format += "| Year | Value | Identifier |\n"
                table_format += "|------|-------|------------|\n"
                for year, data in sorted(years_data.items()):
                    table_format += f"| {year} | {data[0]} | {data[1]} |\n"
            else:
                table_format += "| Year | Value |\n"
                table_format += "|------|-------|\n"
                for year, data in sorted(years_data.items()):
                    table_format += f"| {year} | {data[0]} |\n"
            table_format += "\n"
        return table_format
    
    def save_markdown(self, filename: str, show_variable_key = True):
        """
        Save the generated markdown content to a file.
        
        :param filename: The path and name of the file to save the markdown content.
        """
        logger.info(f"Saving markdown to file: {filename}")
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            if show_variable_key:
                logger.info("Variable keys will be shown in the markdown")
            else:
                logger.info("Variable keys will not be shown in the markdown")

            with open(filename, 'w') as f:
                f.write(self.generate_markdown(show_variable_key=show_variable_key))
            logger.info(f"Markdown file saved successfully: {filename}")
        except IOError as e:
            logger.error(f"IOError while saving markdown file: {str(e)}")
            quit(1)
        except Exception as e:
            logger.error(f"Unexpected error while saving markdown file: {str(e)}")
            quit(1)

# Comprehensive example usage
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

    # Fetch data
    client = CensusAPIClient()
    results = await client.fetch_data(urls)

    # Generate markdown
    formatter = MarkdownFormatter(results)
    output_path = os.path.join(current_dir, "..", "data", "output", "census_data_report.md")
    formatter.save_markdown(output_path)

    print(f"Markdown file generated: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())