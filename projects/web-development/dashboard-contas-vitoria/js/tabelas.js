// Tabelas ordenáveis e exportação para CSV, partilhadas pelos painéis e pelo explorador SQL.

import { coluna, formatar, vazio } from "./formato.js";

/**
 * Cria uma tabela acessível, ordenável por clique (ou Enter) no cabeçalho.
 * @param {string[]} colunas nomes das colunas SQL
 * @param {Array[]} linhas valores em bruto
 * @param {number} consulta número da consulta (para os metadados das colunas)
 */
export function tabelaOrdenavel(colunas, linhas, consulta, { legenda } = {}) {
  const meta = colunas.map((c, i) => coluna(c, consulta, linhas.find(l => !vazio(l[i]))?.[i]));
  const envolvente = document.createElement("div");
  envolvente.className = "tabela";
  envolvente.tabIndex = 0; // permite deslocar a tabela com o teclado
  const t = document.createElement("table");
  if (legenda) { const cap = t.createCaption(); cap.textContent = legenda; cap.className = "sr-only"; }

  const cab = t.createTHead().insertRow();
  const corpo = t.createTBody();
  let ordem = { i: -1, asc: true };

  function preencher() {
    const dados = [...linhas];
    if (ordem.i >= 0) {
      const i = ordem.i;
      dados.sort((a, b) => {
        const x = a[i], y = b[i];
        if (vazio(x)) return 1;
        if (vazio(y)) return -1;
        const r = typeof x === "number" && typeof y === "number" ? x - y : String(x).localeCompare(String(y), "pt");
        return ordem.asc ? r : -r;
      });
    }
    corpo.replaceChildren(...dados.map(l => {
      const tr = document.createElement("tr");
      l.forEach((v, i) => {
        const td = document.createElement("td");
        td.textContent = formatar(meta[i].unidade, v);
        if (meta[i].unidade !== "txt") td.className = "num";
        if (typeof v === "number" && v < 0 && meta[i].unidade === "eur") td.classList.add("negativo");
        tr.appendChild(td);
      });
      return tr;
    }));
  }

  colunas.forEach((c, i) => {
    const th = document.createElement("th");
    th.scope = "col";
    if (meta[i].unidade !== "txt") th.className = "num";
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = meta[i].rotulo;
    b.title = `Ordenar por ${meta[i].rotulo.toLowerCase()} (${c})`;
    b.addEventListener("click", () => {
      ordem = { i, asc: ordem.i === i ? !ordem.asc : meta[i].unidade === "txt" };
      cab.querySelectorAll("th").forEach(x => x.removeAttribute("aria-sort"));
      th.setAttribute("aria-sort", ordem.asc ? "ascending" : "descending");
      preencher();
    });
    th.appendChild(b);
    cab.appendChild(th);
  });
  preencher();
  envolvente.appendChild(t);
  return envolvente;
}

/** CSV para Excel em português: separador ";", vírgula decimal e BOM UTF-8 */
export function descarregarCSV(nome, colunas, linhas) {
  const campo = v => {
    if (vazio(v)) return "";
    const s = typeof v === "number" ? String(v).replace(".", ",") : String(v);
    return /[";\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const texto = [colunas, ...linhas].map(l => l.map(campo).join(";")).join("\r\n");
  const url = URL.createObjectURL(new Blob(["﻿" + texto], { type: "text/csv;charset=utf-8" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: `${nome}.csv` });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
