import os
from app.models import Usuario


def get_current_user(request):
    username = request.cookies.get('usuario')
    if not username:
        return None
    return Usuario.query.filter(
        (Usuario.cd_usr == username) | (Usuario.nm_email == username)
    ).first()


def is_admin(user):
    admin_name = os.getenv('ADMINISTRADOR', '')
    if user is None:
        # Cookie may hold the admin username directly (not in USUARIOS table)
        return False
    return user.cd_usr == admin_name or user.nm_email == admin_name


def is_admin_from_request(request):
    username = request.cookies.get('usuario')
    if not username:
        return False
    admin_name = os.getenv('ADMINISTRADOR', '')
    if username == admin_name:
        return True
    user = Usuario.query.filter(
        (Usuario.cd_usr == username) | (Usuario.nm_email == username)
    ).first()
    return is_admin(user)
