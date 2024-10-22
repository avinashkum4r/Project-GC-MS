import numpy as np
import pandas as pd
import os
import mysql.connector
from mysql.connector import Error

# Step 1: Set fixed seed for reproducibility
np.random.seed(42)  # Fix the seed so that random values can be reproduced

# Step 2: Generate time points and initialize signal
num_points = 1000000
total_duration = 36
time = np.linspace(0, total_duration, num_points)
raw_signal = np.zeros(num_points)

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


# Step 4: Generate raw signal based on peaks
for peak in peaks:
    rt = peak["rt"]
    height = peak["height"]
    width = peak["width"]
    raw_signal += gaussian(time, rt, height, width)

# Step 5: Add invertible noise
noise_level = 0.02 * np.max(raw_signal)  # 2% of max signal
noise = np.random.normal(0, noise_level, num_points)
tracked_noise = noise.copy()  # Track noise for reverse operation
raw_signal += noise

# Step 6: Add invertible drift
drift = 0.001 * np.max(raw_signal) * np.sin(2 * np.pi * time / total_duration)
tracked_drift = drift.copy()  # Track drift for reverse operation
raw_signal += drift

# Step 7: Add random m/z values and track them
mz_values = np.random.uniform(50, 500, num_points)
tracked_mz_values = mz_values.copy()  # Track m/z for reverse operation

# Save the data into a CSV (time, signal, m/z)
raw_data = pd.DataFrame({"Time (min)": time, "Intensity": raw_signal, "m/z": mz_values})
file_path = r"C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\simulated_10lakh_raw_chromatogram.csv"
raw_data.to_csv(file_path, index=False)

# The raw data file is now saved with 1 million points

# Get ENV values
sql_host = os.getenv('MYSQL_HOST')
sql_user = os.getenv('MYSQL_USER')
sql_password = os.getenv('MYSQL_PASSWORD')
sql_db = os.getenv('MYSQL_GCMS_DB')


# Push data to MySQL database
def push_data_to_mysql(csv_file_path):
    try:
        connection = mysql.connector.connect(
            host=sql_host,
            user=sql_user,
            password=sql_password,
            database=sql_db,
            allow_local_infile=True
        )
        if connection.is_connected():
            cursor = connection.cursor()

            create_table = (r"CREATE TABLE IF NOT EXISTS gcms.raw_chromatogram_data ( "
                            r"id INT AUTO_INCREMENT PRIMARY KEY , time FLOAT, intensity FLOAT, mz FLOAT );")

            cursor.execute(create_table)

            cursor.execute('TRUNCATE TABLE gcms.raw_chromatogram_data')
            csv_file_path = csv_file_path.replace("\\", "\\\\")

            load_data = f'''LOAD DATA INFILE '{csv_file_path}' INTO TABLE gcms.raw_chromatogram_data FIELDS
            TERMINATED BY ',' LINES TERMINATED BY '\\n' IGNORE 1 LINES (time, intensity, mz);'''
            try:
                cursor.execute(load_data)
                connection.commit()
            except Error as e:
                print(f"Error: {e}")

            print(f"Data from {csv_file_path} successfully inserted into MySQL database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed successfully")


# ---- Reversing Process ----

def reverse_simulated_data(signal_with_noise_and_drift, tracked_noise, tracked_drift):
    # Reverse by subtracting noise and drift
    original_signal = signal_with_noise_and_drift - tracked_noise - tracked_drift
    return original_signal


# Test reverse process
recovered_signal = reverse_simulated_data(raw_signal, tracked_noise, tracked_drift)
print(len(recovered_signal), type(recovered_signal))

# Data load function trigger
push_data_to_mysql(file_path)
