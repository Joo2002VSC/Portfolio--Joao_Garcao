// Dashboard Vitória SC · aplicação
// Estado dos filtros, navegação, visão geral (quatro dimensões), secções e painéis.

import * as Dados from "./dados.js";
import { formatar, variacaoEuros, inteiro, pct, euros } from "./formato.js";
import { aplicarTema, desenhar, definirDestaque } from "./graficos.js";
import { SECCOES, PAINEIS, PERGUNTAS, ORDEM, GRUPOS, SOLUCOES } from "./paineis.js";
import { tabelaOrdenavel } from "./tabelas.js";
import { montarExplorador } from "./explorador.js";
import { conclusoes, SENTIDO, EPOCA_REEXPRESSA } from "./conclusoes.js";
import { contar, observar, reduzido } from "./animacoes.js";

/* ====================== Estado ====================== */

// O painel apresenta apenas as contas da Vitória Sport Clube – Futebol, SAD.
const estado = { seccao: null, inicio: null, fim: null, epoca: null };
let PADRAO = null;
const figuras = new Map();
let versaoTema = 0;
const valoresKPI = {};
let explorador = null;

const $ = (s, el = document) => el.querySelector(s);
const criar = (tag, cls, texto) => { const e = document.createElement(tag); if (cls) e.className = cls; if (texto !== undefined) e.textContent = texto; return e; };
const codigoConsulta = n => { try { return Dados.consulta(n).codigo ?? String(n); } catch { return String(n); } };
const ligacaoConsulta = n => `<a href="#sql/${n}">${n > 100 ? "consulta complementar" : "consulta"} ${codigoConsulta(n)}</a>`;

function epocasVisiveis() {
  const e = Dados.epocas(), i = e.indexOf(estado.inicio), f = e.indexOf(estado.fim);
  return e.slice(Math.min(i, f), Math.max(i, f) + 1);
}

/* ---------- Estado no endereço (permite partilhar uma vista filtrada) ---------- */

const PARAMS = { inicio: "de", fim: "ate", epoca: "epoca" };

function lerURL() {
  const p = new URLSearchParams(location.search), e = Dados.epocas();
  const valida = v => (e.includes(v) ? v : null);
  estado.inicio = valida(p.get("de")) ?? PADRAO.inicio;
  estado.fim = valida(p.get("ate")) ?? PADRAO.fim;
  estado.epoca = valida(p.get("epoca")) ?? PADRAO.epoca;
  // Endereços com combinações inválidas são corrigidos: período invertido e destaque fora do período
  if (e.indexOf(estado.inicio) > e.indexOf(estado.fim)) [estado.inicio, estado.fim] = [estado.fim, estado.inicio];
  ajustarDestaque();
}

function escreverURL() {
  const p = new URLSearchParams();
  Object.entries(PARAMS).forEach(([k, nome]) => { if (estado[k] !== PADRAO[k]) p.set(nome, estado[k]); });
  const q = p.toString();
  history.replaceState(null, "", `${location.pathname}${q ? `?${q}` : ""}${location.hash}`);
  $("#f-repor").disabled = !q;
}

/* ====================== Painéis ====================== */

function criarFicha(f) {
  const d = criar("details", "ficha");
  d.innerHTML = `<summary>Como se calcula</summary><dl>
    <dt>O que mede</dt><dd></dd><dt>Fórmula</dt><dd><code></code></dd><dt>Dados</dt><dd></dd><dt>Limitações</dt><dd></dd></dl>`;
  const dd = d.querySelectorAll("dd");
  dd[0].textContent = f.mede; $("code", dd[1]).textContent = f.formula; dd[2].textContent = f.dados; dd[3].textContent = f.limitacoes;
  return d;
}

/** Consulta a abrir no explorador a partir de um gráfico (a primeira, quando são várias) */
const sqlDe = p => p.consulta ?? p.consultas?.[0] ?? null;

function criarFigura(p) {
  const fig = criar("figure", "painel" + (p.largo ? " largo" : ""));
  fig.id = `p-${p.id}`;
  fig.tabIndex = -1;
  fig.setAttribute("aria-labelledby", `t-${p.id}`);
  fig.innerHTML = `
    <div class="painel-cabeca">
      <h4 id="t-${p.id}"></h4>
      <div class="painel-acoes">
        ${p.tabela || p.factos || p.matriz ? "" : `<button type="button" class="ver-tabela" aria-pressed="false" aria-controls="v-${p.id}">Ver tabela</button>`}
        ${sqlDe(p) ? `<a class="ver-sql" href="#sql/${sqlDe(p)}" title="Ver a consulta SQL que alimenta este gráfico">SQL</a>` : ""}
      </div>
    </div>
    <p class="descricao"></p>
    <p class="conclusao"></p>
    <div class="vista" id="v-${p.id}"></div>
    ${p.nota ? `<p class="nota-painel"></p>` : ""}`;
  $("h4", fig).textContent = p.pergunta;
  $(".descricao", fig).textContent = p.descricao;
  if (p.nota) $(".nota-painel", fig).textContent = p.nota;
  if (p.ficha) fig.appendChild(criarFicha(p.ficha));
  $(".ver-sql", fig)?.setAttribute("aria-label", `Ver a consulta SQL de «${p.pergunta}»`);
  const reg = { el: fig, p, grafico: null, visto: false, vista: "grafico", tema: -1 };
  $(".ver-tabela", fig)?.addEventListener("click", e => {
    reg.vista = reg.vista === "grafico" ? "tabela" : "grafico";
    e.currentTarget.textContent = reg.vista === "grafico" ? "Ver tabela" : "Ver gráfico";
    e.currentTarget.setAttribute("aria-pressed", String(reg.vista === "tabela"));
    desenharFigura(reg, { recriar: true });
  });
  figuras.set(p.id, reg);
  return fig;
}

function grelhaDe(paineis) {
  const g = criar("div", "grelha");
  paineis.forEach(p => g.appendChild(criarFigura(p)));
  return g;
}

function dadosDoPainel(p) {
  const ctx = { epoca: estado.epoca };
  const brutas = p.dados ? p.dados(ctx) : Dados.linhas(p.consulta);
  const filtradas = p.filtrar ? p.filtrar(brutas) : brutas;
  const rows = p.temporal ? Dados.noIntervalo(filtradas, epocasVisiveis()) : filtradas;
  return { rows, todas: brutas, ctx };
}

