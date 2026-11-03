// Camada de dados: carrega os JSON exportados do projeto SQL, valida-os
// e oferece funções de acesso. Não faz cálculos analíticos: esses vêm das consultas SQL.

let BASE = null;
const CONSULTAS = new Map();

class ErroDados extends Error {}

async function lerJSON(caminho) {
  // "no-cache": o browser confirma com o servidor se o ficheiro mudou (evita dados desatualizados)
  const r = await fetch(caminho, { cache: "no-cache" });
  if (!r.ok) throw new ErroDados(`Não foi possível ler ${caminho} (HTTP ${r.status}).`);
  try { return await r.json(); }
  catch { throw new ErroDados(`O ficheiro ${caminho} não contém JSON válido.`); }
}

function validar(base, consultas) {
  const faltam = ["epocas", "entidades", "kpis", "desporto", "receitas"].filter(k => !Array.isArray(base[k]));
  if (faltam.length) throw new ErroDados(`O ficheiro contas.json está incompleto: falta ${faltam.join(", ")}.`);
  if (!Array.isArray(consultas.consultas) || !consultas.consultas.length) throw new ErroDados("O ficheiro consultas.json não contém consultas.");
  for (const c of consultas.consultas) {
    if (!Number.isInteger(c.n) || !Array.isArray(c.colunas) || !Array.isArray(c.linhas)) {
      throw new ErroDados(`Consulta com formato inválido: ${c.titulo ?? c.n}.`);
    }
    if (c.linhas.some(l => l.length !== c.colunas.length)) throw new ErroDados(`Consulta ${c.n}: há linhas com um número de colunas incorreto.`);
  }
}

export async function carregar() {
  const [base, consultas] = await Promise.all([lerJSON("data/contas.json"), lerJSON("data/consultas.json")]);
  validar(base, consultas);
  BASE = base;
  consultas.consultas.forEach(c => CONSULTAS.set(c.n, c));
  return { base, consultas: consultas.consultas, gerado: consultas.gerado };
}

export const base = () => BASE;
export const epocas = () => BASE.epocas;
export const todasConsultas = () => [...CONSULTAS.values()];
export const consulta = n => {
  const c = CONSULTAS.get(n);
  if (!c) throw new ErroDados(`A consulta ${n} não existe em consultas.json.`);
  return c;
};

/** Linhas de uma consulta como objetos { coluna: valor } */
export function linhas(n) {
  const c = consulta(n);
  return c.linhas.map(l => Object.fromEntries(c.colunas.map((col, i) => [col, l[i]])));
}

/** Indicadores base (vista v_kpis) de uma entidade numa época */
export const kpi = (entidade, epoca) => BASE.kpis.find(k => k.entidade === entidade && k.epoca === epoca) ?? null;
export const desporto = epoca => BASE.desporto.find(d => d.epoca === epoca) ?? null;

/** Filtra linhas pelo intervalo de épocas; linhas sem coluna "epoca" passam sempre */
export function noIntervalo(rows, intervalo) {
  const dentro = new Set(intervalo);
  return rows.filter(r => !("epoca" in r) || dentro.has(r.epoca));
}

/* ---------- Pequenas funções numéricas seguras ---------- */
export const numeros = arr => arr.filter(v => typeof v === "number" && Number.isFinite(v));
export const media = arr => { const n = numeros(arr); return n.length ? n.reduce((s, v) => s + v, 0) / n.length : null; };
export const soma = arr => numeros(arr).reduce((s, v) => s + v, 0);
export const dividir = (a, b) => (typeof a === "number" && typeof b === "number" && b !== 0 ? a / b : null);
export const ultimo = arr => (arr.length ? arr[arr.length - 1] : null);
export { ErroDados };
