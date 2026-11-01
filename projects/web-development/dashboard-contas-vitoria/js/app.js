// Dashboard Vitória SC · lógica do painel
// 1. carrega data/contas.json (gerado por scripts/exportar_json.py)
// 2. guarda o estado dos filtros
// 3. desenha indicadores e gráficos; quando um filtro muda, atualiza-os com transição

/* ====================== Estado e dados ====================== */

// Ordem e cores das entidades como no gráfico 01 do projeto SQL: SAD a preto, Grupo a cinzento, Clube a amarelo
const ENTIDADES = [
  { id: "SAD", nome: "SAD", serie: "SAD", cor: "--tinta" },
  { id: "CONSOLIDADO", nome: "Consolidado", serie: "Grupo consolidado", cor: "--serie-cinza" },
  { id: "CLUBE", nome: "Clube", serie: "Clube", cor: "--amarelo" },
];
const ORDEM_FILTRO = ["SAD", "CLUBE", "CONSOLIDADO"];

const estado = { entidade: "SAD", inicio: null, fim: null, epoca: null };
const vistas = {};        // "grafico" ou "tabela", por cartão
const graficos = {};      // instâncias Chart.js, por cartão
const vistos = new Set(); // cartões que já entraram no ecrã (só esses são desenhados)
const valoresKPI = {};    // último valor mostrado em cada indicador (para a contagem)
let DADOS = null;

const kpi = (entidade, epoca) => DADOS.kpis.find(l => l.entidade === entidade && l.epoca === epoca);
const nomeEntidade = id => ENTIDADES.find(e => e.id === id).nome;

function epocasVisiveis() {
  const i = DADOS.epocas.indexOf(estado.inicio), f = DADOS.epocas.indexOf(estado.fim);
  return DADOS.epocas.slice(Math.min(i, f), Math.max(i, f) + 1);
}

/** Série de valores de um campo, alinhada com as épocas (null onde não há dados) */
function serie(entidade, campo, epocas = epocasVisiveis()) {
  return epocas.map(e => kpi(entidade, e)?.[campo] ?? null);
}

/* ====================== Cores (lidas do CSS, mudam com o tema) ====================== */

const cor = nome => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();

function aplicarTemaChart() {
  Chart.defaults.font.family = '"Archivo", system-ui, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.color = cor("--suave");
  Chart.defaults.borderColor = cor("--grelha");
}

/* ====================== Peças comuns ====================== */

function opcoesBase({ indice = true, legenda = true } = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: indice ? { mode: "index", intersect: false } : { mode: "nearest", intersect: true },
    layout: { padding: { top: 4, right: 6 } },
    plugins: {
      legend: {
        display: legenda, position: "top", align: "start",
        labels: { boxWidth: 22, boxHeight: 10, padding: 16, color: cor("--texto"), font: { size: 13 } },
      },
      // Caixa preta com título amarelo, nos dois temas
      tooltip: {
        backgroundColor: "#111111", titleColor: "#F5D510", bodyColor: "#FFFFFF", footerColor: "#C9C7C8",
        borderColor: "#F5D510", borderWidth: 1, padding: 11, cornerRadius: 2, boxPadding: 5,
        titleFont: { family: '"Archivo Expanded", sans-serif', weight: "800", size: 12 },
        footerFont: { weight: "400" },
        callbacks: { label: c => ` ${c.dataset.label}: ${Formato.euros(c.raw)}` },
        filter: c => c.raw !== null,
      },
    },
    scales: {
      x: { grid: { display: false }, border: { color: cor("--grelha") }, ticks: { maxRotation: 0, autoSkipPadding: 10, color: cor("--suave") } },
      y: {
        ticks: { callback: v => Formato.eixo(v), color: cor("--suave") },
        grid: { color: c => (c.tick.value === 0 ? cor("--tinta") : cor("--grelha")), lineWidth: c => (c.tick.value === 0 ? 1.4 : 1) },
        border: { display: false },
      },
    },
  };
}

