from bcrypt import checkpw, gensalt, hashpw
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

from app.db import close_conn_cursor, context_db_manager, get_connection


class Roles:
    @classmethod
    def get_proyect_roles(cls):
        cnx = get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT * FROM roles_proyecto"

        cursor.execute(query)

        result = cursor.fetchall()

        cursor.close()
        cnx.close()

        return result

    @classmethod
    def proyect_role_name(cls, id: int):
        cnx = get_connection()
        cursor = cnx.cursor()

        query = "SELECT nombre FROM roles_proyecto WHERE id=%s"

        cursor.execute(query, (id,))

        result = cursor.fetchone()

        cursor.close()
        cnx.close()

        if result is not None:
            return result[0]

        return None

    @classmethod
    def get_team_roles(cls):
        cnx = get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT * FROM roles_equipo"

        cursor.execute(query)

        result = cursor.fetchall()

        cursor.close()
        cnx.close()

        return result
