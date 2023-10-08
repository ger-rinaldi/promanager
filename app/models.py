from datetime import date
from typing import Any, Optional, Sequence, Union

from bcrypt import checkpw, gensalt, hashpw
from db import close_conn_cursor, get_connection
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType


class Usuario:
    @classmethod
    def get_user_by_id(cls, id: int) -> Union["Usuario", None]:
        user_info_query_by_id = """SELECT
            u.id, username, nombre, apellido, email,
            prefijo AS telefono_prefijo, telefono_numero
            FROM usuario AS u INNER JOIN prefijo_telefono AS p
            ON u.telefono_prefijo = p.id
            WHERE u.id = %s
            """

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(user_info_query_by_id, (id,))

        loaded_user: RowType | Sequence[Any] | None = cursor.fetchone()

        if loaded_user is not None:
            return_user: "Usuario" = Usuario(**loaded_user)  # type: ignore

        return return_user  # type: ignore

    @classmethod
    def get_user_by_session_id(self, session_id: str) -> Union["Usuario", None]:
        user_info_query_by_id = """SELECT
            u.id, username, nombre, apellido, email,
            prefijo AS telefono_prefijo, telefono_numero
            FROM usuario AS u INNER JOIN prefijo_telefono AS p
            ON u.telefono_prefijo = p.id
            WHERE u.llave_sesion = %s
            """

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        cursor.execute(user_info_query_by_id, (session_id,))

        loaded_user: RowType | Sequence[Any] | None = cursor.fetchone()

        if loaded_user is not None:
            loaded_user: "Usuario" = Usuario(**loaded_user)  # type: ignore

        return loaded_user  # type: ignore

    @classmethod
    def get_user_auth(cls, identif: str, contrasena: str) -> Union["Usuario", None]:
        if not cls._authenticate(identif=identif, passwd=contrasena):
            return None

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
                usuario(username, nombre, apellido, email, telefono_prefijo, telefono_numero, contrasena)
                VALUES  (%s, %s, %s, %s, %s, %s, %s)"""

        values = self.__tuple__()

        cursor_create.execute(sql, values)

        cnx.commit()
        cursor_create.close()
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
        id_name_sur = f"Id: {self.id}, Username: {self.username}, Nombre: {self.nombre}, Apellido: {self.apellido}, "

        mail_phone = f"e-mail: {self.email}, teléfono: {self.telefono_prefijo}-{self.telefono_numero}"

        return id_name_sur + mail_phone

    def __iter__(self) -> None:
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

        if self.id is not None:
            yield "id", self.id

        if self.id_integrante is not None:
            yield "id_integrante", self.id_integrante

        if self.id_miembro is not None:
            yield "id_miembro", self.id_miembro

        if self.rol_proyecto is not None:
            yield "rol_proyecto", self.rol_proyecto

        if self.rol_equipo is not None:
            yield "rol_equipo", self.rol_equipo


class prefijos_telefonicos:
    """Clase encargada de obtener los prefijos telefonicos"""

    @classmethod
    def read_all(cls):
        """Obtener todos los paises y sus codigos sin ID"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_getall = cnx.cursor(dictionary=True)
        cursor_getall.execute(f"SELECT id, prefijo, pais FROM prefijo_telefono")

        return cursor_getall.fetchall()

    @classmethod
    def get_prefix_of_id(cls, id: int) -> Union[str, None]:
        """Obtener todos los paises y sus codigos sin ID"""

        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor_prefix: CursorBase = cnx.cursor()
        cursor_prefix.execute(
            f"SELECT prefijo FROM prefijo_telefono WHERE id = %s",
            (id,),
        )

        prefix: RowType | Sequence[Any] | None = cursor_prefix.fetchone()

        if prefix is not None:
            return str(prefix[0])

        return None


