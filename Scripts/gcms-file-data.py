import os
import pandas as pd
import mysql.connector

# Get ENV values
sql_host = os.getenv('MYSQL_HOST')
sql_user = os.getenv('MYSQL_USER')
sql_password = os.getenv('MYSQL_PASSWORD')
sql_db = os.getenv('MYSQL_GCMS_DB')

connection = mysql.connector.connect(
    host=sql_host,
    user=sql_user,
    password=sql_password,
    database=sql_db,
    allow_local_infile=True
)

cursor = connection.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS gcms.file_of_gcms (id INT PRIMARY KEY AUTO_INCREMENT, component_rt FLOAT, '
               'cas_num VARCHAR(50), compound_name VARCHAR(100), formula VARCHAR(100));')

df = pd.read_excel(r'Input\File of GC-MS.xlsx', engine='openpyxl')
headers = []
for i in df.columns:
    headers.append(i)

cursor.execute('SELECT component_rt FROM gcms.file_of_gcms;')
select_data = cursor.fetchall()
if len(select_data) > 1:
    cursor.execute('TRUNCATE TABLE gcms.file_of_gcms;')

for i, row in df.iterrows():
    cursor.execute('INSERT INTO gcms.file_of_gcms (component_rt, cas_num, compound_name, formula) VALUES (%s, %s, %s, '
                   '%s);'
                   , (row[headers[0]], row[headers[1]], row[headers[2]], row[headers[3]]))

print("Data inserted successfully")
connection.commit()
cursor.close()
connection.close()