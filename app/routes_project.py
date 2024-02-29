from flask import Blueprint, make_response, render_template, request
from werkzeug.utils import redirect
from werkzeug.wrappers import Response

from app.authentication import need_authorization, required_login
from app.models import Proyecto, Roles, Usuario
from app.validation.full import validate_project

bp = Blueprint(
    name="project",
    import_name=__name__,
    url_prefix="/usuario/<string:username>/proyecto",
)


@bp.get("/")
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

    return render_template(
        "tables/generic_table.html",
        data=data,
        data_keys=data_keys,
        resource="proyecto",
        current_user=current_user,
    )


@bp.get("/crear")
@required_login
@need_authorization
def create_proyect(username):
    current_user = Usuario.get_by_username_or_mail(username)

    return render_template(
        "/create_forms/crear-proyecto.html",
        current_user=current_user,
    )


@bp.get("/<int:proyect_id>")
@required_login
@need_authorization
def read_proyect(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    current_proyect = Proyecto.get_by_id(proyect_id)
    errors = []

    return render_template(
        "read_views/read_proyecto.html",
        current_user=current_user,
        current_proyect=current_proyect,
        errors=errors,
    )


@bp.get("/<int:proyect_id>/modificar")
@required_login
@need_authorization
def modify_proyect(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    errors = []

    proyect_to_update = Proyecto.get_by_id(proyect_id)

    return render_template(
        "/update_forms/ajustes-proyecto.html",
        proyect=proyect_to_update,
        errors=errors,
        current_user=current_user,
    )


@bp.get("/<int:proyect_id>/metrics")
@required_login
@need_authorization
def metrics(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    current_proyect = Proyecto.get_by_id(proyect_id)

    return render_template(
        "read_views/metrics_proyecto.html",
        current_proyect=current_proyect,
        current_user=current_user,
    )


@bp.get("/<int:proyect_id>/integrante")
@required_login
def register_new_participants(username, proyect_id):
    current_user = Usuario.get_by_username_or_mail(username)
    current_proyect = Proyecto.get_by_id(proyect_id)
    current_proyect.load_own_resources(as_dicts=True)
    errors = []

    return render_template(
        "/invitaciones/agregar_integrante.html",
        current_user=current_user,
        proyect=current_proyect,
        errors=errors,
        roles=Roles.get_proyect_roles(),
    )