const barra = (label, data, corVar) => ({
  label, data,
  backgroundColor: cor(corVar),
  // O amarelo leva contorno, como nos gráficos do projeto SQL
  borderColor: corVar === "--amarelo" ? cor("--tinta") : cor(corVar),
  borderWidth: corVar === "--amarelo" ? 1 : 0,
  borderRadius: 0, borderSkipped: false,
  maxBarThickness: 28, categoryPercentage: 0.8, barPercentage: 0.9,
});

/** Linha principal: preta, marcadores cheios. Secundária: cinzenta, marcadores ocos. */
const linha = (label, data, corVar, oca = false) => ({
  label, data, borderColor: cor(corVar), backgroundColor: oca ? cor("--cartao") : cor(corVar),
  borderWidth: 2.6, pointRadius: 4.5, pointHoverRadius: 7, pointBorderWidth: oca ? 2.4 : 0,
  pointBorderColor: cor(corVar), pointStyle: "circle", tension: 0, spanGaps: false,
});

/** Área amarela entre duas linhas, só onde a série de cima ultrapassa a de baixo */
const areaAcima = indiceAlvo => ({ target: indiceAlvo, above: cor("--area"), below: "rgba(0,0,0,0)" });

function tabelaSeries(labels, datasets) {
  return {
    colunas: ["Época", ...datasets.map(d => d.label)],
    linhas: labels.map((l, i) => [l, ...datasets.map(d => Formato.euros(d.data[i]))]),
  };
}

/* ====================== Definição de cada gráfico ====================== */
// Cada função devolve { tipo, config, tabela } ou { vazio: "mensagem" }.

