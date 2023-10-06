"""Modulo de funcionalidades generales de webapp WSGI y Jinja Engine.
    Funciones de creación de cookies y validación de sesión, 
    Generación de motor y renderizado de templates Jinja,
    Creación de Blueprints de rutas
    y apliación WSGI encargada de manejar solicitudes y respuestas.
"""

import datetime
import functools
import os
import secrets
import types
from contextvars import ContextVar

from config import DOMAIN
from jinja2 import Environment, FileSystemLoader, Template
from models import Usuario
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.local import LocalProxy
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response

"""
Variables de contexto de ejecución de aplicación y
sus Proxies locales para facilitar su acceso a través
del tiempo de vida de las instancias de aplicación.

_request_ctx_var: definicion de variable de contexto de request (solicitud)
request: LocalProxy de _request_ctx_var

_session_ctx_var: definicion de variable de contexto para diccionario de sesión de usuaro
session: LocalProxy de diccionario de sesión

"""

_request_ctx_var: ContextVar[str] = ContextVar("request")
request: Request = LocalProxy(_request_ctx_var)


_session_ctx_var: ContextVar[dict] = ContextVar("user_session", default={})
session: dict = LocalProxy(_session_ctx_var)


def set_session_values(new_session_values: iter) -> None:
    """
    Esta función establece los valores de la sesión con los datos proporcionados en `new_session_values`.

    Args:
        new_session_values (iter): Iterable que contiene los nuevos valores de sesión en pares clave-valor.

    Raises:
        TypeError: Si `new_session_values` no es un objeto iterable.

    Returns:
        None: Esta función no devuelve ningún valor.
    """
    if not hasattr(new_session_values, "__iter__"):
        raise TypeError("_set_session_values solo acepta objetos iterables")

    for k, v in new_session_values:
        session[k] = v


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

    """Clase que permite crear un objeto Map con sus respectivas Rule
    todas bajo un prefijo determinado (/auth, /user, etc). Permitiendo
    luego ser registradas en una aplicación con lazy loading.
    """

    def __init__(self, base_prefix: str, prefix_endpoint: str = None) -> None:
        """Instanciación de objeto Blueprint.

        Args:
            base_prefix (str): prefijo de las rutas de blueprint
            prefix_endpoint (str): nombre del endpoint correspondiente a la base de la blueprint
        """

        # Map que contendrá las Rule de la Blueprint instanciada
        self.url_map = Map()

        # Prefijo base de la BP, como /auth, /user
        self.base_prefix = self._add_root_to_route(base_prefix)

        # Si se ha definido un endpoint para el prefijo de la BP
        # agregarle el prefijo, caso contrario, dejarlo en None
        if prefix_endpoint is None:
            self.prefix_endpoint = prefix_endpoint
        else:
            self.prefix_endpoint = self._add_prefix_to_route(prefix_endpoint)

        # Si se ha definido un endpoint para el prefijo
        # cargar la Rule al Map
        if self.base_prefix is not None and self.prefix_endpoint is not None:
            self._add_rule(self.base_prefix, self.prefix_endpoint)

        # Lista que permitira a la wsgi_app obtener los endpoints
        # para luego consultar a url_map las rutas correspondientes
        self.endpoints = []

    def _add_root_to_route(self, route: str) -> str:
        """Agregar slash inicial a las rutas recibidas,
        en caso que no lo tengan.

        Args:
            route (str): nombre de ruta

        Returns:
            str: nombre de ruta precedido de un '/' slash
        """

        if not route[0] == "/":
            return f"/{route}"

        return route

    def _add_prefix_to_route(self, route: str) -> str:
        """Agregar prefijo (base) de la BP a las rutas recibidas
        y slash previo a nombre de la ruta, en caso que no lo tuviesen.

        Returns:
            str: nombre de ruta precedido del prefijo de BP
        """

        route = self._add_root_to_route(route)

        if not route.startswith(self.base_prefix):
            return f"{self.base_prefix}{route}"

        return route

    def _add_rule(self, route: str, endpoint: str | types.FunctionType) -> None:
        """Agregar regla (Rule) a url_map (Map).

        Args:
            route (str): direccion, url, nombre de la ruta.
            endpoint (str | types.FunctionType): endpoint o nombre de enpoint a unir con la ruta.
        """
        endpoint_name = _get_endpoint_name(endpoint)

        self.url_map.add(Rule(route, endpoint=endpoint_name))
        self.endpoints.append(endpoint)

    def set_base_prefix(self, prefix_base_of_bp: str) -> None:
        """Establecer prefijo de BP de manera lazy.

        Args:
            prefix_base_of_bp (str): nombre del prefijo.
        """

        self.base_prefix = self._add_root_to_route(prefix_base_of_bp)

    def set_prefix_endpoint(self, endpoint_for_bp_prefix: str) -> None:
        """Establecer endpoint para el prefijo de BP de manera lazy.

        Args:
            endpoint_for_bp_prefix (str): endpoint del prefijo.
        """

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

    def get_endpoints(self) -> list[str | types.FunctionType]:
        """Retornar lista compuesta de enpoints (referencias a las funciones),
        o nombres de endpoints.

        Returns:
            list[str | types.FunctionType]: endpoints de la blueprint.
        """

        return self.endpoints

    def get_map(self) -> Map:
        """Retornar objeto Map compuesto de las Rule de la Blueprint.

        Returns:
            Map: objeto Map con Rules de BP.
        """

        return self.url_map


