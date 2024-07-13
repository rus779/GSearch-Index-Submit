import os
import json
import subprocess
import venv

def ask_question(question, default=None):
    if question == "What web site do you want to service?":
        response = input(f"{question} (Put 'http://' in front or https:// will be used as default): ").strip()
        if not response.startswith(('http://', 'https://')):
            response = 'https://' + response
        return response
    elif default:
        response = input(f"{question} (Press Enter for default: {default}): ").strip()
        return response if response else default
    return input(question + " ").strip()

def create_config_file(script_dir):
    files_dir = ask_question("Where do you want to put files for the script?", script_dir)
    web_site = ask_question("What web site do you want to service?")
    
    exclude_urls = ask_question("Enter URLs to exclude from indexing (comma-separated, can be absolute or relative):").split(',')
    exclude_urls = [url.strip() for url in exclude_urls if url.strip()]
    
    # Convert relative URLs to absolute
    exclude_urls = [url if url.startswith(('http://', 'https://')) else web_site + url for url in exclude_urls]

    custom_search_engine_id = ask_question("What is your Custom Search Engine ID?")
    api_key = ask_question("What is your API key for Google Custom Search API?")
    json_key_file = ask_question("What is the path for Service Account JSON Key file?", os.path.join(script_dir, 'service_account.json'))
    
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

def create_execution_script(venv_path):
    script_content = f"""#!/bin/bash
# Change to the directory containing this script
cd "$(dirname "$0")"

# Activate the virtual environment
source {os.path.join(venv_path, 'bin', 'activate')}

# Run the Python script
python 'Google-Search-Update.py'

# Deactivate the virtual environment
deactivate

echo "Press Enter to close this window..."
read
"""
    with open('run-Google-Search-Update.command', 'w') as f:
        f.write(script_content)
    os.chmod('run-Google-Search-Update.command', 0o755)
    print("Created execution script: run-Google-Search-Update.command")
    print("You can now run the script by double-clicking 'run-Google-Search-Update.command'")

def main():
    print("Welcome to the Google Search Update script setup!")
    script_dir = os.getcwd()
    venv_path = create_virtual_environment(script_dir)
    create_config_file(script_dir)
    install_dependencies(venv_path)
    create_execution_script(venv_path)
    
    if os.path.exists('Google-Search-Update.py'):
        print("'Google-Search-Update.py' file is already in the correct location.")
    else:
        print("Warning: 'Google-Search-Update.py' file not found in the current directory.")
    
    print(f"Setup complete. Virtual environment created at: {venv_path}")
    print("To run the script, double-click 'run-Google-Search-Update.command' or run it from the terminal.")

if __name__ == "__main__":
    main()