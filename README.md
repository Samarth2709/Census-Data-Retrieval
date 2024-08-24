# Census Data Retrieval Tool

## Overview

The Census Data Retrieval Tool is a Python-based application designed to simplify the process of gathering and analyzing US city census data. This tool is particularly useful for commercial real estate investors and researchers who need quick access to structured, relevant census information.

## Features

- Retrieve specific US city census data using the U.S. Census Bureau's API
- Process user-provided API URLs for flexible data selection
- Retrieve data for specified years or year ranges
- Organize data into meaningful sections for easy analysis
- Generate structured markdown output for clear data presentation
- Secure API key management

## Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/census-data-retrieval-tool.git
   cd census-data-retrieval-tool
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Census API key:
   - Copy `.env.example` to `.env`
   - Open `.env` and replace `YOUR_API_KEY_HERE` with your actual Census API key

## Usage

1. Navigate to https://data.census.gov/ and select your desired data table
2. Click the API button to reveal the 'Data Link' and copy the URL
3. Run the tool with the following command:
   ```
   python src/main.py --url "YOUR_COPIED_URL" --years 2020,2021,2022
   ```
   Replace `YOUR_COPIED_URL` with the URL you copied, and adjust the years as needed

4. The tool will generate a markdown file in the `data/processed/` directory with the retrieved and formatted census data

For more detailed information on using the tool, please refer to the user guide in the `docs/` directory.