const DEFINICOES = {
  resultado() {
    const epocas = epocasVisiveis();
    const datasets = ENTIDADES.map(e => barra(e.serie, serie(e.id, "resultado_liquido", epocas), e.cor));
    const opcoes = opcoesBase();
    return {
      tipo: "bar",
      config: { type: "bar", data: { labels: epocas, datasets }, options: opcoes, plugins: [rotulosBarras] },
      tabela: tabelaSeries(epocas, datasets),
    };
  },

  maisvalias() {
    const ent = estado.entidade, epocas = epocasVisiveis();
    const rl = serie(ent, "resultado_liquido", epocas), sem = serie(ent, "rl_sem_mais_valias", epocas);
    if (sem.every(v => v === null)) {
      return { vazio: `Não há dados de transferências para ${ent === "CLUBE" ? "o Clube" : nomeEntidade(ent)} neste intervalo. Escolhe a SAD ou o Consolidado.` };
    }
    const idx = epocas.map((_, i) => i).filter(i => sem[i] !== null);
    const labels = idx.map(i => epocas[i]);
    const datasets = [
      barra("Resultado líquido", idx.map(i => rl[i]), "--tinta"),
      barra("Sem mais-valias", idx.map(i => sem[i]), "--serie-cinza"),
    ];
    return { tipo: "bar", config: { type: "bar", data: { labels, datasets }, options: opcoesBase() }, tabela: tabelaSeries(labels, datasets) };
  },

  pessoal() {
    const ent = estado.entidade, epocas = epocasVisiveis();
    const receitas = serie(ent, "vendas_servicos", epocas), pessoal = serie(ent, "gastos_pessoal", epocas);
    if (receitas.every(v => v === null) && pessoal.every(v => v === null)) {
      return { vazio: `Sem dados de receitas e gastos com pessoal para ${nomeEntidade(ent)} neste intervalo.` };
    }
    const pct = serie(ent, "pct_pessoal_receitas", epocas);
    const opcoes = opcoesBase();
    opcoes.plugins.legend.labels.usePointStyle = true;
    opcoes.plugins.tooltip.callbacks.footer = itens => {
      const p = pct[itens[0].dataIndex];
      return p === null ? "" : `Pessoal = ${Formato.percentagem(p)} das receitas`;
    };
    opcoes.scales.y.beginAtZero = true;
    const datasets = [
      linha("Receitas (vendas e serviços)", receitas, "--tinta"),
      { ...linha("Gastos com pessoal", pessoal, "--serie-cinza-escuro", true), fill: areaAcima(0) },
    ];
    const tabela = tabelaSeries(epocas, datasets);
    tabela.colunas.push("Pessoal / receitas");
    tabela.linhas.forEach((l, i) => l.push(Formato.percentagem(pct[i])));
    return { tipo: "line", config: { type: "line", data: { labels: epocas, datasets }, options: opcoes }, tabela };
  },

  balanco() {
    const ent = estado.entidade, epocas = epocasVisiveis();
    const passivo = serie(ent, "passivo_total", epocas), ativo = serie(ent, "ativo_total", epocas);
    const capital = serie(ent, "capital_proprio", epocas);
    if (passivo.every(v => v === null) && ativo.every(v => v === null)) {
      return { vazio: `Sem dados de balanço para ${nomeEntidade(ent)} neste intervalo.` };
    }
    const opcoes = opcoesBase();
    opcoes.plugins.legend.labels.usePointStyle = true;
    opcoes.plugins.tooltip.callbacks.footer = itens => {
      const c = capital[itens[0].dataIndex];
      return c === null ? "" : `Capital próprio: ${Formato.euros(c)}`;
    };
    opcoes.scales.y.beginAtZero = true;
    const datasets = [
      { ...linha("Passivo", passivo, "--tinta"), fill: areaAcima(1) },
      linha("Ativo", ativo, "--serie-cinza-escuro", true),
    ];
    const tabela = tabelaSeries(epocas, datasets);
    tabela.colunas.push("Capital próprio");
    tabela.linhas.forEach((l, i) => l.push(Formato.euros(capital[i])));
    return {
      tipo: "line",
      config: { type: "line", data: { labels: epocas, datasets }, options: opcoes, plugins: [rotuloCapital] },
      tabela,
    };
  },

  receitas() {
    // Se a época em destaque não tiver composição, mostra a mais recente que tenha
    const com = [...new Set(DADOS.receitas.map(r => r.epoca))].sort();
    const epoca = com.includes(estado.epoca) ? estado.epoca : com[com.length - 1];
    document.querySelectorAll(".epoca-receitas").forEach(el =>
      (el.textContent = epoca === estado.epoca ? epoca : `${epoca} (última época com dados)`));
    const linhas = DADOS.receitas.filter(r => r.epoca === epoca).sort((a, b) => b.valor - a.valor);
    const total = linhas.reduce((s, r) => s + r.valor, 0);

    const opcoes = opcoesBase({ indice: false, legenda: false });
    opcoes.indexAxis = "y";
    opcoes.interaction = { mode: "nearest", axis: "y", intersect: false };
    opcoes.layout.padding.right = 64; // espaço para os valores à direita das barras
    opcoes.plugins.tooltip.callbacks.label = c => ` ${Formato.euros(c.raw)} · ${Formato.percentagem((c.raw / total) * 100)} do total`;
    opcoes.scales = {
      x: { beginAtZero: true, ticks: { callback: v => Formato.eixo(v), color: cor("--suave") }, grid: { color: cor("--grelha") }, border: { display: false } },
      y: { grid: { display: false }, border: { color: cor("--tinta"), width: 1.4 }, ticks: { color: cor("--texto"), font: { size: 12.5 } } },
    };
    // A maior fatia a amarelo, as restantes a preto
    const base = barra("Receitas", linhas.map(r => r.valor), "--tinta");
    base.backgroundColor = linhas.map((_, i) => (i === 0 ? cor("--amarelo") : cor("--tinta")));
    base.borderColor = cor("--tinta");
    base.borderWidth = linhas.map((_, i) => (i === 0 ? 1 : 0));
    base.maxBarThickness = 22;
    return {
      tipo: "hbar",
      config: { type: "bar", data: { labels: linhas.map(r => r.categoria), datasets: [base] }, options: opcoes, plugins: [valoresBarras] },
      tabela: {
        colunas: ["Categoria", "Valor", "Peso"],
        linhas: [...linhas.map(r => [r.categoria, Formato.euros(r.valor), Formato.percentagem((r.valor / total) * 100)]),
                 ["Total", Formato.euros(total), "100,0%"]],
      },
    };
  },

  desporto() {
    const epocas = epocasVisiveis();
    const pontos = epocas.map(e => {
      const d = DADOS.desporto.find(x => x.epoca === e), k = kpi("SAD", e);
      return d && k?.gastos_pessoal ? { x: k.gastos_pessoal, y: d.posicao_liga, epoca: e, pts: d.pontos, europa: d.competicao_europeia } : null;
    }).filter(Boolean);
    if (!pontos.length) return { vazio: "Sem épocas com gastos e classificação neste intervalo." };

    const opcoes = opcoesBase({ indice: false, legenda: false });
    opcoes.plugins.tooltip.callbacks = {
      title: i => i[0].raw.epoca,
      label: c => [` ${c.raw.y}.º lugar · ${c.raw.pts} pontos`, ` Pessoal: ${Formato.euros(c.raw.x)}`, c.raw.europa ? ` ${c.raw.europa}` : ""].filter(Boolean),
    };
    opcoes.scales = {
      x: { title: { display: true, text: "Gastos com pessoal da SAD", color: cor("--suave") }, ticks: { callback: v => Formato.eixo(v), color: cor("--suave") },
           grid: { color: cor("--grelha") }, border: { display: false } },
      y: { reverse: true, min: 1, max: 12, ticks: { stepSize: 1, callback: v => `${v}.º`, color: cor("--suave") },
           title: { display: true, text: "Lugar na Liga", color: cor("--suave") }, grid: { color: cor("--grelha") }, border: { display: false } },
    };
    const destaque = p => p.epoca === estado.epoca;
    const datasets = [{
      label: "Épocas", data: pontos,
      backgroundColor: pontos.map(p => (destaque(p) ? cor("--amarelo") : cor("--tinta"))),
      borderColor: pontos.map(p => (destaque(p) ? cor("--tinta") : cor("--cartao"))),
      borderWidth: pontos.map(p => (destaque(p) ? 2 : 1.5)),
      pointRadius: pontos.map(p => (destaque(p) ? 10 : 7)), pointHoverRadius: 10,
    }];
    return {
      tipo: "scatter",
      config: { type: "scatter", data: { datasets }, options: opcoes, plugins: [rotulosEpocas] },
      tabela: {
        colunas: ["Época", "Gastos com pessoal", "Lugar", "Pontos", "Europa"],
        linhas: pontos.map(p => [p.epoca, Formato.euros(p.x), `${p.y}.º`, p.pts, p.europa ?? "—"]),
      },
    };
  },
};

