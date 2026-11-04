// Motor dos gráficos: cores do tema, opções comuns, séries e plugins.
// As secções (paineis.js) descrevem o que mostrar; este módulo trata de como se desenha.

import { eixo, formatar } from "./formato.js";
import { entrada, transicao } from "./animacoes.js";

/* ---------- Cores ---------- */

const raiz = document.documentElement;
export const cor = nome => getComputedStyle(raiz).getPropertyValue(`--${nome}`).trim();

/** Papéis das séries categóricas: só cinzentos. O verde, o vermelho e o amarelo têm significado
    (positivo, negativo/risco, alerta) e só se usam através de coresSinal e coresCondicao (paineis.js). */
export const PAPEIS = ["tinta", "cinza-escuro", "cinza", "cinza-claro"];

/** Cor de cada papel nas séries, com a paleta do projeto SQL: preto, amarelo, cinzento e amarelo-claro.
    São tons bem distintos, para que séries vizinhas não se confundam. */
const SERIE = { "tinta": "serie-1", "cinza-escuro": "serie-2", "cinza": "serie-3", "cinza-claro": "serie-4" };
export const corSerie = papel => cor(SERIE[papel] ?? papel);

export function aplicarTema() {
  Chart.defaults.font.family = '"Archivo", system-ui, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.color = cor("suave");
  Chart.defaults.borderColor = cor("grelha");
}

/* ---------- Séries ---------- */

/** Barras: as cores claras levam contorno para não se perderem no fundo */
export function barras(label, data, papel = "tinta", extra = {}) {
  // Os amarelos levam um contorno fino para não se perderem no fundo claro
  const claro = ["cinza-escuro", "cinza-claro", "amarelo"].includes(papel);
  return {
    label, data, backgroundColor: corSerie(papel),
    borderColor: claro ? cor("contorno") : corSerie(papel), borderWidth: claro ? 1 : 0,
    borderRadius: 2, borderSkipped: false, maxBarThickness: 30, categoryPercentage: 0.8, barPercentage: 0.9,
    ...extra,
  };
}

/** Linha principal (marcadores cheios) ou secundária (marcadores ocos) */
export function linha(label, data, papel = "tinta", { oca = false, tracejada = false, ...extra } = {}) {
  return {
    label, data, borderColor: corSerie(papel), backgroundColor: oca ? cor("cartao") : corSerie(papel),
    borderWidth: 2.4, borderDash: tracejada ? [6, 4] : [], pointRadius: tracejada ? 0 : 4, pointHoverRadius: 6,
    pointBorderWidth: oca ? 2.2 : 0, pointBorderColor: corSerie(papel), tension: 0, spanGaps: false,
    ...extra,
  };
}

/** Área a vermelho claro entre duas linhas, só onde a série de cima ultrapassa a de baixo */
export const areaAcima = alvo => ({ target: alvo, above: cor("area"), below: "rgba(0,0,0,0)" });

/* ---------- Opções comuns ---------- */

export function opcoes({ unidade = "eur", legenda = true, indice = true, empilhado = false, horizontal = false,
  min, max, inverter = false, tooltipUnidade } = {}) {
  const fmtEixo = eixo[unidade] ?? eixo.int;
  const fmtTooltip = v => formatar(tooltipUnidade ?? unidade, v);
  const valor = {
    stacked: empilhado, min, max, reverse: inverter,
    ticks: { callback: v => fmtEixo(v), color: cor("suave"), maxTicksLimit: 7 },
    grid: { color: c => (c.tick.value === 0 ? cor("cinza-escuro") : cor("grelha")), lineWidth: c => (c.tick.value === 0 ? 1.2 : 1) },
    border: { display: false },
  };
  const categoria = {
    stacked: empilhado, grid: { display: false }, border: { color: cor("grelha") },
    ticks: { maxRotation: 0, autoSkipPadding: 8, color: horizontal ? cor("texto") : cor("suave") },
  };
  return {
    responsive: true, maintainAspectRatio: false, indexAxis: horizontal ? "y" : "x",
    transitions: { resize: { animation: { duration: 0 } } },
    interaction: indice ? { mode: "index", intersect: false, axis: horizontal ? "y" : "x" } : { mode: "nearest", intersect: true },
    layout: { padding: { top: 6, right: 8 } },
    plugins: {
      legend: {
        display: legenda, position: "top", align: "start",
        labels: {
          boxWidth: 20, boxHeight: 10, padding: 14, color: cor("texto"), font: { size: 12.5 },
          // Séries com cor por valor (verde/vermelho): a legenda usa um cinzento neutro, não a cor do primeiro valor
          generateLabels: chart => Chart.defaults.plugins.legend.labels.generateLabels(chart).map(l => {
            const ds = chart.data.datasets[l.datasetIndex];
            if (Array.isArray(ds.backgroundColor)) { l.fillStyle = cor("cinza-escuro"); l.strokeStyle = cor("cinza-escuro"); }
            return l;
          }),
        },
      },
      tooltip: {
        backgroundColor: cor("dica-fundo"), titleColor: cor("dica-texto"), bodyColor: cor("dica-texto"), footerColor: cor("dica-suave"),
        borderColor: cor("dica-borda"), borderWidth: 1, padding: 10, cornerRadius: 6, boxPadding: 5,
        titleFont: { weight: "700", size: 12.5 }, footerFont: { weight: "400" }, usePointStyle: false,
        callbacks: { label: c => ` ${c.dataset.label}: ${fmtTooltip(c.raw)}` },
        filter: c => c.raw !== null && c.raw !== undefined,
      },
    },
    scales: horizontal ? { x: valor, y: categoria } : { x: categoria, y: valor },
  };
}