function desenharFigura(reg, { recriar = false } = {}) {
  const { p, el } = reg;
  const vista = $(".vista", el), conclusao = $(".conclusao", el), botao = $(".ver-tabela", el);
  const { rows, todas, ctx } = dadosDoPainel(p);

  if (!rows.length) {
    reg.grafico?.destroy(); reg.grafico = null;
    vista.replaceChildren(criar("p", "sem-dados", "Sem dados neste intervalo de épocas."));
    conclusao.textContent = "";
    botao?.setAttribute("hidden", "");
    return;
  }
  botao?.removeAttribute("hidden");
  try { conclusao.textContent = p.conclusao ? p.conclusao(rows, todas, ctx) : ""; }
  catch (e) { conclusao.textContent = ""; console.warn(`Conclusão de ${p.id}:`, e); }

  const temaMudou = reg.tema !== versaoTema;
  reg.tema = versaoTema;

  if (p.factos) { vista.replaceChildren(criarFactos(p.factos(rows))); return; }
  if (p.matriz) { vista.replaceChildren(criarMatriz(p.matriz(rows))); return; }
  if (p.tabela || reg.vista === "tabela") {
    reg.grafico?.destroy(); reg.grafico = null;
    const colunas = p.consulta ? Dados.consulta(p.consulta).colunas : Object.keys(rows[0]);
    vista.replaceChildren(tabelaOrdenavel(colunas, rows.map(r => colunas.map(c => r[c] ?? null)), p.consulta, { legenda: p.pergunta }));
    return;
  }

  let config;
  try { config = p.construir(rows, todas, ctx); }
  catch (e) { console.error(`Gráfico ${p.id}:`, e); vista.textContent = "Não foi possível desenhar este gráfico."; return; }

  let canvas = $("canvas", vista);
  if (!canvas || recriar || temaMudou) {
    reg.grafico?.destroy(); reg.grafico = null;
    const tela = criar("div", "tela");
    canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    tela.appendChild(canvas);
    vista.replaceChildren(tela);
  }
  canvas.setAttribute("aria-label", `${p.pergunta} ${conclusao.textContent} Os valores estão disponíveis no botão Ver tabela.`);
  reg.grafico = desenhar(canvas, config, reg.grafico);
}

function criarFactos(lista) {
  const ul = criar("ul", "factos");
  lista.forEach(f => {
    const li = criar("li", f.forte ? "forte" : "");
    li.append(criar("span", "rotulo", f.rotulo), criar("span", "valor", f.valor));
    ul.appendChild(li);
  });
  return ul;
}

/** Matriz de cenários com sombreado sequencial de um só tom */
function criarMatriz(m) {
  const env = criar("div", "tabela matriz");
  env.tabIndex = 0;
  env.setAttribute("role", "region");
  env.setAttribute("aria-label", "Tabela de cenários");
  const t = document.createElement("table");
  const valores = m.linhas.flatMap(l => m.colunas.map(c => m.celula(l, c)).filter(Boolean).map(m.valor));
  const max = Math.max(...valores, 1);
  const cab = t.createTHead().insertRow();
  [m.rotuloLinhas, ...m.colunas.map(c => `${c} lugar`)].forEach((txt, i) => {
    const th = criar("th", i ? "num" : "", txt); th.scope = "col"; cab.appendChild(th);
  });
  const corpo = t.createTBody();
  m.linhas.forEach(l => {
    const tr = corpo.insertRow();
    const th = criar("th", "", l); th.scope = "row"; tr.appendChild(th);
    m.colunas.forEach(c => {
      const r = m.celula(l, c), td = tr.insertCell();
      td.className = "num";
      if (!r) { td.textContent = "—"; return; }
      const f = m.valor(r) / max;
      td.style.setProperty("--intensidade", f.toFixed(3));
      td.classList.toggle("escura", f > 0.62);
      td.append(criar("strong", "", m.texto(r)), criar("small", "", m.detalhe(r)));
    });
  });
  env.appendChild(t);
  return env;
}

/* ====================== Construção das secções ====================== */

/** Ícones das secções (traço simples, herdam a cor do texto) */
const ICONES = {
  geral: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  perguntas: '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.2a2.5 2.5 0 1 1 3.4 2.3c-.7.3-1 .9-1 1.6v.4"/><circle cx="12" cy="16.8" r=".4"/>',
  receitas: '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
  custos: '<path d="M3 7l6 6 4-4 8 8"/><path d="M15 17h6v-6"/>',
  rentabilidade: '<path d="M18 6.6A7 7 0 1 0 18 17.4"/><path d="M4.5 10.2h9M4.5 13.8h9"/>',
  divida: '<circle cx="15" cy="6.5" r="4.6"/><text x="15" y="8.9" text-anchor="middle">€</text><path d="M2 14.5h3.2l3.3 2.2h4.7a1.4 1.4 0 0 0 0-2.8H9.8"/><path d="M8.5 16.7l5.8 1.6 6.4-3.3a1.5 1.5 0 0 0-1.4-2.6l-4.8 2"/><path d="M2 13v8"/>',
  desporto: '<circle cx="12" cy="12" r="9"/><path d="M12 7.5l4 2.9-1.5 4.6h-5L8 10.4z"/><path d="M12 3v4.5M16 10.4l4.5-1.5M14.5 15l2.8 3.8M9.5 15l-2.8 3.8M8 10.4L3.5 8.9"/>',
  cenarios: '<path d="M3 6.5v11"/><path d="M3 12h2.5M8 12h2.5M13 12h7.5"/><path d="M16 7.5L20.5 12 16 16.5"/>',
  solucoes: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.2h5c0-.9.4-1.7 1.1-2.2A6 6 0 0 0 12 3z"/>',
  sql: '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
  metodologia: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
};

/** Fotografias no topo das secções: imagem, legenda e crédito com ligação para a fonte */
const CAPAS = {
  perguntas: { img: "bandeiras", larg: 1600, alt: 642, alt_txt: "Bandeiras do Vitória SC, de Guimarães e de Portugal penduradas na bancada do Estádio D. Afonso Henriques, com adeptos.",
    sobre: "Estádio D. Afonso Henriques", titulo: "Cinco Perguntas sobre as Contas da SAD", credito: "Foto: Vitória SC", fonte: "https://vitoriasc.pt/wp-content/uploads/2026/10/antevisao_noticia-2-1024x683.jpg" },
  desporto: { img: "taca-liga", larg: 1600, alt: 781, alt_txt: "Jogadores do Vitória SC a festejar a conquista da Taça da Liga, com o troféu erguido ao centro.",
    sobre: "Época 2025/26", titulo: "Vencedor da Taça da Liga", credito: "Foto: Público", fonte: "https://imagens.publico.pt/imagens.aspx/2058208?tp=UH&db=IMAGENS&type=JPG", classe: "capa-taca" },
  cenarios: { img: "estadio", larg: 1400, alt: 581, alt_txt: "Estádio D. Afonso Henriques, em Guimarães, cheio e iluminado durante um jogo noturno.",
    sobre: "Guimarães", titulo: "Estádio D. Afonso Henriques", credito: "Foto: AMAP", fonte: "https://www.amap.pt/p/campos-de-jogos-do-vitoria-sport-clube", classe: "capa-estadio" },
  solucoes: { img: "solucoes", larg: 1600, alt: 788, alt_txt: "Jakupovic e Camara, de camisola cor-de-rosa do Vitória SC, a festejar um golo.",
    titulo: "Propostas para a Sustentabilidade Financeira", credito: "Foto: Diário do Minho", fonte: "https://www.diariodominho.pt/storage/posts/doc202610234799816720261023es11_6adbdceb75cee_2xl.jpg", classe: "capa-solucoes" },
};

function criarCapa(c) {
  const f = criar("figure", `capa ${c.classe ?? ""}`);
  f.innerHTML = `<picture>
      <source type="image/webp" srcset="img/${c.img}-800.webp?v=14 800w, img/${c.img}-${c.larg}.webp?v=14 ${c.larg}w" sizes="(max-width: 1240px) 100vw, 1240px">
      <img src="img/${c.img}-${c.larg}.webp?v=14" width="${c.larg}" height="${c.alt}" loading="lazy" alt="">
    </picture>
    <figcaption>${c.sobre ? '<p class="capa-sobre"></p>' : ""}<p class="capa-titulo"></p></figcaption>
    <a class="capa-credito" href="${c.fonte}"></a>`;
  $("img", f).alt = c.alt_txt;
  if (c.sobre) $(".capa-sobre", f).textContent = c.sobre;
  $(".capa-titulo", f).textContent = c.titulo;
  $(".capa-credito", f).textContent = c.credito;
  return f;
}

