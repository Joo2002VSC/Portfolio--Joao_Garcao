// Dashboard Vitória SC · lógica do painel
// 1. carrega data/contas.json (gerado por scripts/exportar_json.py)
// 2. guarda o estado dos filtros
// 3. desenha indicadores e gráficos sempre que um filtro muda

/* ====================== Estado e dados ====================== */

const ENTIDADES = [
  { id: "SAD", nome: "SAD", cor: "--serie-1" },
  { id: "CLUBE", nome: "Clube", cor: "--serie-2" },
  { id: "CONSOLIDADO", nome: "Consolidado", cor: "--serie-3" },
];

const estado = { entidade: "SAD", inicio: null, fim: null, epoca: null };
const vistas = {};   // "grafico" ou "tabela", por cartão
const graficos = {}; // instâncias Chart.js, por cartão
let DADOS = null;

/** Linha de indicadores de uma entidade numa época (ou undefined) */
const kpi = (entidade, epoca) => DADOS.kpis.find(l => l.entidade === entidade && l.epoca === epoca);

/** Épocas dentro do intervalo escolhido nos filtros */
function epocasVisiveis() {
  const i = DADOS.epocas.indexOf(estado.inicio), f = DADOS.epocas.indexOf(estado.fim);
  return DADOS.epocas.slice(Math.min(i, f), Math.max(i, f) + 1);
}

/** Série de valores de um campo, alinhada com as épocas visíveis (null onde não há dados) */
function serie(entidade, campo, epocas = epocasVisiveis()) {
  return epocas.map(e => kpi(entidade, e)?.[campo] ?? null);
}

const nomeEntidade = id => ENTIDADES.find(e => e.id === id).nome;

/* ====================== Cores (lidas do CSS) ====================== */

function cor(nome) {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
}

function aplicarTemaChart() {
  Chart.defaults.font.family = '"Archivo", system-ui, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.color = cor("--suave");
  Chart.defaults.borderColor = cor("--grelha");
}

/* ====================== Opções comuns dos gráficos ====================== */

function opcoesBase({ eixoY = "M€", indice = true } = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    interaction: indice ? { mode: "index", intersect: false } : { mode: "nearest", intersect: true },
    plugins: {
      legend: {
        position: "top", align: "start",
        labels: { usePointStyle: true, pointStyle: "rectRounded", boxWidth: 10, boxHeight: 10, padding: 14, color: cor("--texto") },
      },
      tooltip: {
        backgroundColor: cor("--cartao"), titleColor: cor("--texto"), bodyColor: cor("--texto"), footerColor: cor("--suave"),
        borderColor: cor("--linha"), borderWidth: 1, padding: 10, cornerRadius: 6, boxPadding: 4, usePointStyle: true,
        titleFont: { weight: "700" }, footerFont: { weight: "400" },
        callbacks: { label: c => ` ${c.dataset.label}: ${Formato.euros(c.raw)}` },
        filter: c => c.raw !== null,
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkipPadding: 10 } },
      y: {
        title: { display: !!eixoY, text: eixoY, color: cor("--mudo") },
        ticks: { callback: v => Formato.eixo(v) },
        grid: { color: c => (c.tick.value === 0 ? cor("--mudo") : cor("--grelha")), lineWidth: c => (c.tick.value === 0 ? 1.5 : 1) },
        border: { display: false },
      },
    },
  };
}

const barra = (label, data, corVar) => ({
  label, data, backgroundColor: cor(corVar), borderRadius: 4, borderSkipped: "start",
  maxBarThickness: 26, categoryPercentage: 0.78, barPercentage: 0.92,
});

const linha = (label, data, corVar) => ({
  label, data, borderColor: cor(corVar), backgroundColor: cor(corVar),
  borderWidth: 2, pointRadius: 3, pointHoverRadius: 6, pointBorderColor: cor("--cartao"), pointBorderWidth: 2,
  tension: 0.25, spanGaps: false,
});

/* ====================== Definição de cada gráfico ====================== */
// Cada função devolve { config } para o Chart.js, { vazio: "mensagem" }, e { tabela } para a vista em tabela.

