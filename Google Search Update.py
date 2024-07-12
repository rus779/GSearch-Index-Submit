import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
import pandas as pd
import requests
import logging
from googleapiclient.discovery import build
from config import MAX_INDEXING_URLS_PER_RUN, MAX_SUBMISSION_URLS_PER_RUN, EXCLUDE_URLS, JSON_KEY_FILE, WEB_SITE, FILES_DIR, SITEMAP_DIR, SORTING_RULES, API_KEY, CUSTOM_SEARCH_ENGINE_ID, USE_ALPHABETICAL_SORTING

# Configuration
OUTPUT_CSV_FILE = os.path.join(FILES_DIR, 'URLs.csv')

# Initialize logging
logging.basicConfig(filename='script.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Initialize credentials and HTTP client
credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=["https://www.googleapis.com/auth/indexing"])
http = credentials.authorize(httplib2.Http())

def download_sitemaps(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        sitemaps = []
        urls = []
        if root.tag.endswith('sitemapindex'):
            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                sitemaps.append(loc)
        elif root.tag.endswith('urlset'):
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                urls.append(loc)
        return sitemaps, urls
    except Exception as e:
        logging.error(f"Error downloading sitemap {url}: {str(e)}")
        raise

def save_sitemap_content(url, content):
    if not os.path.exists(SITEMAP_DIR):
        os.makedirs(SITEMAP_DIR)
    filename = os.path.join(SITEMAP_DIR, os.path.basename(url))
    with open(filename, 'wb') as file:
        file.write(content)
    logging.info(f"Sitemap saved to {filename}")

def extract_urls():
    sitemap_url = f"{WEB_SITE}/sitemap.xml"
    sitemaps_to_process = [sitemap_url]
    all_urls = set()

    while sitemaps_to_process:
        current_sitemap = sitemaps_to_process.pop()
        try:
            response = requests.get(current_sitemap)
            response.raise_for_status()
            save_sitemap_content(current_sitemap, response.content)
            sitemaps, urls = download_sitemaps(current_sitemap)
            sitemaps_to_process.extend(sitemaps)
            all_urls.update(urls)
        except Exception as e:
            logging.error(f"Error processing sitemap {current_sitemap}: {str(e)}")
            continue

    filtered_urls = [url for url in all_urls if url not in EXCLUDE_URLS]

    if os.path.exists(OUTPUT_CSV_FILE):
        existing_df = pd.read_csv(OUTPUT_CSV_FILE)
        existing_urls = set(existing_df['URL'].tolist())
        new_urls = [url for url in filtered_urls if url not in existing_urls]
        combined_urls = list(existing_urls.union(new_urls))
    else:
        new_urls = filtered_urls
        combined_urls = filtered_urls

    sorted_urls = []
    for rule in SORTING_RULES.values():
        matching_urls = [url for url in combined_urls if rule(url)]
        if USE_ALPHABETICAL_SORTING:
            matching_urls.sort()
        sorted_urls.extend(matching_urls)
    sorted_urls = list(dict.fromkeys(sorted_urls))

    if os.path.exists(OUTPUT_CSV_FILE):
        existing_df = pd.read_csv(OUTPUT_CSV_FILE)
        new_df = pd.DataFrame({
            'URL': sorted_urls,
            'Indexing Status': '',
            'Date of Index': '',
            'Submitting Status': '',
            'Date of Submitting': ''
        })
        merged_df = pd.merge(new_df, existing_df, on='URL', how='left', suffixes=('', '_existing'))
        for col in ['Indexing Status', 'Date of Index', 'Submitting Status', 'Date of Submitting']:
            merged_df[col] = merged_df[f'{col}_existing'].fillna(merged_df[col])
        merged_df = merged_df.drop(columns=[col for col in merged_df.columns if col.endswith('_existing')])
        merged_df.to_csv(OUTPUT_CSV_FILE, index=False)
    else:
        new_df = pd.DataFrame({
            'URL': sorted_urls,
            'Indexing Status': '',
            'Date of Index': '',
            'Submitting Status': '',
            'Date of Submitting': ''
        })
        new_df.to_csv(OUTPUT_CSV_FILE, index=False)

    logging.info(f"URLs have been saved to {OUTPUT_CSV_FILE}")
    return len(new_urls)

def submit_to_indexing_api():
    df = pd.read_csv(OUTPUT_CSV_FILE)
    df['Indexing Status'] = df['Indexing Status'].fillna('')
    df['Date of Index'] = df['Date of Index'].fillna('')
    urls_to_submit = df[df['Indexing Status'] == '']['URL'].tolist()[:MAX_INDEXING_URLS_PER_RUN]

    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    changed_indexing_status_count = 0
    quota_exceeded = False

    for url in urls_to_submit:
        content = {
            'url': url.strip(),
            'type': "URL_UPDATED"
        }
        json_ctn = json.dumps(content)
        response, content = http.request(ENDPOINT, method="POST", body=json_ctn, headers={'Content-Type': 'application/json'})
        result = json.loads(content.decode())

        if "error" in result:
            if result["error"]["code"] == 429:
                logging.error("Google Quota exceeded for Indexing (Search API)")
                quota_exceeded = True
                break
            else:
                df.loc[df['URL'] == url, ['Indexing Status', 'Date of Index']] = ['Error', '']
        else:
            df.loc[df['URL'] == url, ['Indexing Status', 'Date of Index']] = ['Indexed', datetime.now().strftime("%Y-%m-%d")]
            changed_indexing_status_count += 1

    df.to_csv(OUTPUT_CSV_FILE, index=False)
    logging.info(f"Indexing results have been updated in {OUTPUT_CSV_FILE}")
    return changed_indexing_status_count, quota_exceeded

def submit_to_search_console():
    df = pd.read_csv(OUTPUT_CSV_FILE)
    df['Submitting Status'] = df['Submitting Status'].fillna('')
    df['Date of Submitting'] = df['Date of Submitting'].fillna('')
    df['Indexing Status'] = df['Indexing Status'].fillna('')

    urls_to_submit = df[
        ((df['Indexing Status'] == 'Not Indexed') | (df['Indexing Status'] == '')) &
        (df['Submitting Status'] == '')
    ]['URL'].tolist()[:MAX_SUBMISSION_URLS_PER_RUN]

    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    changed_submitting_status_count = 0
    quota_exceeded = False

    for url in urls_to_submit:
        content = {
            'url': url.strip(),
            'type': "URL_UPDATED"
        }
        json_ctn = json.dumps(content)
        response, content = http.request(ENDPOINT, method="POST", body=json_ctn, headers={'Content-Type': 'application/json'})
        result = json.loads(content.decode())

        if "error" in result:
            if result["error"]["code"] == 429:
                logging.error("Google Quota exceeded for Submitting (Index API)")
                quota_exceeded = True
                break
            else:
                error_message = f"Error submitting URL {url}: {result['error']}"
                logging.error(error_message)
                df.loc[df['URL'] == url, ['Submitting Status', 'Date of Submitting']] = ['Error', '']
        else:
            df.loc[df['URL'] == url, ['Submitting Status', 'Date of Submitting']] = ['Submitted', result['urlNotificationMetadata']['latestUpdate']['notifyTime']]
            changed_submitting_status_count += 1

    df.to_csv(OUTPUT_CSV_FILE, index=False)
    logging.info(f"Submission results have been updated in {OUTPUT_CSV_FILE}")
    return changed_submitting_status_count, quota_exceeded

def log_results(urls_added_count, changed_indexing_status_count, changed_submitting_status_count, 
                indexing_quota_exceeded, submitting_quota_exceeded):
    df = pd.read_csv(OUTPUT_CSV_FILE)
    total_urls = len(df)
    total_indexed = len(df[df['Indexing Status'] == 'Indexed'])
    total_submitted = len(df[df['Submitting Status'] == 'Submitted'])

    results_message = (
        f"Date and Time: {datetime.now()}\n"
        f"1. URLs added from sitemap\n"
        f"   now = {urls_added_count}\n"
        f"   overall = {total_urls}\n"
        f"2. URLs indexed\n"
        f"   now = {changed_indexing_status_count}\n"
        f"   overall = {total_indexed}\n"
    )
    
    if indexing_quota_exceeded:
        results_message += "Google Quota exceeded for Indexing (Search API)\n"
    
    results_message += (
        f"3. URLs submitted\n"
        f"   now = {changed_submitting_status_count}\n"
        f"   overall = {total_submitted}\n"
    )
    
    if submitting_quota_exceeded:
        results_message += "Google Quota exceeded for Submitting (Index API)\n"

    with open('results.txt', 'a') as f:
        f.write(results_message)
        f.write("\n")
    print(results_message)

def main():
    try:
        urls_added_count = extract_urls()
        changed_submitting_status_count, submitting_quota_exceeded = submit_to_search_console()
        changed_indexing_status_count, indexing_quota_exceeded = submit_to_indexing_api()
        log_results(urls_added_count, changed_indexing_status_count, changed_submitting_status_count,
                    indexing_quota_exceeded, submitting_quota_exceeded)
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()