function construirSeccoes() {
  const main = $("#conteudo .dentro");
  const nav = $("#abas");
  SECCOES.forEach(s => {
    const a = criar("a");
    a.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONES[s.id] ?? ""}</svg><span></span>`;
    a.lastChild.textContent = s.nome;
    a.href = `#${s.id}`; a.dataset.seccao = s.id;
    nav.appendChild(a);

    let sec = $(`#sec-${s.id}`);
    if (!sec) { sec = document.createElement("section"); sec.id = `sec-${s.id}`; main.appendChild(sec); }
    sec.classList.add("seccao");
    sec.setAttribute("aria-labelledby", `h-${s.id}`);
    sec.hidden = true;
    const cab = criar("header", "seccao-cabeca");
    cab.innerHTML = `<h2 id="h-${s.id}"></h2><p></p>`;
    $("h2", cab).textContent = s.nome;
    $("p", cab).textContent = s.intro;
    sec.prepend(cab);
    if (CAPAS[s.id]) cab.after(criarCapa(CAPAS[s.id]));

    const paineis = PAINEIS.filter(p => p.seccao === s.id);
    if (ORDEM[s.id]) paineis.sort((x, y) => ORDEM[s.id].indexOf(x.id) - ORDEM[s.id].indexOf(y.id));
    if (s.id === "perguntas") { construirPerguntas(sec); return; }
    if (s.id === "solucoes") { construirSolucoes(sec); return; }
    if (GRUPOS[s.id]) {
      const padrao = GRUPOS[s.id].at(-1)[0];
      GRUPOS[s.id].forEach(([g, titulo, texto]) => {
        const h = criar("div", "grupo-cabeca");
        h.append(criar("h3", "", titulo), criar("p", "", texto));
        sec.append(h, grelhaDe(paineis.filter(p => (p.grupo ?? padrao) === g)));
      });
      return;
    }
    // Painéis com «bloco» vão para o contentor com o mesmo nome (ex.: estrutura acionista na visão geral)
    const blocos = [...new Set(paineis.map(p => p.bloco ?? ""))];
    blocos.forEach(b => {
      const lista = paineis.filter(p => (p.bloco ?? "") === b);
      ($(b ? `[data-paineis="${b}"]` : "[data-paineis]", sec) ?? sec).appendChild(grelhaDe(lista));
    });
  });
}

function construirPerguntas(sec) {
  const q = n => Dados.linhas(n);
  const indice = criar("ol", "indice-perguntas");
  sec.appendChild(indice);
  PERGUNTAS.forEach(per => {
    const li = criar("li");
    li.innerHTML = `<a href="#perguntas/pergunta-${per.n}"></a>`;
    $("a", li).textContent = per.pergunta;
    indice.appendChild(li);

    const art = criar("article", "pergunta-bloco");
    art.id = `pergunta-${per.n}`;
    art.tabIndex = -1;
    art.setAttribute("aria-labelledby", `pq-${per.n}`);
    art.innerHTML = `<header><span class="num" aria-hidden="true">${per.n}</span><h3 id="pq-${per.n}"></h3></header>
      <p class="contexto"></p>
      <p class="resposta-rotulo">Resposta</p>
      <p class="resposta"></p><div class="indicadores"></div><div class="graficos"></div>
      <p class="limitacoes"><strong>Limitações.</strong> <span></span></p>
      <p class="consultas-ref">Consultas: ${per.consultas.map(ligacaoConsulta).join(", ")}</p>`;
    $("h3", art).textContent = per.pergunta;
    $(".contexto", art).textContent = per.contexto ?? "";
    try {
      $(".resposta", art).textContent = per.resposta({ q });
      $(".indicadores", art).appendChild(criarFactos(per.indicadores({ q })));
    } catch (e) { $(".resposta", art).textContent = "Resposta indisponível."; console.warn(e); }
    $(".limitacoes span", art).textContent = per.limitacoes;
    $(".graficos", art).appendChild(grelhaDe(PAINEIS.filter(p => p.seccao === "perguntas" && p.questao === per.n)));
    sec.appendChild(art);
  });
}

function construirSolucoes(sec) {
  const q = n => Dados.linhas(n);
  const aviso = criar("p", "caixa-nota", "Propostas do autor, com base nos indicadores do painel. Não representam a posição da SAD nem constituem aconselhamento financeiro. A prioridade é alta quando o indicador principal está fora da referência.");
  const lista = criar("ol", "solucoes");
  SOLUCOES.forEach(sol => {
    const li = criar("li", "solucao");
    li.id = `solucao-${sol.n}`;
    let alta = false, diag = "", medidas = [], inds = [];
    try { alta = sol.alta({ q }); diag = sol.diagnostico({ q }); medidas = sol.medidas({ q }); inds = sol.indicadores({ q }); }
    catch (e) { console.warn(`Solução ${sol.n}:`, e); }
    const area = SECCOES.find(s => s.id === sol.area);
    li.innerHTML = `<header class="solucao-cabeca"><span class="num" aria-hidden="true">${sol.n}</span><h3></h3>
        <span class="prioridade ${alta ? "alta" : "media"}">Prioridade ${alta ? "alta" : "média"}</span></header>
      <div class="solucao-corpo">
        <div><p class="rotulo-claro">Diagnóstico</p><p class="diagnostico"></p>
          <p class="rotulo-claro">Medidas propostas</p><ul class="medidas"></ul></div>
        <div><p class="rotulo-claro">Indicadores a acompanhar</p>
          <table class="metas"><thead><tr><th scope="col">Indicador</th><th scope="col" class="num">Última época</th><th scope="col">Referência</th></tr></thead><tbody></tbody></table>
          <a class="ver-mais" href="#${sol.area}">Ver a análise em ${area?.nome ?? ""} →</a></div>
      </div>`;
    $("h3", li).textContent = sol.titulo;
    $(".diagnostico", li).textContent = diag;
    $(".medidas", li).replaceChildren(...medidas.map(m => criar("li", "", m)));
    $(".metas tbody", li).replaceChildren(...inds.map(i => {
      const tr = document.createElement("tr");
      const th = criar("th", "", i.rotulo); th.scope = "row";
      tr.append(th, criar("td", "num", i.valor), criar("td", "", i.referencia));
      return tr;
    }));
    lista.appendChild(li);
  });
  sec.append(aviso, lista);
}

function construirMetodologia() {
  const fontes = Dados.base().fontes;
  $("#tabela-fontes").appendChild(tabelaOrdenavel(["epoca", "estado", "documentos"],
    fontes.map(f => [f.epoca, f.estado, f.documentos]), null, { legenda: "Fontes por época" }));
  const div = Dados.consulta(35);
  $("#tabela-divergencias").appendChild(tabelaOrdenavel(div.colunas, div.linhas, 35, { legenda: "Divergências face aos Relatórios e Contas" }));
  $("#n-divergencias").textContent = inteiro(Dados.linhas(35).reduce((s, r) => s + r.divergencias, 0));
}

/* ====================== Visão geral ====================== */

const naConsulta = (n, campo) => ep => Dados.linhas(n).find(r => r.epoca === ep)?.[campo] ?? null;
const serieKPI = campo => ep => Dados.kpi(ep)?.[campo] ?? null;
const serieDR = campo => ep => Dados.dr(ep)?.[campo] ?? null;
const fecho = ep => `30/06/20${ep.slice(-2)}`;

