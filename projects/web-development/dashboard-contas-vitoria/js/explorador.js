// Explorador das consultas SQL: pesquisa, filtro por técnica, código, resultado ordenável,
// exportação e navegação entre consultas.

import { todasConsultas, consulta } from "./dados.js";
import { tabelaOrdenavel, descarregarCSV } from "./tabelas.js";
import { PAINEIS, SECCOES, PERGUNTAS } from "./paineis.js";

/* ---------- Técnicas SQL: detetadas no código, nunca atribuídas à mão ---------- */
// Os comentários são removidos antes da deteção, para não contar técnicas só mencionadas.
export const TECNICAS = [
  { id: "join", nome: "JOIN", re: /\bJOIN\b/i, texto: "Junta linhas de duas tabelas que partilham uma chave (por exemplo, a época e a entidade). LEFT JOIN mantém as linhas da primeira tabela mesmo sem correspondência." },
  { id: "group", nome: "GROUP BY", re: /\bGROUP\s+BY\b/i, texto: "Agrupa linhas com o mesmo valor (por época, por categoria) para lhes aplicar funções de agregação." },
  { id: "agregacao", nome: "Funções de agregação", re: /\b(SUM|AVG|COUNT|MIN|MAX)\s*\(/i, texto: "SUM, AVG, COUNT, MIN e MAX resumem várias linhas num só valor: totais, médias, contagens e extremos." },
  { id: "case", nome: "CASE WHEN", re: /\bCASE\s+WHEN\b/i, texto: "Lógica condicional dentro da consulta: classificar épocas, escolher uma rubrica ou transpor linhas em colunas (pivot)." },
  { id: "cte", nome: "CTE (WITH)", re: /^\s*WITH\b|\)\s*,\s*\w+\s+AS\s*\(/im, texto: "Expressão de tabela comum (Common Table Expression): uma subconsulta com nome, definida no início com WITH, que divide consultas longas em passos legíveis." },
  { id: "recursiva", nome: "CTE recursiva", re: /\bWITH\s+RECURSIVE\b/i, texto: "Uma CTE que se chama a si própria para gerar sequências: lugares de 1.º a 18.º, ou iterações de um cálculo." },
  { id: "janela", nome: "Funções de janela", re: /\bOVER\s*\(|\bOVER\s+\w+/i, texto: "Calculam sobre um conjunto de linhas relacionadas sem as agrupar: totais por época, posições relativas e médias móveis." },
  { id: "laglead", nome: "LAG e LEAD", re: /\b(LAG|LEAD)\s*\(/i, texto: "Leem o valor da linha anterior (LAG) ou seguinte (LEAD) na ordem definida: a base das variações face à época anterior." },
  { id: "ranking", nome: "RANK e ROW_NUMBER", re: /\b(RANK|ROW_NUMBER|DENSE_RANK)\s*\(/i, texto: "Numeram ou ordenam as linhas dentro de cada grupo: a pior época, o máximo histórico." },
  { id: "subconsulta", nome: "Subconsultas", re: /\(\s*SELECT\b/i, texto: "Uma consulta dentro de outra, entre parênteses, para usar um valor calculado como filtro ou coluna." },
  { id: "union", nome: "UNION ALL", re: /\bUNION\s+ALL\b/i, texto: "Junta, umas por baixo das outras, as linhas de várias consultas com as mesmas colunas, por exemplo para passar de formato largo a longo." },
  { id: "nullif", nome: "NULLIF e COALESCE", re: /\b(NULLIF|COALESCE)\s*\(/i, texto: "Tratam valores em falta: NULLIF evita divisões por zero; COALESCE escolhe o primeiro valor não nulo." },
];

const semComentarios = sql => sql.split("\n").map(l => (l.includes("--") ? l.slice(0, l.indexOf("--")) : l)).join("\n");
export const tecnicasDe = c => (c._tecnicas ??= TECNICAS.filter(t => t.re.test(semComentarios(c.sql))).map(t => t.id));

/* ---------- Realce do código (sem dependências) ---------- */

const PALAVRAS = new Set(("SELECT FROM WHERE JOIN LEFT RIGHT INNER OUTER CROSS ON AND OR NOT AS CASE WHEN THEN ELSE END GROUP BY ORDER " +
  "HAVING WITH RECURSIVE UNION ALL OVER PARTITION WINDOW ROWS RANGE BETWEEN PRECEDING FOLLOWING CURRENT ROW UNBOUNDED LIMIT OFFSET " +
  "DISTINCT IN IS NULL LIKE ASC DESC VALUES EXISTS FILTER").split(" "));
const FUNCOES = new Set(("ROUND SUM AVG MAX MIN COUNT LAG LEAD RANK DENSE_RANK ROW_NUMBER NTILE FIRST_VALUE LAST_VALUE COALESCE NULLIF " +
  "ABS SQRT POWER EXP LN SUBSTR REPLACE LENGTH UPPER LOWER CAST PRINTF IIF TOTAL GROUP_CONCAT STRFTIME DATE INTEGER REAL TEXT").split(" "));
const escapar = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const TOKEN = /(--.*$)|('(?:[^']|'')*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z_0-9]*)/g;

/** Devolve HTML com uma linha por <span class="ln">, para a numeração das linhas */
function realcar(sql) {
  return sql.replace(/\s+$/, "").split("\n").map(l => {
    let html = "", ultimo = 0;
    l.replace(TOKEN, (m, com, str, num, pal, pos) => {
      html += escapar(l.slice(ultimo, pos));
      const maiusc = pal?.toUpperCase();
      const cls = com ? "c" : str ? "s" : num ? "n" : PALAVRAS.has(maiusc) ? "k" : FUNCOES.has(maiusc) ? "f" : null;
      html += cls ? `<span class="${cls}">${escapar(m)}</span>` : escapar(m);
      ultimo = pos + m.length;
      return m;
    });
    return `<span class="ln">${html}${escapar(l.slice(ultimo))}</span>`;
  }).join("\n");
}

/** Avisos de coerência encontrados na auditoria (o projeto SQL não foi alterado) */
const AVISOS = {
  8: "Utiliza os juros suportados líquidos (vista v_dr); a consulta 27 utiliza os juros dos financiamentos. Os valores são diferentes.",
  14: "Apesar do título (30/06/2025), o resultado mistura linhas de 30/06/2025 e de 30/06/2026, e a linha TOTAL soma as duas datas. O painel utiliza a consulta 39, que separa as datas.",
  45: "Nas duas primeiras épocas, a média móvel das mais-valias usa menos de três épocas (janela ROWS BETWEEN 2 PRECEDING).",
};

/** Objetivo da consulta: o título e as notas do bloco de comentários inicial (sem a linha «Conceitos», mostrada à parte) */
function objetivo(c) {
  const bloco = [];
  for (const l of c.sql.split("\n")) {
    const t = l.trim();
    if (!t.startsWith("--")) break;
    let txt = t.replace(/^--\s?/, "");
    if (/^Conceitos:/.test(txt)) { const k = txt.indexOf(". "); txt = k >= 0 ? txt.slice(k + 2) : ""; }
    if (txt && !/^@[qd]\b|^[=-]+$/.test(txt)) bloco.push(txt);
  }
  const extra = bloco.join(" ").replace(/\s+/g, " ").trim();
  return extra ? `${c.titulo}. ${extra}` : `${c.titulo}.`;
}

const normal = s => s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

export function montarExplorador(raiz, { aoSelecionar }) {
  const lista = raiz.querySelector("[data-lista]");
  const pesquisa = raiz.querySelector("[data-pesquisa]");
  const contador = raiz.querySelector("[data-contador]");
  const detalhe = raiz.querySelector("[data-detalhe]");
  const seccao = raiz.closest("section") ?? document;
  const filtros = seccao.querySelector("[data-tecnicas]");
  const explicacao = seccao.querySelector("[data-explicacao]");
  const consultas = todasConsultas();
  let tecnica = null;
  let visiveis = consultas;

  // Técnicas usadas, com contagem e explicação
  const usadas = TECNICAS.map(t => ({ ...t, n: consultas.filter(c => tecnicasDe(c).includes(t.id)).length })).filter(t => t.n > 0);
  usadas.forEach(t => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.dataset.id = t.id; b.setAttribute("aria-pressed", "false");
    b.title = t.texto;
    b.innerHTML = `<span></span> <span class="contagem">${t.n}</span>`;
    b.firstChild.textContent = t.nome;
    b.addEventListener("click", () => {
      tecnica = tecnica === t.id ? null : t.id;
      filtros.querySelectorAll(".chip").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.id === tecnica)));
      explicacao.textContent = tecnica ? `${t.nome}: ${t.texto}` : "";
      explicacao.hidden = !tecnica;
      desenharLista();
    });
    filtros.appendChild(b);
  });

  function desenharLista() {
    const termo = normal(pesquisa.value.trim());
    visiveis = consultas.filter(c =>
      (!termo || normal(`${c.codigo} ${c.titulo} ${c.conceitos} ${c.sql}`).includes(termo)) &&
      (!tecnica || tecnicasDe(c).includes(tecnica)));
    contador.textContent = `${visiveis.length} de ${consultas.length} consultas`;
    if (!visiveis.length) {
      const li = document.createElement("li");
      li.className = "sem-resultados";
      li.textContent = `Nenhuma consulta corresponde${termo ? ` a "${pesquisa.value.trim()}"` : ""}${tecnica ? " com esta técnica" : ""}. Experimente outro termo ou limpe os filtros.`;
      lista.replaceChildren(li);
      return;
    }
    const grupos = new Map();
    visiveis.forEach(c => { if (!grupos.has(c.seccao)) grupos.set(c.seccao, []); grupos.get(c.seccao).push(c); });
    const ativa = Number(raiz.dataset.ativa);
    lista.replaceChildren(...[...grupos].map(([seccao, cs]) => {
      const g = document.createElement("li");
      const det = document.createElement("details");
      // Abertos: quando há pesquisa ou filtro, o grupo da consulta ativa e o primeiro
      det.open = Boolean(termo || tecnica) || cs.some(c => c.n === ativa) || seccao === visiveis[0].seccao;
      const titulo = document.createElement("summary");
      titulo.className = "grupo";
      titulo.innerHTML = `<span></span> <span class="contagem">${cs.length}</span>`;
      titulo.firstChild.textContent = seccao;
      const ul = document.createElement("ul");
      cs.forEach(c => {
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type = "button"; b.dataset.n = c.n;
        b.innerHTML = `<span class="n">${escapar(c.codigo)}</span><span></span>`;
        b.lastChild.textContent = c.titulo;
        b.addEventListener("click", () => aoSelecionar(c.n));
        li.appendChild(b);
        ul.appendChild(li);
      });
      det.append(titulo, ul);
      g.appendChild(det);
      return g;
    }));
    marcarAtiva(raiz.dataset.ativa);
  }

  function marcarAtiva(n) {
    lista.querySelectorAll("button[data-n]").forEach(b => {
      const ativa = b.dataset.n === String(n);
      b.classList.toggle("ativa", ativa);
      if (ativa) { b.setAttribute("aria-current", "true"); const d = b.closest("details"); if (d) d.open = true; }
      else b.removeAttribute("aria-current");
    });
  }

  function mostrar(n) {
    let c;
    try { c = consulta(n); } catch { c = consultas[0]; n = c.n; }
    raiz.dataset.ativa = n;
    marcarAtiva(n);
    const ordem = consultas.map(x => x.n), i = ordem.indexOf(n);
    const anterior = consultas[i - 1], seguinte = consultas[i + 1];
    const usos = PAINEIS.filter(p => p.consulta === n);
    const perguntas = PERGUNTAS.filter(p => p.consultas.includes(n));
    const tecs = tecnicasDe(c).map(id => TECNICAS.find(t => t.id === id));

    const nLinhas = c.sql.replace(/\s+$/, "").split("\n").length;
    detalhe.innerHTML = `
      <nav class="det-nav" aria-label="Navegar entre consultas">
        ${anterior ? `<a href="#sql/${anterior.n}">← ${escapar(anterior.codigo)}</a>` : "<span></span>"}
        <span class="det-pos">${i + 1} de ${consultas.length}</span>
        ${seguinte ? `<a href="#sql/${seguinte.n}">${escapar(seguinte.codigo)} →</a>` : "<span></span>"}
      </nav>
      <p class="det-seccao"></p>
      <h3><span class="n">${n > 100 ? "Consulta complementar" : "Consulta"} ${escapar(c.codigo)}</span> <span data-t></span></h3>
      <div class="det-objetivo">
        <p class="rotulo-claro">Objetivo</p>
        <p data-objetivo></p>
        ${c.conceitos ? `<p class="conceitos"><span class="rot">Conceitos (comentário do autor):</span> <span data-c></span></p>` : ""}
        ${tecs.length ? `<ul class="tecnicas-usadas" aria-label="Técnicas SQL detetadas no código">${tecs.map(t => `<li title="${escapar(t.texto)}">${escapar(t.nome)}</li>`).join("")}</ul>` : ""}
        ${AVISOS[n] ? `<p class="aviso" role="note"><strong>Atenção.</strong> <span></span></p>` : ""}
      </div>
      <div class="det-acoes">
        <button type="button" class="botao" data-copiar>Copiar SQL</button>
        <button type="button" class="botao secundario" data-csv>Exportar resultado (CSV)</button>
        ${usos.map(p => `<a class="botao secundario" href="#${p.seccao}/${p.seccao === "perguntas" ? `pergunta-${p.questao}` : p.id}">Ver gráfico em ${escapar(SECCOES.find(s => s.id === p.seccao).nome)}</a>`).join("")}
        ${perguntas.map(p => `<a class="botao secundario" href="#perguntas/pergunta-${p.n}">Pergunta ${p.n}</a>`).join("")}
      </div>
      <details class="det-sql" open>
        <summary>Código SQL <span class="contagem">${nLinhas} linhas</span></summary>
        <pre tabindex="0" aria-label="Código SQL da consulta ${escapar(c.codigo)}"><code></code></pre>
      </details>
      <h4 class="det-res">Resultado <span class="contagem"></span></h4>`;
    detalhe.querySelector(".det-seccao").textContent = c.seccao;
    detalhe.querySelector("[data-t]").textContent = c.titulo;
    if (AVISOS[n]) detalhe.querySelector(".aviso span").textContent = AVISOS[n];
    if (c.conceitos) detalhe.querySelector("[data-c]").textContent = c.conceitos;
    detalhe.querySelector("code").innerHTML = realcar(c.sql);
    // Sem notas no código, o objetivo é a pergunta e a descrição do gráfico que a consulta alimenta
    const obj = objetivo(c), painel = usos.find(p => p.descricao);
    detalhe.querySelector("[data-objetivo]").textContent = obj === `${c.titulo}.` && painel ? `${painel.pergunta} ${painel.descricao}` : obj;
    detalhe.querySelector(".det-res .contagem").textContent = `${c.linhas.length} ${c.linhas.length === 1 ? "linha" : "linhas"} · clique num cabeçalho para ordenar`;
    detalhe.appendChild(tabelaOrdenavel(c.colunas, c.linhas, n, { legenda: `Resultado da consulta ${c.codigo}` }));

    const copiar = detalhe.querySelector("[data-copiar]");
    copiar.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(c.sql); copiar.textContent = "Copiado ✓"; }
      catch { copiar.textContent = "Não foi possível copiar"; }
      setTimeout(() => (copiar.textContent = "Copiar SQL"), 1800);
    });
    detalhe.querySelector("[data-csv]").addEventListener("click", () =>
      descarregarCSV(`consulta-${c.codigo.padStart(2, "0")}`, c.colunas, c.linhas));
  }

  let espera;
  pesquisa.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(desenharLista, 120); });
  raiz.querySelector("[data-limpar]").addEventListener("click", () => {
    pesquisa.value = ""; tecnica = null;
    filtros.querySelectorAll(".chip").forEach(x => x.setAttribute("aria-pressed", "false"));
    explicacao.hidden = true;
    desenharLista(); pesquisa.focus();
  });
  desenharLista();
  return { mostrar };
}
