import boto3
import typer

app = typer.Typer()


@app.command("create_bucket")
def create_bucket(bucket_name: str, location: str):
    if not bucket_name.startswith("job-crawler-"):
        typer.echo("Use name with `job-crawler-` prefix")
        raise typer.Exit()

    typer.echo(f'Bucket will be created in "{location}" region')

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    if bucket.creation_date is None:
        bucket.create(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': location})
        typer.echo(f'Bucket "{bucket.name}" successfully created')
    else:
        typer.echo(f'Bucket "{bucket.name}" already exists')
