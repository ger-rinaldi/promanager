from flask import Blueprint, make_response, render_template, request
from werkzeug.utils import redirect

import app.validation as validation
from app.authentication import generate_session_cookies, required_login
from app.models import Usuario, prefijos_telefonicos

bp = Blueprint(
    name="auth",
    import_name=__name__,
    template_folder="auth",
    url_prefix="/auth",
)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/register", methods=["GET", "POST"])
def register():
    register_template = "auth/register.html"
    errors = []

    if request.method == "POST":
        form = request.form
        email = form["email"]
        password = form["contrasena"]
        name = form["nombre"]
        surname = form["apellido"]
        phone = form["telefono_numero"]
        username = form["username"]

        errors = validation.validate_user(
            password=password,
            email=email,
            name=name,
            surname=surname,
            phonenumber=phone,
            username=username,
        )

        if not errors:
            new_user: "Usuario" = Usuario(**form)
            new_user.create()
            return redirect("/auth/login")

    country_codes = prefijos_telefonicos.read_all()

    return render_template(
        register_template,
        errors=errors,
        country_codes=country_codes,
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    template_name = "auth/login.html"
    errors = []

    if request.method == "POST":
        user_auth_info = request.form

        valid_email = validation.email_address(user_auth_info["identif"])
        registered_email = validation.email_exists(user_auth_info["identif"])
        valid_username = validation.username_length(user_auth_info["identif"])
        registered_username = validation.username_exists(user_auth_info["identif"])

        if not valid_email and not valid_username:
            errors.append("La identificación ingresada no es válida")
        elif valid_username and not registered_username:
            errors.append("Nombre de usuario no registrado.")
        elif valid_email and not registered_email:
            errors.append("Email no registrado")

        if errors:
            response = make_response(render_template(template_name, errors=errors))
            return response

        logged_user = Usuario.get_authenticated(**user_auth_info)

        if not logged_user:
            errors.append("Error al autenticar. Contraseña o e-mail erróneos.")
            response = make_response(render_template(template_name, errors=errors))
            return response

        session_cookie = generate_session_cookies()

        if logged_user.set_session_id(session_cookie["value"]):
            response = redirect(f"/usuario/{logged_user.username}/dashboard")
            response.set_cookie(**session_cookie)

            return response

        else:
            errors.append("Hubo un error al establecer su sesión.")

    return render_template(template_name, errors=errors)


@bp.get("/login_required")
def ask_login():
    response = make_response(render_template("login_required.html"))
    response.status = 401

    return response


@bp.get("/access_denied")
@required_login
def denied_access():
    response = make_response(render_template("access_denied.html"))
    response.status = 403

    return response


@bp.get("/logout")
@required_login
def logout():
    response = redirect("/")

    dummy_cookies = generate_session_cookies()

    response.set_cookie(**dummy_cookies)
    return response
