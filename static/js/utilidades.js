// Captura o campo de CPF.
const campoCPF = document.getElementById("cpf");

// Aplica a máscara apenas se o campo existir na página atual.
if (campoCPF) {

    // Aplica a máscara de CPF ao campo de entrada.
    campoCPF.addEventListener("input", function () {

        // Remove tudo que não for número.
        let valor = this.value.replace(/\D/g, "");

        // Aplica a máscara no padrão do CPF (000.000.000-00).
        if (valor.length <= 3) {
            this.value = valor;
        } else if (valor.length <= 6) {
            this.value = `${valor.slice(0, 3)}.${valor.slice(3)}`;
        } else if (valor.length <= 9) {
            this.value = `${valor.slice(0, 3)}.${valor.slice(3, 6)}.${valor.slice(6)}`;
        } else {
            this.value = `${valor.slice(0, 3)}.${valor.slice(3, 6)}.${valor.slice(6, 9)}-${valor.slice(9, 11)}`;
        }

    });

}