from datetime import datetime

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)

from app import db
from app.models import Video, Assunto
from app.utils import get_current_user, is_admin

video_bp = Blueprint('video', __name__, url_prefix='/video')


@video_bp.route('/<int:video_id>')
def player(video_id):
    video = Video.query.get_or_404(video_id)
    user  = get_current_user(request)

    if not video.dt_aval and not is_admin(user):
        abort(404)

    return render_template('video/player.html', video=video)


@video_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    user = get_current_user(request)
    if not user:
        flash('Faça login para enviar vídeos.', 'error')
        return redirect(url_for('auth.login'))

    assuntos = Assunto.query.order_by(Assunto.cd_assunto).all()

    if request.method == 'POST':
        url_raw    = request.form.get('url_video', '').strip()
        cd_assunto = request.form.get('cd_assunto', '').strip()
        ds_video   = request.form.get('ds_video',   '').strip()[:5000]

        # Extrai apenas o ID do YouTube se for URL completa
        yt_id = url_raw
        if 'youtube.com/watch' in url_raw:
            yt_id = url_raw.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url_raw:
            yt_id = url_raw.split('youtu.be/')[1].split('?')[0]
        yt_id = yt_id[:50]

        if Video.query.filter_by(url_video=yt_id).first():
            flash('Este vídeo já está cadastrado.', 'error')
        else:
            db.session.add(Video(
                cd_assunto = cd_assunto,
                url_video  = yt_id,
                ds_video   = ds_video,
                dt_upload  = datetime.now().strftime('%d/%m/%Y'),
                cd_usr     = user.cd_usr,
            ))
            db.session.commit()
            flash('Vídeo enviado para avaliação!', 'success')
            return redirect(url_for('main.index'))

    return render_template('video/upload.html', assuntos=assuntos)
