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
