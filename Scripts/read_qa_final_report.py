import pandas as pd
import os

df = pd.read_excel(r"input\Qualitative Analysis Report 2 with changes.xlsx", sheet_name=r"Pb+OA+SA 30 Days", engine="openpyxl")
# print(df.columns)

print(os.getenv('MYSQL_USER'))
