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

/* ---------- Realce do código ---------- */

const PALAVRAS = /\b(SELECT|FROM|WHERE|JOIN|LEFT|INNER|ON|AND|OR|NOT|AS|CASE|WHEN|THEN|ELSE|END|GROUP BY|ORDER BY|HAVING|WITH|RECURSIVE|UNION ALL|UNION|OVER|PARTITION BY|WINDOW|ROWS BETWEEN|PRECEDING|CURRENT ROW|LIMIT|DISTINCT|IN|IS|NULL|LIKE|BETWEEN|CAST|INTEGER|ROUND|SUM|AVG|MAX|MIN|COUNT|LAG|LEAD|RANK|ROW_NUMBER|COALESCE|NULLIF|ABS|SQRT|SUBSTR|VALUES)\b/g;
const escapar = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function realcar(sql) {
  return sql.split("\n").map(l => {
    const i = l.indexOf("--");
    const codigo = i >= 0 ? l.slice(0, i) : l, comentario = i >= 0 ? l.slice(i) : "";
    const partes = codigo.split(/('(?:[^']|'')*')/g).map((p, k) =>
      k % 2 ? `<span class="s">${escapar(p)}</span>` : escapar(p).replace(PALAVRAS, '<span class="k">$1</span>'));
    return partes.join("") + (comentario ? `<span class="c">${escapar(comentario)}</span>` : "");
  }).join("\n");
}

/** Avisos de coerência encontrados na auditoria (o projeto SQL não foi alterado) */
const AVISOS = {
  8: "Utiliza os juros suportados líquidos (vista v_dr); a consulta 27 utiliza os juros dos financiamentos. Os valores são diferentes.",
  10: "Em 2021/22, 2023/24 e 2024/25 o resultado consolidado é igual à soma da SAD e do Clube: os ajustes de consolidação não são visíveis nos dados (ver consulta complementar D6).",
  14: "Apesar do título (30/06/2025), o resultado mistura linhas de 30/06/2025 e de 30/06/2026, e a linha TOTAL soma as duas datas. O painel utiliza a consulta 39, que separa as datas.",
  45: "Nas duas primeiras épocas, a média móvel das mais-valias usa menos de três épocas (janela ROWS BETWEEN 2 PRECEDING).",
};

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
    lista.replaceChildren(...[...grupos].map(([seccao, cs]) => {
      const g = document.createElement("li");
      const titulo = document.createElement("p");
      titulo.className = "grupo"; titulo.textContent = seccao;
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
      g.append(titulo, ul);
      return g;
    }));
    marcarAtiva(raiz.dataset.ativa);
  }

  function marcarAtiva(n) {
    lista.querySelectorAll("button[data-n]").forEach(b => {
      const ativa = b.dataset.n === String(n);
      b.classList.toggle("ativa", ativa);
      if (ativa) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current");
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

    detalhe.innerHTML = `
      <nav class="det-nav" aria-label="Navegar entre consultas">
        ${anterior ? `<a href="#sql/${anterior.n}">← ${escapar(anterior.codigo)}</a>` : "<span></span>"}
        <span class="det-pos">${i + 1} de ${consultas.length}</span>
        ${seguinte ? `<a href="#sql/${seguinte.n}">${escapar(seguinte.codigo)} →</a>` : "<span></span>"}
      </nav>
      <p class="det-seccao"></p>
      <h3><span class="n">${n > 100 ? "Consulta complementar" : "Consulta"} ${escapar(c.codigo)}</span> <span data-t></span></h3>
      ${AVISOS[n] ? `<p class="aviso" role="note"><strong>Atenção.</strong> <span></span></p>` : ""}
      ${c.conceitos ? `<p class="conceitos"><span class="rot">Conceitos (comentário do autor):</span> <span data-c></span></p>` : ""}
      ${tecs.length ? `<ul class="tecnicas-usadas" aria-label="Técnicas SQL detetadas no código">${tecs.map(t => `<li title="${escapar(t.texto)}">${escapar(t.nome)}</li>`).join("")}</ul>` : ""}
      <div class="det-acoes">
        <button type="button" class="botao" data-copiar>Copiar SQL</button>
        <button type="button" class="botao" data-csv>Exportar resultado (CSV)</button>
        ${usos.map(p => `<a class="botao secundario" href="#${p.seccao}/${p.seccao === "perguntas" ? `pergunta-${p.questao}` : p.id}">Ver gráfico em ${escapar(SECCOES.find(s => s.id === p.seccao).nome)}</a>`).join("")}
        ${perguntas.map(p => `<a class="botao secundario" href="#perguntas/pergunta-${p.n}">Pergunta ${p.n}</a>`).join("")}
      </div>
      <details class="det-sql" open><summary>Código SQL</summary><pre tabindex="0"><code></code></pre></details>
      <h4 class="det-res">Resultado <span class="contagem"></span></h4>`;
    detalhe.querySelector(".det-seccao").textContent = c.seccao;
    detalhe.querySelector("[data-t]").textContent = c.titulo;
    if (AVISOS[n]) detalhe.querySelector(".aviso span").textContent = AVISOS[n];
    if (c.conceitos) detalhe.querySelector("[data-c]").textContent = c.conceitos;
    detalhe.querySelector("code").innerHTML = realcar(c.sql);
    detalhe.querySelector(".contagem").textContent = `${c.linhas.length} ${c.linhas.length === 1 ? "linha" : "linhas"} · clique num cabeçalho para ordenar`;
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
