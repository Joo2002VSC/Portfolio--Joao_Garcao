// Dashboard Vitória SC · aplicação
// Estado dos filtros, navegação entre secções, indicadores do topo e desenho dos painéis.

import * as Dados from "./dados.js";
import { euros, variacaoEuros, inteiro, formatar } from "./formato.js";
import { aplicarTema, desenhar, definirDestaque } from "./graficos.js";
import { SECCOES, PAINEIS, PERGUNTAS } from "./paineis.js";
import { tabelaOrdenavel } from "./tabelas.js";
import { montarExplorador } from "./explorador.js";
import { contar, observar, reduzido } from "./animacoes.js";

/* ====================== Estado ====================== */

const ENTIDADES = [
  { id: "SAD", nome: "SAD" },
  { id: "CLUBE", nome: "Clube" },
  { id: "CONSOLIDADO", nome: "Grupo consolidado" },
];

const estado = { seccao: "geral", entidade: "SAD", inicio: null, fim: null, epoca: null };
let PADRAO = null;           // estado inicial, para o botão "Repor filtros"
const figuras = new Map();   // id do painel → { el, grafico, visto, vista, tema }
let versaoTema = 0;
const valoresKPI = {};
let explorador = null;

const $ = (s, el = document) => el.querySelector(s);

function epocasVisiveis() {
  const e = Dados.epocas(), i = e.indexOf(estado.inicio), f = e.indexOf(estado.fim);
  return e.slice(Math.min(i, f), Math.max(i, f) + 1);
}

/* ---------- Estado no endereço (permite partilhar uma vista) ---------- */

function lerURL() {
  const p = new URLSearchParams(location.search), e = Dados.epocas();
  const valida = v => (e.includes(v) ? v : null);
  estado.inicio = valida(p.get("de")) ?? PADRAO.inicio;
  estado.fim = valida(p.get("ate")) ?? PADRAO.fim;
  estado.epoca = valida(p.get("epoca")) ?? PADRAO.epoca;
  estado.entidade = ENTIDADES.some(x => x.id === p.get("entidade")) ? p.get("entidade") : PADRAO.entidade;
}

function escreverURL() {
  const p = new URLSearchParams();
  ["inicio", "fim", "epoca", "entidade"].forEach(k => {
    if (estado[k] !== PADRAO[k]) p.set({ inicio: "de", fim: "ate", epoca: "epoca", entidade: "entidade" }[k], estado[k]);
  });
  const q = p.toString();
  history.replaceState(null, "", `${location.pathname}${q ? `?${q}` : ""}${location.hash}`);
  $("#f-repor").disabled = !q;
}

/* ====================== Construção das secções ====================== */

const EMBLEMA = `<img src="img/emblema.png" alt="" width="26" height="38">`;