const DEFINICOES = {
  resultado() {
    const epocas = epocasVisiveis();
    const datasets = ENTIDADES.map(e => barra(e.nome, serie(e.id, "resultado_liquido", epocas), e.cor));
    return {
      config: { type: "bar", data: { labels: epocas, datasets }, options: opcoesBase() },
      tabela: tabelaSeries(epocas, datasets),
    };
  },

  maisvalias() {
    const ent = estado.entidade, epocas = epocasVisiveis();
    const rl = serie(ent, "resultado_liquido", epocas), sem = serie(ent, "rl_sem_mais_valias", epocas);
    if (sem.every(v => v === null)) {
      return { vazio: `Não há dados de transferências para ${nomeEntidade(ent) === "Clube" ? "o Clube" : nomeEntidade(ent)} neste intervalo. Escolhe a SAD ou o Consolidado.` };
    }
    // Só mostra as épocas em que existe o valor sem mais-valias, para comparar par a par
    const idx = epocas.map((_, i) => i).filter(i => sem[i] !== null);
    const labels = idx.map(i => epocas[i]);
    const datasets = [
      barra("Resultado líquido", idx.map(i => rl[i]), "--serie-1"),
      barra("Sem mais-valias", idx.map(i => sem[i]), "--serie-2"),
    ];
    return { config: { type: "bar", data: { labels, datasets }, options: opcoesBase() }, tabela: tabelaSeries(labels, datasets) };
  },

  pessoal() {
    const ent = estado.entidade, epocas = epocasVisiveis();
    const receitas = serie(ent, "vendas_servicos", epocas), pessoal = serie(ent, "gastos_pessoal", epocas);
    if (receitas.every(v => v === null) && pessoal.every(v => v === null)) {
      return { vazio: `Sem dados de receitas e gastos com pessoal para ${nomeEntidade(ent)} neste intervalo.` };
    }
    const pct = serie(ent, "pct_pessoal_receitas", epocas);
    const opcoes = opcoesBase();
    opcoes.plugins.tooltip.callbacks.footer = itens => {
      const p = pct[itens[0].dataIndex];
      return p === null ? "" : `Pessoal = ${Formato.percentagem(p)} das receitas`;
    };
    opcoes.scales.y.beginAtZero = true;
    const datasets = [linha("Vendas e serviços", receitas, "--serie-1"), linha("Gastos com pessoal", pessoal, "--serie-2")];
    const tabela = tabelaSeries(epocas, datasets);
    tabela.colunas.push("Pessoal / receitas");
    tabela.linhas.forEach((l, i) => l.push(Formato.percentagem(pct[i])));
    return { config: { type: "line", data: { labels: epocas, datasets }, options: opcoes }, tabela };
  },

  balanco() {
    const ent = estado.entidade, epocas = epocasVisiveis();
    const datasets = [
      linha("Ativo", serie(ent, "ativo_total", epocas), "--serie-1"),
      linha("Passivo", serie(ent, "passivo_total", epocas), "--serie-2"),
      linha("Capital próprio", serie(ent, "capital_proprio", epocas), "--serie-3"),
    ];
    if (datasets.every(d => d.data.every(v => v === null))) {
      return { vazio: `Sem dados de balanço para ${nomeEntidade(ent)} neste intervalo.` };
    }
    return { config: { type: "line", data: { labels: epocas, datasets }, options: opcoesBase() }, tabela: tabelaSeries(epocas, datasets) };
  },

  receitas() {
    // Se a época em destaque não tiver composição, mostra a mais recente que tenha
    const com = [...new Set(DADOS.receitas.map(r => r.epoca))].sort();
    const epoca = com.includes(estado.epoca) ? estado.epoca : com[com.length - 1];
    document.querySelectorAll(".epoca-receitas").forEach(el =>
      (el.textContent = epoca === estado.epoca ? epoca : `${epoca} (última com dados)`));
    const linhas = DADOS.receitas.filter(r => r.epoca === epoca).sort((a, b) => b.valor - a.valor);
    const total = linhas.reduce((s, r) => s + r.valor, 0);
    const opcoes = opcoesBase({ eixoY: null, indice: false });
    opcoes.indexAxis = "y";
    opcoes.interaction = { mode: "nearest", axis: "y", intersect: false };
    opcoes.plugins.legend.display = false;
    opcoes.plugins.tooltip.callbacks.label = c => ` ${Formato.euros(c.raw)} · ${Formato.percentagem((c.raw / total) * 100)} do total`;
    opcoes.scales = {
      x: { beginAtZero: true, ticks: { callback: v => Formato.eixo(v) }, title: { display: true, text: "M€", color: cor("--mudo") },
           grid: { color: cor("--grelha") }, border: { display: false } },
      y: { grid: { display: false }, ticks: { color: cor("--texto") } },
    };
    const datasets = [{ ...barra("Receitas", linhas.map(r => r.valor), "--serie-1"), borderSkipped: "start", maxBarThickness: 20 }];
    return {
      config: { type: "bar", data: { labels: linhas.map(r => r.categoria), datasets }, options: opcoes },
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

    const destaque = cor("--amarelo");
    const opcoes = opcoesBase({ eixoY: null, indice: false });
    opcoes.plugins.legend.display = false;
    opcoes.plugins.tooltip.callbacks = {
      title: i => i[0].raw.epoca,
      label: c => [` ${c.raw.y}.º lugar · ${c.raw.pts} pontos`, ` Pessoal: ${Formato.euros(c.raw.x)}`, c.raw.europa ? ` ${c.raw.europa}` : ""].filter(Boolean),
    };
    opcoes.scales = {
      x: { title: { display: true, text: "Gastos com pessoal da SAD (M€)", color: cor("--mudo") }, ticks: { callback: v => Formato.eixo(v) },
           grid: { color: cor("--grelha") }, border: { display: false } },
      y: { reverse: true, min: 1, max: 12, ticks: { stepSize: 1, callback: v => `${v}.º` },
           title: { display: true, text: "Lugar na Liga", color: cor("--mudo") }, grid: { color: cor("--grelha") }, border: { display: false } },
    };
    const eDestaque = p => p.epoca === estado.epoca;
    const datasets = [{
      label: "Épocas", data: pontos,
      backgroundColor: pontos.map(p => (eDestaque(p) ? destaque : cor("--serie-1"))),
      borderColor: pontos.map(p => (eDestaque(p) ? cor("--texto") : cor("--cartao"))),
      borderWidth: 2, pointRadius: pontos.map(p => (eDestaque(p) ? 9 : 6)), pointHoverRadius: 9,
    }];
    return {
      config: { type: "scatter", data: { datasets }, options: opcoes, plugins: [rotulosEpocas] },
      tabela: {
        colunas: ["Época", "Gastos com pessoal", "Lugar", "Pontos", "Europa"],
        linhas: pontos.map(p => [p.epoca, Formato.euros(p.x), `${p.y}.º`, p.pts, p.europa ?? "—"]),
      },
    };
  },
};

/** Plugin: escreve a época junto a cada ponto da dispersão (texto pequeno, cor de texto, não da série) */
const rotulosEpocas = {
  id: "rotulosEpocas",
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    const meta = chart.getDatasetMeta(0);
    ctx.save();
    ctx.textBaseline = "middle";
    // Desenha primeiro a época em destaque; as outras só se não colidirem com rótulos já escritos
    const ocupados = [];
    const ordem = meta.data.map((_, i) => i)
      .sort((a, b) => (chart.data.datasets[0].data[b].epoca === estado.epoca) - (chart.data.datasets[0].data[a].epoca === estado.epoca));
    ocupados.push(...meta.data.map(pt => ({ x: pt.x - 7, y: pt.y - 7, w: 14, h: 14 })));
    ordem.forEach(i => {
      const ponto = meta.data[i];
      const p = chart.data.datasets[0].data[i];
      const forte = p.epoca === estado.epoca;
      ctx.font = `${forte ? 700 : 400} 11px "Archivo", sans-serif`;
      ctx.fillStyle = forte ? cor("--texto") : cor("--mudo");
      const larg = ctx.measureText(p.epoca).width;
      const direita = ponto.x + 12 + larg < chart.chartArea.right;
      const x = direita ? ponto.x + 11 : ponto.x - 11 - larg;
      const caixa = { x, y: ponto.y - 7, w: larg, h: 14 };
      const proprio = ocupados.findIndex(o => o.x === ponto.x - 7 && o.y === ponto.y - 7);
      const outros = ocupados.filter((_, j) => j !== proprio);
      if (!forte && outros.some(o => caixa.x < o.x + o.w && caixa.x + caixa.w > o.x && caixa.y < o.y + o.h && caixa.y + caixa.h > o.y)) return;
      ocupados.push(caixa);
      ctx.textAlign = "left";
      ctx.fillText(p.epoca, x, ponto.y);
    });
    ctx.restore();
  },
};