class wsgi:
    """
    Controlador de aplicación WSGI para el manejo de solicitudes y respuestas.

    Esta clase gestiona el procesamiento de solicitudes y respuestas para una
    aplicación web implementada utilizando Werkzeug.

    Atributos:
        url_map (werkzeug.routing.Map): Mapa de enrutamiento de URL.

    Métodos:
        __init__: Instancia un objeto de la aplicación WSGI.
        dispatch_request: Despacha la solicitud al endpoint apropiado.
        app: Función de aplicación WSGI.
        run: Ejecuta la aplicación WSGI utilizando el servidor de desarrollo de Werkzeug.
        route: Decorador para agregar rutas a los endpoints.
        _add_rule: Agrega una regla de ruta para un endpoint.
        register_blueprint: Registra un "blueprint" con la aplicación.
    """

    def __init__(self) -> None:
        """
        Inicializa la aplicación WSGI.

        Inicializa la aplicación WSGI creando un mapa de enrutamiento de URL.

        Args:
            None

        Returns:
            None
        """

        self.url_map = Map()
        self._request_ctx_var = _request_ctx_var
        self.request = request

    def dispatch_request(self) -> Response | Exception:
        """
        Despacha la solicitud al endpoint apropiado.

        Este método coincide la URL de la solicitud con un endpoint y llama
        a la función de endpoint correspondiente.

        Args:
            request (Request): El objeto de solicitud.

        Returns:
            Response: El objeto de respuesta.
        """

        adapter = self.url_map.bind_to_environ(self.request.environ)

        try:
            endpoint, values = adapter.match()
            return getattr(self, f"{endpoint}")(**values)

        except HTTPException as thisExept:
            return thisExept

    def app(self, environ, start_response) -> Response:
        """
        Función de aplicación WSGI.

        Este método procesa la aplicación WSGI utilizando la solicitud despachada.

        Args:
            environ (dict): El entorno WSGI.
            start_response : La función de inicio de respuesta.

        Returns:
            Response: Respuesta generada por el endpoint llamado.
        """

        request = Request(environ)
        self._request_ctx_var.set(request)

        if request.cookies:
            session_id = request.cookies.get("sessionId", None)

            if session_id is not None and not session:
                session_user = Usuario.get_user_by_session_id(session_id)

                if session_user is not None:
                    set_session_values(session_user)

        elif session:
            session.clear()

        response = self.dispatch_request()

        return response(environ, start_response)

    def run(self, **app_config) -> None:
        """
        Ejecuta la aplicación WSGI utilizando el servidor de desarrollo de Werkzeug.

        Este método inicia el servidor de desarrollo y ejecuta la aplicación WSGI.

        Args:
            **app_config: Opciones de configuración adicionales para el servidor.

        Returns:
            None
        """

        from werkzeug.serving import run_simple

        run_simple(application=self, **app_config)

    def route(self, route: str | list) -> types.FunctionType:
        """
        Decorador para agregar rutas a los endpoints.

        Este método es un decorador que agrega rutas a las funciones de endpoint.

        Args:
            route (str or list): La(s) ruta(s) para agregar.

        Returns:
            Function: La función del decorador.
        """

        def wrapped_endpoint(func, *args, **kwargs):
            if isinstance(route, list):
                for r in route:
                    self._add_rule(func, r)
            else:
                self._add_rule(func, route)

        return wrapped_endpoint

    def _add_rule(self, endpoint: str | types.FunctionType, route: str) -> None:
        """
        Agrega una regla de ruta para un punto final.

        Este método agrega una regla de ruta para un punto final al mapa de
        enrutamiento de URL.

        Args:
            endpoint (str | Function): El nombre del punto final o la función.
            route (str): La ruta para agregar.

        Returns:
            None
        """

        endpoint_name = _get_endpoint_name(endpoint)

        if isinstance(endpoint, str):
            self.url_map.add(Rule(route, redirect_to=endpoint_name))
        else:
            self.__setattr__(endpoint_name, endpoint)
            self.url_map.add(Rule(route, endpoint=endpoint_name))

    def register_blueprint(self, blueprint: Blueprint):
        """
        Registra un "blueprint" con la aplicación.

        Este método registra un "blueprint" con la aplicación agregando sus
        endpoints y rutas al mapa de enrutamiento de URL.

        Args:
            blueprint (Blueprint): El "blueprint" para registrar.

        Returns:
            None
        """

        bp_map = blueprint.get_map()
        bp_endpoints = blueprint.get_endpoints()

        for e in bp_endpoints:
            for r in bp_map.iter_rules(endpoint=_get_endpoint_name(e)):
                self._add_rule(e, str(r))

    def __call__(self, environ: dict, start_response) -> Response:
        """
        Función invocable de la aplicación WSGI.

        Este método es una función invocable que procesa la aplicación WSGI
        utilizando la solicitud despachada.

        Args:
            environ (dict): El entorno WSGI.
            start_response (): La función de inicio de respuesta.

        Returns:
            Response: Respuesta generada por la aplicación.
        """

        return self.app(environ, start_response)
