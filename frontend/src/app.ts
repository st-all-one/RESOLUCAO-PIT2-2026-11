/** Inicialização progressiva da interface. */

type RadioMetodo = HTMLInputElement;

function configurarConfirmacoes(): void {
  const formularios = document.querySelectorAll<HTMLFormElement>("form[data-confirmar]");
  for (const formulario of formularios) {
    formulario.addEventListener("submit", (evento: SubmitEvent) => {
      const mensagem = formulario.dataset.confirmar ?? "";
      if (mensagem !== "" && !window.confirm(mensagem)) {
        evento.preventDefault();
      }
    });
  }
}

function metodoSelecionado(formulario: HTMLFormElement): string {
  const marcado = formulario.querySelector<RadioMetodo>("input[name='metodo']:checked");
  return marcado?.value ?? "pix";
}

function configurarPagamento(): void {
  const formularios = document.querySelectorAll<HTMLFormElement>("form[data-pagamento]");
  for (const formulario of formularios) {
    const campo = formulario.querySelector<HTMLElement>("[data-campo-cartao]");
    const entrada = formulario.querySelector<HTMLInputElement>("input[name='numero_cartao']");
    if (campo === null || entrada === null) {
      continue;
    }

    const atualizar = (): void => {
      const cartao = metodoSelecionado(formulario) === "cartao";
      campo.hidden = !cartao;
      entrada.required = cartao;
      if (!cartao) {
        entrada.value = "";
      }
    };

    const opcoes = formulario.querySelectorAll<RadioMetodo>("input[name='metodo']");
    for (const opcao of opcoes) {
      opcao.addEventListener("change", atualizar);
    }
    atualizar();
  }
}

function configurarMascaraCartao(): void {
  const entrada = document.querySelector<HTMLInputElement>("#numero_cartao");
  if (entrada === null) {
    return;
  }
  entrada.addEventListener("input", () => {
    const digitos = entrada.value.replace(/\D/g, "").slice(0, 19);
    entrada.value = digitos.replace(/(\d{4})(?=\d)/g, "$1 ");
  });
}

function iniciar(): void {
  document.documentElement.classList.add("js");
  configurarConfirmacoes();
  configurarPagamento();
  configurarMascaraCartao();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciar);
} else {
  iniciar();
}

export {};
