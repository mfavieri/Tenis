import os
import random
import string
from datetime import datetime

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, make_response, session)
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, mail
from app.models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _serializer():
    return URLSafeTimedSerializer(os.getenv('SECRET_KEY', 'dev-secret'))


# ── LOGIN ────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha   = request.form.get('senha', '')
        lembrar = request.form.get('lembrar') == 'on'

        autenticado = False

        # 1. Busca na tabela USUARIOS
        user = Usuario.query.filter(
            (Usuario.cd_usr == usuario) | (Usuario.nm_email == usuario)
        ).first()
        if user and check_password_hash(user.nm_senha, senha):
            autenticado = True

        # 2. Verifica credenciais do ADMINISTRADOR no config.env
        if not autenticado:
            adm  = os.getenv('ADMINISTRADOR', '')
            sadm = os.getenv('SENHA-ADM', '')
            if usuario == adm and senha == sadm:
                autenticado = True

        if autenticado:
            max_age = 120 * 24 * 3600 if lembrar else None
            resp = make_response(redirect(url_for('main.index')))
            resp.set_cookie('usuario', usuario, max_age=max_age,
                            httponly=True, samesite='Lax')
            return resp

        flash('Usuário ou senha inválidos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('main.index')))
    resp.delete_cookie('usuario')
    return resp


# ── CADASTRO ─────────────────────────────────────────────────────────────────

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'enviar_codigo':
            cd_usr   = request.form.get('cd_usr',   '').strip()[:20]
            nm_email = request.form.get('nm_email', '').strip()[:150]
            cd_fone  = request.form.get('cd_fone',  '').strip()[:15]
            nm_senha = request.form.get('nm_senha',  '')
            nm_conf  = request.form.get('nm_conf',   '')

            if nm_senha != nm_conf:
                flash('As senhas não coincidem.', 'error')
                return render_template('auth/cadastro.html', step='form')

            if Usuario.query.filter(
                (Usuario.cd_usr == cd_usr) | (Usuario.nm_email == nm_email)
            ).first():
                flash('Usuário ou e-mail já cadastrado.', 'error')
                return render_template('auth/cadastro.html', step='form')

            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            session['reg_code'] = code
            session['reg_data'] = {
                'cd_usr':   cd_usr,
                'nm_email': nm_email,
                'cd_fone':  cd_fone,
                'nm_senha': generate_password_hash(nm_senha),
            }

            try:
                msg = Message('Código de verificação – Shared Tênnis',
                              recipients=[nm_email])
                msg.body = (f'Seu código de verificação é: {code}\n\n'
                            'Este código expira em 2 minutos.')
                mail.send(msg)
            except Exception as e:
                flash(f'Erro ao enviar e-mail: {e}', 'error')
                return render_template('auth/cadastro.html', step='form')

            return render_template('auth/cadastro.html', step='verificar',
                                   email=nm_email)

        elif action == 'verificar_codigo':
            digitado = request.form.get('code', '').strip().upper()
            code     = session.get('reg_code')
            reg_data = session.get('reg_data')

            if not code or not reg_data:
                flash('Sessão expirada. Tente novamente.', 'error')
                return render_template('auth/cadastro.html', step='form')

            if digitado != code:
                flash('Código inválido.', 'error')
                return render_template('auth/cadastro.html', step='verificar',
                                       email=reg_data['nm_email'])

            user = Usuario(
                cd_usr      = reg_data['cd_usr'],
                nm_email    = reg_data['nm_email'],
                cd_fone     = reg_data['cd_fone'],
                nm_senha    = reg_data['nm_senha'],
                dt_cadastro = datetime.now().strftime('%d/%m/%Y'),
            )
            db.session.add(user)
            db.session.commit()
            session.pop('reg_code', None)
            session.pop('reg_data', None)

            flash('Cadastro realizado! Faça o login.', 'success')
            return redirect(url_for('auth.login'))

        elif action == 'reenviar_codigo':
            reg_data = session.get('reg_data')
            if not reg_data:
                return redirect(url_for('auth.cadastro'))

            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            session['reg_code'] = code

            try:
                msg = Message('Novo código de verificação – Shared Tênnis',
                              recipients=[reg_data['nm_email']])
                msg.body = f'Seu novo código é: {code}\n\nExpira em 2 minutos.'
                mail.send(msg)
                flash('Novo código enviado!', 'success')
            except Exception as e:
                flash(f'Erro ao reenviar: {e}', 'error')

            return render_template('auth/cadastro.html', step='verificar',
                                   email=reg_data['nm_email'])

    return render_template('auth/cadastro.html', step='form')


# ── ESQUECI MINHA SENHA ───────────────────────────────────────────────────────

@auth_bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        nm_email = request.form.get('nm_email', '').strip()
        user = Usuario.query.filter_by(nm_email=nm_email).first()

        if user:
            token = _serializer().dumps(nm_email, salt='reset-senha')
            link  = url_for('auth.resetar_senha', token=token, _external=True)
            try:
                msg = Message('Redefinir senha – Shared Tênnis', recipients=[nm_email])
                msg.body = (f'Clique no link para redefinir sua senha:\n\n{link}\n\n'
                            'O link expira em 1 hora.')
                mail.send(msg)
            except Exception as e:
                flash(f'Erro ao enviar e-mail: {e}', 'error')
                return render_template('auth/esqueci_senha.html')

        # Sempre exibe a mesma mensagem por segurança
        flash('Se o e-mail estiver cadastrado, você receberá as instruções.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/esqueci_senha.html')


# ── RESETAR SENHA ─────────────────────────────────────────────────────────────

@auth_bp.route('/resetar-senha/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    try:
        nm_email = _serializer().loads(token, salt='reset-senha', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('Link inválido ou expirado.', 'error')
        return redirect(url_for('auth.login'))

    user = Usuario.query.filter_by(nm_email=nm_email).first()
    if not user:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nm_senha = request.form.get('nm_senha', '')
        nm_conf  = request.form.get('nm_conf',  '')

        if nm_senha != nm_conf:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/resetar_senha.html', token=token)

        user.nm_senha = generate_password_hash(nm_senha)
        db.session.commit()
        flash('Senha redefinida com sucesso! Faça o login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/resetar_senha.html', token=token)
