"""Limites de tentativas em memória, por processo."""

from __future__ import annotations

import threading
import time
from collections import deque


class LimiteTentativas:
    """Janela deslizante de falhas por chave."""

    def __init__(self, maximo: int, janela: float) -> None:
        self._maximo = maximo
        self._janela = janela
        self._falhas: dict[str, deque[float]] = {}
        self._trava = threading.Lock()

    def excedido(self, chave: str, agora: float | None = None) -> bool:
        instante = time.monotonic() if agora is None else agora
        with self._trava:
            fila = self._falhas.get(chave)
            if fila is None:
                return False
            self._podar(fila, instante)
            return len(fila) >= self._maximo

    def registrar(self, chave: str, agora: float | None = None) -> None:
        instante = time.monotonic() if agora is None else agora
        with self._trava:
            fila = self._falhas.setdefault(chave, deque())
            self._podar(fila, instante)
            fila.append(instante)

    def limpar(self, chave: str) -> None:
        with self._trava:
            self._falhas.pop(chave, None)

    def _podar(self, fila: deque[float], agora: float) -> None:
        limite = agora - self._janela
        while fila and fila[0] <= limite:
            fila.popleft()
