// Dashboard Vitória SC · aplicação
// Estado dos filtros, navegação, visão geral (quatro dimensões), secções e painéis.

import * as Dados from "./dados.js";
import { formatar, variacaoEuros, inteiro, pct, euros } from "./formato.js";
import { aplicarTema, desenhar, definirDestaque } from "./graficos.js";
import { SECCOES, PAINEIS, PERGUNTAS, ORDEM } from "./paineis.js";
import { tabelaOrdenavel } from "./tabelas.js";
import { montarExplorador } from "./explorador.js";
import { conclusoes } from "./conclusoes.js";
import { contar, observar, reduzido } from "./animacoes.js";

/* ====================== Estado ====================== */

// Descrições editoriais das entidades (a tabela "entidade" da base tem descrições abreviadas para uso interno)
const ENTIDADES = [
  { id: "SAD", nome: "SAD", longo: "Vitória Sport Clube – Futebol, SAD",
    desc: "Sociedade anónima desportiva que gere o futebol profissional: plantel, transferências, competições da UEFA e direitos de TV." },
  { id: "CLUBE", nome: "Clube", longo: "Vitória Sport Clube (associação desportiva)",
    desc: "Associação que detém a maioria do capital da SAD e é proprietária do Estádio D. Afonso Henriques e da Academia; gere as modalidades." },
  { id: "CONSOLIDADO", nome: "Grupo consolidado", longo: "Grupo Vitória Sport Clube (Clube e SAD)",
    desc: "Contas consolidadas do Clube e da SAD, com eliminação das operações intragrupo. Não correspondem à soma simples das duas entidades." },
];

const estado = { seccao: null, entidade: "SAD", inicio: null, fim: null, epoca: null };
let PADRAO = null;
const figuras = new Map();
let versaoTema = 0;
const valoresKPI = {};
let explorador = null;

const $ = (s, el = document) => el.querySelector(s);
const criar = (tag, cls, texto) => { const e = document.createElement(tag); if (cls) e.className = cls; if (texto !== undefined) e.textContent = texto; return e; };
const nomeEntidade = id => ENTIDADES.find(e => e.id === id)?.nome ?? id;
const codigoConsulta = n => { try { return Dados.consulta(n).codigo ?? String(n); } catch { return String(n); } };
const ligacaoConsulta = n => `<a href="#sql/${n}">${n > 100 ? "consulta complementar" : "consulta"} ${codigoConsulta(n)}</a>`;

function epocasVisiveis() {
  const e = Dados.epocas(), i = e.indexOf(estado.inicio), f = e.indexOf(estado.fim);
  return e.slice(Math.min(i, f), Math.max(i, f) + 1);
}

/* ---------- Estado no endereço (permite partilhar uma vista filtrada) ---------- */

const PARAMS = { inicio: "de", fim: "ate", epoca: "epoca", entidade: "entidade" };

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