/* ---------- Plugins ---------- */

let epocaDestaque = null;
export const definirDestaque = e => { epocaDestaque = e; };

/** Faixa cinzenta por trás da época em destaque (gráficos com épocas no eixo x) */
export const destaqueEpoca = {
  id: "destaqueEpoca",
  beforeDatasetsDraw(chart) {
    const labels = chart.data.labels ?? [];
    const i = labels.indexOf(epocaDestaque);
    const x = chart.scales.x;
    if (i < 0 || !x || chart.options.indexAxis === "y") return;
    const passo = labels.length > 1 ? Math.abs(x.getPixelForValue(1) - x.getPixelForValue(0)) : x.width;
    const { top, bottom } = chart.chartArea, cx = x.getPixelForValue(i);
    const ctx = chart.ctx;
    ctx.save();
    ctx.fillStyle = cor("destaque");
    ctx.fillRect(cx - passo / 2, top, passo, bottom - top);
    ctx.restore();
  },
};

/** Linhas de referência horizontais (ex.: 100%, limite de 70% da UEFA, rácio = 1) */
export const referencias = {
  id: "referencias",
  afterDatasetsDraw(chart, _, op) {
    const lista = op?.linhas ?? [];
    if (!lista.length) return;
    const { ctx, chartArea: a } = chart;
    const escala = chart.options.indexAxis === "y" ? chart.scales.x : chart.scales.y;
    ctx.save();
    lista.forEach(({ valor, rotulo }) => {
      const p = escala.getPixelForValue(valor);
      if (!Number.isFinite(p)) return;
      ctx.strokeStyle = cor("cinza-escuro"); ctx.lineWidth = 1.2; ctx.setLineDash([5, 4]);
      ctx.beginPath();
      if (chart.options.indexAxis === "y") { ctx.moveTo(p, a.top); ctx.lineTo(p, a.bottom); }
      else { ctx.moveTo(a.left, p); ctx.lineTo(a.right, p); }
      ctx.stroke();
      if (rotulo) {
        ctx.setLineDash([]);
        ctx.font = '700 11px "Archivo", sans-serif';
        ctx.fillStyle = cor("texto");
        if (chart.options.indexAxis === "y") { ctx.textAlign = "left"; ctx.fillText(rotulo, p + 5, a.top + 10); }
        else { ctx.textAlign = "right"; ctx.textBaseline = "bottom"; ctx.fillText(rotulo, a.right - 2, p - 4); }
      }
    });
    ctx.restore();
  },
};

/** Valor no fim de cada barra horizontal */
export const valoresNasBarras = {
  id: "valoresNasBarras",
  afterDatasetsDraw(chart, _, op) {
    if (!op?.formatar) return;
    const { ctx } = chart;
    ctx.save();
    ctx.font = '700 11.5px "Archivo", sans-serif';
    ctx.fillStyle = cor("texto"); ctx.textBaseline = "middle";
    chart.data.datasets.forEach((ds, d) => {
      const meta = chart.getDatasetMeta(d);
      if (meta.hidden) return;
      meta.data.forEach((b, i) => {
        const v = ds.data[i];
        if (v === null || v === undefined) return;
        if (chart.options.indexAxis === "y") { ctx.textAlign = "left"; ctx.fillText(op.formatar(v), b.x + 6, b.y); }
        else { ctx.textAlign = "center"; ctx.fillText(op.formatar(v), b.x, v >= 0 ? b.y - 9 : b.y + 10); }
      });
    });
    ctx.restore();
  },
};

/* ---------- Desenho ---------- */

/** Cria o gráfico, ou atualiza-o com transição se já existir com o mesmo tipo */
export function desenhar(canvas, config, existente, { recriar = false } = {}) {
  const tipo = config.type;
  config.plugins = [destaqueEpoca, referencias, valoresNasBarras, ...(config.plugins ?? [])];
  if (existente && !recriar && existente.config.type === tipo && existente.canvas === canvas) {
    Object.assign(config.options, transicao());
    existente.data = config.data;
    existente.options = config.options;
    existente.update();
    return existente;
  }
  existente?.destroy();
  Object.assign(config.options, entrada(tipo));
  return new Chart(canvas, config);
}
