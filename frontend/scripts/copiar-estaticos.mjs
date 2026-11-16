// Copia o CSS autoral para o diretório estático servido pelo back-end.

import { cp, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const origem = resolve(import.meta.dirname, "../src/estilo.css");
const destino = resolve(
  import.meta.dirname,
  "../../backend/app/static/css/estilo.css",
);

await mkdir(dirname(destino), { recursive: true });
await cp(origem, destino);
