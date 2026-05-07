conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=pension_ai;"
    "UID=sa;"
    "PWD=StrongPassword123;"
    "TrustServerCertificate=yes;"
)