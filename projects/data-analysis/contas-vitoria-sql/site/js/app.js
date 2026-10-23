// As contas do Vitória SC · separadores, diagrama e consola SQL.
// Usa as constantes de js/dados.js e a biblioteca sql.js (js/vendor/).
/* ---------- Separadores ---------- */
const abas = [...document.querySelectorAll("nav.abas a")];
const paginas = [...document.querySelectorAll(".pagina")];
function mostrar() {
  const hash = decodeURIComponent(location.hash.slice(1)) || "projeto";
  const [pid] = hash.split(":");
  const existe = paginas.some(p => p.dataset.pagina === pid);
  const atual = existe ? pid : "projeto";
  paginas.forEach(p => p.classList.toggle("ativa", p.dataset.pagina === atual));
  abas.forEach(a => a.classList.toggle("ativa", a.dataset.aba === atual));
  const alvo = hash.includes(":") ? document.getElementById(hash) : null;
  if (alvo) alvo.scrollIntoView(); else window.scrollTo(0, 0);
  if (atual === "sql") iniciarSQL();
  if (atual === "projeto") desenharMermaid();
}
window.addEventListener("hashchange", mostrar);

/* ---------- Diagrama ---------- */
let mermaidFeito = false;
function desenharMermaid() {
  if (!CARREGAR_MERMAID || mermaidFeito || !document.querySelector("pre.mermaid")) return;
  mermaidFeito = true;
  import("https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs")
    .then(m => { m.default.initialize({ startOnLoad: false, theme: "neutral" }); m.default.run(); })
    .catch(() => {});
}

/* ---------- Consola SQL ---------- */
const lista = document.getElementById("lista");
CONSULTAS.forEach((c, i) => lista.add(new Option(c.titulo, i)));
lista.addEventListener("change", () => {
  if (lista.value === "") return;
  document.getElementById("sql").value = CONSULTAS[lista.value].sql;
  correr();
});

let db = null, iniciado = false, ultimo = null;
function estado(txt, erro = false) {
  const e = document.getElementById("estado");
  e.textContent = txt; e.classList.toggle("erro", erro);
}
function iniciarSQL() {
  if (iniciado) return;
  iniciado = true;
  const wasm = Uint8Array.from(atob(WASM_B64), c => c.charCodeAt(0));
  initSqlJs({ wasmBinary: wasm }).then(SQL => {
    const bytes = Uint8Array.from(atob(DB_B64), c => c.charCodeAt(0));
    db = new SQL.Database(bytes);
    const t = db.exec("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name")[0];
    const caixa = document.getElementById("tabelas");
    t.values.forEach(([n]) => {
      const b = document.createElement("button");
      b.textContent = n;
      b.onclick = () => { document.getElementById("sql").value = `SELECT * FROM ${n} LIMIT 100;`; correr(); };
      caixa.appendChild(b);
    });
    estado("Pronto. " + t.values.length + " tabelas e vistas carregadas.");
    correr();
  }).catch(e => estado("Não foi possível iniciar o SQLite: " + e.message, true));
}
function formatar(v) {
  if (v === null) return "—";
  if (typeof v === "number") {
    return Number.isInteger(v) ? v.toLocaleString("pt-PT") : v.toLocaleString("pt-PT", { maximumFractionDigits: 2 });
  }
  return String(v);
}
function correr() {
  if (!db) return;
  const sql = document.getElementById("sql").value;
  const caixa = document.getElementById("resultado");
  caixa.innerHTML = "";
  try {
    const t0 = performance.now();
    const res = db.exec(sql);
    const ms = (performance.now() - t0).toFixed(0);
    if (!res.length) { ultimo = null; estado(`Consulta executada em ${ms} ms, sem linhas devolvidas.`); return; }
    const r = res[res.length - 1];
    ultimo = r;
    const tabela = document.createElement("table");
    const cab = tabela.createTHead().insertRow();
    r.columns.forEach(c => { const th = document.createElement("th"); th.textContent = c; cab.appendChild(th); });
    const corpo = tabela.createTBody();
    r.values.forEach(linha => {
      const tr = corpo.insertRow();
      linha.forEach(v => { const td = tr.insertCell(); td.textContent = formatar(v); if (typeof v === "number") td.className = "num"; });
    });
    caixa.appendChild(tabela);
    estado(`${r.values.length} linha(s) em ${ms} ms.`);
  } catch (e) { ultimo = null; estado("Erro: " + e.message, true); }
}
document.getElementById("correr").onclick = correr;
document.getElementById("sql").addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); correr(); }
});
function textoCSV() {
  const esc = v => v === null ? "" : /[",;\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v);
  return [ultimo.columns, ...ultimo.values].map(l => l.map(esc).join(",")).join("\n");
}
document.getElementById("copiar").onclick = () => {
  if (!ultimo) return estado("Corre uma consulta primeiro.", true);
  const tsv = [ultimo.columns, ...ultimo.values].map(l => l.map(v => v === null ? "" : v).join("\t")).join("\n");
  navigator.clipboard.writeText(tsv)
    .then(() => estado("Resultado copiado. Podes colá-lo no Excel."))
    .catch(() => estado("O browser não deixou copiar. Seleciona a tabela e usa Ctrl/⌘ + C.", true));
};
const botaoCSV = document.getElementById("csv");
if (botaoCSV) botaoCSV.onclick = () => {
  if (!ultimo) return estado("Corre uma consulta primeiro.", true);
  const esc = v => v === null ? "" : /[",;\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v);
  const linhas = [ultimo.columns, ...ultimo.values].map(l => l.map(esc).join(","));
  const url = URL.createObjectURL(new Blob(["﻿" + linhas.join("\n")], { type: "text/csv" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: "consulta.csv" });
  a.click(); URL.revokeObjectURL(url);
};

mostrar();
