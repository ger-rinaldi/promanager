from datetime import date
from typing import Any, Iterator, Optional

from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

import app.models.proyecto as proyecto
from app.db import context_db_manager, get_connection


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
        self.proyecto = proyecto.Proyecto.get_by_id(self.id_proyecto)

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

    def __iter__(self) -> Iterator["keyword":"value"]:
        yield "id", self.id
        yield "nombre", self.nombre
        yield "proyecto", self.id_proyecto
        yield "fecha_creacion", self.fecha_creacion

        if hasattr(self, "miembros") and self.miembros is not None:
            yield "miembros", self.miembros

        if hasattr(self, "tareas") and self.tareas is not None:
            yield "tareas", self.tareas
