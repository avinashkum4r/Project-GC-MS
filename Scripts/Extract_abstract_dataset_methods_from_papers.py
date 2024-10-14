import requests
import time
import pandas as pd
from openpyxl import load_workbook

# Function to fetch basic paper data
def fetch_basic_paper_data(paper_id, max_retries=3, timeout_duration=10):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{paper_id}/fullTextXML"
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout_duration)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()  # Assuming the API returns JSON data
        except requests.exceptions.Timeout:
            retries += 1
            print(f"Timeout error for paper ID {paper_id}, retrying ({retries}/{max_retries})...")
            time.sleep(2 ** retries)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for paper ID {paper_id}: {str(e)}")
            return None  # Return None if any error occurs

# Function to process and save the data into an Excel sheet
def save_to_excel(data, file_name='research_papers-v02.xlsx', sheet_name='Papers'):
    df = pd.DataFrame(data)
    try:
        book = load_workbook(file_name)
        writer = pd.ExcelWriter(file_name, engine='openpyxl', mode='a')  # Append mode for existing Excel file
        writer.book = book
        writer.sheets = {ws.title: ws for ws in book.worksheets}
    except FileNotFoundError:
        writer = pd.ExcelWriter(file_name, engine='openpyxl', mode='w')  # Create a new file if it doesn't exist

    df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.close()  # Use writer.close() instead of writer.save()
    print(f"Data saved to {file_name}, sheet: {sheet_name}")

# Function to fetch and save detailed paper data
def fetch_detailed_paper_data(paper_id, max_retries=3, timeout_duration=10):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{paper_id}/detailed"
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout_duration)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()  # Parse JSON response
        except requests.exceptions.Timeout:
            retries += 1
            print(f"Timeout fetching detailed data for paper ID {paper_id}, retrying ({retries}/{max_retries})...")
            time.sleep(2 ** retries)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            print(f"Error fetching detailed data for paper ID {paper_id}: {str(e)}")
            return None  # Skip if error

# Example keywords
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

# Initialize an empty list to store all papers' data
all_papers_data = []

# Iterate through keywords and fetch paper details
for keyword in keywords:
    print(f"Processing keyword: {keyword}")
    # Here you'd ideally call the EuropePMC search API with the keyword (mock response shown here)
    search_results = [  # Mock data
        {"paper_id": "PMC10706466", "title": "Study on Toxic Metals in Maize", "author": "John Doe", "year": "2023", "url": "https://europepmc.org/article/PMC10706466"},
        {"paper_id": "PMC11203194", "title": "Lead Contamination in Zea mays", "author": "Jane Smith", "year": "2022", "url": "https://europepmc.org/article/PMC11203194"},
        # Add more results
    ]

    # Append search results to the papers data with the keyword included
    for result in search_results:
        paper_data = {
            "Keyword": keyword,
            "Title": result.get('title', 'N/A'),
            "Author": result.get('author', 'N/A'),
            "Year": result.get('year', 'N/A'),
            "URL": result.get('url', 'N/A')
        }
        all_papers_data.append(paper_data)

# Save basic paper data to Excel
save_to_excel(all_papers_data, sheet_name="Basic_Paper_Details")

# Now, fetch detailed data for each paper and save it in a separate sheet
detailed_papers_data = []
for paper in all_papers_data:
    paper_id = paper['URL'].split('/')[-1]  # Extract paper ID from the URL
    detailed_data = fetch_detailed_paper_data(paper_id)

    if detailed_data:
        detailed_papers_data.append(detailed_data)
    else:
        # If no detailed data, append basic info with N/A
        detailed_papers_data.append({
            "Paper ID": paper_id,
            "Abstract": "N/A",
            "Methodology": "N/A",
            "Results": "N/A"
        })

# Save detailed paper data to another sheet
save_to_excel(detailed_papers_data, sheet_name="Detailed_Paper_Details")
