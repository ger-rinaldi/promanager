from models import Equipo, Proyecto, Ticket_Tarea, Usuario
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wsgi_app import Blueprint, render_template, request, required_login, session

bp = Blueprint("/usuario")


@bp.route("/dashboard")
@required_login
def dashboard():
    return Response(**render_template("user/dashboard.html"))


@bp.route("/proyecto")
@required_login
def user_proyects():
    data = Proyecto.get_by_participant(session["id"])

    if data:
        data_keys = data[0].keys()
    else:
        data_keys = []

    for d in data:
        if d["publico"] == 1:
            d["publico"] = "Sí"
        else:
            d["publico"] = "No"
        if d["activo"] == 1:
            d["activo"] = "Sí"
        else:
            d["activo"] = "No"

    if request.method == "POST":
        pass
    return Response(
        **render_template(
            "tables/generic_table.html",
            data=data,
            data_keys=data_keys,
            resource="proyecto",
        )
    )


@bp.route("/equipo")
@required_login
def user_teams():
    data = Equipo.get_by_member(session["id"])

    if data:
        data_keys = data[0].keys()
    else:
        data_keys = []

    if request.method == "POST":
        pass

    return Response(
        **render_template(
            "tables/generic_table.html",
            data=data,
            data_keys=data_keys,
            resource="equipo",
        )
    )


@bp.route("/tarea")
@required_login
def user_tasks():
    data = Ticket_Tarea.get_by_asigned_user(session["id"])

    if data:
        data_keys = data[0].keys()
    else:
        data_keys = []

    if request.method == "POST":
        pass

    return Response(
        **render_template(
            "tables/generic_table.html",
            data=data,
            data_keys=data_keys,
            resource="tarea",
        )
    )