/** Converte datasets do Chart.js numa tabela simples (época × séries) */
function tabelaSeries(labels, datasets) {
  return {
    colunas: ["Época", ...datasets.map(d => d.label)],
    linhas: labels.map((l, i) => [l, ...datasets.map(d => Formato.euros(d.data[i]))]),
  };
}

/* ====================== Desenho ====================== */

function desenharCartao(cartao) {
  const id = cartao.dataset.grafico;
  const tela = cartao.querySelector(".tela, .tabela");
  graficos[id]?.destroy();
  delete graficos[id];

  const def = DEFINICOES[id]();
  const botao = cartao.querySelector(".ver-tabela");
  botao.hidden = !!def.vazio;

  // Repõe a área do gráfico
  const nova = document.createElement("div");
  if (def.vazio) {
    nova.className = "tela";
    nova.innerHTML = `<p class="vazio-grafico"></p>`;
    nova.firstChild.textContent = def.vazio;
  } else if (vistas[id] === "tabela") {
    nova.className = "tabela";
    nova.appendChild(criarTabela(def.tabela));
  } else {
    nova.className = "tela";
    const canvas = document.createElement("canvas");
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", cartao.querySelector("h3").textContent);
    nova.appendChild(canvas);
  }
  tela.replaceWith(nova);
  if (!def.vazio && vistas[id] !== "tabela") graficos[id] = new Chart(nova.querySelector("canvas"), def.config);
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
  { campo: "resultado_liquido", nome: "Resultado líquido", bom: "sobe", sinal: true },
  { campo: "rl_sem_mais_valias", nome: "Resultado sem mais-valias", bom: "sobe", sinal: true },
  { campo: "passivo_total", nome: "Passivo", bom: "desce" },
  { campo: "capital_proprio", nome: "Capital próprio", bom: "sobe", sinal: true },
];

