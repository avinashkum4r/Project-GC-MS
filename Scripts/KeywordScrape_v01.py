import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
import time

# Set up logging for debugging and tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class KeywordScrapy:
    def __init__(self):
        # Web scraping targets (URLs)
        self.sources = {
            'Google Scholar': 'https://scholar.google.com/scholar?q={query}',
            'ResearchGate': 'https://www.researchgate.net/search/publication?q={query}',
            # Add more scraping targets here
        }

    def fetch_papers(self, query):
        """
        Scrape research papers from various websites based on a search query.
        """
        all_papers = []

        for source_name, source_url in self.sources.items():
            url = source_url.format(query=query)
            try:
                logging.info(f"Scraping research papers from {source_name} for query: {query}")
                response = requests.get(url,
                                        headers={'User-Agent': 'Mozilla/5.0'})  # Adding headers to mimic a real browser
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Use BeautifulSoup to parse the response
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract papers based on the structure of the source website
                papers = self.parse_response(source_name, soup)
                if papers:
                    all_papers.extend(papers)
                    logging.info(f"Successfully scraped papers from {source_name}")
                else:
                    logging.info(f"No papers found on {source_name} for query: {query}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error occurred while scraping {source_name}: {e}")
            time.sleep(2)  # Sleep between requests to avoid being blocked

        return all_papers

    def parse_response(self, source_name, soup):
        """
        Parse the HTML response and extract useful information about the research papers.
        """
        papers = []

        if source_name == 'Google Scholar':
            # Parse the response from Google Scholar and extract paper details
            for result in soup.find_all('div', class_='gs_ri'):
                title = result.find('h3').text if result.find('h3') else 'N/A'
                authors = result.find('div', class_='gs_a').text if result.find('div', class_='gs_a') else 'N/A'
                url = result.find('a')['href'] if result.find('a') else 'N/A'
                papers.append({
                    'Source': source_name,
                    'Title': title,
                    'Authors': authors,
                    'URL': url,
                    'Year': 'N/A',  # Year may not always be available directly
                })

        elif source_name == 'ResearchGate':
            # Parse the response from ResearchGate and extract paper details
            for result in soup.find_all('div', class_='nova-e-text--size-m'):
                title = result.text.strip() if result else 'N/A'
                url = 'https://www.researchgate.net' + result.find('a')['href'] if result.find('a') else 'N/A'
                papers.append({
                    'Source': source_name,
                    'Title': title,
                    'Authors': 'N/A',  # Authors may require more parsing
                    'URL': url,
                    'Year': 'N/A',  # Year may not always be available directly
                })

        # Add similar parsing logic for additional sources

        return papers


def refactor_keywords():
    """
    Define updated keywords and queries for searching research papers related to GC-MS and heavy metals in Zea mays.
    """
    keywords = [
        'Gas Chromatography Mass Spectrometry lead Zea mays',
        'GC-MS analysis heavy metals maize',
        'Lead contamination in maize research',
        'Heavy metals in Zea mays scholarly articles',
        'Lead exposure in plants research papers',
        'Lead in maize Gas Chromatography research',
        'Heavy metal toxicity in maize scientific papers',
        'GC-MS study on lead in maize',
        'Lead contamination plant research articles',
        'Toxic metals in maize scholarly papers'
    ]
    return keywords


def save_to_excel(data, filename='KeywordResults_v01.xlsx'):
    """
    Save the list of research papers to an Excel file.
    """
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    logging.info(f"Research papers successfully saved to {filename}")


def main():
    # Initialize the KeywordScrapy class
    scraper = KeywordScrapy()

    # Fetch the updated keywords list
    keywords = refactor_keywords()

    # List to hold all research papers
    all_papers = []

    # Iterate through the keywords and scrape research papers
    for keyword in keywords:
        logging.info(f"Processing keyword: {keyword}")
        papers = scraper.fetch_papers(keyword)

        # Handle and log the fetched research papers
        if papers:
            logging.info(f"Total papers scraped for '{keyword}': {len(papers)}")
            all_papers.extend(papers)
        else:
            logging.info(f"No papers found for the keyword: {keyword}")

    # Save the scraped research papers to an Excel file
    if all_papers:
        save_to_excel(all_papers)


if __name__ == "__main__":
    main()