/**
 * Indicadores da síntese financeira. `bom`: +1 se subir é favorável, −1 se é desfavorável.
 * `sinal`: o valor é verde quando positivo e vermelho quando negativo. `balanco`: valor a 30 de junho.
 * `extra`: linha de contexto, também a partir das consultas.
 */
const KPIS = [
  { id: "rendimentos", nome: "Rendimentos operacionais", valor: naConsulta(103, "rendimentos_operacionais"), bom: 1, fonte: 103,
    extra: ep => { const v = naConsulta(103, "vendas_servicos")(ep); return v === null ? "" : `dos quais ${euros(v)} de vendas e serviços prestados`; } },
  { id: "gastos", nome: "Gastos operacionais", valor: naConsulta(58, "total_gastos"), bom: -1, fonte: 58,
    extra: ep => { const v = naConsulta(58, "pessoal_pct")(ep); return v === null ? "" : `${pct(v)} são gastos com pessoal`; } },
  { id: "ro", nome: "Resultado operacional", valor: serieDR("resultado_operacional"), bom: 1, sinal: true, fonte: 102,
    extra: ep => { const v = naConsulta(106, "margem_operacional_pct")(ep); return v === null ? "" : `margem operacional de ${pct(v)}`; } },
  { id: "rl", nome: "Resultado líquido", valor: serieKPI("resultado_liquido"), bom: 1, sinal: true, fonte: 2,
    extra: ep => { const v = serieKPI("rl_sem_mais_valias")(ep); return v === null ? "" : `sem mais-valias: ${euros(v)}`; } },
  { id: "passivo", nome: "Passivo total", valor: serieKPI("passivo_total"), bom: -1, balanco: true, fonte: 101,
    extra: ep => { const v = naConsulta(27, "financiamentos")(ep); return v === null ? "" : `dos quais ${euros(v)} de dívida financeira`; } },
  { id: "capital", nome: "Capitais próprios", valor: serieKPI("capital_proprio"), bom: 1, sinal: true, balanco: true, fonte: 101,
    extra: ep => { const v = naConsulta(101, "autonomia_pct")(ep); return v === null ? "" : `autonomia financeira de ${pct(v)}`; } },
  { id: "pessoal", nome: "Gastos com pessoal", valor: serieKPI("gastos_pessoal"), bom: -1, fonte: 103,
    extra: ep => { const v = naConsulta(103, "pessoal_sobre_vendas_pct")(ep); return v === null ? "" : `${pct(v)} das vendas e serviços prestados`; } },
  { id: "encargos", nome: "Juros dos financiamentos", valor: naConsulta(27, "juros"), bom: -1, fonte: 27,
    extra: ep => {
      const t = naConsulta(27, "taxa_implicita_pct")(ep), dr = serieKPI("juros")(ep);
      return [t !== null && `taxa implícita de ${pct(t)}`, dr !== null && `juros e gastos similares na DR: ${euros(dr)}`].filter(Boolean).join(" · ");
    } },
];

/** Tendência em SVG, sem eixos: épocas em falta ficam em branco; a época em destaque tem um ponto */
function sparkline(valores, destaque) {
  const n = valores.length, nums = valores.filter(v => v !== null);
  if (nums.length < 2) return null;
  const min = Math.min(...nums, 0), max = Math.max(...nums, 0), amp = max - min || 1;
  const x = i => (i / (n - 1)) * 100, y = v => 26 - ((v - min) / amp) * 24;
  let d = "", aberto = false;
  valores.forEach((v, i) => {
    if (v === null) { aberto = false; return; }
    d += `${aberto ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`;
    aberto = true;
  });
  const zero = min < 0 ? `<line x1="0" x2="100" y1="${y(0).toFixed(1)}" y2="${y(0).toFixed(1)}" class="zero"/>` : "";
  const p = valores[destaque];
  const ponto = p !== null && p !== undefined ? `<circle cx="${x(destaque).toFixed(1)}" cy="${y(p).toFixed(1)}" r="2.8"/>` : "";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "-3 -2 106 31");
  svg.setAttribute("preserveAspectRatio", "none");
  svg.setAttribute("aria-hidden", "true");
  svg.classList.add("sparkline");
  svg.innerHTML = `${zero}<path d="${d}"/>${ponto}`;
  return svg;
}

function construirKPIs() {
  const caixa = $("#kpis");
  KPIS.forEach((ind, i) => {
    const d = criar("article", "kpi");
    d.style.setProperty("--i", i); d.dataset.id = ind.id;
    d.setAttribute("aria-labelledby", `kpi-${ind.id}`);
    d.innerHTML = `<header class="kpi-cabeca"><h4 class="nome" id="kpi-${ind.id}"></h4><span class="periodo"></span></header>
      <p class="valor"></p><p class="delta"></p><p class="extra"></p>
      <div class="tendencia"></div>
      <p class="kpi-fonte"><a href="#sql/${ind.fonte}">${ind.fonte > 100 ? codigoConsulta(ind.fonte) : `C${ind.fonte}`}</a></p>`;
    $(".nome", d).textContent = ind.nome;
    $(".kpi-fonte a", d).setAttribute("aria-label", `Fonte de ${ind.nome}: ${ind.fonte > 100 ? "consulta complementar" : "consulta"} ${codigoConsulta(ind.fonte)}`);
    caixa.appendChild(d);
  });
}

function desenharKPIs() {
  const e = Dados.epocas(), i = e.indexOf(estado.epoca);
  KPIS.forEach(ind => {
    const d = $(`.kpi[data-id="${ind.id}"]`);
    const fmt = x => formatar("eur", x);
    const serie = e.map(ep => ind.valor(ep));
    const v = serie[i];
    // Época anterior com valor (há séries com épocas em falta)
    let k = i - 1; while (k >= 0 && serie[k] === null) k--;
    const a = k >= 0 ? serie[k] : null, anterior = k >= 0 ? e[k] : null;
    const elV = $(".valor", d), delta = $(".delta", d);
    $(".periodo", d).textContent = ind.balanco ? `a ${fecho(estado.epoca)}` : estado.epoca;
    d.classList.toggle("vazio", v === null);
    d.classList.toggle("positivo", !!ind.sinal && v !== null && v > 0);
    d.classList.toggle("negativo", !!ind.sinal && v !== null && v < 0);
    if (v === null) { elV.textContent = "sem dados"; elV.removeAttribute("title"); }
    else { contar(elV, valoresKPI[ind.id], v, fmt); elV.title = `${inteiro(v)} €`; }
    valoresKPI[ind.id] = v;

    delta.replaceChildren();
    if (v !== null && a !== null && v !== a) {
      const dif = v - a, favoravel = Math.sign(dif) === ind.bom;
      // A variação percentual só tem leitura direta quando os dois valores são positivos
      const p = v > 0 && a > 0 ? ` (${dif > 0 ? "+" : "−"}${pct(Math.abs(100 * dif / a))})` : "";
      delta.append(criar("span", favoravel ? "melhor" : "pior", `${dif > 0 ? "▲" : "▼"} ${variacaoEuros(dif)}${p}`),
        ` face a ${anterior}`, criar("span", "sr-only", favoravel ? " (evolução favorável)" : " (evolução desfavorável)"));
    } else if (v !== null) {
      delta.textContent = a === null ? "primeira época com dados" : `igual a ${anterior}`;
    }
    $(".extra", d).textContent = v === null ? `Valor não publicado para ${estado.epoca}.` : ind.extra(estado.epoca);

    const t = $(".tendencia", d);
    t.replaceChildren();
    const svg = sparkline(serie, i);
    if (svg) t.appendChild(svg);
    const nums = serie.filter(x => x !== null);
    if (v !== null && nums.length > 2) {
      if (v === Math.max(...nums)) t.appendChild(criar("span", "recorde", "máximo da série"));
      else if (v === Math.min(...nums)) t.appendChild(criar("span", "recorde", "mínimo da série"));
    }
  });
}

