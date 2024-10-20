import mysql.connector
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import os
import openpyxl

# Get ENV values
sql_host = os.getenv('MYSQL_HOST')
sql_user = os.getenv('MYSQL_USER')
sql_password = os.getenv('MYSQL_PASSWORD')
sql_db = os.getenv('MYSQL_GCMS_DB')


# Database connection setup
def create_connection():
    return mysql.connector.connect(
        host=sql_host,
        user=sql_user,
        password=sql_password,
        database=sql_db  # Ensure you're using the correct database
    )


# Fetch raw data from the MySQL table
def fetch_raw_data():
    connection = create_connection()
    cursor = connection.cursor()

    # Select all data from raw_chromatogram_data table
    query = "SELECT time, intensity, mz FROM raw_chromatogram_data"
    cursor.execute(query)

    # Fetch all the rows
    raw_data = cursor.fetchall()

    # Convert to pandas DataFrame for easier analysis
    df = pd.DataFrame(raw_data, columns=['time', 'intensity', 'mz'])

    cursor.close()
    connection.close()

    return df


# Function for peak detection using intensity thresholds
def detect_peaks(df):
    intensity_data = df['intensity'].values

    # Use scipy's find_peaks function to detect peaks
    peaks, _ = find_peaks(intensity_data, height=0.1 * max(intensity_data))  # Adjust the height threshold as needed

    # Add a 'peaks' column to the dataframe
    df['is_peak'] = 0
    df.loc[peaks, 'is_peak'] = 1

    return df, peaks


# Function to integrate peak areas
def integrate_peaks(df, peaks):
    # For simplicity, we calculate the area under the curve as the sum of intensities within each peak region
    peak_areas = []

    for idx, peak in enumerate(peaks):
        # Define a small window around the peak for area calculation (adjust based on data)
        start_idx = max(0, peak - 5)
        end_idx = min(len(df), peak + 5)

        # Calculate the area as the sum of intensities in this window
        area = np.trapz(df['intensity'].iloc[start_idx:end_idx], df['time'].iloc[start_idx:end_idx])

        # Simulated area without overlaps for this example (could be adjusted based on specific needs)
        area_wo = area * 0.9  # Assume 90% of the area is without overlap for this case

        peak_areas.append({
            'peak_number': idx + 1,  # Primary key as peak number
            'start_time': df['time'].iloc[start_idx],
            'retention_time': df['time'].iloc[peak],
            'end_time': df['time'].iloc[end_idx - 1],
            'peak_height': df['intensity'].iloc[peak],
            'peak_area': area,
            'area_wo': area_wo
        })

    return peak_areas


# Main function to execute step 2 analysis
def analyze_chromatogram():
    # Step 1: Fetch the raw chromatogram data
    raw_data_df = fetch_raw_data()

    # Step 2: Detect peaks
    processed_df, peaks = detect_peaks(raw_data_df)

    # Step 3: Integrate peaks to calculate area under the curve
    peak_areas = integrate_peaks(processed_df, peaks)

    # Step 4: Output the final results (retention time, peak height, area, etc.)
    results_df = pd.DataFrame(peak_areas)

    print("Final Chromatogram Analysis Results:")
    print(results_df)

    # Save the results to an Excel file
    excel_file = r'output\final_chromatogram_analysis_simulated.xlsx'
    results_df.to_excel(excel_file, index=False, engine='openpyxl')

    # Step 5: Store the results in MySQL database
    store_analysis_results(results_df)

    return results_df


# Function to store analysis results in MySQL
def store_analysis_results(df):
    connection = create_connection()
    cursor = connection.cursor()

    # Create a new table for the final analysis results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gcms.final_chromatogram_results_simulated (
        peak_number INT PRIMARY KEY,
        start_time FLOAT,
        retention_time FLOAT,
        end_time FLOAT,
        peak_height FLOAT,
        peak_area FLOAT,
        area_wo FLOAT
    )
    ''')

    # Insert the results into the new table
    for index, row in df.iterrows():
        cursor.execute(
            '''
            INSERT INTO gcms.final_chromatogram_results_simulated (peak_number, start_time, retention_time, end_time, peak_height, peak_area, area_wo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''',
            (row['peak_number'], row['start_time'], row['retention_time'], row['end_time'], row['peak_height'],
             row['peak_area'], row['area_wo'])
        )

    connection.commit()
    cursor.close()
    connection.close()


# Execute the analysis script
if __name__ == '__main__':
    analyze_chromatogram()