function criarFigura(p) {
  const fig = document.createElement("figure");
  fig.className = "painel" + (p.largo ? " largo" : "");
  fig.id = `p-${p.id}`;
  fig.innerHTML = `
    <header class="faixa"><h3 id="t-${p.id}"></h3>${EMBLEMA}</header>
    <div class="corpo">
      <div class="cabeca">
        <p class="descricao"></p>
        ${p.tabela || p.factos || p.matriz ? "" : `<button type="button" class="ver-tabela" aria-pressed="false" aria-controls="v-${p.id}">Ver tabela</button>`}
      </div>
      <p class="conclusao"></p>
      <div class="vista" id="v-${p.id}"></div>
      <figcaption class="fonte">Fonte: <a href="#sql/${p.consulta}">consulta ${p.consulta}</a>${p.nota ? ` · <span></span>` : ""}</figcaption>
    </div>`;
  $("h3", fig).textContent = p.pergunta;
  $(".descricao", fig).textContent = p.descricao;
  if (p.nota) $(".fonte span", fig).textContent = p.nota;
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

function construirSeccoes() {
  const main = $("#conteudo");
  const nav = $("#abas");
  SECCOES.forEach(s => {
    const a = document.createElement("a");
    a.href = `#${s.id}`; a.textContent = s.nome; a.dataset.seccao = s.id;
    nav.appendChild(a);

    let sec = $(`#sec-${s.id}`);
    if (!sec) {
      sec = document.createElement("section");
      sec.id = `sec-${s.id}`;
      main.appendChild(sec);
    }
    sec.classList.add("seccao");
    sec.setAttribute("aria-labelledby", `h-${s.id}`);
    sec.hidden = true;
    const cab = document.createElement("header");
    cab.className = "seccao-cabeca";
    cab.innerHTML = `<h2 class="faixa-titulo" id="h-${s.id}"></h2><p></p>`;
    $("h2", cab).textContent = s.nome;
    $("p", cab).textContent = s.intro;
    sec.prepend(cab);

    const paineis = PAINEIS.filter(p => p.seccao === s.id);
    if (paineis.length) {
      const grelha = document.createElement("div");
      grelha.className = "grelha";
      paineis.forEach(p => grelha.appendChild(criarFigura(p)));
      sec.appendChild(grelha);
    }
  });
}

/* ====================== Desenho de um painel ====================== */

function dadosDoPainel(p) {
  let todas = Dados.linhas(p.consulta);
  if (p.filtrar) todas = p.filtrar(todas);
  const rows = p.temporal ? Dados.noIntervalo(todas, epocasVisiveis()) : todas;
  return { rows, todas: Dados.linhas(p.consulta) };
}

function desenharFigura(reg, { recriar = false } = {}) {
  const { p, el } = reg;
  const vista = $(".vista", el);
  const { rows, todas } = dadosDoPainel(p);
  const conclusao = $(".conclusao", el);

  if (!rows.length) {
    reg.grafico?.destroy(); reg.grafico = null;
    vista.replaceChildren(Object.assign(document.createElement("p"), { className: "sem-dados", textContent: "Sem dados neste intervalo de épocas." }));
    conclusao.textContent = "";
    $(".ver-tabela", el)?.setAttribute("hidden", "");
    return;
  }
  $(".ver-tabela", el)?.removeAttribute("hidden");

  try { conclusao.textContent = p.conclusao ? p.conclusao(rows, todas) : ""; }
  catch (e) { conclusao.textContent = ""; console.warn(`Conclusão de ${p.id}:`, e); }

  const temaMudou = reg.tema !== versaoTema;
  reg.tema = versaoTema;

  // Factos (números-chave), matriz de cenários ou tabela
  if (p.factos) { vista.replaceChildren(criarFactos(p.factos(rows))); return; }
  if (p.matriz) { vista.replaceChildren(criarMatriz(p.matriz(rows))); return; }
  if (p.tabela || reg.vista === "tabela") {
    reg.grafico?.destroy(); reg.grafico = null;
    const c = Dados.consulta(p.consulta);
    const idx = new Set(rows.map(r => JSON.stringify(r)));
    const brutas = c.linhas.filter(l => idx.has(JSON.stringify(Object.fromEntries(c.colunas.map((k, i) => [k, l[i]])))));
    vista.replaceChildren(tabelaOrdenavel(c.colunas, brutas, p.consulta, { legenda: p.pergunta }));
    return;
  }

  // Gráfico
  let config;
  try { config = p.construir(rows, todas, { epoca: estado.epoca }); }
  catch (e) { console.error(`Gráfico ${p.id}:`, e); vista.textContent = "Não foi possível desenhar este gráfico."; return; }

  let canvas = $("canvas", vista);
  if (!canvas || recriar || temaMudou) {
    reg.grafico?.destroy(); reg.grafico = null;
    const tela = document.createElement("div");
    tela.className = "tela";
    canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    tela.appendChild(canvas);
    vista.replaceChildren(tela);
  }
  canvas.setAttribute("aria-label", `${p.pergunta} ${conclusao.textContent} A tabela com os valores está disponível no botão Ver tabela.`);
  reg.grafico = desenhar(canvas, config, reg.grafico);
}

function criarFactos(lista) {
  const ul = document.createElement("ul");
  ul.className = "factos";
  lista.forEach(f => {
    const li = document.createElement("li");
    if (f.forte) li.className = "forte";
    li.innerHTML = `<span class="valor"></span><span class="rotulo"></span>`;
    $(".valor", li).textContent = f.valor;
    $(".rotulo", li).textContent = f.rotulo;
    ul.appendChild(li);
  });
  return ul;
}

/** Matriz de cenários com sombreado sequencial (um só tom, do claro ao escuro) */
function criarMatriz(m) {
  const env = document.createElement("div");
  env.className = "tabela matriz";
  env.tabIndex = 0;
  const t = document.createElement("table");
  const valores = m.linhas.flatMap(l => m.colunas.map(c => m.celula(l, c)).filter(Boolean).map(m.valor));
  const max = Math.max(...valores, 1);
  const cab = t.createTHead().insertRow();
  [m.rotuloLinhas, ...m.colunas.map(c => `${c} lugar`)].forEach((txt, i) => {
    const th = document.createElement("th"); th.scope = "col"; th.textContent = txt; if (i) th.className = "num"; cab.appendChild(th);
  });
  const corpo = t.createTBody();
  m.linhas.forEach(l => {
    const tr = corpo.insertRow();
    const th = document.createElement("th"); th.scope = "row"; th.textContent = l; tr.appendChild(th);
    m.colunas.forEach(c => {
      const r = m.celula(l, c), td = tr.insertCell();
      td.className = "num";
      if (!r) { td.textContent = "—"; return; }
      const f = m.valor(r) / max;
      td.style.setProperty("--intensidade", f.toFixed(3));
      td.classList.toggle("escura", f > 0.62);
      td.innerHTML = `<strong></strong><small></small>`;
      $("strong", td).textContent = m.texto(r);
      $("small", td).textContent = m.detalhe(r);
    });
  });
  env.appendChild(t);
  return env;
}

/* ====================== Visão geral: indicadores e perguntas ====================== */

const INDICADORES = [
  { id: "receitas", nome: "Vendas e serviços", valor: k => k?.vendas_servicos, bom: "sobe" },
  { id: "pessoal", nome: "Gastos com pessoal", valor: k => k?.gastos_pessoal, bom: "desce" },
  { id: "maisvalias", nome: "Mais-valias com jogadores", valor: k => k?.mais_valias_liquidas, bom: "sobe" },
  { id: "rl", nome: "Resultado líquido", valor: k => k?.resultado_liquido, bom: "sobe" },
  { id: "rlsem", nome: "Resultado sem mais-valias", valor: k => k?.rl_sem_mais_valias, bom: "sobe" },
  { id: "capital", nome: "Capital próprio (30/06)", valor: k => k?.capital_proprio, bom: "sobe" },
  { id: "divida", nome: "Dívida financeira (30/06)", so: "SAD", consulta: 27, coluna: "financiamentos", bom: "desce" },
  { id: "funcionarios", nome: "Funcionários (média)", so: "SAD", consulta: 31, coluna: "funcionarios", bom: null, unidade: "int" },
];

function valorIndicador(ind, epoca) {
  if (!epoca) return null;
  if (ind.consulta) {
    if (estado.entidade !== ind.so) return null;
    return Dados.linhas(ind.consulta).find(r => r.epoca === epoca)?.[ind.coluna] ?? null;
  }
  return ind.valor(Dados.kpi(estado.entidade, epoca)) ?? null;
}

function construirKPIs() {
  const caixa = $("#kpis");
  INDICADORES.forEach((ind, i) => {
    const d = document.createElement("div");
    d.className = "kpi"; d.style.setProperty("--i", i); d.dataset.id = ind.id;
    d.innerHTML = `<p class="nome"></p><p class="valor"></p><p class="delta"></p>`;
    $(".nome", d).textContent = ind.nome;
    caixa.appendChild(d);
  });

  const seg = $("#f-entidade");
  ENTIDADES.forEach(e => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = e.nome; b.dataset.id = e.id; b.setAttribute("role", "radio");
    b.addEventListener("click", () => { estado.entidade = e.id; atualizar(); });
    seg.appendChild(b);
  });
  seg.addEventListener("keydown", e => {
    if (!["ArrowLeft", "ArrowRight"].includes(e.key)) return;
    const i = ENTIDADES.findIndex(x => x.id === estado.entidade);
    const n = ENTIDADES[(i + (e.key === "ArrowRight" ? 1 : ENTIDADES.length - 1)) % ENTIDADES.length];
    estado.entidade = n.id; atualizar();
    seg.querySelector(`[data-id="${n.id}"]`).focus();
  });
}

