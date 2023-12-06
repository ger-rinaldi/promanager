""" Modulo de la Base de Datos.
    Utilería apara la creación de la DB y sus tablas.
    Obtención y manejo de conexciones.
"""
import os

import mysql.connector
from mysql.connector import Error as dbError
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection

from app.config import DB_CONFIG, DB_NAME, TEST_DB


class context_db_manager:
    def __init__(
        self,
        dict: bool = False,
        named_tuple: bool = False,
        test_db: bool = False,
    ) -> None:
        self.db_config = DB_CONFIG
        self.type = None
        self.connection = None
        self.cursor = None

        if dict and named_tuple:
            raise Exception("No hay cursor dispobible con diccionario y named_tuple")
        elif dict:
            self.type = {"dictionary": True}
        elif named_tuple:
            self.type = {"named_tuple": True}

        if test_db:
            self.db_config["database"] = TEST_DB
        else:
            self.db_config["database"] = DB_NAME

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.db_config)
        if self.type is not None:
            self.cursor = self.connection.cursor(**self.type)
        else:
            self.cursor = self.connection.cursor()

        self.execute = self.cursor.execute
        self.fetchall = self.cursor.fetchall
        self.fetchone = self.cursor.fetchone

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.cursor.close()
        self.connection.close()

        if exc_type:
            print(
                f"""
            There has been han exception: {exc_type}
            Exception message: {exc_value}
            Traceback:
            {exc_tb}
            """
            )


def crear_base_de_datos(test_db: bool = False) -> None:
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
        if test_db:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB}")
        else:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            return None
    except dbError as exception:
        # TODO: Loggear este output a algun lugar
        print(f"There was an error while creating the database:\n {exception}")
    finally:
        cnx.commit()
        cursor.close()
        cnx.close()


def crear_schemas(test_db: bool = False) -> None:
    """Crear las tablas de la base de datos al:
        - inicializar la aplicación
        - en caso de que la base de datos no exista previamente
        - en caso de que la schema haya sufrido una modificación

    Args:
        test (bool): indica si la aplicacion esta utilizando una base de datos
        de testing, en tal caso crea las tablas en esta.
    """

    cnx = get_connection(connect_test_db=test_db)
    cursor = cnx.cursor()

    schema_file = (
        os.path.abspath(
            os.path.join(
                __file__,
                os.pardir,
            )
        )
        + "/schema.sql"
    )

    with open(schema_file, encoding="utf8") as schema:
        # separa cada CREATE statement en su propio string
        # crea una lista de strings,
        # donde cada string es un CREATE TABLE IF EXISTS
        # dividir el archivo schema.sql de esta manera,
        # permite controlar individualmente
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
                f"Hubo un problema al crear las tablas de\
                    {DB_CONFIG['database']}:\n{exception}"
            )

    cnx.commit()
    cursor.close()
    cnx.close()


def tirar_base_de_datos(test_db: bool = False) -> None:
    cnx = mysql.connector.connect(**DB_CONFIG)
    cursor = cnx.cursor()

    try:
        if test_db:
            cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
        else:
            cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
            return None
    except dbError as exception:
        # TODO: Loggear este output a algun lugar
        print(f"There was an error while dropping the database:\n {exception}")
    finally:
        cnx.commit()
        cursor.close()
        cnx.close()


def tirar_tablas_raiz(test_db: bool = False) -> None:
    cnx = get_connection(connect_test_db=test_db)
    cursor = cnx.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS proyecto")
        cursor.execute("DROP TABLE IF EXISTS prefijo_telefono")
        cursor.execute("DROP TABLE IF EXISTS roles_equipo")
        cursor.execute("DROP TABLE IF EXISTS roles_proyecto")
        cursor.execute("DROP TABLE IF EXISTS estado")
    except dbError as exception:
        # TODO: Loggear este output a algun lugar
        print(f"There was an error while dropping the root tables:\n {exception}")
    finally:
        cnx.commit()
        cursor.close()
        cnx.close()


def tirar_tablas_rama(test_db: bool = False) -> None:
    cnx = get_connection(connect_test_db=test_db)
    cursor = cnx.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS miembros_equipo")
        cursor.execute("DROP TABLE IF EXISTS ticket_tarea")
        cursor.execute("DROP TABLE IF EXISTS equipo")
        cursor.execute("DROP TABLE IF EXISTS integrantes_proyecto")
        cursor.execute("DROP TABLE IF EXISTS usuario")
    except dbError as exception:
        # TODO: Loggear este output a algun lugar
        print(f"There was an error while dropping the branch tables:\n {exception}")
    finally:
        cnx.commit()
        cursor.close()
        cnx.close()


def tirar_tablas_hoja(test_db: bool = False) -> None:
    cnx = get_connection(connect_test_db=test_db)
    cursor = cnx.cursor()

    try:
        cursor.execute("DROP TABLE IF EXISTS asignacion_tarea")
    except dbError as exception:
        # TODO: Loggear este output a algun lugar
        print(f"There was an error while dropping the leaf tables:\n {exception}")
    finally:
        cnx.commit()
        cursor.close()
        cnx.close()


def get_connection(
    connect_test_db: bool = False,
) -> MySQLConnection | PooledMySQLConnection:
    """Obtain a mysql-connector connection object

    return: mysql.connector.connect(config)
    """

    if connect_test_db:
        DB_CONFIG["database"] = TEST_DB
    else:
        DB_CONFIG["database"] = DB_NAME

    connection = mysql.connector.connect(**DB_CONFIG)

    return connection


def close_conn_cursor(
    connection: MySQLConnection, cursor: CursorBase | list[CursorBase]
) -> None:
    """Función para facilitar el cierre de conexión y cursores de MYSQL"""

    if isinstance(cursor, list):
        for c in cursor:
            cursor.close()
    else:
        cursor.close()

    connection.close()
