import datetime
import functools
import secrets
import types

from flask import request
from werkzeug.utils import redirect
from werkzeug.wrappers import Response

from app.config import DOMAIN
from app.db import close_conn_cursor, get_connection
from app.models import Equipo, Proyecto, Ticket_Tarea, Usuario


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


def _is_logged() -> bool:
    request_session_id = request.cookies.get("sessionId", False)

    if not request_session_id:
        return False

    cnx = get_connection()

    cursor = cnx.cursor(dictionary=True)

    cursor.execute(
        "SELECT 1 FROM usuario WHERE llave_sesion = %s",
        (request_session_id,),
    )

    key_exists = cursor.fetchone()

    close_conn_cursor(cnx, cursor)

    if key_exists is None:
        return False

    return True


def _has_access() -> bool:
    request_session_id = request.cookies.get("sessionId", False)
    resources_queried = _required_resources()

    user_by_path = Usuario.get_by_username_or_mail(resources_queried["usuario"])
    user_by_cookies = Usuario.get_by_session_id(request_session_id)

    if user_by_path is None or user_by_cookies is None:
        return False

    if (
        user_by_cookies.llave_sesion != user_by_path.llave_sesion
        or user_by_cookies.username != user_by_path.username
    ):
        return False

    resources_queried.pop("usuario")
    user_by_cookies.load_own_resources()

    user_resources = {
        "proyecto": [str(p["id proyecto"]) for p in user_by_cookies.proyectos],
        "equipo": [str(e["id equipo"]) for e in user_by_cookies.equipos],
        "tarea": [str(t["id tarea"]) for t in user_by_cookies.tareas],
    }

    for resource, value in resources_queried.items():
        if value not in user_resources[resource]:
            return False

    return True


def _can_modify():
    resources_queried = _required_resources()

    request_session_id = request.cookies.get("sessionId", False)
    user_in_session = Usuario.get_by_session_id(request_session_id)

    if "proyecto" in resources_queried.keys():
        required_proyect = Proyecto.get_by_id(resources_queried["proyecto"])
        if not required_proyect.user_can_modify(user_in_session.id):
            return False

    if "equipo" in resources_queried.keys():
        required_team = Equipo.get_by_id(resources_queried["equipo"])
        if not required_team.user_can_modify(user_in_session.id):
            return False

    if "tarea" in resources_queried.keys():
        required_task = Ticket_Tarea.get_by_id(resources_queried["tarea"])
        if not required_task.user_can_modify(user_in_session.id):
            return False

    return True


def _required_resources():
    splitted_path = _get_split_request_path()

    resources = ("usuario", "proyecto", "equipo", "tarea")
    queried_resources = {}

    for r in resources:
        if r in splitted_path and splitted_path.index(r) < len(splitted_path) - 1:
            resource_id = splitted_path[splitted_path.index(r) + 1]

            if resource_id == "crear" or resource_id == "":
                continue

            queried_resources[r] = resource_id

    return queried_resources


def _get_split_request_path():
    request_path = request.path
    return request_path.split("/")


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
        if not _is_logged():
            return redirect("/auth/login_required")

        return func(*args, **kwargs)

    return wrapper


def need_authorization(func: types.FunctionType) -> Response:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        if not _has_access():
            return redirect("/auth/access_denied")

        splitted_path = _get_split_request_path()

        if splitted_path[-1] in ["modificar", "eliminar"] and not _can_modify():
            return redirect("/auth/access_denied")

        return func(*args, **kwargs)

    return wrapper
