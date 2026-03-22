from app import db


class Usuario(db.Model):
    __tablename__ = 'USUARIOS'

    cd_usr      = db.Column('cd-usr',      db.String(20),  primary_key=True)
    nm_email    = db.Column('nm-email',    db.String(150), unique=True, nullable=False)
    cd_fone     = db.Column('cd-fone',     db.String(15))
    nm_senha    = db.Column('nm-senha',    db.String(200), nullable=False)  # hash > 20 bytes
    dt_cadastro = db.Column('dt-cadastro', db.String(10))

    videos = db.relationship('Video', backref='usuario', lazy=True)


class Assunto(db.Model):
    __tablename__ = 'ASSUNTO'

    cd_assunto = db.Column('cd-assunto', db.String(8),  primary_key=True)
    ds_assunto = db.Column('ds-assunto', db.String(100), nullable=False)

    videos = db.relationship('Video', backref='assunto', lazy=True)


class Video(db.Model):
    __tablename__ = 'VIDEO'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cd_assunto = db.Column('cd-assunto', db.String(8),    db.ForeignKey('ASSUNTO.cd-assunto'), nullable=False)
    url_video  = db.Column('URL-video',  db.String(50),   unique=True, nullable=False)
    ds_video   = db.Column('ds-video',   db.String(5000))
    dt_upload  = db.Column('dt-upload',  db.String(10))
    dt_aval    = db.Column('dt-aval',    db.String(10))
    cd_usr     = db.Column('cd-usr',     db.String(20),   db.ForeignKey('USUARIOS.cd-usr'))
