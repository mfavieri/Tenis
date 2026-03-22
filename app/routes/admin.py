from datetime import datetime

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)

from app import db
from app.models import Assunto, Video
from app.utils import is_admin_from_request

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _exige_admin():
    if not is_admin_from_request(request):
        abort(403)


# ── ASSUNTOS ──────────────────────────────────────────────────────────────────

@admin_bp.route('/assuntos', methods=['GET', 'POST'])
def assuntos():
    _exige_admin()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            cd = request.form.get('cd_assunto', '').strip()[:8]
            ds = request.form.get('ds_assunto', '').strip()[:100]
            if not cd or not ds:
                flash('Preencha código e descrição.', 'error')
            elif Assunto.query.get(cd):
                flash('Código já existe.', 'error')
            else:
                db.session.add(Assunto(cd_assunto=cd, ds_assunto=ds))
                db.session.commit()
                flash('Assunto cadastrado!', 'success')

        elif action == 'delete':
            cd = request.form.get('cd_assunto')
            assunto = Assunto.query.get(cd)
            if assunto:
                db.session.delete(assunto)
                db.session.commit()
                flash('Assunto removido.', 'success')

        return redirect(url_for('admin.assuntos'))

    lista = Assunto.query.order_by(Assunto.ds_assunto).all()
    return render_template('admin/assuntos.html', lista=lista)


# ── AVALIAR VÍDEOS ────────────────────────────────────────────────────────────

@admin_bp.route('/avaliar', methods=['GET', 'POST'])
def avaliar():
    _exige_admin()

    if request.method == 'POST':
        vid_id = request.form.get('video_id')
        action = request.form.get('action')
        video  = Video.query.get(vid_id)

        if video:
            if action == 'aprovar':
                video.dt_aval = datetime.now().strftime('%d/%m/%Y')
                db.session.commit()
                flash('Vídeo aprovado!', 'success')
            elif action == 'rejeitar':
                db.session.delete(video)
                db.session.commit()
                flash('Vídeo rejeitado e removido.', 'info')

        return redirect(url_for('admin.avaliar'))

    pendentes = Video.query.filter(Video.dt_aval.is_(None)).all()
    return render_template('admin/avaliar.html', pendentes=pendentes)
