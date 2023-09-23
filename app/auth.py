from werkzeug.utils import redirect
from wsgi_app import Blueprint, render_template

bp = Blueprint(default="auth")


@bp.add_route(route="/register")
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

    return render_template(
        register_template,
        errors=errors,
        country_codes=country_codes,
    )


@bp.add_route(route="/login")
def login(request):
    login_template = "auth/login.html"
    return render_template(login_template)
