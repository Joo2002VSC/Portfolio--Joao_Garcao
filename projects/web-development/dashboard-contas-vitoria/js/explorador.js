// Explorador das consultas SQL: pesquisa, código, resultado ordenável e exportação.

import { todasConsultas, consulta } from "./dados.js";
import { tabelaOrdenavel, descarregarCSV } from "./tabelas.js";
import { PAINEIS, SECCOES } from "./paineis.js";

const PALAVRAS = /\b(SELECT|FROM|WHERE|JOIN|LEFT|INNER|ON|AND|OR|NOT|AS|CASE|WHEN|THEN|ELSE|END|GROUP BY|ORDER BY|HAVING|WITH|UNION ALL|UNION|OVER|PARTITION BY|WINDOW|ROWS BETWEEN|PRECEDING|CURRENT ROW|LIMIT|DISTINCT|IN|IS|NULL|LIKE|BETWEEN|CAST|INTEGER|ROUND|SUM|AVG|MAX|MIN|COUNT|LAG|LEAD|RANK|ROW_NUMBER|COALESCE|NULLIF|ABS|SQRT|SUBSTR)\b/g;

/** Avisos de coerência encontrados na auditoria (o projeto SQL não foi alterado) */
const AVISOS = {
  14: "Atenção: apesar do título (30/06/2025), o resultado mistura linhas de 30/06/2025 e de 30/06/2026, e a linha TOTAL soma as duas datas. O dashboard usa a consulta 39, que separa as datas.",
  45: "Nas duas primeiras épocas, a média móvel das mais-valias usa menos de três épocas (janela ROWS BETWEEN 2 PRECEDING).",
  8: "Usa os juros suportados líquidos (vista v_dr); a consulta 27 usa os juros dos financiamentos. Os valores diferem.",
};

const escapar = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

/** Realce simples: comentários, texto entre plicas e palavras-chave */
function realcar(sql) {
  return sql.split("\n").map(l => {
    const i = l.indexOf("--");
    const codigo = i >= 0 ? l.slice(0, i) : l, comentario = i >= 0 ? l.slice(i) : "";
    const partes = codigo.split(/('(?:[^']|'')*')/g).map((p, k) =>
      k % 2 ? `<span class="s">${escapar(p)}</span>` : escapar(p).replace(PALAVRAS, '<span class="k">$1</span>'));
    return partes.join("") + (comentario ? `<span class="c">${escapar(comentario)}</span>` : "");
  }).join("\n");
}

/** Normaliza para pesquisa sem acentos nem maiúsculas */
const normal = s => s.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

export function montarExplorador(raiz, { aoSelecionar }) {
  const lista = raiz.querySelector("[data-lista]");
  const pesquisa = raiz.querySelector("[data-pesquisa]");
  const contador = raiz.querySelector("[data-contador]");
  const detalhe = raiz.querySelector("[data-detalhe]");
  const consultas = todasConsultas();

  function desenharLista() {
    const termo = normal(pesquisa.value.trim());
    const visiveis = consultas.filter(c => !termo || normal(`${c.n} ${c.titulo} ${c.conceitos} ${c.sql}`).includes(termo));
    contador.textContent = `${visiveis.length} de ${consultas.length} consultas`;
    const grupos = new Map();
    visiveis.forEach(c => { if (!grupos.has(c.seccao)) grupos.set(c.seccao, []); grupos.get(c.seccao).push(c); });
    lista.replaceChildren(...[...grupos].map(([seccao, cs]) => {
      const g = document.createElement("li");
      g.innerHTML = `<p class="grupo"></p><ul></ul>`;
      g.querySelector(".grupo").textContent = seccao;
      cs.forEach(c => {
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type = "button"; b.dataset.n = c.n;
        b.innerHTML = `<span class="n">${c.n}</span><span></span>`;
        b.lastChild.textContent = c.titulo;
        b.addEventListener("click", () => aoSelecionar(c.n));
        li.appendChild(b);
        g.querySelector("ul").appendChild(li);
      });
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
    const c = consulta(n);
    raiz.dataset.ativa = n;
    marcarAtiva(n);
    const usos = PAINEIS.filter(p => p.consulta === n);
    detalhe.innerHTML = `
      <header class="det-cabeca">
        <p class="det-seccao"></p>
        <h3 id="det-titulo"><span class="n">Consulta ${n}</span> <span data-t></span></h3>
        ${AVISOS[n] ? `<p class="aviso" role="note"></p>` : ""}
        ${c.conceitos ? `<p class="conceitos"><span class="rot">Conceitos SQL</span> <span data-c></span></p>` : ""}
        <div class="det-acoes">
          <button type="button" class="botao" data-copiar>Copiar SQL</button>
          <button type="button" class="botao" data-csv>Exportar CSV</button>
          ${usos.map(p => `<a class="botao secundario" href="#${p.seccao}/${p.id}">Ver gráfico em ${escapar(SECCOES.find(s => s.id === p.seccao).nome)}</a>`).join("")}
        </div>
      </header>
      <details class="det-sql" open><summary>Código SQL</summary><pre><code></code></pre></details>
      <h4 class="det-res">Resultado <span class="contagem"></span></h4>`;
    detalhe.querySelector(".det-seccao").textContent = c.seccao;
    detalhe.querySelector("[data-t]").textContent = c.titulo;
    if (c.conceitos) detalhe.querySelector("[data-c]").textContent = c.conceitos;
    if (AVISOS[n]) detalhe.querySelector(".aviso").textContent = AVISOS[n];
    detalhe.querySelector("code").innerHTML = realcar(c.sql);
    detalhe.querySelector(".contagem").textContent = `${c.linhas.length} ${c.linhas.length === 1 ? "linha" : "linhas"}`;
    detalhe.appendChild(tabelaOrdenavel(c.colunas, c.linhas, n, { legenda: `Resultado da consulta ${n}` }));

    const copiar = detalhe.querySelector("[data-copiar]");
    copiar.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(c.sql); copiar.textContent = "Copiado ✓"; }
      catch { copiar.textContent = "Não foi possível copiar"; }
      setTimeout(() => (copiar.textContent = "Copiar SQL"), 1800);
    });
    detalhe.querySelector("[data-csv]").addEventListener("click", () =>
      descarregarCSV(`consulta-${String(n).padStart(2, "0")}`, c.colunas, c.linhas));
  }

  let espera;
  pesquisa.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(desenharLista, 120); });
  desenharLista();
  return { mostrar };
}
