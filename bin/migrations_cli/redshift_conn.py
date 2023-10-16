import typer
import psycopg2

app = typer.Typer()


def connect_to_database(host: str, port: int, database: str, user: str, password: str):
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    return conn


def close_database_connection(conn):
    conn.close()


@app.command('query_database')
def query_database(
        host: str = typer.Option(..., help="Database host"),
        port: int = typer.Option(..., help="Database port"),
        database: str = typer.Option(..., help="Database name"),
        user: str = typer.Option(..., help="Database user"),
        password: str = typer.Option(..., help="Database password"),
        query: str = typer.Option(..., help="SQL query"),
        limit: int = typer.Option(..., help="Limit on the number of records to retrieve"),
):
    conn = connect_to_database(host, port, database, user, password)

    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchmany(limit)

        for rec in records:
            print(rec)




