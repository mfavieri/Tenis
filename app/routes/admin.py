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

        elif action == 'edit':
            cd = request.form.get('cd_assunto')
            ds = request.form.get('ds_assunto', '').strip()[:100]
            assunto = Assunto.query.get(cd)
            if assunto and ds:
                assunto.ds_assunto = ds
                db.session.commit()
                flash('Assunto atualizado!', 'success')

        elif action == 'delete':
            cd = request.form.get('cd_assunto')
            assunto = Assunto.query.get(cd)
            if assunto:
                db.session.delete(assunto)
                db.session.commit()
                flash('Assunto removido.', 'success')

        return redirect(url_for('admin.assuntos'))

    lista = Assunto.query.order_by(Assunto.ds_assunto).all()
    editando = request.args.get('edit')
    return render_template('admin/assuntos.html', lista=lista, editando=editando)


# ── VÍDEOS (CRUD) ─────────────────────────────────────────────────────────────

@admin_bp.route('/videos', methods=['GET', 'POST'])
def videos():
    _exige_admin()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'edit':
            vid_id     = request.form.get('video_id')
            cd_assunto = request.form.get('cd_assunto', '').strip()
            ds_video   = request.form.get('ds_video',   '').strip()[:5000]
            video = Video.query.get(vid_id)
            if video:
                video.cd_assunto = cd_assunto
                video.ds_video   = ds_video
                db.session.commit()
                flash('Vídeo atualizado!', 'success')

        elif action == 'delete':
            vid_id = request.form.get('video_id')
            video  = Video.query.get(vid_id)
            if video:
                db.session.delete(video)
                db.session.commit()
                flash('Vídeo removido.', 'success')

        return redirect(url_for('admin.videos'))

    todos    = Video.query.order_by(Video.dt_upload.desc()).all()
    assuntos = Assunto.query.order_by(Assunto.ds_assunto).all()
    editando = request.args.get('edit', type=int)
    return render_template('admin/videos.html', videos=todos,
                           assuntos=assuntos, editando=editando)


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
