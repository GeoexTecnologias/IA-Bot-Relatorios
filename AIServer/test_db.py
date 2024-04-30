import pypyodbc as odbc

driver = "ODBC Driver 18 for SQL Server"
server_name = "dev.geoex.local,2433"
database = "GeoexPlusHomolog"
uid = "brunoprado"
pwd = "Bruno@Prado"

connection_string = f"""
    DRIVER={{{driver}}};
    SERVER={server_name};
    DATABASE={database};
    uid={uid};
    pwd={pwd};
    Trust_Connection=yes;
    TrustServerCertificate=yes;
"""

odbc.connect(connection_string)
print(f"conectado ao banco de dados {database}")
