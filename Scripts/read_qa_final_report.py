import pandas as pd
import mysql.connector
from mysql.connector import Error
import os


# Get ENV values
sql_host = os.getenv('MYSQL_HOST')
sql_user = os.getenv('MYSQL_USER')
sql_password = os.getenv('MYSQL_PASSWORD')
sql_db = os.getenv('MYSQL_GCMS_DB')


def insert_into_db(file_path, sheet, cursor):
    # Read df
    df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
    print(df)

    headers = []
    for i in df.columns:
        headers.append(i)

    for i, row in df.iterrows():
        query = f'''INSERT INTO gcms.qa_final_report(sheet_name, peak, start, retention_time, end, height, 
        area, area_degree) VALUES ('{sheet}', {row[headers[0]]}, {row[headers[1]]}, {row[headers[2]]}, {row[headers[3]]}
        , {row[headers[4]]}, {row[headers[5]]}, {row[headers[6]]});'''
        print(query)
        cursor.execute(query)
    cursor.execute('COMMIT;')
    cursor.close()
    connection.close()


# Main
file_name = r"input\Qualitative Analysis Report_all.xlsx"
df1 = pd.ExcelFile(file_name)
sheet_name = df1.sheet_names
print(sheet_name)

connection = mysql.connector.connect(
    host=sql_host,
    user=sql_user,
    password=sql_password,
    database=sql_db
)
cursor = connection.cursor()
for names in sheet_name:
    try:
        insert_into_db(file_name, names, cursor)
    except Error as e:
        cursor.execute('TRUNCATE TABLE gcms.qa_final_report;')
        connection.commit()
        print(f'{names}, Error: {e}')

cursor.close()
connection.close()
print('Data inserted Successfully')
