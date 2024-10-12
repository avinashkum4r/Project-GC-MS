import requests
import pandas as pd
from habanero import Crossref


def fetch_pubmed(keyword):
    url = f"https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc/?term={keyword}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [(item['title'], item['pmid'], item['url'], item['year']) for item in data['records']]
    return []


def fetch_doaj(keyword):
    url = f"https://doaj.org/api/v2/search/articles/?query={keyword}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [(item['bibjson']['title'], item['bibjson']['identifier'][0]['id'], item['bibjson']['link'][0]['url'],
                 item['bibjson']['published']) for item in data['results']]
    return []


def fetch_crossref(keyword):
    cr = Crossref()
    works = cr.works(query=keyword, select=['title', 'DOI', 'published-print', 'URL'])
    results = []
    for work in works['message']['items']:
        title = work.get('title', ['N/A'])[0]
        doi = work.get('DOI', 'N/A')
        year = 'N/A'
        if 'published-print' in work and 'date-parts' in work['published-print']:
            year = work['published-print']['date-parts'][0][0]
        url = work.get('URL', 'N/A')
        results.append((title, doi, year, url))
    return results


def fetch_europe_pmc(keyword):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={keyword}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [
            (
                item['title'],
                item.get('pmid', 'N/A'),  # Use .get() for pmid to avoid KeyError
                item.get('url', 'N/A'),
                item.get('year', 'N/A')  # Use .get() for the year to avoid KeyError
            )
            for item in data['resultList']['result']
        ]
    return []


def main(keywords):
    results = []
    for keyword in keywords:
        results.extend(fetch_pubmed(keyword))
        results.extend(fetch_doaj(keyword))
        results.extend(fetch_crossref(keyword))
        results.extend(fetch_europe_pmc(keyword))

    # Creating a DataFrame and saving it to an Excel file
    df = pd.DataFrame(results, columns=['Title', 'ID/DOI', 'Year', 'Link'])
    df.to_excel('research_papers.xlsx', index=False)
    print("Data saved to research_papers.xlsx")


if __name__ == "__main__":
    keywords = ["heavy metal toxicity", "plant stress", "metabolomics", "GC-MS"]
    main(keywords)