/* ====================== Rótulos diretos (plugins) ====================== */

/** Valores dentro das barras grandes da SAD, na vertical, como no gráfico 01 do projeto SQL */
const rotulosBarras = {
  id: "rotulosBarras",
  afterDatasetsDraw(chart) {
    const meta = chart.getDatasetMeta(0);
    if (meta.hidden) return;
    const { ctx } = chart;
    ctx.save();
    ctx.font = '700 11px "Archivo", sans-serif';
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    meta.data.forEach((b, i) => {
      const v = chart.data.datasets[0].data[i];
      if (v === null || Math.abs(v) < 5e6) return;
      const texto = Formato.euros(v);
      const altura = Math.abs(b.base - b.y), larg = ctx.measureText(texto).width;
      if (altura < larg + 14 || b.width < 12) return; // não cabe (ou a barra ainda está a crescer)
      ctx.save();
      ctx.translate(b.x, (b.y + b.base) / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.fillStyle = v < 0 ? cor("--rotulo-neg") : cor("--rotulo-pos");
      ctx.fillText(texto, 0, 0);
      ctx.restore();
    });
    ctx.restore();
  },
};

/** Nota do capital próprio na última época visível, como no gráfico 05 do projeto SQL */
const rotuloCapital = {
  id: "rotuloCapital",
  afterDatasetsDraw(chart) {
    const [ps, at] = [chart.getDatasetMeta(0), chart.getDatasetMeta(1)];
    if (ps.hidden || at.hidden) return;
    const dados = chart.data.datasets;
    let i = dados[0].data.length - 1;
    while (i >= 0 && (dados[0].data[i] === null || dados[1].data[i] === null)) i--;
    if (i < 0) return;
    const capital = dados[1].data[i] - dados[0].data[i];
    if (capital >= 0) return;
    // Escreve o texto dentro da área amarela, no troço mais largo das últimas épocas
    const ok = k => k >= 0 && dados[0].data[k] !== null && dados[1].data[k] !== null;
    // (o último troço tende a ser íngreme, por isso prefere-se o anterior, se tiver espaço)
    let melhor = null;
    for (const k of [i - 1, i - 2, i]) {
      if (!ok(k) || !ok(k - 1)) continue;
      const topo = Math.max(ps.data[k].y, ps.data[k - 1].y), fundo = Math.min(at.data[k].y, at.data[k - 1].y);
      if (fundo - topo >= 52) { melhor = { x: (ps.data[k].x + ps.data[k - 1].x) / 2, y: (topo + fundo) / 2 }; break; }
    }
    if (!melhor) return; // área demasiado estreita para três linhas
    const { ctx } = chart;
    ctx.save();
    ctx.font = '700 12px "Archivo", sans-serif';
    ctx.fillStyle = cor("--texto");
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    const meia = ctx.measureText("Capital próprio").width / 2 + 4;
    const x = Math.min(Math.max(melhor.x, chart.chartArea.left + meia), chart.chartArea.right - meia), y = melhor.y;
    [`Capital próprio`, Formato.euros(capital), `em ${chart.data.labels[i]}`]
      .forEach((t, k) => ctx.fillText(t, x, y + (k - 1) * 15));
    ctx.restore();
  },
};

/** Valor no fim de cada barra horizontal */
const valoresBarras = {
  id: "valoresBarras",
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    ctx.save();
    ctx.font = '700 11.5px "Archivo", sans-serif';
    ctx.fillStyle = cor("--texto");
    ctx.textBaseline = "middle";
    chart.getDatasetMeta(0).data.forEach((b, i) => {
      ctx.fillText(Formato.euros(chart.data.datasets[0].data[i]), b.x + 6, b.y);
    });
    ctx.restore();
  },
};

