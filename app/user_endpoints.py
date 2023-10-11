from input_validation import validate_proyect
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


@bp.route("/proyecto/crear")
@required_login
def create_proyect():
    errors: list = []

    if request.method == "POST":
        gerente_id: str = request.form["dueno_id"]

        proyect_info: dict = {}

        proyect_info["nombre"]: str = request.form["nombre"]
        proyect_info["fecha_inicio"]: str = request.form["fecha_inicio"]
        proyect_info["fecha_finalizacion"]: str = request.form["fecha_finalizacion"]
        proyect_info["presupuesto"]: str = request.form["presupuesto"]
        proyect_info["descripcion"]: str = request.form["descripcion"]

        if request.form.get("es_publico", False):
            proyect_info["es_publico"]: bool = True
        else:
            proyect_info["es_publico"]: bool = False

        if request.form.get("activo", False):
            proyect_info["activo"]: bool = True
        else:
            proyect_info["activo"]: bool = False

        errors = validate_proyect.validate_all(
            name=proyect_info["nombre"],
            budget=proyect_info["presupuesto"],
            start_date=proyect_info["fecha_inicio"],
            end_date=proyect_info["fecha_finalizacion"],
        )

        if not errors:
            new_proyect = Proyecto(**proyect_info)
            new_proyect.create()
            new_proyect.register_new_participant(gerente_id, 1)

            return redirect(f"/usuario/proyecto/{new_proyect.id}/integrantes")

    return Response(
        **render_template(
            "/create_forms/crear-proyecto.html",
            errors=errors,
        )
    )


@bp.route("/proyecto/<int:proyect_id>/modificar")
@required_login
def modify_proyect(proyect_id):
    errors = []

    if request.method == "POST":
        proyect_info: dict = request.form.copy()

        if proyect_info.get("descripcion", False):
            proyect_info["descripcion"] = proyect_info["descripcion"].strip()

        if request.form.get("es_publico", False):
            proyect_info["es_publico"]: bool = True
        else:
            proyect_info["es_publico"]: bool = False

        if request.form.get("activo", False):
            proyect_info["activo"]: bool = True
        else:
            proyect_info["activo"]: bool = False

        errors = validate_proyect.validate_all(
            name=proyect_info["nombre"],
            budget=proyect_info["presupuesto"],
            start_date=proyect_info["fecha_inicio"],
            end_date=proyect_info["fecha_finalizacion"],
        )

        if not errors:
            proyect_to_update = Proyecto(**proyect_info, instatiate_components=False)
            proyect_to_update.update()

    proyect_to_update = Proyecto.get_by_id(proyect_id)

    return Response(
        **render_template(
            "/update_forms/ajustes-proyecto.html",
            proyect=proyect_to_update,
            errors=errors,
        )
    )


@bp.route("/proyecto/<int:proyect_id>/eliminar")
@required_login
def delete_proyect(proyect_id):
    if request.method == "POST":
        proyect_to_delete = Proyecto.get_by_id(proyect_id)
        proyect_to_delete.delete()
    return redirect("/usuario/proyecto")


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
