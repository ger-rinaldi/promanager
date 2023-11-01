from authentication import need_authorization, required_login
from input_validation import validate_proyect, validate_user
from models import Equipo, Proyecto, Ticket_Tarea, Usuario, prefijos_telefonicos
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wsgi_app import Blueprint, render_template, request

bp = Blueprint("/usuario/<string:username>")


@bp.route("/modificar")
@required_login
@need_authorization
def modificar_usuario(username):
    template_name = "user/perfil_modificar.html"
    country_codes = prefijos_telefonicos.read_all()

    user_to_update = Usuario.get_by_username_or_mail(username)
    errors = []

    if request.method == "POST":
        form = request.form
        email = form["email"]
        name = form["nombre"]
        surname = form["apellido"]
        prefix = form["telefono_prefijo"]
        phone = form["telefono_numero"]
        nombre_usuario = form["username"]

        errors = validate_user.validate_update(
            email=email,
            name=name,
            surname=surname,
            phonenumber=phone,
            username=nombre_usuario,
        )

        if not errors:
            user_to_update.email = email
            user_to_update.nombre = name
            user_to_update.apellido = surname
            user_to_update.telefono_prefijo = prefix
            user_to_update.telefono_numero = phone
            user_to_update.username = nombre_usuario

            user_to_update.update()
            return redirect(f"perfil")

    return Response(
        **render_template(
            template_name=template_name,
            errors=errors,
            current_user=user_to_update,
            country_codes=country_codes,
        )
    )


@bp.route("/perfil")
@required_login
@need_authorization
def perfil(username):
    template_name = "user/perfil.html"
    current_user = Usuario.get_by_username_or_mail(username)

    return Response(**render_template(template_name, current_user=current_user))


@bp.route("/dashboard")
@required_login
@need_authorization
def dashboard(username):
    current_user = Usuario.get_by_username_or_mail(username)

    return Response(
        **render_template(
            "user/dashboard.html",
            current_user=current_user,
        )
    )


@bp.route("/proyecto")
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


@bp.route("/proyecto/crear")
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


@bp.route("/proyecto/<int:proyect_id>")
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


@bp.route("/proyecto/<int:proyect_id>/modificar")
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

    proyect_to_update = Proyecto.get_by_id(proyect_id)

    return Response(
        **render_template(
            "/update_forms/ajustes-proyecto.html",
            proyect=proyect_to_update,
            errors=errors,
            current_user=current_user,
        )
    )


@bp.route("/proyecto/<int:proyect_id>/eliminar")
@required_login
@need_authorization
def delete_proyect(username, proyect_id):
    if request.method == "POST":
        proyect_to_delete = Proyecto.get_by_id(proyect_id)
        proyect_to_delete.delete()
    return redirect(f"/usuario/{username}/proyecto")


@bp.route("/equipo")
@required_login
@need_authorization
def user_teams(username):
    current_user = Usuario.get_by_username_or_mail(username)
    current_user.load_own_resources()
    data = current_user.equipos

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
            current_user=current_user,
        )
    )


@bp.route("/tarea")
@required_login
@need_authorization
def user_tasks(username):
    current_user = Usuario.get_by_username_or_mail(username)
    current_user.load_own_resources()
    data = current_user.tareas

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
            current_user=current_user,
        )
    )