/** Época junto a cada ponto da dispersão; a época em destaque primeiro, as outras só se não colidirem */
const rotulosEpocas = {
  id: "rotulosEpocas",
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    const meta = chart.getDatasetMeta(0), dados = chart.data.datasets[0].data;
    const ocupados = meta.data.map(pt => ({ x: pt.x - 8, y: pt.y - 8, w: 16, h: 16 }));
    const sobrepoe = (r, ignorar) => ocupados.some((o, j) => j !== ignorar && r.x < o.x + o.w && r.x + r.w > o.x && r.y < o.y + o.h && r.y + r.h > o.y);
    const ordem = meta.data.map((_, i) => i).sort((a, b) => (dados[b].epoca === estado.epoca) - (dados[a].epoca === estado.epoca));
    ctx.save();
    ctx.textBaseline = "middle"; ctx.textAlign = "left";
    ordem.forEach(i => {
      const pt = meta.data[i], forte = dados[i].epoca === estado.epoca;
      ctx.font = `${forte ? 700 : 400} 11.5px "Archivo", sans-serif`;
      ctx.fillStyle = forte ? cor("--texto") : cor("--suave");
      const larg = ctx.measureText(dados[i].epoca).width;
      const direita = pt.x + 14 + larg < chart.chartArea.right;
      const x = direita ? pt.x + 13 : pt.x - 13 - larg;
      const caixa = { x, y: pt.y - 7, w: larg, h: 14 };
      if (!forte && sobrepoe(caixa, i)) return;
      ocupados.push(caixa);
      ctx.fillText(dados[i].epoca, x, pt.y);
    });
    ctx.restore();
  },
};

