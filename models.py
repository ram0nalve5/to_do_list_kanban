# Importe do objeto para manipulação do banco de dados
from database import db

#importe do módulo para data e hora
from datetime import datetime

class Usuario (db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    telefone = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    administrador = db.Column(db.Boolean, nullable=False, default=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    tarefa = db.relationship("Tarefa", backref="usuario", lazy=True)


class StatusTarefa (db.Model):
    __tablename__ = "status_tarefa"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)

    tarefa = db.relationship("Tarefa",backref="status_tarefa", lazy=True)

class Tarefa (db.Model):
    __tablename__ = "tarefa"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    arquivo = db.Column(db.LargeBinary)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    id_status_tarefa = db.Column(db.Integer, db.ForeignKey("status_tarefa.id"), nullable=False)
    