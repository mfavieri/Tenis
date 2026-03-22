from flask import Blueprint, render_template, request
from app.models import Assunto, Video

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    categorias = []
    for assunto in Assunto.query.order_by(Assunto.cd_assunto).all():
        videos = (Video.query
                  .filter_by(cd_assunto=assunto.cd_assunto)
                  .filter(Video.dt_aval.isnot(None))
                  .all())
        if videos:
            categorias.append({'assunto': assunto, 'videos': videos})
    return render_template('index.html', categorias=categorias)


@main_bp.route('/categoria/<cd_assunto>')
def categoria(cd_assunto):
    assunto = Assunto.query.get_or_404(cd_assunto)
    videos = (Video.query
              .filter_by(cd_assunto=cd_assunto)
              .filter(Video.dt_aval.isnot(None))
              .all())
    return render_template('categoria.html', assunto=assunto, videos=videos)


@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    videos = []
    if q:
        videos = (Video.query
                  .filter(Video.ds_video.ilike(f'%{q}%'),
                          Video.dt_aval.isnot(None))
                  .all())
    return render_template('search.html', videos=videos, query=q)
