// Verifica se o usuário está logado ao carregar o painel de gerenciamento.
if (!localStorage.getItem("token")) {

    // Redireciona para o login.
    window.location.href = "index.html";
}


// Função para fazer o logout.
async function fazer_logout() {

    // Recupera o token salvo no navegador da web.
    const token = localStorage.getItem("token");

    // Envia a requisição de logout para o backend.
    await fetch("http://127.0.0.1:5000/api/logout", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    // Remove o token do navegador da web e redireciona para o login.
    localStorage.removeItem("token");
    window.location.href = "index.html";
}