function desenharKPIs() {
  const { entidade, epoca } = estado;
  const anterior = DADOS.epocas[DADOS.epocas.indexOf(epoca) - 1];
  const atual = kpi(entidade, epoca), antes = anterior ? kpi(entidade, anterior) : null;

  document.getElementById("kpi-entidade").textContent = nomeEntidade(entidade);
  document.getElementById("kpi-epoca").textContent = epoca;

  const caixa = document.getElementById("kpis");
  caixa.innerHTML = "";
  INDICADORES.forEach(ind => {
    const v = atual?.[ind.campo] ?? null, a = antes?.[ind.campo] ?? null;
    const div = document.createElement("div");
    div.className = "kpi" + (v === null ? " vazio" : "");
    const nome = document.createElement("p"); nome.className = "nome"; nome.textContent = ind.nome;
    const valor = document.createElement("p");
    valor.className = "valor" + (ind.sinal && v < 0 ? " negativo" : "");
    valor.textContent = v === null ? "sem dados" : Formato.euros(v);
    const delta = document.createElement("p"); delta.className = "delta";
    if (v !== null && a !== null && v !== a) {
      const d = v - a, melhor = (d > 0) === (ind.bom === "sobe");
      const s = document.createElement("span");
      s.className = melhor ? "sobe" : "desce";
      s.textContent = `${d > 0 ? "▲" : "▼"} ${Formato.variacao(d)}`;
      delta.append(s, ` face a ${anterior}`);
    } else {
      delta.textContent = v === null ? " " : "sem época anterior para comparar";
    }
    div.append(nome, valor, delta);
    caixa.appendChild(div);
  });

  // Contexto desportivo da época
  const d = DADOS.desporto.find(x => x.epoca === epoca);
  const partes = d ? [`${d.posicao_liga}.º lugar na Liga, ${d.pontos} pontos`,
    d.competicao_europeia && `${d.competicao_europeia} (${d.fase_europeia.toLowerCase()})`,
    d.trofeu && `vencedor da ${d.trofeu}`].filter(Boolean) : [];
  document.getElementById("kpi-desporto").textContent = partes.length ? `Em campo: ${partes.join(" · ")}.` : "";
  document.querySelectorAll(".epoca-destaque").forEach(el => (el.textContent = epoca));
}

