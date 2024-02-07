import click
from db import (
    crear_base_de_datos,
    crear_schemas,
    tirar_base_de_datos,
    tirar_tablas_hoja,
    tirar_tablas_raiz,
    tirar_tablas_rama,
)
from flask.cli import AppGroup

db_setup: AppGroup = AppGroup("db-cli")


# @db_setup.command("db-setup")
# @click.option("--help", help="display this menu")
# def db_setup(help):
#     print("hiiiiiii")


@db_setup.command("hello")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="commitear cambios",
)
def hello(test_db: bool = False, dry_run: bool = False):
    """Verificar que el script este funcionando"""
    click.echo("HELLO FROM DB")
    if test_db:
        click.echo("TEST")
    else:
        click.echo("PROD")
    if dry_run:
        click.echo("DRY")
    else:
        click.echo("COMMIT")


@db_setup.command("create-db")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
@click.option(
    "--with-tables",
    "-w",
    is_flag=True,
    help="Crear tambien las tablas de la DB",
)
def create_db(test_db: bool = False, with_tables: bool = False):
    """Crear base de datos"""

    crear_base_de_datos(test_db=test_db)

    if with_tables:
        crear_schemas(test_db=test_db)


@db_setup.command("create-schemas")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
def create_schemas(test_db: bool = False):
    """Crear las tablas de la DB"""
    crear_schemas(test_db=test_db)


@db_setup.command("drop-db")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
def drop_db(test_db: bool = False):
    """Tirar la base de datos entera, no backup"""

    tirar_base_de_datos(test_db=test_db)


@db_setup.command("drop-roots")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
def drop_roots(test_db: bool = False):
    """Tirar las tablas raiz (son referidas, no refieren)"""

    tirar_tablas_raiz(test_db=test_db)


@db_setup.command("drop-branches")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
def drop_branches(test_db: bool = False):
    """Tirar las tablas 'rama' (son referidas y refieren)"""

    tirar_tablas_rama(test_db=test_db)


@db_setup.command("drop-leafs")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
def drop_leafs(test_db: bool = False):
    """Tirar tablas hoja (no son referidas si refieres)"""
    tirar_tablas_hoja(test_db=test_db)


@db_setup.command("drop-tables")
@click.option(
    "--test-db",
    "-t",
    is_flag=True,
    help="usar db de pruebas 'promanager_test'",
)
def drop_tables(test_db: bool = False):
    """Tirar las tablas de DB en order: hojas -> ramas -> raices"""

    tirar_tablas_hoja(test_db=test_db)
    tirar_tablas_rama(test_db=test_db)
    tirar_tablas_raiz(test_db=test_db)
