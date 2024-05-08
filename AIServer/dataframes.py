from db_interface import DBInterface
import pandas as pd
import os
from dotenv import load_dotenv
import pymssql


def store_column_data_types_to_file(table_names, output_file):
    db_interface = DBInterface()
    conn = db_interface.conn
    cursor = conn.cursor()

    with open(output_file, "w") as file:
        for table_name in table_names:
            cursor.execute(
                f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
            """
            )
            rows = cursor.fetchall()
            file.write(f"Table: {table_name}")
            for row in rows:
                file.write(f"[Column: {row[0]} {row[1]}],")
            file.write("\n")

    conn.close()


if __name__ == "__main__":
    table_names = [
        "Projeto",
        "ProjetoProgramacaoCarteira",
        "ProjetoProgramacaoBoletimProdutividade",
    ]
    df_tables = store_column_data_types_to_file(table_names, "tables.txt")
