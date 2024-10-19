import numpy as np
import pandas as pd
import os
import mysql.connector
from mysql.connector import Error

# Number of data points (10 lakh = 1 million)
num_points = 1000000
total_duration = 36  # Total time in minutes (duration of chromatogram)
time = np.linspace(0, total_duration, num_points)  # Generate 1 million time points

# Define the peak characteristics from the integration peak list
peaks = [
    {"start": 3.582, "rt": 3.754, "end": 3.817, "height": 1162539252, "area": 7821022971, "width": 0.15},
    {"start": 5.042, "rt": 5.07, "end": 5.142, "height": 326799710, "area": 432422454.4, "width": 0.1},
    {"start": 6.812, "rt": 6.855, "end": 6.934, "height": 674848992.1, "area": 1096761509, "width": 0.12},
    {"start": 7.7, "rt": 7.728, "end": 7.757, "height": 159621812.3, "area": 208008964.9, "width": 0.1},
    {"start": 9.561, "rt": 9.596, "end": 9.629, "height": 171194478, "area": 275192157.7, "width": 0.1},
    {"start": 11.405, "rt": 11.448, "end": 11.541, "height": 133527380.4, "area": 250755487.7, "width": 0.15},
    {"start": 13.078, "rt": 13.119, "end": 13.223, "height": 118130289.9, "area": 257899869, "width": 0.15},
    {"start": 13.505, "rt": 13.537, "end": 13.57, "height": 141181776.8, "area": 240078795.2, "width": 0.1},
    {"start": 13.69, "rt": 13.725, "end": 13.806, "height": 129946621, "area": 252877333.8, "width": 0.1},
    {"start": 14.098, "rt": 14.133, "end": 14.255, "height": 158543181.1, "area": 391590190.7, "width": 0.15},
]


# Gaussian function to simulate each peak
def gaussian(x, rt, height, width):
    return height * np.exp(-((x - rt) ** 2) / (2 * width ** 2))


# Simulate signal from all peaks
raw_signal = np.zeros(num_points)

for peak in peaks:
    rt = peak["rt"]
    height = peak["height"]
    width = peak["width"]  # Use the width (converted to FWHM for Gaussian function)
    raw_signal += gaussian(time, rt, height, width)

# Step 2: Add instrument noise (Gaussian noise for baseline fluctuations)
noise_level = 0.02 * np.max(raw_signal)  # Set noise level as 2% of maximum signal
noise = np.random.normal(0, noise_level, num_points)
raw_signal += noise

# Step 3: Add drift to simulate signal drift over time
drift = 0.001 * np.max(raw_signal) * np.sin(2 * np.pi * time / total_duration)
raw_signal += drift

# Step 4: Simulate m/z spectra (optional, here we simulate random m/z values at each point)
mz_values = np.random.uniform(50, 500, num_points)  # Simulate mass-to-charge ratio between 50 and 500

# Save the generated raw data to a CSV file (time, intensity, m/z)
raw_data = pd.DataFrame({"Time (min)": time, "Intensity": raw_signal, "m/z": mz_values})
file_path = r"output\simulated_10lakh_raw_chromatogram.csv"
raw_data.to_csv(file_path, index=False)

# The raw data file is now saved with 1 million points

# Get ENV values
sql_host = os.getenv('MYSQL_HOST')
sql_user = os.getenv('MYSQL_USER')
sql_password = os.getenv('MYSQL_PASSWORD')
sql_db = os.getenv('MYSQL_GCMS_DB')


# Push data to MySQL database
def pudh_data_to_mysql(csv_file_path):
    try:
        connection = mysql.connector.connect(
            host=sql_host,
            user=sql_user,
            password=sql_password,
            database=sql_db
        )
        if connection.is_connected():
            cursor = connection.cursor()

            create_table = r"CREATE TABLE IF NOT EXISTS raw_chromatogram_data ( \
                id INT AUTO_INCREMENT PRIMARY KEY, \
                time FLOAT, \
                intensity FLOAT, \
                mz FLOAT \
            );"

            cursor.execute(create_table)

            load_data = f'''LOAD DATA INFILE '{file_path.replace("\\", "\\\\")}'
            INTO TABLE raw_chromatogram_data
            FIELDS TERMINATED BY ',' 
            IGNORE 1 LINES
            (time, intensity, mz);'''

            cursor.execute(load_data)

            print(f"Data from {csv_file_path} successfully inserted into MySQL database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed successfully")


# Data load function trigger
pudh_data_to_mysql(file_path)
