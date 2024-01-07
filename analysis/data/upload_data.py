import pandas as pd
import sqlite3
from decimal import Decimal
import re


def extract_and_save_to_sqlite(csv_file, sqlite_db, table_name='job_desc'):
    # Extract data from CSV and save to SQLite
    df = pd.read_csv(csv_file)
    conn = sqlite3.connect(sqlite_db)
    df.to_sql(table_name, conn, if_exists='replace', index=False)


def transform_data_and_save_to_sqlite(sqlite_db, input_table='job_desc', output_table='job_desc_transformed'):
    # Transform data and save to SQLite
    conn = sqlite3.connect(sqlite_db)
    data = pd.read_sql(f'SELECT * FROM {input_table}', conn)

    def convert_salary(salary_str):
        # Function to convert salary strings to Decimal and add the corresponding label
        if isinstance(salary_str, str):
            match = re.search(r'\d+(\.\d+)?', salary_str)
            if match:
                numeric_part = match.group()
                numeric_value = Decimal(numeric_part.replace(',', ''))
                if 'K' in salary_str:
                    return int(numeric_value), 'per year'
                elif ',' in salary_str:
                    return int(numeric_value), 'per year'
                elif '.' in salary_str:
                    return int(numeric_value), 'per hour'
                else:
                    return int(numeric_value), 'per hour'
        else:
            return salary_str, ''

    data['min_salary_year'], data['salary_type'] = zip(*data['min_salary'].apply(convert_salary))
    data['max_salary_year'], _ = zip(*data['max_salary'].apply(convert_salary))

    data.loc[data['salary_type'] == 'per hour', ['min_salary_year', 'max_salary_year']] *= 40 * 52
    data.loc[data['salary_type'] == 'per hour', ['min_salary_year', 'max_salary_year']] /= 1000

    data = data.fillna(value=0)
    data = data.astype({"min_salary_year": 'int', "max_salary_year": 'int'})

    data.to_sql(output_table, conn, if_exists='replace', index=False)


def main():
    # Main function to execute the script
    extract_and_save_to_sqlite('combined_results.csv', 'job_desc.db')
    transform_data_and_save_to_sqlite('job_desc.db')

    # Fetch and print the first row of the transformed data
    conn = sqlite3.connect('job_desc.db')
    res = pd.read_sql('SELECT * FROM job_desc_transformed LIMIT 1', conn)


if __name__ == "__main__":
    main()
