/** Inicialização progressiva da interface. */

function iniciar(): void {
  document.documentElement.classList.add("js");
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciar);
} else {
  iniciar();
}

export {};
