from flask import Blueprint, jsonify, request

from app.authentication import need_authorization, required_login
from app.db import context_db_manager
from app.models import Usuario

user_service = Blueprint(
    name="user_service",
    import_name=__name__,
    url_prefix="/usuario/<string:username>",
)


@user_service.post("/eliminar")
@required_login
@need_authorization
def delete_user(username):
    user_to_delete = Usuario.get_by_username_or_mail(username)

    if user_to_delete is None:
        not_found = jsonify(message="El recurso solicitado no fue encontrado")
        not_found.status = 404
        return not_found

    if not user_to_delete._authenticate(username, request.form.get("contrasena_1", "")):
        access_denied = jsonify(message="No tienes acceso al recurso autorizado")
        access_denied.status = 403
        return access_denied

    user_to_delete.delete()

    success = jsonify(message="Eliminado exitosamente")
    success.status = 200
    return success