function desenharKPIs() {
  const e = Dados.epocas(), epoca = estado.epoca, anterior = e[e.indexOf(epoca) - 1];
  $("#kpi-entidade").textContent = ENTIDADES.find(x => x.id === estado.entidade).nome;
  $("#kpi-epoca").textContent = epoca;
  $("#f-entidade").querySelectorAll("button").forEach(b => {
    const ativo = b.dataset.id === estado.entidade;
    b.setAttribute("aria-checked", String(ativo));
    b.tabIndex = ativo ? 0 : -1;
  });

  INDICADORES.forEach(ind => {
    const d = $(`.kpi[data-id="${ind.id}"]`);
    const v = valorIndicador(ind, epoca), a = valorIndicador(ind, anterior);
    const fmt = x => formatar(ind.unidade ?? "eur", x);
    const elV = $(".valor", d), delta = $(".delta", d);
    d.classList.toggle("vazio", v === null);
    d.classList.toggle("negativo", typeof v === "number" && v < 0 && (ind.unidade ?? "eur") === "eur");
    if (v === null) elV.textContent = ind.so && estado.entidade !== ind.so ? `só ${ind.so}` : "sem dados";
    else contar(elV, valoresKPI[ind.id], v, fmt);
    valoresKPI[ind.id] = v;

    delta.textContent = "";
    if (v !== null && a !== null && v !== a) {
      const dif = v - a;
      const s = document.createElement("span");
      if (ind.bom) s.className = (dif > 0) === (ind.bom === "sobe") ? "melhor" : "pior";
      s.textContent = `${dif > 0 ? "▲" : "▼"} ${ind.unidade === "int" ? (dif > 0 ? "+" : "−") + inteiro(Math.abs(dif)) : variacaoEuros(dif)}`;
      delta.append(s, ` face a ${anterior}`);
      if (ind.bom) {
        const sr = document.createElement("span");
        sr.className = "sr-only";
        sr.textContent = s.className === "melhor" ? " (melhoria)" : " (agravamento)";
        delta.appendChild(sr);
      }
    } else if (v !== null) {
      delta.textContent = a === null ? "sem época anterior comparável" : `igual a ${anterior}`;
    }
  });

  const d = Dados.desporto(epoca);
  const partes = d ? [`${d.posicao_liga}.º lugar na Liga, ${d.pontos} pontos`,
    d.competicao_europeia && `${d.competicao_europeia} (${(d.fase_europeia ?? "").toLowerCase()})`,
    d.trofeu && `vencedor da ${d.trofeu}`].filter(Boolean) : [];
  const campo = $("#em-campo");
  campo.textContent = partes.length ? `Em campo: ${partes.join(" · ")}.` : "";
  campo.hidden = !partes.length;
}

