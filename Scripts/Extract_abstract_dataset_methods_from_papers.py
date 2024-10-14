import pandas as pd
from openpyxl import load_workbook
import requests


def fetch_paper_details(paper_id):
    """Fetch detailed paper data from the Europe PMC API."""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{paper_id}/detailed"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return JSON data
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching detailed data for paper ID {paper_id}: {err}")
        return None  # Return None if there was an error


def save_to_excel(data, file_name='research_papers-v02.xlsx', sheet_name='Detailed_Paper_Details'):
    """Save data to an Excel file."""
    df = pd.DataFrame(data)  # Convert data to DataFrame

    try:
        # Try to load the existing workbook
        book = load_workbook(file_name)
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a') as writer:
            writer.book = book
            # Check if the sheet already exists
            if sheet_name in writer.book.sheetnames:
                startrow = writer.book[sheet_name].max_row
                df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False, header=False)
            else:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    except FileNotFoundError:
        # If the file does not exist, create a new one
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def main():
    """Main function to fetch and save research papers data."""
    keywords = [
        "Gas Chromatography Mass Spectrometry lead Zea mays",
        "GC-MS analysis heavy metals maize",
        "Lead contamination in maize research",
        "Heavy metals in Zea mays scholarly articles",
        "Lead exposure in plants research papers",
        "Lead in maize Gas Chromatography research",
        "Heavy metal toxicity in maize scientific papers",
        "GC-MS study on lead in maize",
        "Lead contamination plant research articles",
        "Toxic metals in maize scholarly papers",
    ]

    all_papers_data = []  # List to hold all fetched paper data

    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        # Here, implement your logic to search and retrieve paper IDs based on the keyword
        # For demonstration purposes, we will use the following paper IDs
        paper_ids = ['PMC10706466', 'PMC11203194']  # Example paper IDs, replace with actual logic

        for paper_id in paper_ids:
            details = fetch_paper_details(paper_id)
            if details is not None:
                all_papers_data.append(details)  # Append fetched details to the list

    # Save all fetched paper data to Excel
    if all_papers_data:
        save_to_excel(all_papers_data)
    else:
        print("No data fetched.")


if __name__ == "__main__":
    main()
