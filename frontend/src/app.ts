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

type Formatador = (valor: string) => string;

function somenteDigitos(valor: string, limite: number): string {
  return valor.replace(/\D/g, "").slice(0, limite);
}

function formatarCep(valor: string): string {
  const digitos = somenteDigitos(valor, 8);
  return digitos.replace(/^(\d{5})(\d)/, "$1-$2");
}

function formatarTelefone(valor: string): string {
  const digitos = somenteDigitos(valor, 11);
  if (digitos.length === 0) {
    return "";
  }
  if (digitos.length <= 2) {
    return `(${digitos}`;
  }
  const ddd = `(${digitos.slice(0, 2)}) `;
  const resto = digitos.slice(2);
  if (resto.length <= 4) {
    return `${ddd}${resto}`;
  }
  const corte = resto.length > 8 ? 5 : 4;
  return `${ddd}${resto.slice(0, corte)}-${resto.slice(corte)}`;
}

function formatarPreco(valor: string): string {
  const limpo = valor.replace(/[^\d,.]/g, "");
  if (limpo === "" || limpo === "," || limpo === ".") {
    return "";
  }
  const usaVirgula = limpo.includes(",");
  const semMilhar = usaVirgula ? limpo.replace(/\./g, "") : limpo;
  const separador = usaVirgula ? "," : ".";
  const pontos = semMilhar.split(".").length - 1;
  if (!usaVirgula && pontos > 1) {
    return semMilhar.replace(/\./g, "");
  }
  if (!semMilhar.includes(separador)) {
    return semMilhar;
  }
  const [inteiro = "", ...resto] = semMilhar.split(separador);
  const centavos = resto.join("").replace(/\D/g, "").slice(0, 2);
  return `${inteiro === "" ? "0" : inteiro},${centavos}`;
}

function aplicarMascara(seletor: string, formatar: Formatador): void {
  const entrada = document.querySelector<HTMLInputElement>(seletor);
  if (entrada === null) {
    return;
  }
  const aplicar = (): void => {
    entrada.value = formatar(entrada.value);
  };
  entrada.addEventListener("input", aplicar);
  aplicar();
}

function configurarMascaras(): void {
  aplicarMascara("#cep", formatarCep);
  aplicarMascara("#telefone", formatarTelefone);
  aplicarMascara("#numero_cartao", (valor) =>
    somenteDigitos(valor, 19).replace(/(\d{4})(?=\d)/g, "$1 "),
  );
  aplicarMascara("#uf", (valor) => valor.replace(/[^a-z]/gi, "").slice(0, 2).toUpperCase());
  aplicarMascara("#preco", formatarPreco);
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

  cep.addEventListener("blur", () => {
    void consultar();
  });
}

function configurarMenu(): void {
  const botao = document.querySelector<HTMLButtonElement>(".menu-botao");
  const menu = document.querySelector<HTMLElement>("#menu-principal");
  if (botao === null || menu === null) {
    return;
  }

  const fechar = (devolverFoco = false): void => {
    menu.classList.remove("aberto");
    botao.setAttribute("aria-expanded", "false");
    botao.setAttribute("aria-label", "Abrir menu");
    if (devolverFoco) {
      botao.focus();
    }
  };

  botao.addEventListener("click", () => {
    const abrir = !menu.classList.contains("aberto");
    menu.classList.toggle("aberto", abrir);
    botao.setAttribute("aria-expanded", String(abrir));
    botao.setAttribute("aria-label", abrir ? "Fechar menu" : "Abrir menu");
  });

  document.addEventListener("click", (evento: MouseEvent) => {
    const alvo = evento.target;
    if (
      alvo instanceof Node &&
      !menu.contains(alvo) &&
      !botao.contains(alvo) &&
      menu.classList.contains("aberto")
    ) {
      fechar();
    }
  });

  document.addEventListener("keydown", (evento: KeyboardEvent) => {
    if (evento.key === "Escape" && menu.classList.contains("aberto")) {
      fechar(true);
    }
  });

  menu.addEventListener("click", (evento: MouseEvent) => {
    const alvo = evento.target;
    if (alvo instanceof Element && alvo.closest("a") !== null) {
      fechar();
    }
  });

  const desktop = window.matchMedia("(width >= 48rem)");
  desktop.addEventListener("change", (evento) => {
    if (evento.matches) {
      fechar();
    }
  });
}

function iniciar(): void {
  document.documentElement.classList.add("js");
  configurarMenu();
  configurarConfirmacoes();
  configurarPagamento();
  configurarMascaras();
  configurarCep();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciar);
} else {
  iniciar();
}

export {};
