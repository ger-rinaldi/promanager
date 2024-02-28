from datetime import date
from typing import Optional, Union

from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import CursorBase
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.types import RowType

import app.models.equipo as equipo_mod
import app.models.proyecto as proyecto_mod
from app.db import get_connection


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
        proyecto: Union[int, "proyecto_mod.Proyecto"],
        equipo: Union[int, "equipo_mod.Equipo"],
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
        self.proyecto = proyecto_mod.Proyecto.get_by_id(proyecto)
        self.equipo = equipo_mod.Equipo.get_by_id(equipo)
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
