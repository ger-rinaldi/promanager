import os

from db import get_connection
from jinja2 import Environment, FileSystemLoader
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response


class Promanager:
    def __init__(self) -> None:
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_path), autoescape=True
        )
        self.url_map = Map([])
