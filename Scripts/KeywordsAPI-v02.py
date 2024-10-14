import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Your API Keys
pubmed_api_key = "5babd27a66ec1dc6ed4d8b8d0c649c962709"  # Replace with your PubMed API key
serpapi_key = "0c0e2b743d23b3d4d8d6df2bf5d2e287ce6ccc9646a483b4ffff818f400355cc"  # Replace with your SerpApi key


# Class for API Fetching
class API:
    @staticmethod
    def search_europepmc(query):
        try:
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}&resulttype=core&format=json&limit=15"
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from EuropePMC: {e}")
            return None

    @staticmethod
    def search_pubmed(query, api_key):
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&api_key={api_key}&retmax=15"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from PubMed: {e}")
            return None

    @staticmethod
    def search_semantic_scholar(query):
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=15"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Semantic Scholar: {e}")
            return None

    @staticmethod
    def search_google_scholar_serpapi(query, api_key):
        try:
            url = f"https://serpapi.com/search.json?q={query}&engine=google_scholar&api_key={api_key}&num=15"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Google Scholar (SerpApi): {e}")
            return None


# Class for Web Scraping
class WebScraping:
    def __init__(self):
        # Initialize Selenium WebDriver
        self.driver = webdriver.Chrome()  # Ensure you have the appropriate WebDriver installed
        print("Initialized Selenium WebDriver.")

    def scrape_google_scholar(self, query):
        try:
            self.driver.get(f"https://scholar.google.com/scholar?q={query}")
            time.sleep(2)  # Allow the page to load

            papers_data = []
            results = self.driver.find_elements(By.CSS_SELECTOR, "h3.gs_rt")

            for result in results[:15]:  # Limit to 15 results
                title = result.text
                link = result.find_element(By.TAG_NAME, "a").get_attribute("href")

                # Attempt to extract authors and year from the adjacent elements
                try:
                    citation_info = result.find_element(By.XPATH, "./following-sibling::div[1]").text
                    authors_year = citation_info.split('-')
                    authors = authors_year[0].strip() if authors_year else 'N/A'
                    year = authors_year[1].strip() if len(authors_year) > 1 else 'N/A'
                except Exception as e:
                    print(f"Error extracting authors and year: {e}")
                    authors = 'N/A'
                    year = 'N/A'

                paper_info = {
                    'source': 'Google Scholar',
                    'keyword': query,
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'url': link,
                    'paper_id': 'N/A'  # Paper ID not available from Google Scholar
                }
                papers_data.append(paper_info)

            print(f"Scraped {len(papers_data)} papers from Google Scholar for query '{query}'.")
            return papers_data
        except Exception as e:
            print(f"Error scraping Google Scholar: {e}")
            return []

    def close(self):
        self.driver.quit()
        print("Closed Selenium WebDriver.")


# Function to extract paper data from results
def extract_paper_data(results, keyword, source):
    papers_data = []
    for paper in results:
        title = paper.get('title', 'N/A')
        authors = ', '.join([author['name'] for author in paper.get('authors', [])]) if 'authors' in paper else 'N/A'
        year = paper.get('year', 'N/A')
        url = paper.get('url', 'N/A')
        paper_id = paper.get('paperId', 'N/A')

        paper_info = {
            'source': source,
            'keyword': keyword,
            'title': title,
            'authors': authors,
            'year': year,
            'url': url,
            'paper_id': paper_id
        }
        papers_data.append(paper_info)

    return papers_data


# Function to fetch research papers
def fetch_research_papers(keywords, pubmed_api_key, serpapi_key):
    api_results = []
    web_results = []

    for keyword in keywords:
        print(f"Fetching papers for keyword: '{keyword}'")
        # API Searches
        europepmc_results = API.search_europepmc(keyword)
        if europepmc_results and 'resultList' in europepmc_results:
            api_results.extend(extract_paper_data(europepmc_results['resultList']['result'], keyword, 'EuropePMC'))

        pubmed_results = API.search_pubmed(keyword, pubmed_api_key)
        if pubmed_results and 'esearchresult' in pubmed_results:
            for pmid in pubmed_results['esearchresult']['idlist']:
                # Fetch additional information for each PMID
                pubmed_detail_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json&api_key={pubmed_api_key}"
                try:
                    detail_response = requests.get(pubmed_detail_url)
                    detail_response.raise_for_status()
                    detail_data = detail_response.json()
                    if 'result' in detail_data and pmid in detail_data['result']:
                        paper_info = {
                            'source': 'PubMed',
                            'keyword': keyword,
                            'title': detail_data['result'][pmid].get('title', 'N/A'),
                            'authors': ', '.join([author['name'] for author in
                                                  detail_data['result'][pmid].get('authors', [])]) if 'authors' in
                                                                                                      detail_data[
                                                                                                          'result'][
                                                                                                          pmid] else 'N/A',
                            'year': detail_data['result'][pmid].get('pubdate', 'N/A').split(' ')[0],
                            # Extract only the year
                            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}",
                            'paper_id': pmid
                        }
                        api_results.append(paper_info)
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching details for PubMed ID {pmid}: {e}")

        semantic_results = API.search_semantic_scholar(keyword)
        if semantic_results and 'data' in semantic_results:
            api_results.extend(extract_paper_data(semantic_results['data'], keyword, 'Semantic Scholar'))

        # Google Scholar results using SerpApi
        serpapi_results = API.search_google_scholar_serpapi(keyword, serpapi_key)
        if serpapi_results and 'organic_results' in serpapi_results:
            for result in serpapi_results['organic_results']:
                paper_info = {
                    'source': 'Google Scholar (SerpApi)',
                    'keyword': keyword,
                    'title': result.get('title', 'N/A'),
                    'authors': ', '.join(result.get('authors', ['N/A'])),
                    'year': result.get('year', 'N/A'),
                    'url': result.get('link', 'N/A'),
                    'paper_id': result.get('paperId', 'N/A')  # Replace with the actual key from SerpApi if available
                }
                api_results.append(paper_info)

        # Web Scraping Searches
        scraper = WebScraping()
        web_results.extend(scraper.scrape_google_scholar(keyword))
        scraper.close()

    return pd.DataFrame(api_results), pd.DataFrame(web_results)


# Function to compare and clean data
def compare_and_clean_data(api_df, web_df):
    # Perform a merge or comparison based on title and URL to find unique entries
    combined_df = pd.concat([api_df, web_df]).drop_duplicates(subset=['title', 'url'], keep='first')
    print(f"Combined data contains {len(combined_df)} unique entries.")
    return combined_df.reset_index(drop=True)


# Example usage
if __name__ == "__main__":
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

    api_df, web_df = fetch_research_papers(keywords, pubmed_api_key, serpapi_key)
    final_results_df = compare_and_clean_data(api_df, web_df)

    # Saving to Excel
    final_results_df.to_excel("research_papers.xlsx", index=False)
    print("Research papers saved to 'research_papers.xlsx'")
