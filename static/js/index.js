// Função para fazer o login.
async function fazer_login() {

    // Captura os dados do formulário.
    const cpf = document.getElementById("cpf").value;
    const senha = document.getElementById("senha").value;
    const mensagem = document.getElementById("mensagem");

    try {

        // Envia os dados para o backend.
        const resposta = await fetch("http://127.0.0.1:5000/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cpf, senha })
        });

        const dados = await resposta.json();

        // Verifica se o login foi bem-sucedido.
        if (resposta.ok) {

            // Salva o token no navegador da web e redireciona para o painel de gerenciamento.
            localStorage.setItem("token", dados.token);
            window.location.href = "../templates/dashboard.html";

        } else {

            // Exibe a mensagem de erro retornada pelo backend.
            mensagem.className = "alert alert-danger";
            mensagem.textContent = dados.erro;

            // Remove a mensagem de erro após 3 segundos.
            setTimeout(function () {
                mensagem.className = "";
                mensagem.textContent = "";
            }, 4000);

        }

    } catch {

        // Exibe a mensagem de erro caso o backend não esteja disponível.
        mensagem.className = "alert alert-warning";
        mensagem.textContent = "Não foi possível atender sua requisição no momento. Tente mais tarde...";

        // Remove a mensagem de erro após 3 segundos.
        setTimeout(function () {
            mensagem.className = "";
            mensagem.textContent = "";
        }, 4000);

    }

}