import requests
import pandas as pd
import time
from tenacity import retry, stop_after_attempt, wait_fixed

# Your API Keys
pubmed_api_key = "5babd27a66ec1dc6ed4d8b8d0c649c962709"


# Retry mechanism for API calls with a maximum of 3 attempts and 2 seconds wait
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_pubmed_data(keyword, api_key=pubmed_api_key):
    """
    Fetches data from PubMed using a keyword.
    """
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={keyword}&retmode=json&api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from PubMed for keyword: {keyword}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_europepmc_data(keyword):
    """
    Fetches data from EuropePMC using a keyword.
    """
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={keyword}&format=json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from EuropePMC for keyword: {keyword}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_semanticscholar_data(keyword):
    """
    Fetches data from Semantic Scholar using a keyword.
    """
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&fields=title,authors,year,url"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from Semantic Scholar for keyword: {keyword}")


def parse_paper_data(source_data, source):
    """
    Extracts relevant information (title, authors, year, URL) from API data.
    If a field is missing, returns 'N/A'.
    """
    papers = []

    if source == 'pubmed':
        for paper_id in source_data.get('esearchresult', {}).get('idlist', []):
            details = {
                'title': f"PubMed Paper {paper_id}",  # PubMed ESearch does not return titles directly
                'authors': 'N/A',  # PubMed ESearch does not return authors directly
                'year': 'N/A',
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
            }
            papers.append(details)

    elif source == 'europepmc':
        for paper in source_data.get('resultList', {}).get('result', []):
            details = {
                'title': paper.get('title', 'N/A'),
                'authors': ', '.join(
                    [author.get('fullName', 'N/A') for author in paper.get('authorList', {}).get('author', [])]),
                'year': paper.get('pubYear', 'N/A'),
                'url': paper.get('doi', 'N/A')
            }
            papers.append(details)

    elif source == 'semanticscholar':
        for paper in source_data.get('data', []):
            details = {
                'title': paper.get('title', 'N/A'),
                'authors': ', '.join([author.get('name', 'N/A') for author in paper.get('authors', [])]),
                'year': paper.get('year', 'N/A'),
                'url': paper.get('url', 'N/A')
            }
            papers.append(details)

    return papers


def retrieve_and_process_papers(keywords):
    """
    Main function to retrieve papers and save them to Excel, handling failed attempts.
    """
    all_paper_data = []

    for keyword in keywords:
        print(f"Processing keyword: {keyword}")

        # Try fetching from PubMed
        try:
            pubmed_data = fetch_pubmed_data(keyword)
            pubmed_papers = parse_paper_data(pubmed_data, 'pubmed')
            for paper in pubmed_papers:
                paper['keyword'] = keyword
                all_paper_data.append(paper)
        except Exception as e:
            print(f"Error fetching from PubMed: {e}")

        # Try fetching from EuropePMC
        try:
            europepmc_data = fetch_europepmc_data(keyword)
            europepmc_papers = parse_paper_data(europepmc_data, 'europepmc')
            for paper in europepmc_papers:
                paper['keyword'] = keyword
                all_paper_data.append(paper)
        except Exception as e:
            print(f"Error fetching from EuropePMC: {e}")

        # Try fetching from Semantic Scholar
        try:
            semanticscholar_data = fetch_semanticscholar_data(keyword)
            semanticscholar_papers = parse_paper_data(semanticscholar_data, 'semanticscholar')
            for paper in semanticscholar_papers:
                paper['keyword'] = keyword
                all_paper_data.append(paper)
        except Exception as e:
            print(f"Error fetching from Semantic Scholar: {e}")

        time.sleep(1)  # Be kind to APIs with a small delay

    # Convert to DataFrame
    df = pd.DataFrame(all_paper_data, columns=['keyword', 'title', 'authors', 'year', 'url'])

    # Save to Excel
    df.to_excel("research_papers-v02.xlsx", index=False)
    print("Data successfully saved to 'research_papers-v02.xlsx'.")


# Keywords to search
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

# Run the function
retrieve_and_process_papers(keywords)
