from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response
from wsgi_app import Blueprint, get_session_cookies, make_response, render_template

bp = Blueprint(base_prefix="auth")


@bp.route(endpoint_route="/register", is_prefix_endpoint=True)
def register(request):
    from input_validation import validate_user
    from models import Usuario, prefijos_telefonicos

    register_template = "auth/register.html"
    errors = []

    if request.method == "POST":
        form = request.form
        email = form["email"]
        password = form["contrasena"]
        name = form["nombre"]
        surname = form["apellido"]
        phone = form["telefono_numero"]

        errors = validate_user.validate_all(
            password=password,
            email=email,
            name=name,
            surname=surname,
            phonenumber=phone,
        )

        if not errors:
            new_user: "Usuario" = Usuario(**form)
            new_user.create()
            return redirect("/")

    country_codes = prefijos_telefonicos.read_all()

    return make_response(
        render_template(
            register_template,
            errors=errors,
            country_codes=country_codes,
        )
    )


@bp.route(endpoint_route="/login")
def login(request: Request):
    template_name = "auth/login.html"
    response = make_response(render_template(template_name))
    errors = []

    if request.method == "POST":
        from models import Usuario

        user_auth_info = request.form

        logged_user = Usuario.get_user_auth(**user_auth_info)

        if not logged_user:
            errors.append("Error al autenticar. Contraseña o e-mail erróneos.")

        session_cookie = get_session_cookies()

        if logged_user.set_session_id(session_cookie["value"]):
            response.set_cookie(**session_cookie)
        else:
            errors.append("Hubo un error al establecer su sesión.")

        redered_template = render_template(template_name, errors=errors)

        response.response = redered_template["response"]
        response.mimetype = redered_template["mimetype"]

    return response
