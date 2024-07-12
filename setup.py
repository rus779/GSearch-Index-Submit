import os
import json
import subprocess
import venv

def ask_question(question, default=None):
    if default:
        response = input(f"{question} (Press Enter for default: {default}): ").strip()
        return response if response else default
    return input(question + " ").strip()

def create_config_file(script_dir):
    files_dir = ask_question("Where do you want to put files for the script? (Press Enter to use the current directory)", script_dir)
    web_site = ask_question("What web site do you want to service?")
    exclude_urls = []
    while True:
        url = ask_question("Enter a URL to exclude from indexing (or press Enter to finish):")
        if not url:
            break
        exclude_urls.append(url)
    custom_search_engine_id = ask_question("What is your Custom Search Engine ID?")
    api_key = ask_question("What is your API key for Google Custom Search API?")
    json_key_file = ask_question("What is the path for Service Account JSON Key file? (Press Enter to use the current directory)", os.path.join(script_dir, 'service_account.json'))
    
    use_alphabetical_sorting = ask_question("Do you want to sort URLs alphabetically? (yes/no)").lower() == 'yes'

    config_content = f"""
import os

# Configuration variables
MAX_INDEXING_URLS_PER_RUN = 100
MAX_SUBMISSION_URLS_PER_RUN = 200
EXCLUDE_URLS = {json.dumps(exclude_urls)}
JSON_KEY_FILE = '{os.path.relpath(json_key_file, script_dir)}'
WEB_SITE = '{web_site}'
FILES_DIR = '{os.path.relpath(files_dir, script_dir)}'
SITEMAP_DIR = os.path.join(FILES_DIR, 'sitemaps')
API_KEY = '{api_key}'
CUSTOM_SEARCH_ENGINE_ID = '{custom_search_engine_id}'

# Sorting rules (generic placeholders)
SORTING_RULES = {{
    '1_urls': lambda url: True,  # Replace with your first sorting rule
    '2_urls': lambda url: True,  # Replace with your second sorting rule
    '3_urls': lambda url: True,  # Replace with your third sorting rule
    '4_urls': lambda url: True   # Replace with your fourth sorting rule
}}

# Alphabetical sorting option
USE_ALPHABETICAL_SORTING = {use_alphabetical_sorting}
"""

    with open(os.path.join(script_dir, 'config.py'), 'w') as f:
        f.write(config_content)

    print("Configuration file 'config.py' created successfully.")

def install_dependencies(venv_path):
    required_packages = [
        'oauth2client',
        'httplib2',
        'pandas',
        'requests',
        'google-api-python-client'
    ]

    pip_path = os.path.join(venv_path, 'bin', 'pip')
    for package in required_packages:
        subprocess.check_call([pip_path, "install", package])

    print("All required packages have been installed.")

def create_virtual_environment(script_dir):
    venv_path = os.path.join(script_dir, 'venv')
    venv.create(venv_path, with_pip=True)
    return venv_path

def main():
    print("Welcome to the Google Search Update script setup!")
    script_dir = os.getcwd()
    venv_path = create_virtual_environment(script_dir)
    create_config_file(script_dir)
    install_dependencies(venv_path)
    
    # Check if 'Google Search Update.py' exists in the current directory
    source_file = 'Google Search Update.py'
    if os.path.exists(source_file):
        print(f"'{source_file}' file is already in the correct location.")
    else:
        print(f"Warning: '{source_file}' file not found in the current directory.")
        print("Please ensure that 'Google Search Update.py' is in the same directory as 'setup.py'.")
    
    print(f"Setup complete. Virtual environment created at: {venv_path}")
    print("To activate the virtual environment and run the script:")
    print(f"1. Run: source {os.path.join(venv_path, 'bin', 'activate')}")
    print(f"2. Then run: python '{source_file}'")

if __name__ == "__main__":
    main()
