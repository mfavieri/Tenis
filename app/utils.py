import os
from types import SimpleNamespace
from app.models import Usuario


def get_current_user(request):
    username = request.cookies.get('usuario')
    if not username:
        return None

    # Busca na tabela USUARIOS
    user = Usuario.query.filter(
        (Usuario.cd_usr == username) | (Usuario.nm_email == username)
    ).first()
    if user:
        return user

    # Admin definido no config.env (não precisa estar na tabela)
    admin_name = os.getenv('ADMINISTRADOR', '')
    if username == admin_name:
        return SimpleNamespace(cd_usr=admin_name, nm_email=None)

    return None


def is_admin(user):
    if user is None:
        return False
    admin_name = os.getenv('ADMINISTRADOR', '')
    email = getattr(user, 'nm_email', None)
    return user.cd_usr == admin_name or (email and email == admin_name)


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
