import requests
import pandas as pd
from habanero import Crossref


def fetch_crossref(keyword):
    """Fetch articles from Crossref using the provided keyword."""
    cr = Crossref()
    works = cr.works(query=keyword)
    results = []

    for work in works['message']['items']:
        title = work.get('title', ['N/A'])[0]  # Get title, default to 'N/A'
        doi = work.get('DOI', 'N/A')  # Get DOI, default to 'N/A'
        url = work.get('URL', 'N/A')  # Get URL, default to 'N/A'
        year = work.get('published-print', {}).get('date-parts', [[None]])[0][0]  # Get publication year
        results.append((title, doi, year, url))

    return results


def fetch_europe_pmc(keyword):
    """Fetch articles from Europe PMC using the provided keyword."""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={keyword}&format=json"
    response = requests.get(url)
    data = response.json()
    results = []

    for item in data.get('resultList', {}).get('result', []):
        title = item.get('title', 'N/A')
        pmid = item.get('pmid', 'N/A')
        url = f"https://europepmc.org/article/pmc/{pmid}" if pmid != 'N/A' else 'N/A'
        year = item.get('pubYear', 'N/A')
        results.append((title, pmid, year, url))

    return results


def save_results_to_excel(results, filename='KeywordResults.xlsx'):
    """Save the collected results to an Excel file."""
    df = pd.DataFrame(results, columns=['Title', 'DOI/PMID', 'Year', 'URL'])
    df.to_excel(filename, index=False)
    print(f"Results saved to {filename}")


def main(keywords):
    all_results = []

    for keyword in keywords:
        print(f"Fetching results for: {keyword}")
        crossref_results = fetch_crossref(keyword)
        europe_pmc_results = fetch_europe_pmc(keyword)

        all_results.extend(crossref_results)
        all_results.extend(europe_pmc_results)

    save_results_to_excel(all_results)


if __name__ == "__main__":
    # Sample keywords to search
    keywords = ['GC-MS', 'mass spectrometry', 'chemical analysis', 'zea mays', 'gas chromatography',
                'heavy metal toxicity', 'lead', 'metabolomics', 'plant stress']
    main(keywords)
