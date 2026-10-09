// Verifica se o usuário está logado ao carregar a página.
if (!localStorage.getItem("token")) {
    window.location.href = "../templates/index.html";
}

// Carrega a lista de usuários ao abrir a página.
listar_usuarios();


// Função para salvar um novo usuário.
async function salvar_usuario() {

    // Captura os dados do formulário.
    const nome = document.getElementById("nome").value;
    const cpf = document.getElementById("cpf").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const telefone = document.getElementById("telefone").value;
    const data_nascimento = document.getElementById("data-nascimento").value;
    const administrador = document.getElementById("administrador").checked;
    const mensagem = document.getElementById("mensagem");

    try {

        // Envia os dados para o backend.
        const resposta = await fetch("http://127.0.0.1:5000/api/usuarios", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({ nome, cpf, email, senha, telefone, data_nascimento, administrador })
        });

        const dados = await resposta.json();

        // Verifica se o cadastro foi bem-sucedido.
        if (resposta.ok) {

            // Exibe a mensagem de sucesso e limpa o formulário.
            mensagem.className = "alert alert-success";
            mensagem.textContent = dados.mensagem;
            cancelar();
            listar_usuarios();

            setTimeout(function () {
                mensagem.className = "";
                mensagem.textContent = "";
            }, 4000);

        } else {

            // Exibe a mensagem de erro retornada pelo backend.
            mensagem.className = "alert alert-danger";
            mensagem.textContent = dados.erro;

            setTimeout(function () {
                mensagem.className = "";
                mensagem.textContent = "";
            }, 4000);

        }

    } catch {

        // Exibe a mensagem de erro caso o backend não esteja disponível.
        mensagem.className = "alert alert-warning";
        mensagem.textContent = "Não foi possível atender sua requisição no momento. Tente mais tarde...";

        setTimeout(function () {
            mensagem.className = "";
            mensagem.textContent = "";
        }, 4000);

    }

}


// Função para listar todos os usuários na tabela.
async function listar_usuarios() {

    try {

        // Envia a requisição para o backend.
        const resposta = await fetch("http://127.0.0.1:5000/api/usuarios", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });

        const dados = await resposta.json();

        // Captura o corpo da tabela.
        const tabela = document.getElementById("tabela-usuarios");
        tabela.innerHTML = "";

        // Preenche a tabela com os usuários retornados pelo backend.
        dados.forEach(function (usuario) {

            tabela.innerHTML += `
                <tr>
                    <td>${usuario.nome}</td>
                    <td>${usuario.cpf}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.telefone || "—"}</td>
                    <td>${usuario.administrador ? "Sim" : "Não"}</td>
                    <td>
                        <button class="btn btn-sm btn-warning">Editar</button>
                        <button class="btn btn-sm btn-danger">Excluir</button>
                    </td>
                </tr>
            `;

        });

    } catch {

        console.error("Não foi possível carregar os usuários...");

    }

}


// Função para cancelar e limpar o formulário.
function cancelar() {

    // Limpa todos os campos do formulário.
    document.getElementById("id-usuario").value = "";
    document.getElementById("nome").value = "";
    document.getElementById("cpf").value = "";
    document.getElementById("email").value = "";
    document.getElementById("senha").value = "";
    document.getElementById("telefone").value = "";
    document.getElementById("data-nascimento").value = "";
    document.getElementById("administrador").checked = false;

}