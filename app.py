# Importa o Flask para criar a aplicação da web.
from flask import Flask, request, jsonify

# Importa o objeto de manipulação do banco de dados.
from database import db

# Importa as classes/tabelas de banco de dados.
from models import Usuario, StatusTarefa, Tarefa

# Importa a biblioteca para criptografar senhas.
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# Importa a biblioteca que faz interação com o back-end.
from flask_cors import CORS

# Importa a biblioteca para autenticação de Token da Web (JWT).
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity


# Importa a biblioteca para manipular datas.
from datetime import timedelta

# Importa os módulos para manipular variáveis de ambiente.
from dotenv import load_dotenv
import os

# Cria a aplicação da web.
app = Flask(__name__)

# Define que o frontend possa requisitar recursos do backend.
CORS(app)

# Carrega as variáveis de ambiente (.env).
load_dotenv()

# Configura o banco de dados MySQL.
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configura o Token da Web (JWT).
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

# Inicializa o gerenciador de Tokens da Web (JWT).
jwt = JWTManager(app)

# Vincula o banco de dados à aplicação da web.
db.init_app(app)

# Cria as tabelas de banco de dados, caso não existam.
with app.app_context():

    db.create_all()

    # Insere o administrador caso não exista.
    if not Usuario.query.filter_by(cpf="123.456.789-10").first():

        master = Usuario(       
            nome="Administrador",
            cpf="123.456.789-10",
            email="administrador@email.com",
            senha=generate_password_hash("123456"),
            administrador=True
        )

        db.session.add(master)
        db.session.commit()


# Rota para login de usuário.
@app.route("/api/login", methods=["POST"])
def login():

    # Recebe os dados do frontend.
    dados = request.get_json()
    cpf = dados.get("cpf")
    senha = dados.get("senha")

    # Busca o usuário no banco de dados pelo CPF.
    usuario = Usuario.query.filter_by(cpf=cpf).first()

    # Verifica se o usuário existe e se a senha está correta.
    if not usuario or not check_password_hash(usuario.senha, senha):

        # Login incorreto.
        return jsonify({"erro": "CPF ou senha inválidos..."}), 401

    else:

        # Login correto.
        token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "administrador": usuario.administrador
            }
        )

        return jsonify({"token": token}), 200


# Rota para logout de usuário.
@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():

    return jsonify({"mensagem": "Logout realizado com sucesso!"}), 200


# Rota para cadastrar um novo usuário.
@app.route("/api/usuarios", methods=["POST"])
@jwt_required()
def cadastrar_usuario():

    # Verifica se o usuário é um administrador.
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro": "Acesso negado!"}), 403

    # Recebe os dados do frontend.
    dados = request.get_json()
    nome = dados.get("nome")
    cpf = dados.get("cpf")
    email = dados.get("email")
    senha = dados.get("senha")
    telefone = dados.get("telefone")
    data_nascimento = dados.get("data_nascimento")
    administrador = dados.get("administrador", False)

    # Tenta salvar os dados no banco de dados.
    try:

        # Verifica se o usuário já está cadastrado.
        if Usuario.query.filter((Usuario.cpf == cpf) | (Usuario.email == email)).first():

            return jsonify({"erro": "CPF ou e-mail já cadastrados..."}), 409
        
        else:

            # Cria um novo objeto de usuário.
            novo_usuario = Usuario(
                nome = nome,
                cpf = cpf,
                email = email,
                senha = generate_password_hash(senha),
                telefone = telefone,
                data_nascimento = data_nascimento,
                administrador = administrador
            )

            # Insere o novo no usuário no banco de dados.
            db.session.add(novo_usuario)
            db.session.commit()

            return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201

    except Exception as e:

        # Desfaz as alterações feitas no banco de dados.
        db.session.rollback()

        return jsonify({"erro": "Não foi possível cadastrar o usuário..."}), 500


# Rota para listar os usuários cadastrados.
@app.route("/api/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios():

    # Verifica se o usuário é um administrador.
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro": "Acesso negado!"}), 403

    # Tenta buscar os dados no banco de dados.
    try:

        # Busca todos os usuários cadastrados no banco de dados.
        usuarios = Usuario.query.all()

        resultado = [
            {
                "id": usuario.id,
                "nome": usuario.nome,
                "cpf": usuario.cpf,
                "email": usuario.email,
                "telefone": usuario.telefone,
                "administrador": usuario.administrador
            }
            for usuario in usuarios
        ]

        return jsonify(resultado), 200

    except Exception as e:

        return jsonify({"erro": "Não foi possível listar os usuários cadastrados..."}), 500
    

# Rota para cadastrar um novo status de tarefa.
@app.route("/api/status-tarefa", methods=["POST"])
@jwt_required()
def cadastrar_status_tarefa():

    usuario_logado = get_jwt()

    # Verifica se o usuário é administrador.
    if not usuario_logado["administrador"]:

        return jsonify({
            "erro": "Acesso negado..."
        }), 403

    # Recebe os dados do frontend.
    dados = request.get_json()

    nome = dados.get("nome")

    try:

        # Verifica se já existe.
        if StatusTarefa.query.filter_by(nome=nome).first():

            return jsonify({
                "erro": "Status tarefa já cadastrado..."
            }), 409

        else:

            # Cria novo status.
            novo_status_tarefa = StatusTarefa(
                nome=nome
            )

            db.session.add(novo_status_tarefa)
            db.session.commit()

            return jsonify({
                "mensagem": "Status cadastrado com sucesso!"
            }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "erro": "Não foi possível cadastrar o status..."
        }), 500
    
