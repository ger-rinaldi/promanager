from flask import Blueprint

from app.api.gral_info import info_api
from app.api.project import project_service
from app.api.user import user_service

full_api = Blueprint(import_name=__name__, name="full_api", url_prefix="/api")

full_api.register_blueprint(project_service)
full_api.register_blueprint(user_service)
full_api.register_blueprint(info_api)
