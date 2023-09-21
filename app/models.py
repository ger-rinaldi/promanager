from typing import Any, Sequence, Union

from bcrypt import gensalt, hashpw
from db import get_connection
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType


class usuario:
    tablename = "usuario"
    fields = (
        "id",
        "nombre",
        "apellido",
        "email",
        "telefono_prefijo",
        "telefono_numero",
        "contraseña",
    )
    all_fields: str = ", ".join(fields)
    no_id_fields: str = ", ".join(fields[1:])
    no_pass_fields: str = ", ".join(fields[: len(fields) - 1])

    @classmethod
    def create(
        cls,
        nombre: str,
        apellido: str,
        mail: str,
        prefijo_tel: int,
        telefono: str,
        contraseña: str,
    ) -> None:
        "Crear nuevo registro de usuario en la base de datos"

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_create: CursorBase = cnx.cursor()

        sql = f"INSERT INTO {cls.tablename}({cls.no_id_fields})\
                VALUES  (%s, %s, %s, %s, %s, %s)"

        values = (
            nombre,
            apellido,
            mail,
            prefijo_tel,
            telefono,
            hashpw(password=contraseña.encode("utf8"), salt=gensalt()),
        )

        cursor_create.execute(sql, values)

        cnx.commit()
        cursor_create.close()
        cnx.close()

    @classmethod
    def load_user(cls, id: int) -> Union["usuario", None]:
        sql = f"SELECT {cls.no_pass_fields} FROM {cls.tablename} WHERE id = %s"

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(sql, (id,))

        loaded_user: RowType | Sequence[Any] | None = cursor.fetchone()

        if loaded_user is not None:
            return_user: "usuario" = usuario(**loaded_user)  # type: ignore

        return return_user  # type: ignore

    def __init__(
        self,
        id: int,
        nombre: str,
        apellido: str,
        email: str,
        telefono_prefijo: str,
        telefono_numero: str,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.mail = email
        self.prefijo_telefono = telefono_prefijo
        self.numero_telefono = telefono_numero

    def __tuple__(self) -> tuple:
        """Retornar atributos de usuario como tupla


        Returns:
            tuple: (id, nombre, apellido, mail)
        """
        return (self.id, self.nombre, self.apellido, self.mail)


class prefijos_telefonicos:
    """Clase encargada de obtener los prefijos telefonicos"""

    tablename = "prefijo_telefono"

    @classmethod
    def read_all(cls):
        """Obtener todos los paises y sus codigos sin ID"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_getall = cnx.cursor(dictionary=True)
        cursor_getall.execute(
            f"SELECT id, prefijo, pais FROM {prefijos_telefonicos.tablename}"
        )

        return cursor_getall.fetchall()

    @classmethod
    def get_prefix_of_id(cls, id: int) -> Union[str, None]:
        """Obtener todos los paises y sus codigos sin ID"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_prefix: CursorBase = cnx.cursor()
        cursor_prefix.execute(
            f"SELECT prefijo FROM {prefijos_telefonicos.tablename} WHERE id = %s",
            (id,),
        )

        prefix: RowType | Sequence[Any] | None = cursor_prefix.fetchone()

        if prefix is not None:
            return str(prefix[0])

        return None
