import os

from models import Usuario
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from wsgi_app import make_response, render_template, request, wsgi


def create_app(with_static=True):
    new_app = wsgi()

    if with_static:
        new_app.app = SharedDataMiddleware(
            new_app.app,
            {"/static": os.path.join(os.path.dirname(__file__), "static")},
        )

    @new_app.route(["/", "/home"])
    def home_page():
        session_key = request.cookies.get("sessionId", False)
        if session_key:
            logged_user = Usuario.get_by_session_id(session_key)

            if logged_user is not None:
                return redirect(f"/usuario/{logged_user.username}/dashboard")

        return make_response(render_template("home.html"))

    import routes_auth

    new_app.register_blueprint(routes_auth.bp)

    import routes_user

    new_app.register_blueprint(routes_user.bp)

    import api

    new_app.register_blueprint(api.bp)

    return new_app
