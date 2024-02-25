from flask import Blueprint, jsonify, request

from app.authentication import need_authorization, required_login
from app.db import context_db_manager
from app.models import Roles

info_api = Blueprint(
    name="gral_info",
    import_name=__name__,
)


@info_api.get("/proyecto/roles")
def get_proyect_roles():
    return jsonify(Roles.get_proyect_roles())
