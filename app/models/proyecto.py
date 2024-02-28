from datetime import date
from typing import Any, Iterator, Optional, Union

from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

import app.models.equipo as equipo
import app.models.ticket_tarea as ticket_tarea
import app.models.usuario as usuario
from app.db import get_connection


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
                self.participantes.append(usuario.Usuario(**i))

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
                self.equipos.append(equipo.Equipo(**t))

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
                self.tareas.append(ticket_tarea.Ticket_Tarea(**t))

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

    def __iter__(self) -> Iterator["keyword":"value"]:
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