/* ====================== Desenho dos cartões ====================== */

function areaDoCartao(cartao) { return cartao.querySelector(".tela, .tabela"); }

function desenharCartao(cartao, { recriar = false } = {}) {
  const id = cartao.dataset.grafico;
  if (!vistos.has(id)) return; // ainda não chegou ao ecrã: desenha-se quando chegar
  const def = DEFINICOES[id]();
  const botao = cartao.querySelector(".ver-tabela");
  botao.hidden = !!def.vazio;

  const emGrafico = !def.vazio && vistas[id] === "grafico";
  const atual = graficos[id];

  // Mesmo tipo de gráfico já no ecrã: atualiza os dados e deixa o Chart.js fazer a transição
  if (emGrafico && atual && !recriar && atual.$tipo === def.tipo) {
    def.config.options.animation = Animacoes.transicao();
    atual.data = def.config.data;
    atual.options = def.config.options;
    atual.update();
    return;
  }

  atual?.destroy();
  delete graficos[id];
  const nova = document.createElement("div");
  if (def.vazio) {
    nova.className = "tela";
    const p = document.createElement("p");
    p.className = "vazio-grafico"; p.textContent = def.vazio;
    nova.appendChild(p);
  } else if (!emGrafico) {
    nova.className = "tabela";
    nova.appendChild(criarTabela(def.tabela));
  } else {
    nova.className = "tela";
    const canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", cartao.querySelector("h3").textContent);
    nova.appendChild(canvas);
  }
  areaDoCartao(cartao).replaceWith(nova);
  if (emGrafico) {
    const entrada = Animacoes.entrada(def.tipo);
    if (entrada === false) def.config.options.animation = false;
    else {
      const { y, radius, ...geral } = entrada;
      def.config.options.animation = geral;
      def.config.options.animations = { ...(y && { y }), ...(radius && { radius }) };
    }
    const grafico = new Chart(nova.querySelector("canvas"), def.config);
    grafico.$tipo = def.tipo;
    graficos[id] = grafico;
  }
}

function criarTabela({ colunas, linhas }) {
  const t = document.createElement("table");
  const cab = t.createTHead().insertRow();
  colunas.forEach(c => { const th = document.createElement("th"); th.textContent = c; cab.appendChild(th); });
  const corpo = t.createTBody();
  linhas.forEach(l => { const tr = corpo.insertRow(); l.forEach(v => (tr.insertCell().textContent = v)); });
  return t;
}

/* ---------- Indicadores do topo ---------- */

const INDICADORES = [
  { campo: "vendas_servicos", nome: "Vendas e serviços", bom: "sobe" },
  { campo: "gastos_pessoal", nome: "Gastos com pessoal", bom: "desce" },
  { campo: "resultado_liquido", nome: "Resultado líquido", bom: "sobe" },
  { campo: "rl_sem_mais_valias", nome: "Sem mais-valias", bom: "sobe" },
  { campo: "passivo_total", nome: "Passivo", bom: "desce" },
  { campo: "capital_proprio", nome: "Capital próprio", bom: "sobe" },
];