# Rota para listar status de tarefas.
@app.route("/api/status-tarefa", methods=["GET"])
@jwt_required()
def listar_status_tarefa():

    try:

        status_tarefas = StatusTarefa.query.all()

        resultado = [
            {
                "id": status_tarefa.id,
                "nome": status_tarefa.nome
            }
            for status_tarefa in status_tarefas
        ]

        return jsonify(resultado), 200

    except Exception as e:

        return jsonify({
            "erro": "Não foi possível listar os status..."
        }), 500
    

@app.route("/api/tarefas", methods=["POST"])
@jwt_required()
def cadastrar_tarefa():
    try:
        id_usuario = get_jwt_identity()

        titulo= request.form.get("titulo")
        descricao = request.form.get("descricao")
        id_status_tarefa = request.form.get("id_status_tarefa")
        arquivo = request.files.get("arquivo")

    
        if not StatusTarefa.query.get(id_status_tarefa):
            return jsonify({"erro": "Status de tarefa não encontrado..."}), 404
        
        nova_tarefa = Tarefa(titulo=titulo,
                            descricao=descricao,
                            id_usuario=id_usuario,
                            arquivo=arquivo.read() if arquivo else None,
                            id_status_tarefa = request.form.get("id_status_tarefa"))
        db.session.add(nova_tarefa)
        db.session.commit()
        return jsonify({"mensagem":"tarefa cadastrada com sucesso"}), 201
     
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro":"Não foi possível cadastrar a tarefa..."}), 500


@app.route("/api/tarefas", methods=["GET"])
@jwt_required()
def listar_tarefas():
    try:
        tarefas = Tarefa.query.all()
        resultado = [{
            "id" : tarefas.id,
            "titulo" : tarefas.titulo,
            "descricao" : tarefas.descricao,
            "criado_em" : tarefas.criado_em.strftime("%d/%m/%Y %H:%M"),
            "id_usuario" : tarefas.id_usuario,
            "nome_usuario" : tarefas.usuario.nome,
            "id_status_tarefa" : tarefas.id_status_tarefa,
            "nome_status_tarefa" : tarefas.status_tarefa.nome,
            "tem_arquivo" : tarefas.arquivo is not None
        } for tarefa in tarefas]
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro":"Não foi possível buscar as tarefas..."}), 500
    








@app.route("/api/usuarios/<int:id>", methods=["PUT"])
@jwt_required()
def atualizar_usuario(id):
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro":"Acesso negado!"}), 403
    
    dados = request.get_json()
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"erro":"Usuário não encontrado!"}), 404
        
        usuario.nome = dados.get("nome", usuario.nome)
        usuario.telefone = dados.get("telefone", usuario.telefone)
        usuario.data_nascimento = dados.get("data_nascimento", usuario.data_nascimento)
        usuario.administrador = dados.get("administrador", usuario.administrador)
        if dados.get("senha"):
            usuario.senha = generate_password_hash(dados["senha"])
        
        db.session.commit()
        return jsonify({"mensagem":"Usuário atualizado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível atualizar o usuário!"}), 500
    


@app.route("/api/usuario/int<id>", methods=["DELETE"])
@jwt_required()
def excluir_usuario(id):
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro":"Acesso negado!"}), 403
    
    try:
        usuario = Usuario.query.get(id)
        db.session.remove(usuario)
        db.session.commit()
        return jsonify({"mensagem":"Usuário excluído com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro":"Não foi possível excluir o usuário!"}), 500


@app.route("/api/status-tarefa/<int:id>", methods=["PUT"])
@jwt_required()
def atualizar_status_tarefa(id):
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro":"Acesso negado!"}), 403
    
    dados = request.get_json()
    try:
        status_tarefa = StatusTarefa.query.get(id)
        if not status_tarefa:
            return jsonify({"erro":"Status de tarefa não encontrado!"}), 404
        
        status_tarefa.nome = dados.get("nome", status_tarefa.nome) 
        db.session.commit()
        return jsonify({"mensagem":"Usuário atualizado com sucesso"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível atualizar o usuário!"}), 500

@app.route("/api/status-tarefa/int<id>", methods=["DELETE"])
@jwt_required()
def excluir_status_tarefa(id):
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro":"Acesso negado!"}), 403
    
    try:
        status_tarefa = StatusTarefa.query.get(id)
        db.session.remove(status_tarefa)
        db.session.commit()
        return jsonify({"mensagem":"Status de tarefa excluído com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro":"Não foi possível excluir o usuário!"}), 500


@app.route("/api/tarefa/<int:id>", methods=["PUT"])
@jwt_required()
def atualizar_tarefa(id):
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro":"Acesso negado!"}), 403
    
    dados = request.get_json()
    try:
        tarefa = Tarefa.query.get(id)
        if not tarefa:
            return jsonify({"erro":"Tarefa não encontrada!"}), 404
        
        tarefa.titulo = dados.get("titulo", tarefa.titulo)
        tarefa.descricao = dados.get("descricao", tarefa.descricao)
        tarefa.arquivo = dados.get("arquivo", tarefa.arquivo)
        db.session.commit()
        return jsonify({"mensagem":"Tarefa atualizada com sucesso"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Não foi possível atualizar a tarefa!"}), 500

@app.route("/api/status_tarefa/int:<id>", methods=["DELETE"])
@jwt_required()
def excluir_tarefa(id):
    claims = get_jwt()
    if not claims["administrador"]:
        return jsonify({"erro":"Acesso negado!"}), 403
    
    try:
        tarefa = Tarefa.query.get(id)
        db.session.remove(tarefa)
        db.session.commit()
        return jsonify({"mensagem":"Tarefa excluída com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro":"Não foi possível excluir a tarefa!"}), 500





# Executa a aplicação da web com depuração ativa.
if __name__ == "__main__":

    app.run(debug=True)