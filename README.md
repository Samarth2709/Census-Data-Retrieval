# Census Data Retrieval Tool

## Project Description

The Census Data Retrieval Tool is a Python-based application designed to fetch and process US city census data from the U.S. Census Bureau's API. This tool is particularly useful for commercial real estate investors and analysts who need structured, easy-to-read census data for their decision-making processes.

The application reads a JSON configuration file containing census statistics information, dynamically generates API URLs for specified years, retrieves the data, and presents it in a structured markdown format. This format is optimized for both human readability and further processing by Language Models (LLMs).

### Key Features:
- Dynamic API URL generation based on user-defined statistics and years
- Efficient data retrieval from the U.S. Census Bureau's API
- Structured markdown output for easy analysis
- Flexible configuration through JSON input files

### Challenges Faced:
One major challenge in developing this tool was identifying the correct statistic codes for the Census API configuration. The U.S. Census Bureau provides a vast array of statistics, each with its unique code. Matching these codes to the desired statistics proved to be a complex task, requiring careful research and validation.

## Installation and Setup

To install and run the Census Data Retrieval Tool, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/census-data-retrieval-tool.git
   cd census-data-retrieval-tool
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Census API key:
   - Create a `.env` file in the project root directory
   - Add your Census API key to the file:
     ```
     CENSUS_API_KEY=your_api_key_here
     ```

## How to Use the Project

1. Prepare your input JSON file:
   - The input file should be named `census_stats_config.json` and placed in the `data/input/` directory.
   - The file should have the following structure:
     ```json
     {
       "statistics": [
         {
           "name": "Population",
           "description": "Total population count",
           "api_url": "https://api.census.gov/data/[year]/acs/acs5?get=B01003_001E&for=place:*&in=state:06",
           "years": [2019, 2020, 2021]
         },
         {
           "name": "Median Income",
           "description": "Median household income",
           "api_url": "https://api.census.gov/data/[year]/acs/acs5?get=B19013_001E&for=place:*&in=state:06",
           "years": [2018, 2019, 2020]
         }
       ],
     "location": "Libertyville, Illinois"
     }
     ```
   - Each statistic in the "statistics" array should include:
     - "name": A descriptive name for the statistic
     - "description": A brief description of what the statistic represents
     - "api_url": The URL for the Census API, with "[year]" as a placeholder
     - "years": An array of years for which to fetch the data

2. Run the main script:
   ```
   python src/main.py
   ```

3. The script will process the input, fetch the data, and generate a markdown report in the `data/output/` directory.

### Using Backup URLs

The tool supports the use of backup URLs for each statistic. To include a backup URL:

1. In your `census_stats_config.json` file, you can add a `cell_number` field for each statistic. This will be used to generate a backup URL if the primary URL fails:
   ```json
   {
     "statistics": [
       {
         "name": "Population",
         "description": "Total population count",
         "api_url": "https://api.census.gov/data/[year]/acs/acs5?get=B01003_001E&for=place:*&in=state:06",
         "years": [2019, 2020, 2021],
         "cell_number": "B01003_001E"
       }
     ],
     "location": "Libertyville, Illinois"
   }
   ```

2. The tool will attempt to use the primary URL first. If that fails, it will automatically generate and try a backup URL using the provided cell number.

## Reference Links
These links are important when creating the census_stat_config.json file. They provide information on API urls, API variables, available datasets, and usage instructions.

- [US Census Data Tables](https://data.census.gov/table)
- [Census Bureau Data API Course](https://www.census.gov/data/academy/courses/intro-to-the-census-bureau-data-api.html#2)
- [Working with the Census Data API](https://www.census.gov/content/dam/Census/library/publications/2020/acs/acs_api_handbook_2020_ch02.pdf)
- [Available Tables and Variables for Datasets](https://api.census.gov/data.html)
- [Request an API Key](https://api.census.gov/data/key_signup.html)