function construirPerguntas() {
  const ol = $("#perguntas");
  const q = n => Dados.linhas(n);
  PERGUNTAS.forEach(p => {
    const li = document.createElement("li");
    li.innerHTML = `<p class="p"></p><p class="r"></p><p class="fonte"></p>`;
    $(".p", li).textContent = p.pergunta;
    try { $(".r", li).textContent = p.resposta({ q }); }
    catch (e) { $(".r", li).textContent = "Resposta indisponível."; console.warn(e); }
    $(".fonte", li).innerHTML = "Fonte: " + p.consultas.map(n => `<a href="#sql/${n}">consulta ${n}</a>`).join(", ");
    ol.appendChild(li);
  });
}

/* ====================== Filtros ====================== */

function construirFiltros() {
  const e = Dados.epocas();
  [["f-inicio", "inicio"], ["f-fim", "fim"], ["f-epoca", "epoca"]].forEach(([id, chave]) => {
    const s = $(`#${id}`);
    e.forEach(x => s.add(new Option(x, x)));
    s.addEventListener("change", () => {
      estado[chave] = s.value;
      if (e.indexOf(estado.inicio) > e.indexOf(estado.fim)) [estado.inicio, estado.fim] = [estado.fim, estado.inicio];
      atualizar({ recriar: chave !== "epoca" });
    });
  });
  $("#f-repor").addEventListener("click", () => { Object.assign(estado, { ...PADRAO, seccao: estado.seccao }); atualizar({ recriar: true }); });
}

function sincronizarFiltros() {
  $("#f-inicio").value = estado.inicio;
  $("#f-fim").value = estado.fim;
  $("#f-epoca").value = estado.epoca;
  const n = epocasVisiveis().length;
  $("#f-resumo").textContent = `${n} ${n === 1 ? "época" : "épocas"}`;
}

/** Aplica o estado: filtros, indicadores e painéis já desenhados da secção visível */
function atualizar({ recriar = false } = {}) {
  definirDestaque(estado.epoca);
  sincronizarFiltros();
  escreverURL();
  if (estado.seccao === "geral") desenharKPIs();
  figuras.forEach(reg => {
    if (reg.visto && !reg.el.closest(".seccao").hidden) desenharFigura(reg, { recriar });
  });
}

/* ====================== Navegação ====================== */

