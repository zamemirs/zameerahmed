import asyncio
import json
import logging
import os
import time
import urllib.request
from urllib.parse import urlparse

import nest_asyncio
import requests
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.serialization import AzureJSONEncoder
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup
from pyppeteer import launch
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

nest_asyncio.apply()


def url_fetch(url):
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
    req = urllib.request.Request(url, headers=headers1)
    html_out = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html_out, 'html.parser')
    return soup


def extract_options(html, selector):
    soup = BeautifulSoup(html, 'html.parser')
    select = soup.find('select', {'id': selector})
    options = select.find_all('option')

    # Get the value of each option
    option_values = [option['value'] for option in options]

    return option_values


def scrape(url, raw_filename, type, folder):
    async def _scrape(url, browser):
        # Launch the browser
        browser = await launch()

        # Open a new page
        page = await browser.newPage()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        await page.setUserAgent(user_agent)
        """ await page.setRequestInterception(True)
        async def intercept(request):
            if request.resourceType in ['image', 'media']:
                await request.abort()
            else:
                await request.continue_()
        page.on('request', lambda req: asyncio.ensure_future(intercept(req))) """

        # Go to the url with a longer timeout
        try:
            await page.goto(url, timeout=60000)  # 60 seconds
        except Exception as e:
            print(f"An error occurred while loading the page: {str(e)}")
            await browser.close()
            return None

        # Wait for the content to load
        await asyncio.sleep(1)  # sleep if necessary

        # Get the page content
        content = await page.content()
        if content is None:
            print("Failed to retrieve content from the webpage.")
            await browser.close()
            return None

        # Use BeautifulSoup to parse the page content
        soup = BeautifulSoup(content, 'html.parser')

        # Close the browser
        await browser.close()
        data_html = soup.prettify()
        return data_html  # writetoblob(data_html,raw_filename,type,folder)

    return asyncio.get_event_loop().run_until_complete(_scrape(url, BROWSER))


async def download_pages(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, timeout=60000)

    # Get the page's HTML
    html = await page.content()

    # Extract the option values
    options1 = extract_options(html, "fundTypeSelect")
    options2 = extract_options(html, "shareClassPerf")

    # print(options1)

    # print(options2)
    for option1 in options1:
        # Select an option in the first dropdown
        await page.select('#fundTypeSelect', option1)
        await page.reload()
        # print(page.url)

        for option2 in options2:
            # print(option1 , option2)
            # Select an option in the second dropdown
            await page.select('#shareClassPerf', option2)

            await asyncio.sleep(1)  # Wait for the page to load after selection
            # Download the page
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            data_html = soup.prettify()
            customfilename = f"{raw_filename}_{option1}_{option2}"
            # print(customfilename)
            writetoblob(data_html, customfilename, "html", folder)

    await browser.close()


def analyze_read(formUrl):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=FR_endpoint, credential=AzureKeyCredential(FR_key)
    )

    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-document", formUrl)
    # document_analysis_client.begin_analyze_document_from_url()
    result = poller.result()

    resp_json = json.dumps(result.to_dict(), cls=AzureJSONEncoder)
    # print(resp_json)
    return resp_json


def analyze_read_localfile(localfile):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=FR_endpoint, credential=AzureKeyCredential(FR_key)
    )

    poller = document_analysis_client.begin_analyze_document("prebuilt-document", localfile)
    result = poller.result()

    resp_json = json.dumps(result.to_dict(), cls=AzureJSONEncoder)
    # print(resp_json)
    return resp_json


def download_pdf(url, save_path):
    # Create a session object
    s = requests.Session()

    # Set the retry parameters
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])

    # Set the retry parameters in the session
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # Attempt to download the file
    response = s.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        with open(save_path, 'wb') as output_file:
            output_file.write(response.content)
    else:
        print(f"Request failed with status code: {response.status_code}")


def writetoblob(value, raw_filename, type, folder):
    service = BlobServiceClient.from_connection_string(conn_str=adls_connection_string)

    # Get a reference to the container
    container = service.get_container_client(container_name)

    # Upload the file
    blob_file_name = f"{timestr}\\{folder}\\{raw_filename}.{type}"
    container.upload_blob(name=blob_file_name, data=value, overwrite=True)
    local_path = os.path.join(base_directory, f"{folder}")
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    outputfile = os.path.join(local_path, f"{raw_filename}.{type}" if type else raw_filename)

    save_file = open(outputfile, 'w+', encoding='utf-8')
    save_file.write(value)
    save_file.close()


if __name__ == "__main__":

    # Configure logging
    logging.basicConfig(filename='../app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    timestr = time.strftime("%Y%m%d%H%M%S")
    base_directory = os.path.join(os.getcwd(), "scrapperoutput", timestr)

    adls_connection_string = "DefaultEndpointsProtocol=https;AccountName=webscrapinginvesco;AccountKey=uMTMEbOPyEPG5uVVcoAzX93x+RqezNQhFVjN7lwDncKYhlecahv4ynEaHBRXg+G6C49GjjHHx9pK+AStBnzviw==;EndpointSuffix=core.windows.net"

    container_name = "raw"
    FR_endpoint = "https://webscrapingformrecognizer.cognitiveservices.azure.com/"  # https://invescopoc.cognitiveservices.azure.com/"
    FR_key = "6b9b4390701d47d3adb6a37268b7387d"  # ee4f9868709941888f3fedf57878a1cd"
    BROWSER = asyncio.get_event_loop().run_until_complete(launch())

    # TODO : fetch file from DB or azure or cloud
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_json_path = os.path.join(BASE_DIR, 'web_scrapping_program/input.json')

    with open(input_json_path, 'r') as f:
        config_list = json.load(f)

    # Loop over each configuration in the list
    for config in config_list:
        try:
            # Access data in the configuration
            raw_filename = config['raw_filename']
            url = config['url']
            type = config['type']
            folder = config['folder_name']
            print(f"Extraction of Data from url:{url}")

            if type == 'html':
                returnvalue = scrape(url, raw_filename, type, folder)
                # returnvalue = asyncio.get_event_loop().run_until_complete(scrape(url))
                writetoblob(returnvalue, raw_filename, type, folder)

            elif type == 'pdf':
                returnvalue = analyze_read(url)
                writetoblob(returnvalue, raw_filename, type, folder)

            elif type == 'links':
                returnvalue = url_fetch(url)
                divs = returnvalue.find_all('div', class_='document-item')

                # Find all a tags in this div
                for div in divs:
                    links = div.find_all('a')

                    for link in links:
                        # print(link)
                        actual_link = link.get('href')
                        print(actual_link)
                        parsed_url = urlparse(actual_link)
                        filename = os.path.basename(parsed_url.path)
                        temp_path_pdf = os.path.join(base_directory, f"{folder}", "temp")
                        temp_path_pdf_name = os.path.join(base_directory, f"{folder}", "temp", f"{filename}")

                        if not os.path.exists(temp_path_pdf):
                            os.makedirs(temp_path_pdf)
                        download_pdf(actual_link, temp_path_pdf_name)

                        with open(temp_path_pdf_name, "rb") as f:
                            form = f.read()
                        returnpdf = analyze_read_localfile(form)
                        writetoblob(returnpdf, filename, "", folder)
            elif type == 'subpages':
                asyncio.run(download_pages(url))
            else:
                print("unrecongnised format")
        except Exception as e:
            print('Exception caught: ', str(e))
            continue
    print("RESULT:"f"{timestr}")
