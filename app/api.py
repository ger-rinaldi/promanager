from authentication import need_authorization, required_login
from db import context_db_manager
from models import Proyecto, Usuario
from werkzeug.wrappers import Response
from wsgi_app import Blueprint, make_json, request

bp = Blueprint("/api/usuario/<string:username>")


@bp.route("/proyecto/<proyect_id>/tareas_equipo")
@required_login
@need_authorization
def task_per_team(username, proyect_id):
    data = None

    with context_db_manager(dict=True) as db:
        db.execute(
            """select
            e.id, e.nombre, count(tt.id) as total
            from proyecto as p
            inner join equipo as e
            on p.id = e.proyecto
            left join ticket_tarea as tt
            on e.id = tt.equipo
            where p.id = %s
            group by e.id
            """,
            (proyect_id,),
        )

        data = db.fetchall()

    if data is None or not data:
        not_found = make_json(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    return make_json(*data)


@bp.route("/proyecto/<proyect_id>/miembros_equipo")
@required_login
@need_authorization
def members_per_team(username, proyect_id):
    data = None

    with context_db_manager(dict=True) as db:
        db.execute(
            """select
            e.id, e.nombre, count(m.id) as "total"
            from equipo as e
            inner join miembros_equipo as m
            on e.id = m.equipo
            where e.proyecto = %s
            group by e.id
            """,
            (proyect_id,),
        )

        data = db.fetchall()

    if data is None or not data:
        not_found = make_json(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    return make_json(*data)


@bp.route("/proyecto/<proyect_id>/estado_tareas")
@required_login
@need_authorization
def tasks_per_status(username, proyect_id):
    data = None

    with context_db_manager(dict=True) as db:
        db.execute(
            """select
            st.id, st.nombre, count(tt.id) as "total"
            from estado as st
            inner join ticket_tarea as tt
            on st.id = tt.estado
            where tt.proyecto = %s
            group by st.id
            """,
            (proyect_id,),
        )

        data = db.fetchall()

    if data is None or not data:
        not_found = make_json(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    return make_json(*data)


@bp.route("/proyecto/<proyect_id>/eliminar")
@required_login
@need_authorization
def delete_proyect(username, proyect_id):
    if request.method != "POST":
        bad_request = make_json(message="Mala peticion solo se recibe POST")
        bad_request.status = 400

        return bad_request

    proyect_to_delete = Proyecto.get_by_id(proyect_id)

    if proyect_to_delete is None:
        not_found = make_json(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    proyect_to_delete.delete()

    success = make_json(
        message="Eliminado exitosamente",
    )

    success.status = 200
    return success


@bp.route("/eliminar")
@required_login
@need_authorization
def delete_user(username):
    if request.method != "POST":
        bad_request = make_json(message="Mala peticion solo se recibe POST")
        bad_request.status = 400
        return bad_request

    user_to_delete = Usuario.get_by_username_or_mail(username)

    if user_to_delete is None:
        not_found = make_json(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    if not user_to_delete._authenticate(username, request.form.get("contrasena_1", "")):
        access_denied = make_json(message="No tienes acceso al recurso autorizado")
        access_denied.status = 403
        return access_denied

    user_to_delete.delete()

    success = make_json(message="Eliminado exitosamente")
    success.status = 200
    return success