function desenharVariacoes() {
  const lista = $("#variacoes");
  const rows = Dados.linhas(104).filter(r => r.epoca === estado.epoca && r.variacao !== null);
  // Ordena pela variação em euros: a percentual engana quando a base é pequena ou muda de sinal
  rows.sort((a, b) => Math.abs(b.variacao) - Math.abs(a.variacao));
  lista.replaceChildren(...(rows.length ? rows.slice(0, 5).map(r => {
    const li = criar("li");
    const mudouSinal = Math.sign(r.valor) !== Math.sign(r.anterior) && r.valor !== 0 && r.anterior !== 0;
    const ambosPositivos = r.valor > 0 && r.anterior > 0;
    const sinal = mudouSinal ? " (mudou de sinal)" : ambosPositivos && r.variacao_pct !== null ? ` (${r.variacao_pct > 0 ? "+" : "−"}${pct(Math.abs(r.variacao_pct))})` : "";
    // O ativo não tem sentido favorável definido: fica a cinzento
    const sentido = SENTIDO[r.indicador], favoravel = Math.sign(r.variacao) === sentido;
    const v = criar("span", `var ${sentido ? (favoravel ? "melhor" : "pior") : ""}`, `${variacaoEuros(r.variacao)}${sinal}`);
    if (sentido) v.appendChild(criar("span", "sr-only", favoravel ? " (favorável)" : " (desfavorável)"));
    li.append(criar("span", "ind", r.indicador), v,
      criar("span", "ref", `${euros(r.anterior)} em ${r.epoca_anterior} → ${euros(r.valor)}`));
    return li;
  }) : [criar("li", "vazio", "Sem época anterior comparável.")]));

  const ext = Dados.linhas(105).filter(r => r.n_epocas > 2);
  const corpo = $("#extremos tbody");
  corpo.replaceChildren(...ext.map(r => {
    const tr = document.createElement("tr");
    const celula = (ep, v) => {
      const td = criar("td", "num" + (ep === estado.epoca ? " atual" : ""));
      td.append(criar("strong", "", euros(v)), criar("small", "", ep));
      return td;
    };
    const th = criar("th", "", r.indicador); th.scope = "row";
    tr.append(th, celula(r.epoca_maximo, r.maximo), celula(r.epoca_minimo, r.minimo), criar("td", "num", inteiro(r.n_epocas)));
    return tr;
  }));
  $("#extremos").hidden = !ext.length;
  $("#extremos-vazio").hidden = ext.length > 0;
}

function desenharConclusoes() {
  const c = conclusoes(estado.epoca);
  const grupos = [["melhorias", "Evolução", "Face à época anterior: favorável e desfavorável"], ["riscos", "Riscos", "Valores fora dos limiares de referência"],
    ["atencao", "Alertas", "Dependência das vendas e peso dos gastos"], ["estruturais", "Alterações estruturais", "Pessoal, dívida e contas"]];
  $("#conclusoes").replaceChildren(...grupos.map(([k, titulo, sub]) => {
    const div = criar("div", `concl concl-${k}`);
    const cab = criar("div", "concl-cabeca");
    cab.append(criar("h4", "", titulo), criar("span", "concl-n", String(c[k].length)));
    cab.lastChild.setAttribute("aria-label", `${c[k].length} ${c[k].length === 1 ? "ponto" : "pontos"}`);
    div.append(cab, criar("p", "sub", sub));
    const ul = criar("ul");
    if (!c[k].length) ul.appendChild(criar("li", "vazio", "Nada a assinalar nesta época."));
    c[k].forEach(item => {
      const li = criar("li");
      if (item.sentido) {
        li.className = item.sentido;
        li.appendChild(criar("span", "etiqueta", item.sentido === "favoravel" ? "▲ Favorável" : "▼ Desfavorável"));
      }
      li.append(criar("span", "", item.texto), " ");
      const a = criar("a", "src", item.n > 100 ? codigoConsulta(item.n) : `C${item.n}`);
      a.href = `#sql/${item.n}`;
      a.setAttribute("aria-label", `Fonte: consulta ${codigoConsulta(item.n)}`);
      li.appendChild(a);
      ul.appendChild(li);
    });
    div.appendChild(ul);
    return div;
  }));
}

/**
 * Estado das contas da época em destaque: parciais, reexpressas ou sujeitas a aprovação.
 * Vem da tabela de fontes e da consulta 36; devolve [texto longo, texto curto] por situação.
 */
function estadoContas(ep) {
  const f = Dados.base().fontes.find(x => x.epoca === ep), avisos = [];
  if (f && /^Apenas/.test(f.estado)) avisos.push([`Dados parciais: ${f.estado.charAt(0).toLowerCase()}${f.estado.slice(1)}`, "dados parciais", "alerta"]);
  if (ep === EPOCA_REEXPRESSA) avisos.push(["Valores originalmente publicados; reexpressos no Relatório e Contas seguinte (consulta 36)", "valores originais, depois reexpressos", "info"]);
  if (f && /sujeito a aprovação da AG/.test(f.documentos)) avisos.push(["Contas aprovadas pelo Conselho de Administração, sujeitas a aprovação da Assembleia Geral", "contas sujeitas a aprovação da AG", "alerta"]);
  const i = Dados.epocas().indexOf(ep);
  if (Dados.epocas()[i - 1] === EPOCA_REEXPRESSA) avisos.push([`Variações calculadas face aos valores originais de ${EPOCA_REEXPRESSA}`, null, "info"]);
  return avisos;
}

function construirCartoesGeral() {
  const q = n => Dados.linhas(n);
  $("#cartoes-perguntas").replaceChildren(...PERGUNTAS.map(per => {
    const li = criar("li", "cartao-pergunta");
    li.innerHTML = `<span class="num" aria-hidden="true">${per.n}</span><h4><a href="#perguntas/pergunta-${per.n}"></a></h4><p></p><span class="seta" aria-hidden="true">Ver análise →</span>`;
    $("a", li).textContent = per.pergunta;
    let resposta = "";
    try { resposta = per.resposta({ q }); } catch (e) { console.warn(e); }
    // Primeira frase da resposta, calculada a partir das consultas
    const frases = resposta.split(/(?<=\.)\s/);
    $("p", li).textContent = frases[0].length < 25 && frases[1] ? `${frases[0]} ${frases[1]}` : frases[0];
    return li;
  }));
  const contagem = id => PAINEIS.filter(p => p.seccao === id).length;
  $("#cartoes-areas").replaceChildren(...SECCOES.filter(s => ["receitas", "custos", "rentabilidade", "divida", "desporto", "cenarios", "solucoes"].includes(s.id)).map(s => {
    const li = criar("li", "cartao-area");
    li.innerHTML = `<h4><a href="#${s.id}"></a></h4><p></p><span class="contagem"></span>`;
    $("a", li).textContent = s.nome;
    $("p", li).textContent = s.intro;
    $(".contagem", li).textContent = s.id === "solucoes" ? `${SOLUCOES.length} propostas` : `${contagem(s.id)} visualizações e tabelas`;
    return li;
  }));
}

