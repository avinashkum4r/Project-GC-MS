import pandas as pd

df = pd.ExcelFile(r'Input\Qualitative Analysis Report_all.xlsx')
print(df.sheet_names)