import requests
import pandas as pd

def search_figshare(keyword):
    """Search datasets on Figshare."""
    url = f'https://api.figshare.com/v2/articles/search?search_for={keyword}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Check if data is a list or dict and adjust accordingly
        if isinstance(data, list):
            return data  # If it's a list, return it directly
        elif isinstance(data, dict) and 'items' in data:
            return data['items']  # If it's a dict with 'items', return the items
        else:
            print(f"Unexpected data format: {data}")
            return []
    else:
        print(f"Error fetching Figshare datasets: {response.status_code}")
        return []


def search_pubchem(keyword):
    """Search datasets on PubChem."""
    url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{keyword}/JSON'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for compound in data.get('PC_Compounds', []):
            title = compound.get('record', {}).get('name', 'N/A')
            cid = compound.get('cid', 'N/A')
            datasets.append({'title': title, 'cid': cid, 'platform': 'PubChem'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching PubChem datasets: {e}")

    return datasets


def search_metabolomics(keyword):
    """Search datasets on Metabolomics."""
    url = f'http://metabolomics.chem.ox.ac.uk/Metabolomics/api/dataset/search?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('title', 'N/A')
            datasets.append({'title': title, 'platform': 'Metabolomics'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Metabolomics datasets: {e}")

    return datasets


def search_mona(keyword):
    """Search datasets on MoNA."""
    url = f'https://mona.uwm.edu/api/v1/search?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('name', 'N/A')
            datasets.append({'title': title, 'platform': 'MoNA'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching MoNA datasets: {e}")

    return datasets


def search_metlin(keyword):
    """Search datasets on METLIN."""
    url = f'https://metlin.scripps.edu/api/molecules?search={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data:
            title = record.get('name', 'N/A')
            datasets.append({'title': title, 'platform': 'METLIN'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching METLIN datasets: {e}")

    return datasets


def search_massbank(keyword):
    """Search datasets on MassBank Europe."""
    url = f'https://massbank.eu/MassBank/massbank?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('name', 'N/A')
            datasets.append({'title': title, 'platform': 'MassBank Europe'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching MassBank datasets: {e}")

    return datasets


def search_gnps(keyword):
    """Search datasets on GNPS."""
    url = f'https://gnps.ucsd.edu/gnpslibrary/search?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('name', 'N/A')
            datasets.append({'title': title, 'platform': 'GNPS'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching GNPS datasets: {e}")

    return datasets


def search_metabolights(keyword):
    """Search datasets on Metabolights."""
    url = f'http://www.ebi.ac.uk/metabolights/ws/studies?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('title', 'N/A')
            datasets.append({'title': title, 'platform': 'Metabolights'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Metabolights datasets: {e}")

    return datasets


def search_prime(keyword):
    """Search datasets on PRIMe."""
    url = f'https://prime.chem.ox.ac.uk/api/search?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('name', 'N/A')
            datasets.append({'title': title, 'platform': 'PRIMe'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching PRIMe datasets: {e}")

    return datasets


def search_massive(keyword):
    """Search datasets on MassIVE."""
    url = f'https://massive.ucsd.edu/api/v1/search?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('title', 'N/A')
            datasets.append({'title': title, 'platform': 'MassIVE'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching MassIVE datasets: {e}")

    return datasets


def search_proteomexchange(keyword):
    """Search datasets on ProteomeXchange."""
    url = f'https://www.proteomexchange.org/api/search?query={keyword}'
    datasets = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for record in data.get('results', []):
            title = record.get('title', 'N/A')
            datasets.append({'title': title, 'platform': 'ProteomeXchange'})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching ProteomeXchange datasets: {e}")

    return datasets


def search_datasets(keyword):
    """Search for datasets across multiple platforms."""
    datasets = []
    datasets.extend(search_figshare(keyword))
    datasets.extend(search_pubchem(keyword))
    datasets.extend(search_metabolomics(keyword))
    datasets.extend(search_mona(keyword))
    datasets.extend(search_metlin(keyword))
    datasets.extend(search_massbank(keyword))
    datasets.extend(search_gnps(keyword))
    datasets.extend(search_metabolights(keyword))
    datasets.extend(search_prime(keyword))
    datasets.extend(search_massive(keyword))
    datasets.extend(search_proteomexchange(keyword))

    return datasets


if __name__ == "__main__":
    keywords = [
        "GC-MS",
        "Plant Metabolites",
        "Heavy Metals",
        "Lead Contamination",
        "Metabolomics",
        "Mass Spectrometry",
        "Data Analysis",
        "Metabolic Profiling",
        "Zea Mays"
    ]

    for keyword in keywords:
        print(f"Searching for datasets related to: {keyword}")
        results = search_datasets(keyword)
        if results:
            print(f"Found datasets for {keyword}:")
            for dataset in results:
                print(dataset)  # Adjust this line as per the dataset structure
                df = pd.DataFrame(dataset)
                df.to_excel("Dataset GC-MS.xlsx", sheet_name=keyword)

        else:
            print(f"No datasets found for {keyword}.")
