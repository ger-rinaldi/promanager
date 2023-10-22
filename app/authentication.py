import datetime
import functools
import secrets
import types

from config import DOMAIN
from db import close_conn_cursor, get_connection
from models import Usuario
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wsgi_app import request


def generate_session_cookies() -> dict:
    """Función para generar las cookies de sesión de usuario.
    "key": "sessionId",
    "value": id de sesión,
    "max_age": 5 días,
    "expires": 5 días,
    "path": "/",
    "domain": dominio del sitio,
    "secure": True,
    "httponly": True,
    "samesite": "lax",

    Returns:
        dict: con los valores previamente expresados.
    """

    max_age = datetime.timedelta(days=5)
    expires = datetime.datetime.now(datetime.timezone.utc) + max_age

    session_cookies = {
        "key": "sessionId",
        "value": secrets.token_urlsafe(16),
        "max_age": max_age,
        "expires": expires,
        "path": "/",
        "domain": DOMAIN,
        "secure": True,
        "httponly": True,
        "samesite": "lax",
    }

    return session_cookies



def required_login(func: types.FunctionType) -> Response:
    """Decorador de verificación de sesion de usuario en cliente.
    Recibe la función de un endpoint/vista y la ejecuta solamente
    si el usuarió cuenta con cookies de sesión y dicha sesión
    esta registrada en la base de datos.

    Returns:
        Function: ejecuta la funcion de endpoint y retorna su respuesta (response).
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        if "sessionId" in request.cookies.keys():
            sessionId = request.cookies["sessionId"]
        else:
            return redirect("/auth/login_required")

        from db import close_conn_cursor, get_connection

        cnx = get_connection()

        cursor = cnx.cursor()

        cursor.execute("SELECT 1 FROM usuario WHERE llave_sesion = %s", (sessionId,))

        query_result = cursor.fetchone()

        close_conn_cursor(cnx, cursor)

        if query_result is None:
            return redirect("/auth/login_required")

        return func(*args, **kwargs)

    return wrapper
