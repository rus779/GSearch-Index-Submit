This script is made for these purposes: to get 'index' status for URLs on your site and to submit non-indexed URLs to Google Search Console. 
This way Google will know about your pages and their content (new and old) faster and you'll be sure about their index situation.

It uses Google's official APIs: Google Custom Search API (for getting index status) and Indexing API (for submitting to index).
There are limits set by Google (and they're presented in 'config' file):
1) 100 URLs per day to get index status
2) 200 URLs per day to submit URLs to Google Index.

It's great because it allows you automate this process without Google UI and it has bigger submitting limit.

To use this script you'll need 3 things:
1) Custom Search Engine ID
2) API key
3) Service Account JSON Key.

You may use this article for the instructions: https://medium.com/@vithanage.sadith/automating-url-submission-to-google-for-indexing-with-custom-search-api-and-indexing-api-d993908ad176

Steps you need to do to work with this script:
0) create a folder where all files will be stored
1) download the script files ('setup', 'Google-Search-Update') to the folder
2) put into this folder 'Service Account JSON Key'
3) rename this file = 'service_account'
4) run 'setup' file (like 'python3 setup.py')
5) answer the questions it'll ask you
6) the code will do the follow:
  = creates virtual environment, so nothing on your machine will be affected
  = installs things it needs to run the code
  = creates 'config' file where all variables will be stored (the questions above will write down them for you there, but you can change them anytime)
  = creates 'sitemap' folder (there downloaded sitemaps will be stored)
  = creates 'run-Google-Search-Update.command' file so you can run the script by click (or you can start the script manually).

After setup you can run 'run-Google-Search-Update' file and it will do the following:
1) download sitemap files (if there are several of them it'll get them too)
2) extract URLs from it. URLs and their statuses will be stored in 'URLs.csv' file
3) sort them if needed (it follows the rules from 'config')
4) asks Google about their index status and write down it 
5) submit the URLs without 'Indexed' status to Google
6) at the end you'll get:
   = 'URLs' file with statuses
   = brief summary of what have been done on the screen and in the 'results.txt' file
   = 'script.log' file where it writes down what happened with more details.
