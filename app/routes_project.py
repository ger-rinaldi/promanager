from authentication import need_authorization, required_login
from input_validation import validate_proyect
from models import Proyecto, Roles, Usuario
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wsgi_app import Blueprint, render_template, request

bp = Blueprint("/usuario/<string:username>/proyecto")


@bp.route(is_prefix_endpoint=True)
@required_login
@need_authorization
def user_proyects(username):
    current_user = Usuario.get_by_username_or_mail(username)
    current_user.load_own_resources()
    data = current_user.proyectos

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
            current_user=current_user,
        )
    )


@bp.route("/crear")
@required_login
@need_authorization
def create_proyect(username):
    current_user = Usuario.get_by_username_or_mail(username)
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

            return redirect(f"{new_proyect.id}")

    return Response(
        **render_template(
            "/create_forms/crear-proyecto.html",
            errors=errors,
            current_user=current_user,
        )
    )


@bp.route("/<int:proyect_id>")
@required_login
@need_authorization
def read_proyect(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    current_proyect = Proyecto.get_by_id(proyect_id)
    errors = []

    return Response(
        **render_template(
            "read_views/read_proyecto.html",
            current_user=current_user,
            current_proyect=current_proyect,
            errors=errors,
        )
    )


@bp.route("/<int:proyect_id>/modificar")
@required_login
@need_authorization
def modify_proyect(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
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
            return redirect(f"/usuario/{current_user.username}/proyecto/{proyect_id}")

    proyect_to_update = Proyecto.get_by_id(proyect_id)

    return Response(
        **render_template(
            "/update_forms/ajustes-proyecto.html",
            proyect=proyect_to_update,
            errors=errors,
            current_user=current_user,
        )
    )


@bp.route("/<int:proyect_id>/metrics")
@required_login
@need_authorization
def metrics(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    current_proyect = Proyecto.get_by_id(proyect_id)

    return Response(
        **render_template(
            "read_views/metrics_proyecto.html",
            current_proyect=current_proyect,
            current_user=current_user,
        )
    )


@bp.route("/<int:proyect_id>/integrante")
@required_login
def register_new_participants(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    current_proyect = Proyecto.get_by_id(proyect_id)
    current_proyect.load_own_resources(as_dicts=True)
    errors = []

    return Response(
        **render_template(
            "/invitaciones/agregar_integrante.html",
            current_user=current_user,
            proyect=current_proyect,
            errors=errors,
            roles=Roles.get_proyect_roles(),
        )
    )
