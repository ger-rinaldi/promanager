""" Modulo de la Base de Datos.
    Utilería apara la creación de la DB y sus tablas.
    Obtención y manejo de conexciones.
"""
import os

import mysql.connector
from mysql.connector import Error as dbError

from config import DB_CONFIG, DB_NAME, TEST_DB  # pylint: disable=no-name-in-module


def crear_base_de_datos(test: bool):
    """Crear la base de datos al:
        - inicializar la aplicación
        - en caso de que la base de datos no exista previamente
        - en caso de que la schema haya sufrido una modificación

    Args:
        test (bool): indica si la aplicacion esta utilizando una base de datos
        de testing, en tal caso crea una acorde.
    """
    cnx = mysql.connector.connect(**DB_CONFIG)
    cursor = cnx.cursor()

    try:
        if test:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB}")
        else:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    except dbError as exception:
        # TODO: Loggear este output a algun lugar
        print(f"There was an error while creating the database:\n {exception}")
    finally:
        cursor.close()
        cnx.close()


def crear_schemas(test: bool):
    """Crear las tablas de la base de datos al:
        - inicializar la aplicación
        - en caso de que la base de datos no exista previamente
        - en caso de que la schema haya sufrido una modificación

    Args:
        test (bool): indica si la aplicacion esta utilizando una base de datos
        de testing, en tal caso crea las tablas en esta.
    """

    cnx = get_connection(test)
    cursor = cnx.cursor()

    schema_file = os.path.abspath(os.path.join(__file__, os.pardir)) + "/schema.sql"

    with open(schema_file, encoding="utf8") as schema:
        # separa cada CREATE statement en su propio string
        # crea una lista de strings, donde cada string es un CREATE TABLE IF EXISTS
        # dividir el archivo schema.sql de esta manera, permite controlar individualmente
        # cada CREATE

        # Unir todas las listas retornadas por .readlines()
        tables_commands = "".join(schema.readlines())
        # separar cada create statement, estan delimitados por '-- table'
        # y quitar el comentario inicial
        tables_commands = tables_commands.split("-- table")[1:]

    for table in tables_commands:
        # Por cada CREATE, try ejecutarlo
        # loggear cualquier error resultante
        try:
            cursor.execute(table)
        except dbError as exception:
            # TODO: Loggear este output a algun lugar que no sea stdout
            print(
                f"Hubo un problema al crear las tablas de {DB_CONFIG['database']}:\n{exception}"
            )

    cnx.commit()
    cursor.close()
    cnx.close()


def get_connection(test: bool):
    """Obtain a mysql-connector connection object

    return: mysql.connector.connect(config)
    """

    if test:
        DB_CONFIG["database"] = TEST_DB
    else:
        DB_CONFIG["database"] = DB_NAME

    connection = mysql.connector.connect(**DB_CONFIG)

    return connection


def close_cursors(*cursors: object | list):
    """Close one or many mysql-connector cursors"""
    for cursor in cursors:
        cursor.close()
