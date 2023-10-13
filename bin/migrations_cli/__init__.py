"""
CLI tools for databases management. Keep here commands to create/update tables structures,
data migration.
"""
import typer

from . import aws

app = typer.Typer()

app.add_typer(aws.app, name="aws")

