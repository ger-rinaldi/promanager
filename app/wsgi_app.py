import functools
import os

from jinja2 import Environment, FileSystemLoader
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

template_path = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)


def render_template(template_name, **context):
    template = jinja_env.get_template(template_name)
    return Response(template.render(context), mimetype="text/html")


class Blueprint:
    def __init__(self, default: str) -> None:
        self.url_map = Map()
        self.default = default
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

    def add_route(self, route):
        def wrapped_endpoint(func, *args, **kwargs):
            if isinstance(route, list):
                for r in route:
                    self._add_endpoint(func, r)

        return wrapped_endpoint

    def _add_endpoint(self, endpoint, route):
        endpoint_name = endpoint.__name__
        self.__setattr__(endpoint_name, endpoint)
        self.url_map.add(Rule(route, endpoint=endpoint_name))

    def add_blueprint(self, blueprint: Blueprint):
        bp_map = blueprint.get_map()
        bp_endpoints = blueprint.get_endpoints()

        for e in bp_endpoints:
            for r in bp_map.iter_rules(endpoint=e.__name__):
                self._add_endpoint(e, str(r))

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
