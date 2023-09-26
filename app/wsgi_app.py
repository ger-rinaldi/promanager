import datetime
import functools
import os
import secrets
import types

from config import DOMAIN
from jinja2 import Environment, FileSystemLoader, Template
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response

template_path = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)


def render_template(template_name: str, **context) -> dict[Template, str]:
    """Retorna un template jinja renderizado.

    Args:
        template_name (str): Nombre y path de template dentro de app/templates
        context (kwargs): Valores que el template pueda requerir para su renderización.
    Returns:
        dict: retorna un diccionario con el template como 'response' y mimetype de text/html
    """

    template = jinja_env.get_template(template_name)
    return {"response": template.render(context), "mimetype": "text/html"}


def get_session_cookies() -> dict:
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

    now = datetime.datetime.now(datetime.timezone.utc)
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
        request: Request = args[0]

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


def make_response(response_attr: dict) -> Response:
    """_summary_

    Args:
    response_attr: atributos con los que la respuesta del servidor
    debe ser instanciada.

    Returns:
        Response: respuesta de servidor.
    """

    return Response(**response_attr)


def _get_endpoint_name(endpoint: str | types.FunctionType) -> str:
    """Obtiene el nombre de los endpoints que recibe,
    permite abtrae el manejo de la situación de enpoints que sean
    strings o funciones.

    Visibilidad privada, sólo del módulo.

    Args:
        endpoint (str, Function): endpoint del cual debe obtenerse el nombre, si str, retornar sin cambios.

    Raises:
        Exception: Solo acepta str y Function

    Returns:
        str: nombre del endpoint
    """

    if isinstance(endpoint, types.FunctionType):
        return endpoint.__name__
    elif isinstance(endpoint, str):
        return endpoint

    raise Exception("_get_endpoint_name expects either a Function or a str")


class Blueprint:
    def __init__(self, base_prefix: str, prefix_endpoint: str = None) -> None:
        self.url_map = Map()
        self.base_prefix = self._add_root_to_route(base_prefix)

        if prefix_endpoint is None:
            self.prefix_endpoint = prefix_endpoint
        else:
            self.prefix_endpoint = self._add_prefix_to_route(prefix_endpoint)

        if self.base_prefix is not None and self.prefix_endpoint is not None:
            self._add_rule(self.base_prefix, self.prefix_endpoint)

        self.endpoints = []

    def _add_root_to_route(self, route):
        if not route[0] == "/":
            return f"/{route}"

        return route

    def _add_prefix_to_route(self, route):
        route = self._add_root_to_route(route)

        if not route.startswith(self.base_prefix):
            return f"{self.base_prefix}{route}"

        return route

    def _add_rule(self, route, endpoint):
        endpoint_name = _get_endpoint_name(endpoint)

        self.url_map.add(Rule(route, endpoint=endpoint_name))
        self.endpoints.append(endpoint)

    def set_base_prefix(self, prefix_base_of_bp):
        self.base_prefix = self._add_root_to_route(prefix_base_of_bp)

    def set_prefix_endpoint(self, endpoint_for_bp_prefix):
        self.prefix_endpoint = endpoint_for_bp_prefix

    def route(self, endpoint_route=None, is_prefix_endpoint: bool = False):
        # cases to handle

        if endpoint_route is not None:
            endpoint_route = self._add_prefix_to_route(endpoint_route)

        def wrapped_endpoint(endpoint_function, *args, **kwargs):
            # if a route has been passed, take it along with the function
            # and add it as a Rule to the url_map
            if endpoint_route is not None:
                self._add_rule(endpoint_route, endpoint_function)

            # if a route has been passed, and this is to be the endpoint of bp prefix
            # then it is the route, not the function, that has to added as
            # the endpoint
            if (
                endpoint_route is not None
                and is_prefix_endpoint
                and self.prefix_endpoint is None
            ):
                self.set_prefix_endpoint(endpoint_route)

            # if no route was passed, and this is to be the endpoint of bp prefix
            # then it is the function that has to be added as the endpoint
            if (
                endpoint_route is None
                and is_prefix_endpoint
                and self.prefix_endpoint is None
            ):
                self.set_prefix_endpoint(endpoint_function)

            # once the endpoint of the bp have been set,
            # add the prefix and its endpoint as a rule
            if is_prefix_endpoint and self.prefix_endpoint is not None:
                self._add_rule(self.base_prefix, self.prefix_endpoint)

        return wrapped_endpoint

    def get_endpoints(self):
        return self.endpoints

    def get_map(self):
        return self.url_map


class wsgi:
    def __init__(self) -> None:
        self.url_map = Map()

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"{endpoint}")(request, **values)
        except HTTPException as thisExept:
            return thisExept

    def app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def run(self, **app_config):
        from werkzeug.serving import run_simple

        run_simple(application=self, **app_config)

    def route(self, route):
        def wrapped_endpoint(func, *args, **kwargs):
            if isinstance(route, list):
                for r in route:
                    self._add_rule(func, r)
            else:
                self._add_rule(func, route)

        return wrapped_endpoint

    def _add_rule(self, endpoint, route):
        endpoint_name = _get_endpoint_name(endpoint)

        if isinstance(endpoint, str):
            self.url_map.add(Rule(route, redirect_to=endpoint_name))
        else:
            self.__setattr__(endpoint_name, endpoint)
            self.url_map.add(Rule(route, endpoint=endpoint_name))

    def register_blueprint(self, blueprint: Blueprint):
        bp_map = blueprint.get_map()
        bp_endpoints = blueprint.get_endpoints()

        for e in bp_endpoints:
            for r in bp_map.iter_rules(endpoint=_get_endpoint_name(e)):
                self._add_rule(e, str(r))

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
