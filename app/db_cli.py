import click
from db import (
    crear_base_de_datos,
    crear_schemas,
    tirar_base_de_datos,
    tirar_tablas_hoja,
    tirar_tablas_raiz,
    tirar_tablas_rama,
)


@click.group
@click.option("--help", help="display this menu")
def db_setup(help):
    pass


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
@click.option(
    "--commit-run",
    is_flag=True,
    help="commitear cambios",
)
def hello(test_db, commit_run):
    """Verificar que el script este funcionando"""
    click.echo("HELLO FROM DB")
    if test_db:
        click.echo("TEST")
    if not commit_run:
        click.echo("NO COMMIT, YES DRY")


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
def create_db(test_db: bool):
    crear_base_de_datos(test_db=test_db)


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
def create_schemas(test_db: bool = False):
    crear_schemas(test_db=test_db)


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
def drop_db(test_db: bool = False):
    tirar_base_de_datos(test_db=test_db)


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
def drop_roots(test_db: bool = False):
    tirar_tablas_raiz(test_db=test_db)


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
def drop_branches(test_db: bool = False):
    tirar_tablas_rama(test_db=test_db)


@db_setup.command()
@click.option(
    "--test-db",
    is_flag=True,
    help="usar db de pruebas",
)
def drop_leafs(test_db: bool = False):
    tirar_tablas_hoja(test_db=test_db)


if __name__ == "__main__":
    db_setup()
