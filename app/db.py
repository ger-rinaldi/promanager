""" Modulo de la Base de Datos.
    Utilería apara la creación de la DB y sus tablas.
    Obtención y manejo de conexciones.
"""
import os

import mysql.connector
from mysql.connector import Error as dbError

from config import DB_CONFIG, DB_NAME, TEST_DB  # pylint: disable=no-name-in-module
