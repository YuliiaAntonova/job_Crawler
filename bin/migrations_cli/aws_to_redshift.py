import typer
import psycopg2
import os
import boto3

app = typer.Typer()


@app.command('aws_to_redshift')
def copy_to_redshift(
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        access_key: str,
        secret_key: str,
        s3_location: str
):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        typer.echo("Connected to Redshift")

        cursor = conn.cursor()

        query_str = 'select * from jobs limit 10'
        cursor.execute(query_str)

        os.environ.setdefault('AWS_ACCESS_KEY_ID', access_key)
        os.environ.setdefault('AWS_SECRET_ACCESS_KEY', secret_key)

        s3_client = boto3.client('s3')
        s3_client.list_buckets()

        table_name = 'jobs'
        copy_stmt = f"""
        COPY {table_name}
        FROM '{s3_location}'
        CREDENTIALS 'aws_access_key_id={access_key};aws_secret_access_key={secret_key}'
        REGION 'us-east-2'
        ACCEPTINVCHARS
        FORMAT AS parquet;
        """

        cursor = conn.cursor()
        cursor.execute(copy_stmt)
        typer.echo("Data copied to Redshift")

        query_stmt = 'SELECT count(*) from jobs'
        cursor.execute(query_stmt)
        result = cursor.fetchall()

        typer.echo(f"Total records in the 'jobs' table: {result[0][0]}")

    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}")
    finally:
        if conn:
            conn.close()