function desenharGeral() {
  document.querySelectorAll("[data-ref-epoca]").forEach(el => (el.textContent = estado.epoca));
  document.querySelectorAll("[data-ref-fecho]").forEach(el => (el.textContent = fecho(estado.epoca)));
  const sel = epocasVisiveis();
  document.querySelectorAll("[data-ref-intervalo]").forEach(el => (el.textContent = sel.length > 1 ? `${sel[0]} a ${sel[sel.length - 1]}` : sel[0]));
  const selos = $("#estado-contas");
  selos.replaceChildren(...estadoContas(estado.epoca).map(([longo, , tipo]) => criar("li", `selo selo-${tipo}`, longo)));
  selos.hidden = !selos.children.length;
  desenharKPIs();
  desenharVariacoes();
  desenharConclusoes();

  const d = Dados.desporto(estado.epoca);
  const partes = d ? [`${d.posicao_liga}.º lugar na Liga, ${d.pontos} pontos`,
    d.competicao_europeia && `${d.competicao_europeia} (${(d.fase_europeia ?? "").toLowerCase()})`,
    d.trofeu && `vencedor da ${d.trofeu}`].filter(Boolean) : [];
  const campo = $("#em-campo");
  campo.textContent = partes.length ? `Desempenho desportivo em ${estado.epoca}: ${partes.join(" · ")}.` : "";
  campo.hidden = !partes.length;
}

/* ====================== Filtros ====================== */

function construirFiltros() {
  const e = Dados.epocas(), n = e.length;
  const ini = $("#f-inicio"), fim = $("#f-fim");
  $("#linha-tempo").style.setProperty("--n", n);
  [ini, fim].forEach(r => { r.max = n - 1; });

  // Pegas do período: atualizam o texto ao arrastar e os gráficos ao largar (ou a cada tecla)
  const mover = qual => {
    ancora = null;
    let i = Number(ini.value), f = Number(fim.value);
    if (i > f) { if (qual === "inicio") i = f; else f = i; ini.value = i; fim.value = f; }
    estado.inicio = e[i]; estado.fim = e[f];
    ajustarDestaque();
    sincronizarFiltros();
  };
  ini.addEventListener("input", () => mover("inicio"));
  fim.addEventListener("input", () => mover("fim"));
  [ini, fim].forEach(r => r.addEventListener("change", () => atualizar({ recriar: true })));

  // Atalhos de período
  const atalhos = [["Todas", 0], ["Últimas 5", n - 5], ["Últimas 3", n - 3]];
  const caixa = $("#f-atalhos");
  atalhos.forEach(([rot, k]) => {
    const b = criar("button", "atalho", rot);
    b.type = "button"; b.dataset.inicio = e[Math.max(0, k)];
    b.addEventListener("click", () => {
      ancora = null;
      Object.assign(estado, { inicio: b.dataset.inicio, fim: e[n - 1] });
      ajustarDestaque();
      atualizar({ recriar: true });
    });
    caixa.appendChild(b);
  });

  // Época em destaque: grupo de botões de opção, com navegação por setas
  const grupo = $("#f-epocas");
  e.forEach(x => {
    const b = criar("button", "epoca-btn", `${x.slice(2, 4)}/${x.slice(-2)}`);
    b.type = "button"; b.dataset.epoca = x;
    b.setAttribute("role", "radio");
    b.setAttribute("aria-label", x);
    b.title = x;
    b.addEventListener("click", () => clicarEpoca(x));
    grupo.appendChild(b);
  });
  // O segundo clique só conta se for logo a seguir, na linha do tempo; Esc ou um clique fora cancelam
  document.addEventListener("keydown", ev => { if (ev.key === "Escape" && ancora) { ancora = null; sincronizarFiltros(); } });
  document.addEventListener("click", ev => { if (ancora && !ev.target.closest("#f-epocas")) { ancora = null; sincronizarFiltros(); } });
  grupo.addEventListener("keydown", ev => {
    const passo = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[ev.key];
    const vis = epocasVisiveis();
    let alvo = null;
    if (passo) alvo = vis[Math.min(vis.length - 1, Math.max(0, vis.indexOf(estado.epoca) + passo))];
    if (ev.key === "Home") alvo = vis[0];
    if (ev.key === "End") alvo = vis[vis.length - 1];
    if (!alvo) return;
    ev.preventDefault();
    ancora = null;
    escolherDestaque(alvo);
    $(`.epoca-btn[data-epoca="${alvo}"]`, grupo).focus();
  });
  $("#f-repor").addEventListener("click", () => { ancora = null; Object.assign(estado, { ...PADRAO, seccao: estado.seccao }); atualizar({ recriar: true }); });
}

/** Época do primeiro clique, à espera de um segundo para definir o período */
let ancora = null;

function clicarEpoca(x) {
  const e = Dados.epocas();
  if (ancora && x !== ancora) {
    // Segundo clique: período entre as duas épocas; fica em destaque a última clicada
    const [a, b] = [e.indexOf(ancora), e.indexOf(x)].sort((p, q) => p - q);
    Object.assign(estado, { inicio: e[a], fim: e[b], epoca: x });
    ancora = null;
    atualizar({ recriar: true });
    return;
  }
  if (ancora === x) { ancora = null; sincronizarFiltros(); return; }
  // Primeiro clique: põe a época em destaque (alargando o período, se estiver fora) e guarda-a como âncora
  ancora = x;
  const i = e.indexOf(x), mudaPeriodo = i < e.indexOf(estado.inicio) || i > e.indexOf(estado.fim);
  if (i < e.indexOf(estado.inicio)) estado.inicio = x;
  if (i > e.indexOf(estado.fim)) estado.fim = x;
  estado.epoca = x;
  atualizar({ recriar: mudaPeriodo });
}

function escolherDestaque(ep) {
  if (ep === estado.epoca || !epocasVisiveis().includes(ep)) return;
  estado.epoca = ep;
  atualizar();
}

/** A época em destaque tem de estar dentro do período; se ficar de fora, passa para o extremo mais próximo */
function ajustarDestaque() {
  const e = Dados.epocas(), vis = epocasVisiveis();
  if (vis.includes(estado.epoca)) return;
  estado.epoca = e.indexOf(estado.epoca) < e.indexOf(vis[0]) ? vis[0] : vis[vis.length - 1];
}