function construirKPIs() {
  const caixa = document.getElementById("kpis");
  INDICADORES.forEach((ind, i) => {
    const div = document.createElement("div");
    div.className = "kpi"; div.style.setProperty("--i", i); div.dataset.campo = ind.campo;
    div.innerHTML = `<p class="nome"></p><p class="valor"></p><p class="delta"></p>`;
    div.querySelector(".nome").textContent = ind.nome;
    caixa.appendChild(div);
  });
}

function desenharKPIs() {
  const { entidade, epoca } = estado;
  const anterior = DADOS.epocas[DADOS.epocas.indexOf(epoca) - 1];
  const atual = kpi(entidade, epoca), antes = anterior ? kpi(entidade, anterior) : null;
  document.getElementById("kpi-entidade").textContent = nomeEntidade(entidade);
  document.getElementById("kpi-epoca").textContent = epoca;

  INDICADORES.forEach(ind => {
    const div = document.querySelector(`.kpi[data-campo="${ind.campo}"]`);
    const v = atual?.[ind.campo] ?? null, a = antes?.[ind.campo] ?? null;
    const elValor = div.querySelector(".valor"), delta = div.querySelector(".delta");
    div.classList.toggle("vazio", v === null);
    if (v === null) elValor.textContent = "sem dados";
    else Animacoes.contar(elValor, valoresKPI[ind.campo] ?? null, v, Formato.euros);
    valoresKPI[ind.campo] = v;

    delta.textContent = "";
    if (v !== null && a !== null && v !== a) {
      const d = v - a, melhor = (d > 0) === (ind.bom === "sobe");
      const s = document.createElement("span");
      s.className = melhor ? "sobe" : "desce";
      s.textContent = `${d > 0 ? "▲" : "▼"} ${Formato.variacao(d)}`;
      delta.append(s, ` face a ${anterior}`);
    } else if (v !== null) {
      delta.textContent = "sem época anterior para comparar";
    }
  });

  const d = DADOS.desporto.find(x => x.epoca === epoca);
  const partes = d ? [`${d.posicao_liga}.º lugar na Liga, ${d.pontos} pontos`,
    d.competicao_europeia && `${d.competicao_europeia} (${d.fase_europeia.toLowerCase()})`,
    d.trofeu && `vencedor da ${d.trofeu}`].filter(Boolean) : [];
  const campo = document.getElementById("kpi-desporto");
  campo.textContent = partes.length ? `Em campo: ${partes.join(" · ")}.` : "";
  campo.hidden = !partes.length;
}

function desenharTudo(opcoes) {
  aplicarTemaChart();
  desenharKPIs();
  document.querySelectorAll(".cartao[data-grafico]").forEach(c => desenharCartao(c, opcoes));
}

/* ====================== Filtros ====================== */

function moverIndicador() {
  const caixa = document.getElementById("f-entidade");
  const ativo = caixa.querySelector('button[aria-checked="true"]');
  const ind = caixa.querySelector(".indicador");
  ind.style.width = `${ativo.offsetWidth}px`;
  ind.style.transform = `translateX(${ativo.offsetLeft}px)`;
}

