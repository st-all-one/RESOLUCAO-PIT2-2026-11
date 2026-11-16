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

interface CepResposta {
  logradouro?: string;
  bairro?: string;
  cidade?: string;
  uf?: string;
}

function configurarCep(): void {
  const cep = document.querySelector<HTMLInputElement>("#cep");
  const status = document.querySelector<HTMLElement>("[data-cep-status]");
  if (cep === null || status === null) {
    return;
  }

  const logradouro = document.querySelector<HTMLInputElement>("#logradouro");
  const bairro = document.querySelector<HTMLInputElement>("#bairro");
  const cidade = document.querySelector<HTMLInputElement>("#cidade");
  const uf = document.querySelector<HTMLInputElement>("#uf");
  const numero = document.querySelector<HTMLInputElement>("#numero");

  const consultar = async (): Promise<void> => {
    const digitos = cep.value.replace(/\D/g, "").slice(0, 8);
    cep.value = digitos;
    if (digitos.length !== 8) {
      return;
    }

    status.textContent = "Buscando endereço…";
    try {
      const resposta = await fetch(`/cep/${digitos}`, {
        headers: { Accept: "application/json" },
      });
      if (!resposta.ok) {
        let mensagem = "Não foi possível consultar o CEP. Preencha manualmente.";
        try {
          const problema = (await resposta.json()) as { detail?: string };
          if (typeof problema.detail === "string") {
            mensagem = problema.detail;
          }
        } catch {
          // Mantém a mensagem genérica se o corpo não for JSON.
        }
        status.textContent = mensagem;
        return;
      }
      const dados = (await resposta.json()) as CepResposta;
      if (logradouro !== null) logradouro.value = dados.logradouro ?? "";
      if (bairro !== null) bairro.value = dados.bairro ?? "";
      if (cidade !== null) cidade.value = dados.cidade ?? "";
      if (uf !== null) uf.value = dados.uf ?? "";
      status.textContent = "Endereço encontrado. Confira e informe o número.";
      numero?.focus();
    } catch {
      status.textContent = "Não foi possível consultar o CEP. Preencha manualmente.";
    }
  };

  cep.addEventListener("input", () => {
    cep.value = cep.value.replace(/\D/g, "").slice(0, 8);
  });
  cep.addEventListener("blur", () => {
    void consultar();
  });
}

function iniciar(): void {
  document.documentElement.classList.add("js");
  configurarConfirmacoes();
  configurarPagamento();
  configurarMascaraCartao();
  configurarCep();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciar);
} else {
  iniciar();
}

export {};