function sincronizarFiltros() {
  const e = Dados.epocas(), n = e.length, i = e.indexOf(estado.inicio), f = e.indexOf(estado.fim);
  const ini = $("#f-inicio"), fim = $("#f-fim");
  ini.value = i; fim.value = f;
  ini.setAttribute("aria-valuetext", estado.inicio);
  fim.setAttribute("aria-valuetext", estado.fim);
  // Quando as duas pegas coincidem no fim, a inicial fica por cima para poder ser arrastada
  ini.style.zIndex = i === f && f === n - 1 ? 3 : 2;
  const passo = 100 / (n - 1);
  $("#f-preenchido").style.left = `${i * passo}%`;
  $("#f-preenchido").style.width = `${(f - i) * passo}%`;
  const vis = epocasVisiveis();
  document.querySelectorAll(".epoca-btn").forEach(b => {
    const ativa = b.dataset.epoca === estado.epoca, dentro = vis.includes(b.dataset.epoca);
    b.setAttribute("aria-checked", String(ativa));
    b.tabIndex = ativa ? 0 : -1;
    b.classList.toggle("fora", !dentro);
    b.classList.toggle("ancora", b.dataset.epoca === ancora);
  });
  const ajuda = $("#ajuda-destaque");
  ajuda.textContent = ancora
    ? `Clique noutra época para analisar o período entre ${ancora} e essa época (Esc para cancelar).`
    : "Clique numa época para a pôr em destaque e depois noutra para definir o período entre as duas. Também pode arrastar as pegas amarelas.";
  ajuda.classList.toggle("ativa", !!ancora);
  document.querySelectorAll(".atalho").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.inicio === estado.inicio && estado.fim === e[n - 1])));
  // Em ecrãs estreitos, mantém visível a época em destaque na linha do tempo (sem mexer na página)
  const rolar = $(".linha-tempo-rolar"), btn = $(".epoca-btn[aria-checked='true']");
  if (btn && rolar.scrollWidth > rolar.clientWidth) rolar.scrollLeft = btn.offsetLeft - rolar.clientWidth / 2 + btn.offsetWidth / 2;
  const nv = vis.length;
  const resumo = $("#f-resumo");
  resumo.replaceChildren(criar("strong", "", nv > 1 ? `${vis[0]} a ${vis[nv - 1]}` : vis[0]), ` · ${nv} ${nv === 1 ? "época" : "épocas"} · em destaque `,
    criar("strong", "", estado.epoca));
  estadoContas(estado.epoca).forEach(([, curto]) => { if (curto) resumo.append(` · ${curto}`); });
}

function atualizar({ recriar = false } = {}) {
  definirDestaque(estado.epoca);
  sincronizarFiltros();
  escreverURL();
  if (estado.seccao === "geral") desenharGeral();
  figuras.forEach(reg => {
    if (reg.visto && !reg.el.closest(".seccao").hidden) desenharFigura(reg, { recriar });
  });
}

/* ====================== Pesquisa global ====================== */

const sem = t => t.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

/** Índice de tudo o que se pode encontrar: gráficos, indicadores, perguntas, soluções, glossário e consultas */
function indicePesquisa() {
  const nomeSec = id => SECCOES.find(s => s.id === id)?.nome ?? "";
  const itens = [];
  KPIS.forEach(k => itens.push({ titulo: k.nome, tipo: "Indicador", sec: "Visão Geral", destino: "geral/h-sintese" }));
  PAINEIS.forEach(p => itens.push({ titulo: p.pergunta, texto: p.descricao, tipo: "Gráfico", sec: nomeSec(p.seccao),
    destino: p.seccao === "perguntas" ? `perguntas/pergunta-${p.questao}` : `${p.seccao}/${p.id}` }));
  PERGUNTAS.forEach(p => itens.push({ titulo: p.pergunta, texto: p.contexto, tipo: "Pergunta", sec: "Cinco Perguntas", destino: `perguntas/pergunta-${p.n}` }));
  SOLUCOES.forEach(p => itens.push({ titulo: p.titulo, tipo: "Solução", sec: "Soluções", destino: `solucoes/solucao-${p.n}` }));
  document.querySelectorAll(".glossario dt").forEach((dt, i) => {
    dt.id ||= `glossario-${i}`;
    itens.push({ titulo: dt.textContent, texto: dt.nextElementSibling?.textContent, tipo: "Glossário", sec: "Metodologia e Fontes", destino: `metodologia/${dt.id}` });
  });
  Dados.todasConsultas().forEach(c => itens.push({ titulo: c.titulo, tipo: `Consulta ${c.codigo}`, sec: "Consultas SQL", destino: `sql/${c.n}` }));
  itens.forEach(i => { i.chaveTitulo = sem(i.titulo); i.chave = sem(`${i.titulo} ${i.texto ?? ""}`); });
  return itens;
}

function construirPesquisa() {
  const itens = indicePesquisa();
  const painel = $("#pesquisa-global"), campo = $("#campo-pesquisa"), lista = $("#resultados-pesquisa"), estadoP = $("#pesquisa-estado"), botao = $("#abrir-pesquisa");
  let atual = -1, resultados = [];

  const abrir = () => { painel.hidden = false; botao.setAttribute("aria-expanded", "true"); campo.focus(); campo.select(); };
  const fechar = (devolverFoco = true) => {
    painel.hidden = true; botao.setAttribute("aria-expanded", "false"); campo.setAttribute("aria-expanded", "false");
    if (devolverFoco) botao.focus();
  };
  const ir = r => { fechar(false); campo.value = ""; desenhar(); navegar(r.destino); };

  function desenhar() {
    const termos = sem(campo.value.trim()).split(/\s+/).filter(Boolean);
    if (!termos.length) { lista.replaceChildren(); estadoP.textContent = "Escreva um indicador, uma rubrica ou um conceito."; campo.setAttribute("aria-expanded", "false"); return; }
    // Todos os termos têm de aparecer; os resultados com os termos no título vêm primeiro
    resultados = itens.filter(i => termos.every(t => i.chave.includes(t)))
      .map(i => ({ ...i, peso: termos.filter(t => i.chaveTitulo.includes(t)).length * 10 - (i.tipo.startsWith("Consulta") ? 3 : 0) }))
      .sort((a, b) => b.peso - a.peso).slice(0, 12);
    atual = resultados.length ? 0 : -1;
    lista.replaceChildren(...resultados.map((r, k) => {
      const li = criar("li");
      li.id = `res-${k}`; li.setAttribute("role", "option");
      li.append(criar("span", "res-titulo", r.titulo), criar("span", "res-meta", `${r.tipo} · ${r.sec}`));
      li.addEventListener("mousedown", ev => ev.preventDefault());
      li.addEventListener("click", () => ir(r));
      return li;
    }));
    marcar();
    campo.setAttribute("aria-expanded", String(resultados.length > 0));
    estadoP.textContent = resultados.length ? `${resultados.length} ${resultados.length === 1 ? "resultado" : "resultados"} · Enter para abrir` : "Nenhum resultado. Experimente outro termo.";
  }
  function marcar() {
    lista.querySelectorAll("li").forEach((li, k) => li.setAttribute("aria-selected", String(k === atual)));
    if (atual >= 0) { campo.setAttribute("aria-activedescendant", `res-${atual}`); $(`#res-${atual}`)?.scrollIntoView({ block: "nearest" }); }
    else campo.removeAttribute("aria-activedescendant");
  }

  botao.addEventListener("click", () => (painel.hidden ? abrir() : fechar()));
  $("#fechar-pesquisa").addEventListener("click", () => fechar());
  campo.addEventListener("input", desenhar);
  campo.addEventListener("keydown", ev => {
    if (ev.key === "ArrowDown" && resultados.length) { atual = (atual + 1) % resultados.length; marcar(); ev.preventDefault(); }
    else if (ev.key === "ArrowUp" && resultados.length) { atual = (atual - 1 + resultados.length) % resultados.length; marcar(); ev.preventDefault(); }
    else if (ev.key === "Enter" && atual >= 0) { ir(resultados[atual]); ev.preventDefault(); }
    else if (ev.key === "Escape") { fechar(); ev.stopPropagation(); }
  });
  document.addEventListener("keydown", ev => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k") { ev.preventDefault(); abrir(); }
  });
  document.addEventListener("click", ev => { if (!painel.hidden && !ev.target.closest(".faixa-abas")) fechar(false); });
  desenhar();
}

