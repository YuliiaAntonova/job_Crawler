"""
CLI tools for databases management. Keep here commands to create/update tables structures,
data migration.
"""
import typer

from . import aws, web_to_gcs

app = typer.Typer()

app.add_typer(aws.app, name="aws")
app.add_typer(web_to_gcs.app, name="web_to_gcs")
