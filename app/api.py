from authentication import need_authorization, required_login
from db import context_db_manager
from models import Proyecto, Roles, Usuario
from werkzeug.wrappers import Response
from wsgi_app import Blueprint, make_json, request

bp = Blueprint("/api/usuario/<string:username>")


@bp.route("/proyecto/<proyect_id>/gral_stats")
@required_login
@need_authorization
def general_stats(username, proyect_id):
    with context_db_manager(dict=True) as db:
        db.execute(
            """select
            COALESCE(e.total_equipos, 0)  as "total_equipos"
            , COALESCE(tt.total_tareas, 0)  as "total_tareas"
            , COALESCE(ipr.total_integrantes, 0)  as "total_integrantes"
            from proyecto as p
            left join
            (select proyecto, count(id) as total_equipos from equipo group by proyecto)
            as e
            on p.id = e.proyecto
            left join
            (select proyecto, count(id) as total_tareas from ticket_tarea group by proyecto)
            as tt
            on p.id = tt.proyecto
            inner join
            (select proyecto, count(id) as total_integrantes from integrantes_proyecto group by proyecto)
            as ipr
            on p.id = ipr.proyecto
            where p.id = %s
            group by p.id;""",
            (proyect_id,),
        )

        data = db.fetchall()

    if data is None or not data:
        not_found = make_json(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    return make_json(**data[0])


@bp.route("/proyecto/<proyect_id>/user_stats")
@required_login
@need_authorization
def user_stats(username, proyect_id):
    with context_db_manager(dict=True) as db:
        data = {}

        total_tasks_n_teams = """SELECT
                COUNT(me.id) AS total_equipos
                , COALESCE(SUM(asigt.total), 0) AS total_tareas
                FROM usuario AS u
                INNER JOIN integrantes_proyecto AS ipr
                ON u.id = ipr.integrante
                INNER JOIN miembros_equipo AS me
                ON ipr.id = me.miembro
                INNER JOIN
                (SELECT COUNT(id) AS total, miembro FROM asignacion_tarea group by miembro) AS asigt
                ON me.id = asigt.miembro
                WHERE ipr.proyecto = %s AND u.username = %s"""

        db.execute(total_tasks_n_teams, (proyect_id, username))
        total_tasks_n_teams = db.fetchall()

        if total_tasks_n_teams is None:
            not_found = make_json(message="El recurso solicitado no fue encontrado")
            not_found.status = 404
            return not_found

        data.update(total_tasks_n_teams[0])
        data["total_tareas"] = int(data["total_tareas"])
        total_per_state = """SELECT
                st.nombre, COUNT(tt.id) AS "total"
                FROM usuario AS u
                INNER JOIN integrantes_proyecto AS ipr
                ON u.id = ipr.integrante
                INNER JOIN miembros_equipo AS me
                ON ipr.id = me.miembro
                INNER JOIN asignacion_tarea AS asigt
                ON me.id = asigt.miembro
                INNER JOIN ticket_tarea AS tt
                ON asigt.ticket_tarea = tt.id
                INNER JOIN estado AS st
                ON tt.estado = st.id
                WHERE ipr.proyecto = %s AND u.username = %s
                group by st.nombre
                order by st.id;"""

        db.execute(total_per_state, (proyect_id, username))
        query_result = db.fetchall()

        if query_result is None:
            not_found = make_json(message="El recurso solicitado no fue encontrado")
            not_found.status = 404
            return not_found

        data["por_estado"] = query_result

    return make_json(**data)


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
            st.id, st.nombre,
            IFNULL(count(tt.id), 0) as total
            from estado as st
            left join ticket_tarea as tt
            on st.id = tt.estado
            and tt.proyecto = %s
            group by st.id
            order by st.id
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


@bp.route("/proyecto/<proyect_id>/integrante/agregar")
@required_login
@need_authorization
def add_integrant(username, proyect_id):
    if request.method != "POST":
        bad_request = make_json(message="Mala peticion solo se recibe POST")
        bad_request.status = 400
        return bad_request

    errors = []

    current_proyect = Proyecto.get_by_id(proyect_id)
    current_proyect.load_own_resources(as_dicts=True)

    new_participant = Usuario.get_by_username_or_mail(
        request.form["participant_identif"]
    )
    participant_role = request.form.get("role", "rol_no_valido")

    if new_participant is None:
        errors.append("El usuario indicado no fue encontrado")

    elif new_participant.username in [
        p["username"] for p in current_proyect.participantes
    ]:
        errors.append("Este usuario ya participa en el proyecto")

    if not participant_role.isnumeric():
        errors.append("El rol seleccionado es inválido")

    elif int(participant_role) not in [x["id"] for x in Roles.get_proyect_roles()]:
        errors.append("El rol seleccionado no existe")

    if errors:
        error_response = make_json(message=errors)
        error_response.status = 400
        return error_response

    current_proyect.register_new_participant(new_participant.id, participant_role)

    success = make_json(
        message=f"El participante {new_participant.username} ha sido \
registrado como {Roles.proyect_role_name(participant_role)} con exito"
    )
    success.status = 200
    return success


@bp.route("/proyecto/<proyect_id>/integrante/modificar")
# @required_login
# @need_authorization
def update_integrant(username, proyect_id):
    if request.method != "POST":
        bad_request = make_json(message="Mala peticion solo se recibe POST")
        bad_request.status = 400
        return bad_request

    errors = []

    current_proyect = Proyecto.get_by_id(proyect_id)
    current_proyect.load_own_resources(as_dicts=True)

    participant_to_update = Usuario.get_by_username_or_mail(
        request.form["participant_identif"]
    )
    participant_role = request.form.get("role", "rol_no_valido")

    if participant_to_update is None:
        errors.append("El usuario indicado no fue encontrado")

    elif not participant_to_update.username in [
        p["username"] for p in current_proyect.participantes
    ]:
        errors.append("El usuario a modificar no participa del proyecto")

    if not participant_role.isnumeric():
        errors.append("El rol seleccionado es inválido")

    elif int(participant_role) not in [x["id"] for x in Roles.get_proyect_roles()]:
        errors.append("El rol seleccionado no existe")

    if errors:
        error_response = make_json(message=errors)
        error_response.status = 400
        return error_response

    current_proyect.update_participant(participant_to_update.id, participant_role)

    success = make_json(
        message=f"El participante {participant_to_update.username} ha \
sido establecido como {Roles.proyect_role_name(participant_role)} con exito"
    )
    success.status = 200
    return success


@bp.route("/proyecto/<proyect_id>/integrante/remover")
@required_login
@need_authorization
def remove_integrant(username, proyect_id):
    if request.method != "POST":
        bad_request = make_json(message="Mala peticion solo se recibe POST")
        bad_request.status = 400
        return bad_request

    current_proyect = Proyecto.get_by_id(proyect_id)
    current_proyect.load_own_resources(as_dicts=True)

    participant_to_remove = Usuario.get_by_username_or_mail(
        request.form["participant_identif"]
    )

    if participant_to_remove is None:
        no_such_user = make_json(message="El usuario indicado no fue encontrado")
        no_such_user.status = 404
        return no_such_user

    if not participant_to_remove.username in [
        p["username"] for p in current_proyect.participantes
    ]:
        not_a_participant = make_json(
            message="El usuario a remover no participa del proyecto"
        )
        not_a_participant.status = 409
        return not_a_participant

    current_proyect.delete_participant(participant_to_remove.id)

    success = make_json(
        message=f"El participante {participant_to_remove.username} ha sido removido con exito"
    )
    success.status = 200
    return success
