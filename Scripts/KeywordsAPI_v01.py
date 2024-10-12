import requests
import logging
import pandas as pd
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchPaperFetcher:
    def __init__(self, keywords, max_retries=3, retry_delay=5):
        self.keywords = keywords
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.results = []

    def fetch_papers(self):
        for keyword in self.keywords:
            logger.info(f"Processing keyword: {keyword}")
            self.keyword = keyword
            self._fetch_from_sources()
        self._save_results()

    def _fetch_from_sources(self):
        europepmc_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={self.keyword}&format=json"
        pubmed_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={self.keyword}&retmode=json"
        semanticscholar_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={self.keyword}&fields=title,authors,url"

        self._make_request(europepmc_url, "EuropePMC")
        self._make_request(pubmed_url, "PubMed")
        self._make_request(semanticscholar_url, "Semantic Scholar", exponential_backoff=True)

    def _make_request(self, url, source, exponential_backoff=False):
        retries = 0
        delay = self.retry_delay
        while retries < self.max_retries:
            try:
                logger.info(f"Fetching research papers from {source} for query: {self.keyword}")
                response = requests.get(url)

                # Check if the response status code indicates rate limiting (429)
                if response.status_code == 429:
                    logger.error(f"Rate limited by {source}. Waiting before retrying...")
                    if exponential_backoff:
                        delay *= 2  # Exponential backoff
                    sleep(delay)
                    retries += 1
                    continue

                # Check for successful status code
                response.raise_for_status()

                # Check if the response is empty
                if not response.text.strip():
                    raise ValueError(f"Empty response from {source}")

                # Check the content type to ensure we are receiving JSON
                if 'application/json' in response.headers.get('Content-Type', ''):
                    logger.info(f"Research papers successfully retrieved from {source}")
                    papers = self._parse_response(response.json(), source)
                    self.results.extend(papers)  # Add results to the list
                    return papers
                else:
                    # Log unexpected content type and response text
                    logger.error(f"Unexpected content type from {source}: {response.headers.get('Content-Type')}")
                    logger.error(f"Response from {source}: {response.text[:500]}")  # Log first 500 chars for debugging
                    raise ValueError(f"Unexpected response format from {source}")

            except ValueError as ve:
                logger.error(f"Parsing error for {source}: {ve}")
                return None
            except requests.exceptions.RequestException as e:
                retries += 1
                logger.error(f"Error occurred while fetching data from {source}: {e}")
                if retries < self.max_retries:
                    logger.info(f"Retrying... ({retries}/{self.max_retries})")
                    sleep(delay)
                else:
                    logger.error(f"Failed to retrieve data from {source} after {self.max_retries} attempts.")
                    return None

    def _parse_response(self, data, source):
        papers = []
        if source == "EuropePMC":
            for paper in data.get('resultList', {}).get('result', []):
                papers.append({
                    'Title': paper.get('title', ''),
                    'Authors': ', '.join(author.get('fullName', '') for author in paper.get('authorList', {}).get('author', [])),
                    'Source': source,
                    'URL': f"https://europepmc.org/article/{paper.get('id')}"
                })
        elif source == "PubMed":
            for paper in data.get('esearchresult', {}).get('idlist', []):
                papers.append({
                    'Title': paper,
                    'Authors': 'N/A',
                    'Source': source,
                    'URL': f"https://pubmed.ncbi.nlm.nih.gov/{paper}/"
                })
        elif source == "Semantic Scholar":
            for paper in data.get('data', []):
                papers.append({
                    'Title': paper.get('title', ''),
                    'Authors': ', '.join(author.get('name', '') for author in paper.get('authors', [])),
                    'Source': source,
                    'URL': paper.get('url', '')
                })
        return papers

    def _save_results(self):
        if self.results:
            df = pd.DataFrame(self.results)
            file_name = "research_papers-v01.xlsx"
            df.to_excel(file_name, index=False)
            logger.info(f"Results saved to {file_name}")
        else:
            logger.info("No results to save.")

# Keywords for the research queries
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

# Instantiate and run the fetcher
fetcher = ResearchPaperFetcher(keywords)
fetcher.fetch_papers()