class Proyecto:
    @classmethod
    def get_by_participant(cls, participant_id):
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_query: str = """SELECT
                p.id as 'id proyecto', p.nombre as 'nombre proyecto'
                , p.es_publico as "publico", p.activo, p.presupuesto
                , p.fecha_inicio as "fecha inicio", p.fecha_finalizacion as "fecha finalizacion"
                , i.id as 'id integrante', rp.nombre as 'rol'
                FROM
                proyecto as  p
                INNER JOIN
                integrantes_proyecto as i
                ON p.id = i.proyecto
                INNER JOIN
                roles_proyecto as rp
                ON rp.id = i.rol
                WHERE i.integrante = %s
                ORDER BY p.id
        """

        cursor.execute(select_query, (participant_id,))

        proyects_of_participant: RowType | None = cursor.fetchall()

        cursor.close()
        cnx.close()

        return proyects_of_participant

    @classmethod
    def get_by_id(cls, id) -> Union["Proyecto", None]:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_query: str = "SELECT * FROM proyecto WHERE id = %s"

        cursor.execute(select_query, (id,))

        loaded_proyect: RowType | None = cursor.fetchone()

        if loaded_proyect is not None:
            loaded_proyect: "Proyecto" = Proyecto(**loaded_proyect)

        cursor.close()
        cnx.close()

        return loaded_proyect

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        es_publico: bool,
        activo: bool,
        presupuesto: float,
        fecha_inicio: date,
        fecha_finalizacion: date,
        id: Optional[int] = None,
        instatiate_components: Optional[bool] = True,
        components_as_dicts: Optional[bool] = True,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.es_publico = es_publico
        self.activo = activo
        self.presupuesto = presupuesto
        self.fecha_inicio = fecha_inicio
        self.fecha_finalizacion = fecha_finalizacion
        if instatiate_components:
            self.participantes = []
            self._fetch_all_participants(as_dicts=components_as_dicts)
            self.equipos = []
            self._fetch_all_teams(as_dicts=components_as_dicts)
            self.tareas = []
            self._fetch_all_tasks(as_dicts=components_as_dicts)

    def create(self) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        insert_query: str = """INSERT INTO 
        proyecto(nombre, descripcion, es_publico, activo,
        presupuesto, fecha_inicio, fecha_finalizacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(insert_query, self.__tuple__())

        cnx.commit()
        cursor.close()
        cnx.close()
        self._query_id()

    def delete(self) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        delete_query: str = "DELETE FROM proyecto WHERE id = %s"

        cursor.execute(delete_query, (self.id,))

        cnx.commit()
        cursor.close()
        cnx.close()


    def _query_id(self):
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        fetch_id = """SELECT id FROM proyecto WHERE nombre = %s"""

        cursor.execute(fetch_id, (self.nombre,))
        self.id = cursor.fetchone()[0]

        cursor.close()
        cnx.close()

        return self.id

    def _fetch_all_participants(self, as_dicts: bool = True) -> list[RowType]:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_intg_query: str = """SELECT
            i.id as id_integrante, rp.nombre as rol_proyecto,
            u.id as id, u.nombre, u.apellido, u.email, u.telefono_prefijo, u.telefono_numero
            FROM
            integrantes_proyecto as i
            INNER JOIN
            usuario as u
            ON i.integrante = u.id
            INNER JOIN
            roles_proyecto as rp
            ON rp.id = i.rol
            WHERE i.proyecto = %s
        """

        cursor.execute(select_intg_query, (self.id,))

        all_integrantes = cursor.fetchall()

        cursor.close()
        cnx.close()

        if as_dicts:
            self.participantes = all_integrantes
        else:
            for i in all_integrantes:
                self.participantes.append(Usuario(**i))

    def _fetch_all_teams(self, as_dicts: bool) -> list[RowType]:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_teams_query: str = """SELECT * from equipo WHERE proyecto = %s"""

        cursor.execute(select_teams_query, (self.id,))

        all_teams = cursor.fetchall()

        cursor.close()
        cnx.close()

        if as_dicts:
            self.equipos = all_teams
        else:
            for t in all_teams:
                self.equipos.append(Equipo(**t))

    def _fetch_all_tasks(self, as_dicts: bool) -> list[RowType]:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_tasks_query: str = """SELECT * from ticket_tarea WHERE proyecto = %s"""

        cursor.execute(select_tasks_query, (self.id,))

        all_tasks = cursor.fetchall()

        cursor.close()
        cnx.close()

        if as_dicts:
            self.tareas = all_tasks
        else:
            for t in all_tasks:
                self.tareas.append(Ticket_Tarea(**t))

    def __tuple__(self, with_id: bool = False) -> tuple:
        self_as_tuple: list[Any] = [
            self.nombre,
            self.descripcion,
            self.es_publico,
            self.activo,
            self.presupuesto,
            self.fecha_inicio,
            self.fecha_finalizacion,
        ]

        if with_id:
            self_as_tuple.insert(0, self.id)

        return tuple(self_as_tuple)

    def __repr__(self) -> str:
        return f"id: {self.id}, nombre: {self.nombre}, presupuesto: {self.presupuesto}, inicio: {self.fecha_inicio}"

    def __iter__(self) -> None:
        yield "id", self.id
        yield "nombre", self.nombre
        yield "descripcion", self.descripcion
        yield "es_publico", self.es_publico
        yield "activo", self.activo
        yield "presupuesto", self.presupuesto
        yield "fecha_inicio", self.fecha_inicio
        yield "fecha_finalizacion", self.fecha_finalizacion
        yield "participantes", self.participantes
        yield "equipos", self.equipos


class Ticket_Tarea:
    @classmethod
    def get_by_asigned_user(cls, user_id):
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_query: str = """select
            t.id as "id tarea", t.proyecto as "proyecto padre", t.equipo as "equipo encargado"
            , t.nombre, t.estado, t.fecha_asignacion as "asignada a equipo", t.fecha_limite as "limite"
            , a.id as "asignacion nº", a.fecha_asignacion as "asignada a usuario"
            from
            ticket_tarea as t
            inner join
            asignacion_tarea as a
            on t.id = a.ticket_tarea
            inner join
            miembros_equipo as m
            on a.miembro = m.id
            inner join
            usuario as u
            on m.miembro = u.id
            where u.id = %s
            order by t.id;
        """

        cursor.execute(select_query, (user_id,))

        tasks_of_user: RowType | None = cursor.fetchall()

        cursor.close()
        cnx.close()

        return tasks_of_user

    def __init__(
        self,
        proyecto: Union[int, "Proyecto"],
        equipo: Union[int, "Equipo"],
        nombre: str,
        estado: int | str,
        descripcion: str,
        fecha_creacion: date,
        fecha_asignacion: date,
        fecha_limite: date,
        fecha_finalizacion: date,
        id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.proyecto = proyecto
        self.equipo = equipo
        self.nombre = nombre
        self.estado = estado
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion
        self.fecha_asignacion = fecha_asignacion
        self.fecha_limite = fecha_limite
        self.fecha_finalizacion = fecha_finalizacion


class Equipo:
    @classmethod
    def get_by_member(cls, member_id):
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_query: str = """SELECT
                e.id as "id equipo", e.nombre as "nombre equipo", e.proyecto as "proyecto padre"
                , m.id as "id miembro", re.nombre as "rol", m.suspendido
                FROM
                equipo as  e
                INNER JOIN
                miembros_equipo as m
                ON e.id = m.equipo
                INNER JOIN
                roles_equipo as re
                ON re.id = m.rol
                WHERE m.miembro = %s
                ORDER BY e.id;
        """

        cursor.execute(select_query, (member_id,))

        teams_of_member: RowType | None = cursor.fetchall()

        cursor.close()
        cnx.close()

        return teams_of_member

    def __init__(
        self,
        nombre: str,
        fecha_creacion: date,
        proyecto: Union[int, "Proyecto"],
        id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.fecha_creacion = fecha_creacion
        self.proyecto = proyecto