function desenharTudo() {
  aplicarTemaChart();
  desenharKPIs();
  document.querySelectorAll(".cartao[data-grafico]").forEach(desenharCartao);
}

/* ====================== Filtros ====================== */

function preencherFiltros() {
  const segmentos = document.getElementById("f-entidade");
  ENTIDADES.forEach(e => {
    const b = document.createElement("button");
    b.type = "button"; b.role = "radio"; b.textContent = e.nome; b.dataset.id = e.id;
    b.setAttribute("aria-checked", String(e.id === estado.entidade));
    b.addEventListener("click", () => {
      estado.entidade = e.id;
      segmentos.querySelectorAll("button").forEach(x => x.setAttribute("aria-checked", String(x === b)));
      desenharTudo();
    });
    segmentos.appendChild(b);
  });

  const selects = { inicio: "f-inicio", fim: "f-fim", epoca: "f-epoca" };
  Object.entries(selects).forEach(([chave, id]) => {
    const s = document.getElementById(id);
    DADOS.epocas.forEach(e => s.add(new Option(e, e)));
    s.value = estado[chave];
    s.addEventListener("change", () => {
      estado[chave] = s.value;
      // Mantém o intervalo coerente: início nunca depois do fim
      if (DADOS.epocas.indexOf(estado.inicio) > DADOS.epocas.indexOf(estado.fim)) {
        [estado.inicio, estado.fim] = [estado.fim, estado.inicio];
        document.getElementById("f-inicio").value = estado.inicio;
        document.getElementById("f-fim").value = estado.fim;
      }
      desenharTudo();
    });
  });
}

function prepararBotoesTabela() {
  document.querySelectorAll(".cartao[data-grafico]").forEach(cartao => {
    const id = cartao.dataset.grafico;
    vistas[id] = "grafico";
    const b = document.createElement("button");
    b.type = "button"; b.className = "ver-tabela"; b.textContent = "Ver tabela";
    b.addEventListener("click", () => {
      vistas[id] = vistas[id] === "grafico" ? "tabela" : "grafico";
      b.textContent = vistas[id] === "grafico" ? "Ver tabela" : "Ver gráfico";
      desenharCartao(cartao);
    });
    cartao.querySelector("header").appendChild(b);
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
    desenharTudo();
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (!raiz.dataset.theme) desenharTudo(); });
}

/* ====================== Arranque ====================== */

async function iniciar() {
  try {
    const r = await fetch("data/contas.json");
    if (!r.ok) throw new Error(r.status);
    DADOS = await r.json();
  } catch (erro) {
    document.querySelector("main .dentro").innerHTML =
      `<p class="nota">Não foi possível carregar <code>data/contas.json</code>. Abre a página através de um servidor
       (por exemplo, a extensão Live Server do VS Code ou <code>python -m http.server</code>), não diretamente do disco.</p>`;
    console.error(erro);
    return;
  }

  const ep = DADOS.epocas;
  estado.inicio = ep[0];
  estado.fim = ep[ep.length - 1];
  // Época em destaque: a mais recente com resultado da SAD
  estado.epoca = [...ep].reverse().find(e => kpi("SAD", e)?.resultado_liquido != null);
  document.getElementById("intervalo-total").textContent = `${ep[0]} – ${ep[ep.length - 1]}`;

  prepararTema();
  preencherFiltros();
  prepararBotoesTabela();
  await document.fonts.ready;
  desenharTudo();
}

iniciar();