/* ====================== Navegação ====================== */

/** Muda de secção substituindo o endereço atual (sem nova entrada no histórico do browser) */
function navegar(destino) {
  history.replaceState(null, "", `${location.pathname}${location.search}#${destino}`);
  mostrarSeccao();
}

function mostrarSeccao() {
  const [id, alvo] = decodeURIComponent(location.hash.slice(1)).split("/");
  const seccao = SECCOES.some(s => s.id === id) ? id : "geral";
  const mudou = seccao !== estado.seccao;
  estado.seccao = seccao;
  document.querySelectorAll(".seccao").forEach(s => (s.hidden = s.id !== `sec-${seccao}`));
  document.querySelectorAll("#abas a").forEach(a => {
    if (a.dataset.seccao === seccao) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  document.title = `${SECCOES.find(s => s.id === seccao).nome} · As Contas da Vitória SC SAD`;
  // Mantém a aba ativa visível em ecrãs estreitos, sem mexer no foco
  const aba = $("#abas a[aria-current]"), abas = $("#abas");
  if (aba && (aba.offsetLeft < abas.scrollLeft || aba.offsetLeft + aba.offsetWidth > abas.scrollLeft + abas.clientWidth)) {
    abas.scrollLeft = aba.offsetLeft - 16;
  }

  if (seccao === "geral") desenharGeral();
  if (seccao === "sql") {
    const n = Number(alvo) || Number($("[data-explorador]").dataset.ativa) || 1;
    explorador.mostrar(n);
    if (alvo && innerWidth < 980) $("[data-detalhe]").scrollIntoView({ behavior: reduzido ? "auto" : "smooth", block: "start" });
  }

  const daSeccao = [...figuras.values()].filter(r => r.el.closest(".seccao")?.id === `sec-${seccao}`);
  daSeccao.filter(r => r.visto).forEach(r => desenharFigura(r, { recriar: true }));
  observar(daSeccao.filter(r => !r.visto).map(r => r.el), el => {
    const reg = [...figuras.values()].find(r => r.el === el);
    reg.visto = true;
    el.classList.add("visivel");
    desenharFigura(reg, { recriar: true });
  });

  if (alvo && seccao !== "sql") {
    const destino = $(`#p-${alvo}`) ?? document.getElementById(alvo);
    if (destino) requestAnimationFrame(() => {
      destino.scrollIntoView({ behavior: reduzido ? "auto" : "smooth", block: "start" });
      destino.focus({ preventScroll: true });
    });
  } else if (mudou) {
    window.scrollTo({ top: 0 });
  }
}

/* ---------- Tema ---------- */

function prepararTema() {
  const raiz = document.documentElement;
  try { const t = localStorage.getItem("tema"); if (t) raiz.dataset.theme = t; } catch { /* sem armazenamento */ }
  const botao = $("#f-tema");
  const escuro = () => (raiz.dataset.theme ? raiz.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches);
  const rotular = () => {
    const txt = escuro() ? "Mudar para modo claro" : "Mudar para modo escuro";
    botao.setAttribute("aria-label", txt); botao.title = txt;
  };
  rotular();
  const mudar = () => { versaoTema++; aplicarTema(); atualizar({ recriar: true }); rotular(); };
  botao.addEventListener("click", () => {
    raiz.dataset.theme = escuro() ? "light" : "dark";
    try { localStorage.setItem("tema", raiz.dataset.theme); } catch { /* ignora */ }
    mudar();
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (!raiz.dataset.theme) mudar(); });
}

/* ====================== Arranque ====================== */

async function iniciar() {
  document.documentElement.classList.add("js");
  let info;
  try {
    info = await Dados.carregar();
  } catch (erro) {
    console.error(erro);
    const caixa = $("#conteudo .dentro");
    caixa.innerHTML = `<div class="erro-carregar" role="alert"><h2>Não foi possível carregar os dados</h2><p></p>
      <p>Se abriu o ficheiro diretamente a partir do disco, utilize um servidor local (extensão Live Server do VS Code ou <code>python -m http.server</code>).</p></div>`;
    $(".erro-carregar p", caixa).textContent = erro.message;
    return;
  }

  const e = Dados.epocas();
  PADRAO = {
    inicio: e[0], fim: e[e.length - 1],
    epoca: [...e].reverse().find(x => Dados.kpi(x)?.resultado_liquido != null),
  };
  lerURL();
  const nProjeto = info.consultas.filter(c => c.n < 100).length, nComp = info.consultas.length - nProjeto;
  const preencher = (sel, txt) => document.querySelectorAll(sel).forEach(el => (el.textContent = txt));
  preencher("[data-n-consultas]", nProjeto);
  preencher("[data-n-complementares]", nComp);
  preencher("[data-n-total-painel]", nProjeto + nComp);
  preencher("[data-n-epocas]", e.length);
  if (info.totalProjeto) { preencher("[data-n-total]", info.totalProjeto); preencher("[data-n-excluidas]", info.totalProjeto - nProjeto); }
  preencher("[data-intervalo]", `${e[0]} – ${e[e.length - 1]}`);
  const gerado = new Date(`${info.gerado}T12:00:00`);
  if (!Number.isNaN(gerado.getTime())) {
    preencher("[data-gerado]", gerado.toLocaleDateString("pt-PT", { day: "numeric", month: "long", year: "numeric" }));
    document.querySelectorAll("[data-frase-gerado]").forEach(el => (el.hidden = false));
    preencher("[data-ano]", gerado.getFullYear());
  }
  const nota = $("#nota-ambito-sql");
  nota.textContent = `O projeto SQL tem ${info.totalProjeto ?? nProjeto} consultas, numeradas de 1 a ${info.totalProjeto ?? nProjeto}. Aqui apresentam-se as ${nProjeto} que tratam das contas da SAD, com a numeração original, e ${nComp} consultas complementares do painel (D1 a D${nComp}), escritas para este painel sobre a mesma base de dados.` +
    (info.excluidas.length ? ` Os números em falta (${info.excluidas.slice(0, -1).join(", ")} e ${info.excluidas.at(-1)}) correspondem a consultas sobre o Clube ou o Grupo consolidado, que podem ser consultadas no ficheiro 04_analises.sql do projeto.` : "");

  construirSeccoes();
  construirKPIs();
  construirPesquisa();
  construirCartoesGeral();
  construirMetodologia();
  construirFiltros();
  explorador = montarExplorador($("[data-explorador]"), { aoSelecionar: n => navegar(`sql/${n}`) });
  prepararTema();
  await document.fonts.ready;
  aplicarTema();
  definirDestaque(estado.epoca);
  sincronizarFiltros();
  escreverURL();
  window.addEventListener("hashchange", mostrarSeccao);
  // As ligações internas (#secção) trocam o endereço sem criar entradas no histórico:
  // o botão «Voltar» do browser regressa à página anterior, e não à secção anterior do painel.
  document.addEventListener("click", ev => {
    const a = ev.target.closest('a[href^="#"]');
    if (!a || ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    const destino = a.getAttribute("href").slice(1);
    ev.preventDefault();
    if (destino === "conteudo") { $("#conteudo").focus(); $("#conteudo").scrollIntoView(); return; } // «Saltar para o conteúdo»
    navegar(destino);
  });
  mostrarSeccao();
}

iniciar();
