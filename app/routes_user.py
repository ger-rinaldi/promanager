from authentication import need_authorization, required_login
from input_validation import validate_user
from models import Usuario, prefijos_telefonicos
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wsgi_app import Blueprint, render_template, request

bp = Blueprint("/usuario/<string:username>", "dashboard")


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
            return redirect(f"/usuario/{user_to_update.username}/perfil")

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
