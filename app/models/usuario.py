from typing import Any, Iterator, Optional, Sequence, Union

from bcrypt import checkpw, gensalt, hashpw
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

import app.models.equipo as equipo
import app.models.proyecto as proyecto
import app.models.ticket_tarea as ticket_tarea
from app.db import close_conn_cursor, get_connection


class Usuario:
    @classmethod
    def get_by_id(cls, id: int) -> Union["Usuario", None]:
        user_info_query_by_id = """SELECT
            u.id, username, nombre, apellido, email,
            prefijo AS telefono_prefijo, telefono_numero,
            llave_sesion
            FROM usuario AS u INNER JOIN prefijo_telefono AS p
            ON u.telefono_prefijo = p.id
            WHERE u.id = %s
            """

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(user_info_query_by_id, (id,))

        loaded_user: RowType | Sequence[Any] | None = cursor.fetchone()

        if loaded_user is not None:
            return Usuario(**loaded_user)

        return None

    @classmethod
    def get_by_session_id(self, session_id: str) -> Union["Usuario", None]:
        user_info_query_by_id = """SELECT
            u.id, username, nombre, apellido, email,
            prefijo AS telefono_prefijo, telefono_numero,
            llave_sesion
            FROM usuario AS u INNER JOIN prefijo_telefono AS p
            ON u.telefono_prefijo = p.id
            WHERE u.llave_sesion = %s
            """

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(user_info_query_by_id, (session_id,))

        loaded_user: RowType | Sequence[Any] | None = cursor.fetchone()

        if loaded_user is not None:
            return Usuario(**loaded_user)

        return None

    @classmethod
    def get_authenticated(cls, identif: str, contrasena: str) -> Union["Usuario", None]:
        if not cls._authenticate(identif=identif, passwd=contrasena):
            return None

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        user_info_query_by_email = """SELECT
            u.id, username, nombre, apellido, email,
            prefijo AS telefono_prefijo, telefono_numero,
            llave_sesion
            FROM usuario AS u INNER JOIN prefijo_telefono AS p
            ON u.telefono_prefijo = p.id
            WHERE %s IN (email, username)
            """

        cursor.execute(user_info_query_by_email, (identif,))

        authenticated_user_info: dict = cursor.fetchone()

        close_conn_cursor(cnx, cursor)

        return Usuario(**authenticated_user_info)

    @classmethod
    def _authenticate(cls, identif: str, passwd: str) -> bool:
        query_pass_by_email = (
            "SELECT contrasena FROM usuario WHERE %s IN (email, username)"
        )

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(
            query_pass_by_email,
            (identif,),
        )

        query_result: dict | None = cursor.fetchone()

        if query_result is None:
            return False

        fetched_passwd: str = query_result["contrasena"]

        close_conn_cursor(cnx, cursor)

        return checkpw(passwd.encode("utf8"), fetched_passwd.encode("utf8"))

    @classmethod
    def remove_session(cls, user_id: int) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        sql = "UPDATE usuario SET llave_sesion = 'not_logged' WHERE id = %s"

        cursor.execute(sql, (user_id,))

        cursor.close()
        cnx.close()

    @classmethod
    def get_by_username_or_mail(cls, identif: str):
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        user_info_query_by_email = """SELECT
            u.id, username, nombre, apellido, email,
            prefijo AS telefono_prefijo, telefono_numero
            FROM usuario AS u INNER JOIN prefijo_telefono AS p
            ON u.telefono_prefijo = p.id
            WHERE %s IN (email, username)
            """

        cursor.execute(user_info_query_by_email, (identif,))

        user_info: dict = cursor.fetchone()

        close_conn_cursor(cnx, cursor)

        if user_info is not None:
            return Usuario(**user_info)

        return None

    def __init__(
        self,
        username: str,
        nombre: str,
        apellido: str,
        email: str,
        telefono_prefijo: str,
        telefono_numero: str,
        contrasena: Optional[str] = None,
        id: Optional[int] = None,
        id_integrante: Optional[int] = None,
        id_miembro: Optional[int] = None,
        rol_proyecto: Optional[str] = None,
        rol_equipo: Optional[str] = None,
        llave_sesion: Optional[str] = None,
    ) -> None:
        self.id = id
        self.username = username
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono_prefijo = telefono_prefijo
        self.telefono_numero = telefono_numero
        self.id_integrante = id_integrante
        self.id_miembro = id_miembro
        self.rol_proyecto = rol_proyecto
        self.rol_equipo = rol_equipo
        self.llave_sesion = llave_sesion

        if contrasena is not None and not contrasena[0:3] == "$2b":
            self.contrasena = hashpw(contrasena.encode("utf8"), gensalt())
        else:
            self.contrasena = contrasena

    def create(self) -> None:
        """Crear nuevo registro de usuario en la base de datos
        con el objeto usuario ya instanciado"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_create: CursorBase = cnx.cursor()

        sql = """INSERT INTO
                usuario(username, nombre, apellido, email, telefono_prefijo, \
                telefono_numero, contrasena)
                VALUES  (%s, %s, %s, %s, %s, %s, %s)"""

        values = self.__tuple__()

        cursor_create.execute(sql, values)

        cnx.commit()
        cursor_create.close()
        cnx.close()

    def update(self) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        sql = """UPDATE usuario SET 
        username = %s, nombre = %s, apellido = %s,  
        email = %s, telefono_prefijo = %s, telefono_numero = %s
        WHERE id = %s"""

        values = (*self.__tuple__(), self.id)

        cursor.execute(sql, values)

        cnx.commit()

        cursor.close()
        cnx.close()

    def delete(self) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        sql = "DELETE FROM usuario WHERE id = %s"

        cursor.execute(sql, (self.id,))

        cnx.commit()

        cursor.close()
        cnx.close()

    def set_session_id(self, sessionId):
        update_session_query = "UPDATE usuario SET llave_sesion = %s WHERE id = %s"

        verify_session_update = "SELECT llave_sesion FROM usuario WHERE id = %s"

        values = (sessionId, self.id)

        cnx = get_connection()
        cursor = cnx.cursor()

        cursor.execute(update_session_query, values)
        cnx.commit()
        cursor.execute(verify_session_update, (self.id,))

        queried_session_id = cursor.fetchone()

        close_conn_cursor(cnx, cursor)

        if queried_session_id is not None and sessionId == queried_session_id[0]:
            return True

        return False

    def load_own_resources(self):
        self.proyectos = proyecto.Proyecto._get_all_of_participant(self.id)
        self.equipos = equipo.Equipo._get_by_member(self.id)
        self.tareas = ticket_tarea.Ticket_Tarea._get_by_asigned_user(self.id)

    def load_session_key(self):
        verify_session_update = "SELECT llave_sesion FROM usuario WHERE id = %s"

        cnx = get_connection()
        cursor = cnx.cursor()

        cursor.execute(verify_session_update, (self.id,))

        queried_session_id = cursor.fetchone()

        close_conn_cursor(cnx, cursor)

        if queried_session_id is not None:
            self.llave_sesion = queried_session_id[0]

    def __tuple__(self, with_id: bool = False) -> tuple:
        """Retornar atributos de usuario como tupla


        Returns:
            tuple: (id, username, nombre, apellido, email)
        """

        atributos_usuario: list[Any] = [
            self.username,
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

    def __repr__(self) -> str:
        """Dunder Method para convertir al objeto usuario (su información)
        en un string.

        Returns:
            str: string con informacion de objeto usuario.
        """

        # Para reducir el largo de linea
        # se crean dos strings por separado
        user_as_string = f"Id: {self.id}, Username: {self.username}, \
        Nombre: {self.nombre}, Apellido: {self.apellido}, e-mail: {self.email}, \
        teléfono: {self.telefono_prefijo}-{self.telefono_numero}"

        return user_as_string

    def __iter__(self) -> Iterator["keyword":"value"]:
        """Dunder Method para permitir iterar sobre ciertos atributos del objeto usuario.
        id, nombre, apellido, email, telefono.

        Yields:
            None: la funcion no usa return, sino yield para cada atributo.
        """

        yield "username", self.username
        yield "nombre", self.nombre
        yield "apellido", self.apellido
        yield "email", self.email
        yield "telefono", f"{self.telefono_prefijo}-{self.telefono_numero}"

        if hasattr(self, "id") and self.id is not None:
            yield "id", self.id

        if hasattr(self, "id_integrante") and self.id_integrante is not None:
            yield "id_integrante", self.id_integrante

        if hasattr(self, "id_miembro") and self.id_miembro is not None:
            yield "id_miembro", self.id_miembro

        if hasattr(self, "rol_proyecto") and self.rol_proyecto is not None:
            yield "rol_proyecto", self.rol_proyecto

        if hasattr(self, "rol_equipo") and self.rol_equipo is not None:
            yield "rol_equipo", self.rol_equipo

        if hasattr(self, "llave_sesion") and self.llave_sesion is not None:
            yield "llave_sesion", self.llave_sesion