function mostrarSeccao() {
  const [id, alvo] = decodeURIComponent(location.hash.slice(1)).split("/");
  const seccao = SECCOES.some(s => s.id === id) ? id : "geral";
  const mudou = seccao !== estado.seccao;
  estado.seccao = seccao;
  document.querySelectorAll(".seccao").forEach(s => (s.hidden = s.id !== `sec-${seccao}`));
  document.querySelectorAll("#abas a").forEach(a => {
    if (a.dataset.seccao === seccao) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  document.title = `${SECCOES.find(s => s.id === seccao).nome} · Dashboard Vitória SC`;
  // Em ecrãs estreitos, mantém a aba ativa visível sem mexer no foco nem na página
  const aba = $("#abas a[aria-current]"), abas = $("#abas");
  if (aba && (aba.offsetLeft < abas.scrollLeft || aba.offsetLeft + aba.offsetWidth > abas.scrollLeft + abas.clientWidth)) {
    abas.scrollLeft = aba.offsetLeft - 16;
  }

  if (seccao === "geral") desenharKPIs();
  if (seccao === "sql") {
    const n = Number(alvo) || Number($("#sec-sql [data-explorador]").dataset.ativa) || 1;
    explorador.mostrar(n);
    // Em ecrãs estreitos a lista fica por cima: leva o leitor ao resultado escolhido
    if (alvo && innerWidth < 980) $("[data-detalhe]").scrollIntoView({ behavior: reduzido ? "auto" : "smooth", block: "start" });
  }

  // Painéis desta secção: desenha os já vistos; os outros quando entrarem no ecrã
  const daSeccao = [...figuras.values()].filter(r => r.p.seccao === seccao);
  daSeccao.filter(r => r.visto).forEach(r => desenharFigura(r, { recriar: true }));
  observar(daSeccao.filter(r => !r.visto).map(r => r.el), el => {
    const reg = [...figuras.values()].find(r => r.el === el);
    reg.visto = true;
    el.classList.add("visivel");
    desenharFigura(reg, { recriar: true });
  });

  if (alvo && seccao !== "sql") {
    const fig = $(`#p-${alvo}`);
    if (fig) requestAnimationFrame(() => { fig.scrollIntoView({ behavior: reduzido ? "auto" : "smooth", block: "start" }); fig.focus({ preventScroll: true }); });
  } else if (mudou) {
    window.scrollTo({ top: 0 });
  }
}

/* ---------- Tema claro/escuro ---------- */

function prepararTema() {
  const raiz = document.documentElement;
  try { const t = localStorage.getItem("tema"); if (t) raiz.dataset.theme = t; } catch { /* sem armazenamento */ }
  const botao = $("#f-tema");
  const rotular = () => {
    const escuro = raiz.dataset.theme ? raiz.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    botao.setAttribute("aria-label", escuro ? "Mudar para modo claro" : "Mudar para modo escuro");
    botao.title = botao.getAttribute("aria-label");
    return escuro;
  };
  rotular();
  const mudar = () => { versaoTema++; aplicarTema(); atualizar({ recriar: true }); rotular(); };
  botao.addEventListener("click", () => {
    raiz.dataset.theme = rotular() ? "light" : "dark";
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
    $("#conteudo").innerHTML = `<div class="erro-carregar" role="alert"><h2>Não foi possível carregar os dados</h2><p></p>
      <p>Abre a página através de um servidor (extensão Live Server do VS Code ou <code>python -m http.server</code>), não diretamente do disco.</p></div>`;
    $("#conteudo .erro-carregar p").textContent = erro.message;
    return;
  }

  const e = Dados.epocas();
  PADRAO = {
    entidade: "SAD", inicio: e[0], fim: e[e.length - 1],
    epoca: [...e].reverse().find(x => Dados.kpi("SAD", x)?.resultado_liquido != null),
  };
  lerURL();
  $("#intervalo-total").textContent = `${e[0]} – ${e[e.length - 1]}`;
  $("#n-consultas").textContent = info.consultas.length;
  $("#gerado").textContent = new Date(info.gerado).toLocaleDateString("pt-PT", { day: "numeric", month: "long", year: "numeric" });

  construirSeccoes();
  construirKPIs();
  construirPerguntas();
  construirFiltros();
  explorador = montarExplorador($("#sec-sql [data-explorador]"), { aoSelecionar: n => { location.hash = `sql/${n}`; } });
  prepararTema();
  await document.fonts.ready;
  aplicarTema();
  definirDestaque(estado.epoca);
  sincronizarFiltros();
  escreverURL();
  window.addEventListener("hashchange", mostrarSeccao);
  estado.seccao = null;
  mostrarSeccao();
}

iniciar();