function criarFigura(p) {
  const fig = criar("figure", "painel" + (p.largo ? " largo" : ""));
  fig.id = `p-${p.id}`;
  fig.tabIndex = -1;
  fig.setAttribute("aria-labelledby", `t-${p.id}`);
  fig.innerHTML = `
    <div class="painel-cabeca">
      <h4 id="t-${p.id}"></h4>
      ${p.tabela || p.factos || p.matriz ? "" : `<button type="button" class="ver-tabela" aria-pressed="false" aria-controls="v-${p.id}">Ver tabela</button>`}
    </div>
    <p class="descricao"></p>
    <p class="conclusao"></p>
    <div class="vista" id="v-${p.id}"></div>
    <figcaption class="fonte">Fonte: ${p.consulta ? ligacaoConsulta(p.consulta) : p.fonteTexto}${p.nota ? " · <span></span>" : ""}</figcaption>`;
  $("h4", fig).textContent = p.pergunta;
  $(".descricao", fig).textContent = p.descricao;
  if (p.nota) $(".fonte span", fig).textContent = p.nota;
  if (p.ficha) fig.insertBefore(criarFicha(p.ficha), $(".fonte", fig));
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
  const ctx = { epoca: estado.epoca, entidade: estado.entidade };
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
    vista.replaceChildren(criar("p", "sem-dados", "Sem dados para esta entidade ou neste intervalo de épocas."));
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

const GRUPOS_RACIOS = {
  contabilistico: ["Resultados contabilísticos", "O que as contas registam em cada exercício: lucro ou prejuízo, e a respetiva origem."],
  sustentabilidade: ["Sustentabilidade financeira", "A solidez da estrutura financeira: capital próprio, endividamento e capacidade de cumprir os compromissos."],
};

function construirSeccoes() {
  const main = $("#conteudo .dentro");
  const nav = $("#abas");
  SECCOES.forEach(s => {
    const a = criar("a", "", s.nome);
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

    const paineis = PAINEIS.filter(p => p.seccao === s.id);
    if (ORDEM[s.id]) paineis.sort((x, y) => ORDEM[s.id].indexOf(x.id) - ORDEM[s.id].indexOf(y.id));
    if (s.id === "perguntas") { construirPerguntas(sec); return; }
    if (s.id === "racios") {
      Object.entries(GRUPOS_RACIOS).forEach(([g, [titulo, texto]]) => {
        const h = criar("div", "grupo-cabeca");
        h.append(criar("h3", "", titulo), criar("p", "", texto));
        sec.append(h, grelhaDe(paineis.filter(p => p.grupo === g)));
      });
      return;
    }
    if (paineis.length) ($("[data-paineis]", sec) ?? sec).appendChild(grelhaDe(paineis));
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
      <p class="resposta"></p><div class="indicadores"></div><div class="graficos"></div>
      <p class="limitacoes"><strong>Limitações.</strong> <span></span></p>
      <p class="fonte">Consultas: ${per.consultas.map(ligacaoConsulta).join(", ")}</p>`;
    $("h3", art).textContent = per.pergunta;
    try {
      $(".resposta", art).textContent = per.resposta({ q });
      $(".indicadores", art).appendChild(criarFactos(per.indicadores({ q })));
    } catch (e) { $(".resposta", art).textContent = "Resposta indisponível."; console.warn(e); }
    $(".limitacoes span", art).textContent = per.limitacoes;
    $(".graficos", art).appendChild(grelhaDe(PAINEIS.filter(p => p.seccao === "perguntas" && p.questao === per.n)));
    sec.appendChild(art);
  });
}

function construirEntidades() {
  const caixa = $("#entidades-descricao");
  const cob = Dados.linhas(17);
  ENTIDADES.forEach(e => {
    const c = cob.find(x => x.entidade === e.id);
    const div = criar("div", "entidade-ficha");
    div.append(criar("h3", "", e.nome), criar("p", "nome-longo", e.longo), criar("p", "", e.desc));
    if (c) div.appendChild(criar("p", "cobertura", `${c.epocas_com_dados} épocas com demonstração de resultados · em média, ${String(c.rubricas_por_epoca).replace(".", ",")} rubricas por época`));
    caixa.appendChild(div);
  });
}

function construirMetodologia() {
  const fontes = Dados.base().fontes;
  $("#tabela-fontes").appendChild(tabelaOrdenavel(["entidade", "epoca", "estado", "documentos"],
    fontes.map(f => [nomeEntidade(f.entidade), f.epoca, f.estado, f.documentos]), null, { legenda: "Fontes por entidade e época" }));
  const div = Dados.consulta(35);
  $("#tabela-divergencias").appendChild(tabelaOrdenavel(div.colunas, div.linhas, 35, { legenda: "Divergências face aos Relatórios e Contas" }));
  $("#n-divergencias").textContent = inteiro(Dados.linhas(35).reduce((s, r) => s + r.divergencias, 0));
}

/* ====================== Visão geral ====================== */

const serieKPI = campo => (ent, ep) => Dados.kpi(ent, ep)?.[campo] ?? null;
const serieDR = campo => (ent, ep) => Dados.base().dr.find(r => r.entidade === ent && r.epoca === ep)?.[campo] ?? null;

const DIMENSAO_A = [
  { id: "ativo", nome: "Ativo total", valor: serieKPI("ativo_total"), bom: 1 },
  { id: "passivo", nome: "Passivo total", valor: serieKPI("passivo_total"), bom: -1 },
  { id: "capital", nome: "Capital próprio", valor: serieKPI("capital_proprio"), bom: 1 },
  { id: "rl", nome: "Resultado líquido", valor: serieKPI("resultado_liquido"), bom: 1 },
];
const DIMENSAO_B = [
  { id: "vendas", nome: "Vendas e serviços prestados", valor: serieKPI("vendas_servicos"), bom: 1 },
  {
    id: "rendimentos", nome: "Rendimentos operacionais", bom: 1,
    // SAD: soma das rubricas (consulta complementar D3); restantes: rubrica agregada da DR
    valor: (ent, ep) => (ent === "SAD" ? Dados.linhas(103).find(r => r.epoca === ep)?.rendimentos_operacionais ?? null : serieDR("rendimentos_operacionais")(ent, ep)),
  },
  { id: "pessoal", nome: "Gastos com pessoal", valor: serieKPI("gastos_pessoal"), bom: -1 },
  { id: "ro", nome: "Resultado operacional", valor: serieDR("resultado_operacional"), bom: 1 },
  { id: "maisvalias", nome: "Mais-valias com jogadores", valor: serieKPI("mais_valias_liquidas"), bom: 1 },
  { id: "pessoalpct", nome: "Gastos com pessoal / vendas", valor: serieKPI("pct_pessoal_receitas"), bom: -1, unidade: "pct" },
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
  const ponto = p !== null && p !== undefined ? `<circle cx="${x(destaque).toFixed(1)}" cy="${y(p).toFixed(1)}" r="2.6"/>` : "";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "-3 -2 106 31");
  svg.setAttribute("preserveAspectRatio", "none");
  svg.setAttribute("aria-hidden", "true");
  svg.classList.add("sparkline");
  svg.innerHTML = `${zero}<path d="${d}"/>${ponto}`;
  return svg;
}

function construirKPIs(caixa, defs) {
  defs.forEach((ind, i) => {
    const d = criar("div", "kpi");
    d.style.setProperty("--i", i); d.dataset.id = ind.id;
    d.innerHTML = `<p class="nome"></p><p class="valor"></p><p class="delta"></p><div class="tendencia"></div>`;
    $(".nome", d).textContent = ind.nome;
    caixa.appendChild(d);
  });
}

function desenharKPIs(defs) {
  const e = Dados.epocas(), i = e.indexOf(estado.epoca), anterior = e[i - 1];
  defs.forEach(ind => {
    const d = $(`.kpi[data-id="${ind.id}"]`);
    const unidade = ind.unidade ?? "eur", fmt = x => formatar(unidade, x);
    const serie = e.map(ep => ind.valor(estado.entidade, ep));
    const v = serie[i], a = i > 0 ? serie[i - 1] : null;
    const elV = $(".valor", d), delta = $(".delta", d);
    d.classList.toggle("vazio", v === null);
    if (v === null) elV.textContent = "sem dados";
    else contar(elV, valoresKPI[ind.id], v, fmt);
    valoresKPI[ind.id] = v;

    delta.textContent = "";
    if (v !== null && a !== null && v !== a) {
      const dif = v - a, melhor = Math.sign(dif) === ind.bom;
      const txt = unidade === "pct" ? `${dif > 0 ? "+" : "−"}${pct(Math.abs(dif)).replace("%", " p.p.")}` : variacaoEuros(dif);
      delta.append(criar("span", melhor ? "melhor" : "pior", `${dif > 0 ? "▲" : "▼"} ${txt}`), ` face a ${anterior}`,
        criar("span", "sr-only", melhor ? " (melhoria)" : " (agravamento)"));
    } else if (v !== null) {
      delta.textContent = a === null ? (anterior ? `sem valor em ${anterior}` : "primeira época da série") : `igual a ${anterior}`;
    }

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
  const rows = Dados.linhas(104).filter(r => r.entidade === estado.entidade && r.epoca === estado.epoca && r.variacao !== null);
  // Ordena pela variação em euros: a percentual engana quando a base é pequena ou muda de sinal
  rows.sort((a, b) => Math.abs(b.variacao) - Math.abs(a.variacao));
  lista.replaceChildren(...(rows.length ? rows.slice(0, 5).map(r => {
    const li = criar("li");
    // A variação percentual só tem leitura direta quando os dois valores são positivos
    const mudouSinal = Math.sign(r.valor) !== Math.sign(r.anterior) && r.valor !== 0 && r.anterior !== 0;
    const ambosPositivos = r.valor > 0 && r.anterior > 0;
    const sinal = mudouSinal ? " (mudou de sinal)" : ambosPositivos && r.variacao_pct !== null ? ` (${r.variacao_pct > 0 ? "+" : "−"}${pct(Math.abs(r.variacao_pct))})` : "";
    li.append(criar("span", "ind", r.indicador), criar("span", "var", `${variacaoEuros(r.variacao)}${sinal}`),
      criar("span", "ref", `${euros(r.anterior)} em ${r.epoca_anterior} → ${euros(r.valor)}`));
    return li;
  }) : [criar("li", "vazio", "Sem época anterior comparável para esta entidade.")]));

  const ext = Dados.linhas(105).filter(r => r.entidade === estado.entidade && r.n_epocas > 2);
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
  const grupos = [["melhorias", "Melhorias", "Face à época anterior"], ["riscos", "Riscos", "Valores fora dos limiares de referência"],
    ["atencao", "Pontos de atenção", "Dependência das vendas e peso dos gastos"], ["estruturais", "Alterações estruturais", "Pessoal, dívida e contas"]];
  $("#conclusoes").replaceChildren(...grupos.map(([k, titulo, sub]) => {
    const div = criar("div", `concl concl-${k}`);
    div.append(criar("h4", "", titulo), criar("p", "sub", sub));
    const ul = criar("ul");
    if (!c[k].length) ul.appendChild(criar("li", "vazio", "Nada a assinalar nesta época."));
    c[k].forEach(item => {
      const li = criar("li");
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
  $("#conclusoes-nota").hidden = estado.entidade === "SAD";
}

function construirSeletorEntidade() {
  const seg = $("#f-entidade");
  ENTIDADES.forEach(e => {
    const b = criar("button", "", e.nome);
    b.type = "button"; b.dataset.id = e.id; b.setAttribute("role", "radio");
    b.addEventListener("click", () => { estado.entidade = e.id; atualizar(); });
    seg.appendChild(b);
  });
  seg.addEventListener("keydown", ev => {
    if (!["ArrowLeft", "ArrowRight"].includes(ev.key)) return;
    ev.preventDefault();
    const i = ENTIDADES.findIndex(x => x.id === estado.entidade);
    const n = ENTIDADES[(i + (ev.key === "ArrowRight" ? 1 : ENTIDADES.length - 1)) % ENTIDADES.length];
    estado.entidade = n.id; atualizar();
    seg.querySelector(`[data-id="${n.id}"]`).focus();
  });
}

function desenharGeral() {
  const ent = ENTIDADES.find(x => x.id === estado.entidade);
  document.querySelectorAll("[data-ref-epoca]").forEach(el => (el.textContent = estado.epoca));
  // Data de fecho do exercício: a época 2025/26 termina a 30 de junho de 2026
  document.querySelectorAll("[data-ref-fecho]").forEach(el => (el.textContent = `30 de junho de 20${estado.epoca.slice(-2)}`));
  $("#entidade-nome").textContent = ent.longo;
  $("#entidade-desc").textContent = ent.desc;
  $("#f-entidade").querySelectorAll("button").forEach(b => {
    const ativo = b.dataset.id === estado.entidade;
    b.setAttribute("aria-checked", String(ativo));
    b.tabIndex = ativo ? 0 : -1;
  });
  desenharKPIs(DIMENSAO_A);
  desenharKPIs(DIMENSAO_B);
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
  $("#f-resumo").textContent = `${n} ${n === 1 ? "época" : "épocas"} no intervalo`;
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
  document.title = `${SECCOES.find(s => s.id === seccao).nome} · As contas do Vitória SC`;
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
    entidade: "SAD", inicio: e[0], fim: e[e.length - 1],
    epoca: [...e].reverse().find(x => Dados.kpi("SAD", x)?.resultado_liquido != null),
  };
  lerURL();
  const nProjeto = info.consultas.filter(c => c.n < 100).length;
  document.querySelectorAll("[data-n-consultas]").forEach(el => (el.textContent = nProjeto));
  document.querySelectorAll("[data-intervalo]").forEach(el => (el.textContent = `${e[0]} – ${e[e.length - 1]}`));
  $("#gerado").textContent = new Date(info.gerado).toLocaleDateString("pt-PT", { day: "numeric", month: "long", year: "numeric" });

  construirSeccoes();
  construirSeletorEntidade();
  construirKPIs($("#kpis-a"), DIMENSAO_A);
  construirKPIs($("#kpis-b"), DIMENSAO_B);
  construirEntidades();
  construirMetodologia();
  construirFiltros();
  explorador = montarExplorador($("[data-explorador]"), { aoSelecionar: n => { location.hash = `sql/${n}`; } });
  prepararTema();
  await document.fonts.ready;
  aplicarTema();
  definirDestaque(estado.epoca);
  sincronizarFiltros();
  escreverURL();
  window.addEventListener("hashchange", mostrarSeccao);
  mostrarSeccao();
}

iniciar();
