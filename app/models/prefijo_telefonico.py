from typing import Any, Sequence, Union

from bcrypt import checkpw, gensalt, hashpw
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

from app.db import close_conn_cursor, context_db_manager, get_connection


class prefijos_telefonicos:
    """Clase encargada de obtener los prefijos telefonicos"""

    @classmethod
    def read_all(cls):
        """Obtener todos los paises y sus codigos sin ID"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_getall = cnx.cursor(dictionary=True)
        cursor_getall.execute("SELECT id, prefijo, pais FROM prefijo_telefono")

        return cursor_getall.fetchall()

    @classmethod
    def get_prefix_of_id(cls, id: int) -> Union[str, None]:
        """Obtener todos los paises y sus codigos sin ID"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_prefix: CursorBase = cnx.cursor()
        cursor_prefix.execute(
            "SELECT prefijo FROM prefijo_telefono WHERE id = %s",
            (id,),
        )

        prefix: RowType | Sequence[Any] | None = cursor_prefix.fetchone()

        if prefix is not None:
            return str(prefix[0])

        return None