function preencherFiltros() {
  const segmentos = document.getElementById("f-entidade");
  const indicador = document.createElement("span");
  indicador.className = "indicador"; indicador.setAttribute("aria-hidden", "true");
  segmentos.appendChild(indicador);
  ORDEM_FILTRO.forEach(id => {
    const b = document.createElement("button");
    b.type = "button"; b.setAttribute("role", "radio"); b.textContent = nomeEntidade(id); b.dataset.id = id;
    b.setAttribute("aria-checked", String(id === estado.entidade));
    b.addEventListener("click", () => {
      if (estado.entidade === id) return;
      estado.entidade = id;
      segmentos.querySelectorAll("button").forEach(x => x.setAttribute("aria-checked", String(x === b)));
      moverIndicador();
      desenharTudo();
    });
    segmentos.appendChild(b);
  });
  addEventListener("resize", moverIndicador);

  const selects = { inicio: "f-inicio", fim: "f-fim", epoca: "f-epoca" };
  Object.entries(selects).forEach(([chave, id]) => {
    const s = document.getElementById(id);
    DADOS.epocas.forEach(e => s.add(new Option(e, e)));
    s.value = estado[chave];
    s.addEventListener("change", () => {
      estado[chave] = s.value;
      if (DADOS.epocas.indexOf(estado.inicio) > DADOS.epocas.indexOf(estado.fim)) {
        [estado.inicio, estado.fim] = [estado.fim, estado.inicio];
        document.getElementById("f-inicio").value = estado.inicio;
        document.getElementById("f-fim").value = estado.fim;
      }
      // Mudar o intervalo muda o número de épocas: aí recria-se o gráfico (as barras voltam a crescer)
      desenharTudo({ recriar: chave !== "epoca" });
    });
  });
}

function prepararCartoes() {
  const cartoes = [...document.querySelectorAll(".cartao[data-grafico]")];
  cartoes.forEach(cartao => {
    const id = cartao.dataset.grafico;
    vistas[id] = "grafico";
    const b = document.createElement("button");
    b.type = "button"; b.className = "ver-tabela"; b.textContent = "Ver tabela";
    b.addEventListener("click", () => {
      vistas[id] = vistas[id] === "grafico" ? "tabela" : "grafico";
      b.textContent = vistas[id] === "grafico" ? "Ver tabela" : "Ver gráfico";
      desenharCartao(cartao, { recriar: true });
    });
    cartao.querySelector(".cabeca").appendChild(b);
  });
  // Cada cartão entra (e o seu gráfico anima-se) quando chega ao ecrã
  Animacoes.observar(cartoes, cartao => {
    cartao.classList.add("visivel");
    vistos.add(cartao.dataset.grafico);
    setTimeout(() => desenharCartao(cartao, { recriar: true }), Animacoes.reduzido ? 0 : 180);
  });
}

/* ---------- Tema claro/escuro ---------- */

function prepararTema() {
  const raiz = document.documentElement;
  try { const t = localStorage.getItem("tema"); if (t) raiz.dataset.theme = t; } catch { /* sem armazenamento */ }
  document.getElementById("f-tema").addEventListener("click", () => {
    const escuroAgora = raiz.dataset.theme ? raiz.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    raiz.dataset.theme = escuroAgora ? "light" : "dark";
    try { localStorage.setItem("tema", raiz.dataset.theme); } catch { /* ignora */ }
    desenharTudo({ recriar: true });
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (!raiz.dataset.theme) desenharTudo({ recriar: true }); });
}

/* ====================== Arranque ====================== */

async function iniciar() {
  document.documentElement.classList.add("js");
  try {
    const r = await fetch("data/contas.json");
    if (!r.ok) throw new Error(r.status);
    DADOS = await r.json();
  } catch (erro) {
    document.querySelector("main .dentro").innerHTML =
      `<p class="em-campo">Não foi possível carregar <code>data/contas.json</code>. Abre a página através de um servidor
       (por exemplo, a extensão Live Server do VS Code ou <code>python -m http.server</code>), não diretamente do disco.</p>`;
    console.error(erro);
    return;
  }

  const ep = DADOS.epocas;
  estado.inicio = ep[0];
  estado.fim = ep[ep.length - 1];
  estado.epoca = [...ep].reverse().find(e => kpi("SAD", e)?.resultado_liquido != null);
  document.getElementById("intervalo-total").textContent = `${ep[0]} – ${ep[ep.length - 1]}`;

  prepararTema();
  construirKPIs();
  preencherFiltros();
  await document.fonts.ready;
  moverIndicador();
  aplicarTemaChart();
  desenharKPIs();
  prepararCartoes();
}

iniciar();
