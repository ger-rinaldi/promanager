from flask import Blueprint, make_response, render_template, request
from werkzeug.utils import redirect
from werkzeug.wrappers import Response

from app.authentication import need_authorization, required_login
from app.input_validation import validate_user
from app.models import Usuario, prefijos_telefonicos

bp = Blueprint(
    name="user",
    import_name=__name__,
    url_prefix="/usuario/<string:username>",
)


@bp.route("/modificar", methods=["GET", "POST"])
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

    return render_template(
        template_name=template_name,
        errors=errors,
        current_user=user_to_update,
        country_codes=country_codes,
    )


@bp.get("/perfil")
@required_login
@need_authorization
def perfil(username):
    template_name = "user/perfil.html"
    current_user = Usuario.get_by_username_or_mail(username)

    return render_template(template_name, current_user=current_user)


@bp.get("/")
@bp.get("/dashboard")
@required_login
@need_authorization
def dashboard(username):
    current_user = Usuario.get_by_username_or_mail(username)

    return render_template(
        "user/dashboard.html",
        current_user=current_user,
    )


@bp.get("/equipo")
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

    return render_template(
        "tables/generic_table.html",
        data=data,
        data_keys=data_keys,
        resource="equipo",
        current_user=current_user,
    )


@bp.get("/tarea")
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

    return render_template(
        "tables/generic_table.html",
        data=data,
        data_keys=data_keys,
        resource="tarea",
        current_user=current_user,
    )
