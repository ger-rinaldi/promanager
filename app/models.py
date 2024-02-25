from datetime import date
from typing import Any, Optional, Sequence, Union

from bcrypt import checkpw, gensalt, hashpw
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

from app.db import close_conn_cursor, context_db_manager, get_connection


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
        self.proyectos = Proyecto._get_all_of_participant(self.id)
        self.equipos = Equipo._get_by_member(self.id)
        self.tareas = Ticket_Tarea._get_by_asigned_user(self.id)

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


class Proyecto:
    @classmethod
    def _get_all_of_participant(cls, participant_id):
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
        instatiate_components: Optional[bool] = False,
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
            self.load_own_resources(components_as_dicts)

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

    def update(self) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        insert_query: str = """UPDATE proyecto
        SET
        nombre=%s, descripcion=%s, es_publico=%s, activo=%s,
        presupuesto=%s, fecha_inicio=%s, fecha_finalizacion=%s
        WHERE id=%s"""

        cursor.execute(insert_query, (*self.__tuple__(), self.id))

        cnx.commit()
        cursor.close()
        cnx.close()

    def delete(self) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        delete_query: str = "DELETE FROM proyecto WHERE id = %s"

        cursor.execute(delete_query, (self.id,))

        cnx.commit()
        cursor.close()
        cnx.close()

    def register_new_participant(self, participant_id: int, role_id: int) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        insert_participant = """INSERT INTO
        integrantes_proyecto(proyecto, integrante, rol )
        VALUES (%s, %s, %s)"""

        cursor.execute(insert_participant, (self.id, participant_id, role_id))

        cnx.commit()
        cursor.close()
        cnx.close()
        self._fetch_all_participants()

    def update_participant(self, participant_id: int, role_id: int) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        update_participant = """UPDATE integrantes_proyecto
        SET rol=%s
        WHERE proyecto=%s AND integrante=%s"""

        cursor.execute(update_participant, (role_id, self.id, participant_id))

        cnx.commit()
        cursor.close()
        cnx.close()
        self._fetch_all_participants()

    def delete_participant(self, participant_id: int) -> None:
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor()

        update_participant = """DELETE FROM integrantes_proyecto
        WHERE proyecto=%s AND integrante=%s"""

        cursor.execute(update_participant, (self.id, participant_id))

        cnx.commit()
        cursor.close()
        cnx.close()
        self._fetch_all_participants()

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
            i.id,
            rp.nombre as rol,
            u.username,  u.nombre, u.apellido, u.email, CONCAT(pf.prefijo, "-", u.telefono_numero) as "telefono_numero"
            FROM
            integrantes_proyecto as i
            INNER JOIN
            roles_proyecto as rp
            ON rp.id = i.rol
            INNER JOIN
            usuario as u
            ON i.integrante = u.id
            INNER JOIN
            prefijo_telefono as pf
            ON pf.id = u.telefono_prefijo
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

    def load_own_resources(self, as_dicts: bool):
        self._fetch_all_participants(as_dicts)
        self._fetch_all_tasks(as_dicts)
        self._fetch_all_teams(as_dicts)

    def user_can_modify(self, user_id):
        query = """
        select true
        from integrantes_proyecto
        where integrante = %s and proyecto = %s and rol = %s
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, (user_id, self.id, 1))

        result = cursor.fetchone()

        if result is not None and result[0] == 1:
            return True

        return False

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
        return f"id: {self.id}, nombre: {self.nombre}, \
            presupuesto: {self.presupuesto}, inicio: {self.fecha_inicio}"

    def __iter__(self) -> None:
        yield "id", self.id
        yield "nombre", self.nombre
        yield "descripcion", self.descripcion
        yield "es_publico", self.es_publico
        yield "activo", self.activo
        yield "presupuesto", self.presupuesto
        yield "fecha_inicio", self.fecha_inicio
        yield "fecha_finalizacion", self.fecha_finalizacion

        if hasattr(self, "participantes") and self.participantes is not None:
            yield "participantes", self.participantes

        if hasattr(self, "equipos") and self.equipos is not None:
            yield "equipos", self.equipos


class Ticket_Tarea:
    @classmethod
    def _get_by_asigned_user(cls, user_id):
        cnx: MySQLConnection | PooledMySQLConnection = get_connection()
        cursor: CursorBase = cnx.cursor(dictionary=True)

        select_query: str = """select
            t.id as "id tarea", t.proyecto as "proyecto padre", t.equipo as "equipo encargado"
            , t.nombre, t.estado, t.fecha_asignacion as "asignada a equipo"
            , t.fecha_limite as "limite", a.id as "asignacion nº"
            , a.fecha_asignacion as "asignada a usuario"
            from
            ticket_tarea as t
            inner join
            asignacion_tarea as a
            on t.id = a.ticket_tarea
            inner join
            miembros_equipo as m
            on a.miembro = m.id
            inner join
            integrantes_proyecto as ipr
            on m.miembro = ipr.id
            inner join
            usuario as u
            on ipr.integrante = u.id
            where u.id = %s
            order by t.id;
        """

        cursor.execute(select_query, (user_id,))

        tasks_of_user: RowType | None = cursor.fetchall()

        cursor.close()
        cnx.close()

        return tasks_of_user

    @classmethod
    def get_by_id(csl, task_id):
        query = """
        SELECT
        id, proyecto, equipo, nombre, estado, descripcion,
        fecha_creacion, fecha_asignacion,
        fecha_limite, fecha_finalizacion
        FROM
        ticket_tarea
        WHERE id = %s
        """

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, (task_id,))

        queried_task = cursor.fetchone()

        if queried_task is not None:
            return Ticket_Tarea(**queried_task)

        return None

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
        self.proyecto = Proyecto.get_by_id(proyecto)
        self.equipo = Equipo.get_by_id(equipo)
        self.nombre = nombre
        self.estado = estado
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion
        self.fecha_asignacion = fecha_asignacion
        self.fecha_limite = fecha_limite
        self.fecha_finalizacion = fecha_finalizacion

    def user_can_modify(self, user_id):
        if self.proyecto.user_can_modify(user_id) or self.equipo.user_can_modify(
            user_id
        ):
            return True

        return False


class Equipo:
    @classmethod
    def _get_by_member(cls, member_id):
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
                INNER JOIN
                integrantes_proyecto as ipr
                ON ipr.id = m.miembro
                INNER JOIN
                usuario as u
                ON u.id = ipr.integrante
                WHERE u.id = %s
                ORDER BY e.id;
        """

        cursor.execute(select_query, (member_id,))

        teams_of_member: RowType | None = cursor.fetchall()

        cursor.close()
        cnx.close()

        return teams_of_member

    @classmethod
    def _get_by_project(cls, project_id: int):
        query = "SELECT * FROM equipo WHERE proyecto = %s"

        with context_db_manager(dict=True) as conn:
            conn.execute(query, (project_id,))

            teams_of_project: list[dict] | None = conn.fetchall()

        return teams_of_project

    @classmethod
    def get_by_id(csl, task_id):
        query = """
        SELECT
        nombre, fecha_creacion, proyecto, id
        FROM
        equipo
        WHERE id = %s
        """

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, (task_id,))

        queried_team = cursor.fetchone()

        if queried_team is not None:
            return Equipo(**queried_team)

        return None

    @classmethod
    def exists(cls, team_atribute: int | str):
        existance_query = "SELECT 1 FROM equipo WHERE %s IN (id, nombre);"

        with context_db_manager() as conn:
            conn.execute(existance_query, (team_atribute,))

            query_result = conn.fetchone()

        if query_result is None:
            return False

        return True

    def __init__(
        self,
        nombre: str,
        proyecto: int,
        fecha_creacion: Optional[date] = None,
        id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.fecha_creacion = fecha_creacion
        self.id_proyecto = proyecto

    def _query_id(self):
        with context_db_manager() as conn:
            conn.execute("SELECT id FROM equipo WHERE nombre = %s", (self.nombre,))
            self.id = conn.fetchone()[0]

    def create(self) -> None:
        if self.fecha_creacion is None:
            fields = "(proyecto, nombre)"
            value_placeholder = "(%s,%s)"
            values = (self.id_proyecto, self.nombre)
        else:
            fields = "(proyecto, nombre, fecha_creacion)"
            value_placeholder = "(%s,%s,%s)"
            values = (self.id_proyecto, self.nombre, self.fecha_creacion)

        create_query = f"INSERT INTO equipo{fields} VALUES {value_placeholder}"

        with context_db_manager() as db_conn:
            db_conn.execute(
                create_query,
                values,
            )
            db_conn.connection.commit()

        self._query_id()

    def update(self) -> None:
        with context_db_manager() as conn:
            conn.execute(
                """UPDATE equipo 
                SET nombre = %s, fecha_creacion = %s
                WHERE id = %s""",
                (self.nombre, self.fecha_creacion, self.id),
            )
            conn.connection.commit()

    def delete(self) -> None:
        with context_db_manager() as conn:
            conn.execute(
                "DELETE FROM equipo WHERE id = %s",
                (self.id,),
            )
            conn.connection.commit()

    def user_can_modify(self, user_id):
        query = """
            select true
            from
            miembros_equipo as m
            inner join
            integrantes_proyecto as ipr
            on m.miembro = ipr.id
            inner join
            usuario as u
            on ipr.integrante = u.id
            where u.id = %s and m.equipo = %s and (m.rol = %s  or ipr.rol = %s);
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, (user_id, self.id, 1, 1))

        result = cursor.fetchone()

        if result is not None and result[0] == 1:
            return True

        return False

    def load_own_resources(self, project_class: bool) -> None:
        self._fetch_all_tasks()
        self._fetch_all_members()
        self._fetch_project(project_class)

    def register_new_member(self, member_id: int, role_id: int) -> None:
        pass

    def update_member(self, member_id: int, role_id: int) -> None:
        pass

    def delete_member(self, member_id: int) -> None:
        pass

    def _fetch_all_members(self) -> list[RowType]:
        with context_db_manager(dict=True) as conn:
            conn.execute(
                """
            SELECT me.id, rp.nombre as rol, u.username, u.nombre, u.apellido, u.email,
                CONCAT(pf.prefijo, "-", u.telefono_numero) as "telefono_numero"
            FROM
                miembros_equipo as me
                INNER JOIN roles_equipo as rp ON rp.id = me.rol
                INNER JOIN usuario as u ON me.miembro = u.id
                INNER JOIN prefijo_telefono as pf ON pf.id = u.telefono_prefijo
            WHERE
                me.equipo = %s
                        """,
                (self.id,),
            )

            self.miembros = conn.fetchall()

    def _fetch_project(self, as_dict: bool) -> list[RowType]:
        self.proyecto = Proyecto.get_by_id(self.id_proyecto)

        if not as_dict:
            self.proyecto = dict(self.proyecto)

    def _fetch_all_tasks(self) -> list[RowType]:
        with context_db_manager(dict=True) as conn:
            conn.execute("SELECT * FROM ticket_tarea WHERE equipo = %s", (self.id,))

            self.tareas = conn.fetchall()

    def __tuple__(self, with_id: bool = False) -> tuple:
        self_as_tuple: list[Any] = [
            self.id_proyecto,
            self.nombre,
        ]

        if self.fecha_creacion is not None:
            self_as_tuple.append(self.fecha_creacion)

        if with_id:
            self_as_tuple.insert(0, self.id)

        return tuple(self_as_tuple)

    def __repr__(self) -> str:
        return f"id: {self.id}, nombre: {self.nombre}, \
proyecto: {self.id_proyecto}, creado: {self.fecha_creacion}"

    def __iter__(self):
        yield "id", self.id
        yield "nombre", self.nombre
        yield "proyecto", self.id_proyecto
        yield "fecha_creacion", self.fecha_creacion

        if hasattr(self, "miembros") and self.miembros is not None:
            yield "miembros", self.miembros

        if hasattr(self, "tareas") and self.tareas is not None:
            yield "tareas", self.tareas


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
