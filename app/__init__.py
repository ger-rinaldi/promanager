import os

from flask import Flask, make_response, render_template, request
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect

from app.models import Usuario


def create_app(with_static=True):
    new_app = Flask(__name__)

    @new_app.route("/")
    def home_page():
        session_key = request.cookies.get("sessionId", False)
        if session_key:
            logged_user = Usuario.get_by_session_id(session_key)

            if logged_user is not None:
                return redirect(f"/usuario/{logged_user.username}/dashboard")

        return make_response(render_template("home.html"))

    import app.routes_auth

    new_app.register_blueprint(app.routes_auth.bp)

    import app.routes_user

    new_app.register_blueprint(app.routes_user.bp)

    import app.routes_project

    new_app.register_blueprint(app.routes_project.bp)

    import app.api

    new_app.register_blueprint(app.api.bp)

    return new_app
