from input_validation import Errors, validate_user
from models import Usuario, prefijos_telefonicos
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response
from wsgi_app import (
    Blueprint,
    generate_session_cookies,
    make_response,
    render_template,
    request,
    session,
    set_session_values,
)

bp = Blueprint(base_prefix="auth")


@bp.route(endpoint_route="/register", is_prefix_endpoint=True)
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

        errors = validate_user.validate_all(
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

    return make_response(
        render_template(
            register_template,
            errors=errors,
            country_codes=country_codes,
        )
    )


@bp.route(endpoint_route="/login")
def login():
    template_name = "auth/login.html"
    errors = []

    if request.method == "POST":
        user_auth_info = request.form

        valid_email = validate_user.email_address_validator(user_auth_info["identif"])
        registered_email = validate_user.check_email_not_registered(
            user_auth_info["identif"]
        )
        valid_username = validate_user.username_length(user_auth_info["identif"])
        registered_username = not validate_user.username_not_registered(
            user_auth_info["identif"]
        )

        if not valid_email and not valid_username:
            errors.append("La identificación ingresada no es válida")
        elif valid_username and not registered_username:
            errors.append("Nombre de usuario no registrado.")
        elif valid_email and not registered_email:
            errors.append("Email no registrado")

        if errors:
            response = make_response(render_template(template_name, errors=errors))
            return response

        logged_user = Usuario.get_user_auth(**user_auth_info)

        if not logged_user:
            errors.append("Error al autenticar. Contraseña o e-mail erróneos.")
            response = make_response(render_template(template_name, errors=errors))
            return response

        session_cookie = generate_session_cookies()

        if logged_user.set_session_id(session_cookie["value"]):
            set_session_values(logged_user)
            response = redirect("/usuario/dashboard")
            response.set_cookie(**session_cookie)

            return response

        else:
            errors.append("Hubo un error al establecer su sesión.")

    response = make_response(render_template(template_name, errors=errors))
    return response


@bp.route("/login_required")
def ask_login():
    response = make_response(render_template("login_required.html"))
    response.status = 401

    return response


@bp.route("/logout")
def logout():
    Usuario.remove_session(session["id"])

    session.clear()

    response = redirect("/")

    dummy_cookies = generate_session_cookies()

    response.set_cookie(**dummy_cookies)
    return response
