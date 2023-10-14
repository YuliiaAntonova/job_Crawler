import pyarrow
import typer
import boto3
import pandas as pd

app = typer.Typer()


@app.command('web_to_gcs')
def web_to_gcs(file_path: str, s3_bucket: str, s3_key: str):
    s3 = boto3.resource('s3')
    # Read the data from the specified CSV file
    df = pd.read_csv(file_path)
    # Convert and save the data to a Parquet file
    parquet_file_name = file_path.replace('.csv', '.parquet')
    df.to_parquet(parquet_file_name, engine='pyarrow')

    # Upload the Parquet file to the specified S3 bucket and key
    s3.Object(s3_bucket, s3_key).put(Body=open(parquet_file_name, 'rb'))
    typer.echo(f"Uploaded {parquet_file_name} to S3 bucket {s3_bucket} with key {s3_key}")
