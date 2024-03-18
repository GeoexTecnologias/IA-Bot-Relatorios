import json
import csv
import pymssql
import os


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    status = 'conexao realizada com sucesso!'
    return pymssql.connect(server, username, password, database), uri, status


DBs = ["GeoexPlusHomolog"]


# Preparing a CSV file
metadata_dict = {"tables": []}

for db in DBs:
    print(f"Buscando metadados para o banco de dados: {db}")
    table_list = []
    try:
        conn = pymssql.connect(host=os.getenv('SERVER'), user=os.getenv(
            'USERNAME'), password=os.getenv("PASSWORD"), database=db)
        cursor = conn.cursor()
        tb_names_qr = "SELECT table_name FROM information_schema.tables"
        cursor.execute(tb_names_qr)
        row = cursor.fetchone()

        while row:
            table_name = row[0]
            print(f"Nome da tabela: {table_name}")
            table_info = {"table_name": table_name, "columns": []}

            # Obtenha as colunas da tabela
            qr = f"SELECT TOP (1) * FROM [{db}].[dbo].[{table_name}]"
            cursor.execute(qr)
            header = [col[0] for col in cursor.description]

            for col in header:
                table_info["columns"].append(col)

            metadata_dict["tables"].append(table_info)
            row = cursor.fetchone()

        cursor.close()

    except Exception as ex:
        print(ex)

# Escreva os dados no arquivo .jsonl
with open("CellSense_05_metadata.jsonl", "w") as jsonl_file:
    for table_info in metadata_dict["tables"]:
        json.dump(table_info, jsonl_file)
        jsonl_file.write("\n")

print("Arquivo CellSense_05_metadata.jsonl criado com sucesso!")
# convert csv to json without repeating the database name and table name
