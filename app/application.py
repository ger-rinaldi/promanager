import os

from db import get_connection
from jinja2 import Environment, FileSystemLoader
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response


def create_app(with_static=True):
    new_app = Promanager()
    if with_static:
        new_app.wsgi_app = SharedDataMiddleware(
            new_app.wsgi_app,
            {"/static": os.path.join(os.path.dirname(__file__), "static")},
        )
    return new_app


class Promanager:
    def __init__(self) -> None:
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_path), autoescape=True
        )
        self.url_map = Map([])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"{endpoint}")(request, **values)
        except HTTPException as thisExept:
            return thisExept

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def render_template(self, template_name, **context):
        template = self.jinja_env.get_template(template_name)
        return Response(template.render(context), mimetype="text/html")

    def run(self, **app_config):
        from werkzeug.serving import run_simple

        run_simple(application=self, **app_config)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
