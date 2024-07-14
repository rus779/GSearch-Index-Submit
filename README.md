## Google Search Console URL Indexing Script

This Python script automates the process of checking the indexing status of URLs on your website and submitting non-indexed URLs to Google Search Console for faster indexing. It leverages Google's official APIs: Google Custom Search API for retrieving indexing status and Indexing API for submitting URLs.

### Key Features
- Retrieves indexing status for up to 100 URLs per run
- Submits up to 200 non-indexed URLs to Google Search Console per run
- Extracts URLs from sitemaps (supports multiple sitemaps)
- Allows excluding specific URLs from indexing
- Sorts URLs based on configurable rules and optional alphabetical sorting
- Stores URL data in a CSV file for tracking and future runs

### Prerequisites
To use this script, you'll need:
1. Custom Search Engine ID
2. API key for Google Custom Search API
3. Service Account JSON Key for Google Indexing API

Refer to these resources for setup instructions:
- [Programmable Search Engine](https://developers.google.com/custom-search/docs/overview)
- [Indexing API Quickstart](https://developers.google.com/search/apis/indexing-api/v3/quickstart)

### Setup
1. Create a folder to store the script files.
2. Download the script files (`setup.py`, `Google-Search-Update.py`) into the folder.
3. Place your Service Account JSON Key file in the same folder and rename it to `service_account.json`.
4. Run the setup script: `python3 setup.py`
5. Answer the prompts to configure the script settings.

The setup script will:
- Create a virtual environment to isolate dependencies
- Install required Python packages
- Create a `config.py` file with your settings
- Create a `sitemaps` folder to store downloaded sitemaps
- Create a `run-Google-Search-Update.command` file for easy script execution

### Usage
After setup, you can run the script by double-clicking the `run-Google-Search-Update.command` file or executing it from the terminal.

The script will perform the following steps:
1. Download sitemap files and extract URLs
2. Sort URLs based on configured rules
3. Check the indexing status of URLs using Google Custom Search API
4. Submit non-indexed URLs to Google Search Console using Indexing API
5. Store URL data and statuses in the `URLs.csv` file

Upon completion, you will find:
- `URLs.csv`: File containing URLs and their indexing statuses
- `results.txt`: Summary of the script's actions
- `script.log`: Detailed log of the script's execution

### Limitations
Please note the following limitations set by Google:
- 100 URLs per day for checking indexing status
- 200 URLs per day for submitting to Google Search Console

### Troubleshooting
If you encounter any issues or errors, please check the `script.log` file for detailed information. Ensure that your API keys and service account JSON key are valid and have the necessary permissions.

For further assistance, please refer to the Google Search Console and Google Cloud Platform documentation or contact their support channels.
