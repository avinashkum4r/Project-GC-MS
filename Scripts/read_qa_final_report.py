import pandas as pd
import mysql.connector
from mysql.connector import Error
import os


def insert_into_db(file_path, sheet):
    # Get ENV values
    sql_host = os.getenv('MYSQL_HOST')
    sql_user = os.getenv('MYSQL_USER')
    sql_password = os.getenv('MYSQL_PASSWORD')
    sql_db = os.getenv('MYSQL_GCMS_DB')

    connection = mysql.connector.connect(
        host=sql_host,
        user=sql_user,
        password=sql_password,
        database=sql_db
    )
    cursor = connection.cursor()

    # Read df
    df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
    print(df)

    headers = []
    for i in df.columns:
        headers.append(i)

    for i, row in df.iterrows():
        if i == 0:
            continue
        query = f'''INSERT INTO gcms.qa_final_report(sheet_name, peak, start, retention_time, end, height, 
        area, area_degree) VALUES ('{sheet}', {row[headers[0]]}, {row[headers[1]]}, {row[headers[2]]}, {row[headers[3]]}
        , {row[headers[4]]}, {row[headers[5]]}, {row[headers[6]]});'''
        print(query)
        cursor.execute(query)
    cursor.execute('COMMIT;')
    cursor.close()
    connection.close()


# Main
file_name = r"input\Qualitative Analysis Report 2 with changes.xlsx"
df1 = pd.ExcelFile(file_name)
sheet_name = df1.sheet_names
print(sheet_name)
for i in sheet_name:
    try:
        insert_into_db(file_name, i)
    except Error as e:
        print(f'{i}, Error: {e}')
