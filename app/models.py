from typing import Any, Optional, Sequence, Union

from bcrypt import gensalt, hashpw
from db import get_connection
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType


class Usuario:
    __tablename__ = "usuario"
    __fields__ = (
        "id",
        "nombre",
        "apellido",
        "email",
        "telefono_prefijo",
        "telefono_numero",
        "contrasena",
    )
    _str_all_fields: str = ", ".join(__fields__)
    _str_no_id_fields: str = ", ".join(__fields__[1:])
    _str_no_pwd_fields: str = ", ".join(__fields__[: len(__fields__) - 1])

    def create(self) -> None:
        """Crear nuevo registro de usuario en la base de datos
        con el objeto usuario ya instanciado"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_create: CursorBase = cnx.cursor()

        sql = f"INSERT INTO {Usuario.__tablename__}({Usuario._str_no_id_fields})\
                VALUES  (%s, %s, %s, %s, %s, %s)"

        values = self.__tuple__()

        cursor_create.execute(sql, values)

        cnx.commit()
        cursor_create.close()
        cnx.close()

    @classmethod
    def get_user_by_id(cls, id: int) -> Union["Usuario", None]:
        sql = f"SELECT {cls._str_no_pwd_fields} FROM {cls.__tablename__} WHERE id = %s"

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(sql, (id,))

        loaded_user: RowType | Sequence[Any] | None = cursor.fetchone()

        if loaded_user is not None:
            return_user: "Usuario" = Usuario(**loaded_user)  # type: ignore

        return return_user  # type: ignore

    def __init__(
        self,
        nombre: str,
        apellido: str,
        email: str,
        telefono_prefijo: str,
        telefono_numero: str,
        contrasena: Optional[str] = None,
        id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono_prefijo = telefono_prefijo
        self.telefono_numero = telefono_numero

        if contrasena is not None and not contrasena[0:3] == "$2b":
            self.contrasena = hashpw(contrasena.encode("utf8"), gensalt())
        else:
            self.contrasena = contrasena

    def __tuple__(self, with_id: bool = False) -> tuple:
        """Retornar atributos de usuario como tupla


        Returns:
            tuple: (id, nombre, apellido, email)
        """

        atributos_usuario: list[Any] = [
            self.nombre,
            self.apellido,
            self.email,
            self.telefono_prefijo,
            self.telefono_numero,
        ]

        if with_id:
            atributos_usuario.insert(0, self.id)

        if self.contrasena:
            atributos_usuario.append(self.contrasena)

        return tuple(atributos_usuario)


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
