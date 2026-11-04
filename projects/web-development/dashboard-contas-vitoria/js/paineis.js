// Definição de cada visualização: a pergunta a que responde, a consulta SQL de onde vem,
// como se desenha e a conclusão, calculada a partir dos dados filtrados.
// Nenhum valor é inventado aqui: tudo sai das linhas das consultas.

import { barras, linha, areaAcima, opcoes, cor, letra } from "./graficos.js";
import { euros, pct, razao, vezes, racio, inteiro, decimal, lugar, milhoes, pp, variacaoEuros } from "./formato.js";
import { media, soma, dividir, ultimo, numeros, linhas } from "./dados.js";

/* ---------- Auxiliares ---------- */

const col = (rows, c) => rows.map(r => r[c] ?? null);
const epocasDe = rows => rows.map(r => r.epoca);
const contar = (rows, f) => rows.filter(f).length;
const com = (rows, c) => rows.filter(r => typeof r[c] === "number");
const plural = (n, s, p) => `${n} ${n === 1 ? s : p}`;
const fimEpoca = e => `30/06/20${e.slice(-2)}`;
const intervaloTexto = rows => (rows.length ? (rows.length === 1 ? rows[0].epoca : `${rows[0].epoca}–${ultimo(rows).epoca}`) : "");

/** Gráfico temporal genérico: uma série por coluna, épocas no eixo x */
function temporal(rows, series, { tipo = "bar", ...op } = {}) {
  const datasets = series.map(s => {
    const dados = s.calcular ? rows.map(s.calcular) : col(rows, s.col);
    const ds = (s.tipo ?? tipo) === "line"
      ? linha(s.rotulo, dados, s.papel, { oca: s.oca, tracejada: s.tracejada })
      : barras(s.rotulo, dados, s.papel, s.extra);
    if (s.tipo && s.tipo !== tipo) ds.type = s.tipo;
    if (s.stack) ds.stack = s.stack;
    if (s.fill) ds.fill = s.fill;
    if (s.cores) ds.backgroundColor = dados.map(s.cores);
    if (s.pontosCor) { ds.pointBackgroundColor = dados.map(s.pontosCor); ds.pointBorderColor = ds.pointBackgroundColor; }
    return ds;
  });
  return { type: tipo, data: { labels: epocasDe(rows), datasets }, options: opcoes(op) };
}

const comReferencias = (config, linhas) => { config.options.plugins.referencias = { linhas }; return config; };

/* ---------- Evolução previsível da sociedade ----------
   Fonte: Relatório e Contas da SAD 2025/26, relatório de gestão («Orçamento época desportiva 2026-2027»,
   «Continuidade da atividade e perspetivas de reequilíbrio financeiro» e «Evolução previsível da sociedade»).
   Valores do orçamento aprovado pelo Conselho de Administração; não estão na base SQL. */
export const ORCAMENTO = [
  { rubrica: "Rendimentos operacionais (sem transferências)", fecho_2025_26: 15102461, previsao_2026_27: 15969405 },
  { rubrica: "Gastos com pessoal", fecho_2025_26: 21730779, previsao_2026_27: 19634443 },
  { rubrica: "Fornecimentos e serviços externos", fecho_2025_26: 8997162, previsao_2026_27: 7346755 },
  { rubrica: "Gastos operacionais (sem amortizações)", fecho_2025_26: 32308639, previsao_2026_27: 28369292 },
  { rubrica: "Resultado das operações com atletas", fecho_2025_26: 18763394, previsao_2026_27: 24622100 },
  { rubrica: "Amortizações", fecho_2025_26: 6964397, previsao_2026_27: 4967138 },
  { rubrica: "Encargos financeiros líquidos", fecho_2025_26: 5602741, previsao_2026_27: 5585847 },
  { rubrica: "Resultado antes de impostos", fecho_2025_26: -11009920, previsao_2026_27: 1669228 },
];
/** Saldo de transações e empréstimos de atletas (relatório de gestão de 2025/26) e valor orçamentado para 2026/27 */
export const SALDO_ATLETAS = [
  { epoca: "2021/22", saldo: 11389130 }, { epoca: "2022/23", saldo: 22922094 }, { epoca: "2023/24", saldo: 6867824 },
  { epoca: "2024/25", saldo: 27605726 }, { epoca: "2025/26", saldo: 18763394 }, { epoca: "2026/27 (orçamento)", saldo: 24622100, previsto: true },
];
const mediaHistorica = () => media(col(SALDO_ATLETAS.filter(r => !r.previsto), "saldo"));

/* ---------- Estrutura acionista ----------
   Fonte: Relatório e Contas da SAD 2025/26 — nota 1 (900 000 ações de 5 €: 610 533 da categoria A, detidas pelo
   Vitória Sport Clube, e 289 467 da categoria B) e relatório de gestão (V Sports com 29%, a passar para 46% com a
   compra ao Clube de ações representativas de 17% do capital). Não está na base SQL: são os valores do relatório. */
const ACOES_TOTAL = 900000, ACOES_CLUBE = 610533;
const PCT_CLUBE = (100 * ACOES_CLUBE) / ACOES_TOTAL; // 67,84%
const ACIONISTAS = {
  atual: [
    { acionista: "Vitória Sport Clube", categoria: "A", pct_capital: PCT_CLUBE },
    { acionista: "V Sports", categoria: "B", pct_capital: 29 },
    { acionista: "Outros acionistas", categoria: "B", pct_capital: 100 - PCT_CLUBE - 29 },
  ],
  operacao: [
    { acionista: "Vitória Sport Clube", categoria: "A", pct_capital: PCT_CLUBE - 17 },
    { acionista: "V Sports", categoria: "B", pct_capital: 46 },
    { acionista: "Outros acionistas", categoria: "B", pct_capital: 100 - PCT_CLUBE - 29 },
  ],
};

/** Percentagem escrita dentro de cada fatia (branco sobre preto, preto sobre amarelo e cinzento) */
const rotulosFatias = {
  id: "rotulosFatias",
  afterDatasetsDraw(chart) {
    const { ctx } = chart, meta = chart.getDatasetMeta(0), ds = chart.data.datasets[0];
    ctx.save();
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    meta.data.forEach((arco, i) => {
      const v = ds.data[i];
      if (v < 8) return; // fatias pequenas: o valor fica na legenda e na dica
      const { x, y } = arco.tooltipPosition();
      ctx.font = letra(700, v > 20 ? 17 : 13);
      ctx.fillStyle = ds.texto[i];
      ctx.fillText(pct(v), x, y);
    });
    ctx.restore();
  },
};

/** Gráfico circular com as fatias destacadas (afastadas do centro e separadas por um traço branco) */
function circular(rows) {
  const cores = ["#111111", "#F5D510", "#A9A7A8"], texto = ["#FFFFFF", "#111111", "#111111"];
  return {
    type: "pie",
    data: {
      labels: rows.map(r => `${r.acionista} · ${pct(r.pct_capital)}`),
      datasets: [{ data: col(rows, "pct_capital"), backgroundColor: cores, texto, borderColor: "#FFFFFF", borderWidth: 3,
        offset: [6, 22, 30], hoverOffset: 30 }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, layout: { padding: 12 },
      plugins: {
        legend: { position: "bottom", labels: { color: cor("texto"), boxWidth: 16, boxHeight: 16, padding: 14, font: { size: 13, weight: "600" } } },
        tooltip: {
          backgroundColor: cor("dica-fundo"), titleColor: cor("dica-texto"), bodyColor: cor("dica-texto"), borderColor: cor("dica-borda"), borderWidth: 1, padding: 10,
          callbacks: { label: c => ` ${rows[c.dataIndex].acionista}: ${pct(rows[c.dataIndex].pct_capital)} do capital (ações da categoria ${rows[c.dataIndex].categoria})` },
        },
      },
    },
    plugins: [rotulosFatias],
  };
}

/** Composição de um grupo de rubricas (consulta 59): barras horizontais, 2024/25 a cinzento claro e 2025/26 a escuro */
function composicao(rows) {
  const cfg = {
    type: "bar",
    data: { labels: col(rows, "rubrica").map(r => r.replace("Direitos televisivos", "Direitos de TV")), datasets: [
      barras("2025/26", col(rows, "valor_2025_26"), "tinta", { maxBarThickness: 14 }),
      barras("2024/25", col(rows, "valor_2024_25"), "cinza", { maxBarThickness: 14 }),
    ] },
    options: opcoes({ horizontal: true, min: 0 }),
  };
  cfg.options.scales.y.ticks.autoSkip = false;
  cfg.options.scales.y.ticks.callback = function (v) { const t = this.getLabelForValue(v); return t.length > 34 ? `${t.slice(0, 33)}…` : t; };
  return cfg;
}

/** Barras de uma só série: a vermelho (risco) ou a amarelo (alerta) os valores que cumprem uma condição */
const coresCondicao = (cond, alerta = "vermelho") => (v => (v !== null && cond(v) ? cor(alerta) : cor("tinta")));
/** Barras de resultados: verde quando positivo, vermelho quando negativo (a posição face ao zero repete a informação) */
const coresSinal = v => (v === null || v === 0 ? cor("cinza") : v < 0 ? cor("vermelho") : cor("verde"));

/* =====================================================================
   SECÇÕES
   ===================================================================== */

export const SECCOES = [
  { id: "geral", nome: "Início", intro: "Os principais indicadores financeiros da SAD na época em destaque: síntese, leitura da época, evolução, estrutura acionista e pontos de entrada para a análise." },
  { id: "previsao", nome: "Evolução Previsível", titulo: "Evolução Previsível da Sociedade", intro: "O que a Administração prevê para 2026/27 e para o plano de negócios 2026–2031, segundo o Relatório e Contas de 2025/26. São previsões e intenções, não resultados." },
  { id: "receitas", nome: "Receitas", intro: "A origem das receitas: a atividade corrente, a composição das vendas (incluindo os direitos de TV), as competições europeias e a venda de jogadores." },
  { id: "custos", nome: "Gastos", intro: "A evolução e a composição dos gastos operacionais: pessoal, fornecimentos e serviços externos, amortizações e outros gastos." },
  { id: "rentabilidade", nome: "Rentabilidade", intro: "Do resultado operacional ao resultado líquido: margens e peso das mais-valias nos resultados." },
  { id: "divida", nome: "Endividamento", intro: "Estrutura financeira (ativo, passivo e capitais próprios) e dívida financeira, encargos financeiros, fluxos de caixa e liquidez." },
  { id: "desporto", nome: "Futebol", intro: "Os resultados desportivos da equipa principal e a sua relação com os gastos." },
  { id: "cenarios", nome: "Cenários", intro: "Simulações do projeto SQL. São ilustrativas: dependem de pressupostos sobre contratos e classificações." },
  { id: "solucoes", nome: "Soluções", intro: "Propostas para a sustentabilidade financeira da SAD, a partir dos indicadores da última época disponível. Cada proposta junta o diagnóstico, as medidas e os indicadores a acompanhar." },
  { id: "sql", nome: "Consultas SQL", intro: "As consultas do projeto SQL sobre as contas da SAD e as consultas complementares do painel: objetivo, código, técnicas e resultado." },
  { id: "metodologia", nome: "Metodologia e Fontes", intro: "Fontes, tratamento dos dados, critérios de comparação, convenções e limitações." },
];

/** Subgrupos dentro de uma secção: [chave, título, texto]. Os painéis sem grupo ficam no último. */
export const GRUPOS = {
  divida: [
    ["estrutura", "Estrutura Financeira", "O que a SAD detém, o que deve e a diferença entre ambos: capitais próprios, autonomia, solvabilidade e endividamento."],
    ["financiamento", "Dívida, Encargos Financeiros e Liquidez", "A parte remunerada do passivo, o seu custo, os instrumentos utilizados e a capacidade de cumprir os compromissos."],
  ],
};

/* =====================================================================
   VISUALIZAÇÕES
   Campos: id, seccao, consulta, pergunta, descricao, nota, largo, construir(rows), conclusao(rows),
           temporal (true = filtra pelo intervalo de épocas), tabela (true = mostra como tabela)
   ===================================================================== */

export const PAINEIS = [
  /* ---------------- Visão geral ---------------- */
  {
    id: "dependencia-vendas", seccao: "rentabilidade", consulta: 2, largo: true, temporal: true,
    pergunta: "A SAD consegue ter lucro sem vender jogadores?",
    descricao: "Resultado líquido com e sem as mais-valias líquidas da venda de jogadores.",
    construir: rows => temporal(rows, [
      { col: "rl", rotulo: "Resultado líquido", papel: "tinta", cores: coresSinal },
      { col: "rl_sem_mais_valias", rotulo: "Sem mais-valias", papel: "cinza" },
    ]),
    conclusao: rows => {
      const neg = contar(rows, r => r.rl_sem_mais_valias < 0);
      const soVendas = contar(rows, r => r.leitura);
      return `Sem mais-valias, o resultado seria negativo em ${neg} de ${rows.length} épocas. ` +
        `Em ${plural(soVendas, "época", "épocas")}, houve lucro apenas porque as mais-valias superaram esse défice.`;
    },
  },

  /* ---------------- Receitas e transferências ---------------- */
  {
    id: "rendimentos", seccao: "receitas", consulta: 57, largo: true, temporal: true,
    pergunta: "Quanto dos rendimentos vem de fora da operação corrente?",
    descricao: "Rendimentos operacionais da SAD por rubrica. A rubrica «Outros rendimentos» inclui os ganhos com a alienação de passes.",
    construir: rows => temporal(rows, [
      { col: "vendas_servicos", rotulo: "Vendas e serviços prestados", papel: "tinta" },
      { col: "outros_rendimentos", rotulo: "Outros rendimentos (inclui mais-valias)", papel: "cinza-escuro" },
      { col: "subsidios", rotulo: "Subsídios à exploração", papel: "cinza" },
    ], { empilhado: true }),
    conclusao: rows => {
      const u = ultimo(rows);
      return `Em média, ${pct(media(col(rows, "outros_rendimentos_pct")))} dos rendimentos operacionais vieram de outros rendimentos` +
        (u ? `; em ${u.epoca}, ${pct(u.outros_rendimentos_pct)}.` : ".");
    },
  },
  {
    id: "valor-europa", seccao: "receitas", consulta: 21,
    pergunta: "Quanto vale uma época europeia?",
    descricao: "Vendas e serviços prestados e resultado líquido médios da SAD por tipo de época (2013/14 a 2025/26).",
    construir: rows => {
      const labels = rows.map(r => r.tipo.replace(/^\d+\.\s*/, ""));
      const cfg = {
        type: "bar",
        data: { labels, datasets: [barras("Vendas e serviços prestados (média)", col(rows, "receita_media"), "tinta"), barras("Resultado líquido (média)", col(rows, "rl_medio"), "cinza")] },
        options: opcoes(),
      };
      cfg.options.plugins.tooltip.callbacks.footer = i => `${plural(rows[i[0].dataIndex].epocas, "época", "épocas")}: ${rows[i[0].dataIndex].lista}`;
      return cfg;
    },
    conclusao: rows => {
      const g = rows[0], s = ultimo(rows);
      return `Nas épocas com fase de grupos, as vendas e serviços prestados foram em média de ${euros(g.receita_media)}, contra ${euros(s.receita_media)} nas épocas sem Europa; ` +
        `o resultado líquido médio foi de ${euros(g.rl_medio)}, contra ${euros(s.rl_medio)}.`;
    },
    nota: "Não depende do intervalo de épocas: cada grupo agrega todas as épocas desse tipo. Médias de poucas épocas, que não isolam outros fatores (por exemplo, as vendas de jogadores).",
  },
  {
    id: "vendas-por-euro", seccao: "receitas", consulta: 54, temporal: true,
    pergunta: "As vendas de jogadores superam as vendas e serviços prestados?",
    descricao: "Vendas brutas de jogadores por cada euro de receita da atividade corrente (direitos de TV, bilheteira, patrocínios, quotização).",
    construir: rows => comReferencias(temporal(rows, [
      { col: "vendas_por_euro_de_receita", rotulo: "Vendas por euro de receita", papel: "cinza" },
      { col: "media_movel_3_epocas", rotulo: "Média móvel (3 épocas)", papel: "tinta", tipo: "line" },
    ], { unidade: "x", min: 0 }), [{ valor: 1, rotulo: "Vendas = receitas" }]),
    conclusao: rows => `As vendas superaram as receitas da atividade corrente em ${contar(rows, r => r.vendas_por_euro_de_receita > 1)} de ${rows.length} épocas` +
      (rows.length ? `; em ${ultimo(rows).epoca}, ${racio(ultimo(rows).vendas_por_euro_de_receita)} € de vendas por cada euro de receita.` : "."),
  },
  {
    id: "mais-valias", seccao: "receitas", consulta: 12, temporal: true,
    pergunta: "Quanto das vendas de jogadores se transforma em mais-valia?",
    descricao: "Vendas brutas e mais-valias líquidas (depois do valor contabilístico e dos custos da venda).",
    construir: rows => {
      const cfg = temporal(rows, [
        { col: "vendas_brutas", rotulo: "Vendas brutas", papel: "tinta" },
        { col: "mais_valias_liquidas", rotulo: "Mais-valias líquidas", papel: "cinza-escuro" },
      ]);
      cfg.options.plugins.tooltip.callbacks.footer = i => `Mais-valias = ${pct(rows[i[0].dataIndex].mais_valias_sobre_vendas_pct)} das vendas`;
      return cfg;
    },
    conclusao: rows => {
      const v = soma(col(rows, "vendas_brutas")), m = soma(col(rows, "mais_valias_liquidas"));
      return `Em ${intervaloTexto(rows)}, a SAD vendeu ${euros(v)} em jogadores e ficou com ${euros(m)} de mais-valias (${pct(100 * dividir(m, v))}).`;
    },
  },
  {
    id: "reservas-ocultas", seccao: "receitas", consulta: 41, temporal: true,
    pergunta: "Por quanto se vende um jogador face ao valor no balanço?",
    descricao: "Múltiplo de venda: vendas brutas a dividir pelo valor contabilístico dos jogadores vendidos.",
    construir: rows => temporal(rows, [{ col: "multiplo_de_venda", rotulo: "Múltiplo de venda", papel: "tinta" }], { unidade: "x", legenda: false }),
    conclusao: rows => {
      const v = soma(col(rows, "vendas_brutas")), c = soma(col(rows, "valor_contabilistico_vendido"));
      return `No conjunto de ${intervaloTexto(rows)}, os jogadores vendidos renderam ${vezes(dividir(v, c))} o valor por que estavam registados no balanço.`;
    },
    nota: "O balanço regista os passes ao custo de aquisição: os jogadores formados no clube têm um valor contabilístico quase nulo.",
  },
  {
    id: "custo-vendas", seccao: "receitas", consulta: 46, temporal: true,
    pergunta: "Quanto das vendas fica com intermediários e terceiros?",
    descricao: "Custo das vendas (comissões, direitos de terceiros) em percentagem das vendas brutas.",
    filtrar: rows => rows.filter(r => /^\d{4}\/\d{2}$/.test(r.epoca)),
    construir: rows => temporal(rows, [{ col: "custo_vendas_pct", rotulo: "Custo das vendas / vendas", papel: "cinza-escuro" }], { unidade: "pct", legenda: false, min: 0 }),
    conclusao: (rows, todas) => {
      const d = todas.filter(r => r.epoca.startsWith("dívida"));
      const ud = ultimo(d);
      if (!rows.length) return "";
      return `O peso passou de ${pct(rows[0].custo_vendas_pct)} (${rows[0].epoca}) para ${pct(ultimo(rows).custo_vendas_pct)} (${ultimo(rows).epoca})` +
        (ud ? `. A dívida a intermediários desportivos era de ${euros(ud.custo_vendas)} a ${ud.epoca.replace("dívida ", "")}.` : ".");
    },
  },
  {
    id: "passes", seccao: "receitas", consulta: 40, temporal: true,
    pergunta: "A SAD investe em passes mais do que amortiza?",
    descricao: "Aquisições e amortizações de passes, e valor do plantel no balanço.",
    construir: rows => temporal(rows, [
      { col: "aquisicoes", rotulo: "Aquisições", papel: "tinta" },
      { col: "amortizacoes", rotulo: "Amortizações", papel: "cinza" },
      { col: "valor_contabilistico_plantel", rotulo: "Plantel no balanço", papel: "cinza-escuro", tipo: "line", oca: true },
    ]),
    conclusao: rows => `Investimento líquido em ${intervaloTexto(rows)}: ${euros(soma(col(rows, "investimento_liquido")))}. ` +
      `O plantel valia ${euros(ultimo(rows)?.valor_contabilistico_plantel)} no balanço em ${ultimo(rows)?.epoca}.`,
  },
  /* ---------------- Custos e pessoal ---------------- */
  {
    id: "gastos-rubricas", seccao: "custos", consulta: 58, largo: true, temporal: true,
    pergunta: "Que gastos cresceram mais?",
    descricao: "Gastos operacionais da SAD por rubrica.",
    construir: rows => temporal(rows, [
      { col: "pessoal", rotulo: "Pessoal", papel: "tinta" },
      { col: "fse", rotulo: "Fornecimentos e serviços externos", papel: "cinza-escuro" },
      { col: "depreciacoes", rotulo: "Depreciações e amortizações", papel: "cinza" },
      { calcular: r => (r.mercadorias ?? 0) + (r.outros_gastos ?? 0) + (r.imparidades_provisoes ?? 0), rotulo: "Outros gastos", papel: "cinza-claro" },
    ], { empilhado: true }),
    conclusao: rows => {
      if (rows.length < 2) return "";
      const a = rows[0], b = ultimo(rows);
      const fator = dividir(b.total_gastos, a.total_gastos);
      const evolucao = fator >= 1.05 ? `multiplicaram-se por ${decimal(Math.round(10 * fator) / 10)}`
        : fator <= 0.95 ? `diminuíram ${pct(100 * (1 - fator))}` : "mantiveram-se praticamente estáveis";
      return `Os gastos operacionais passaram de ${euros(a.total_gastos)} (${a.epoca}) para ${euros(b.total_gastos)} (${b.epoca}): ${evolucao}. ` +
        `Os gastos com pessoal representam ${pct(b.pessoal_pct)} do total.`;
    },
    nota: "«Outros gastos» agrega custo das mercadorias vendidas, outros gastos e perdas, imparidades e provisões.",
  },
  {
    id: "gastos-vs-receitas", seccao: "custos", consulta: 56, largo: true, temporal: true,
    pergunta: "As receitas e as vendas de jogadores cobrem os gastos?",
    descricao: "Gastos operacionais (à esquerda), face às receitas da atividade corrente somadas às mais-valias com jogadores (à direita).",
    construir: rows => {
      const cfg = temporal(rows, [
        { col: "gastos_operacionais", rotulo: "Gastos operacionais", papel: "tinta", stack: "gastos" },
        { col: "receitas_operacao", rotulo: "Receitas da atividade corrente", papel: "cinza-escuro", stack: "receitas" },
        { col: "receitas_transferencias", rotulo: "Mais-valias com jogadores", papel: "cinza", stack: "receitas" },
      ], { empilhado: true });
      cfg.options.plugins.tooltip.callbacks.footer = i => `Saldo: ${euros(rows[i[0].dataIndex].saldo_com_receitas_operacao)}`;
      return cfg;
    },
    conclusao: rows => `Mesmo com as mais-valias, o saldo foi negativo em ${contar(rows, r => r.saldo_com_receitas_operacao < 0)} de ${rows.length} épocas. ` +
      `As mais-valias cobriram entre ${pct(Math.min(...numeros(col(rows, "transferencias_cobrem_pct"))))} e ${pct(Math.max(...numeros(col(rows, "transferencias_cobrem_pct"))))} dos gastos.`,
  },
  {
    id: "custos-fixos", seccao: "custos", largo: true, consulta: 42, temporal: true,
    pergunta: "As vendas e serviços prestados cobrem os gastos de estrutura?",
    descricao: "Vendas e serviços prestados em percentagem dos gastos de estrutura (gastos com pessoal, fornecimentos e serviços externos, depreciações e amortizações).",
    construir: rows => comReferencias(temporal(rows, [
      { col: "cobertura_pct", rotulo: "Vendas / gastos de estrutura", papel: "cinza-escuro" },
    ], { unidade: "pct", legenda: false, min: 0, max: 120 }), [{ valor: 100, rotulo: "Cobertura total" }]),
    conclusao: rows => (contar(rows, r => r.cobertura_pct >= 100) === 0
      ? `Em nenhuma das ${plural(rows.length, "época", "épocas")} as vendas e serviços prestados cobriram os gastos de estrutura. `
      : `As vendas e serviços prestados cobriram os gastos de estrutura em ${contar(rows, r => r.cobertura_pct >= 100)} de ${rows.length} épocas. `) +
      `Défice médio antes de vendas: ${euros(media(col(rows, "defice_antes_de_vendas")))} por época.`,
  },
  {
    id: "uefa", seccao: "custos", consulta: 45, temporal: true,
    pergunta: "A SAD cumpriria o limite de custos do plantel da UEFA?",
    descricao: "Remunerações do plantel e amortizações de passes, em percentagem das receitas acrescidas da média de três épocas das mais-valias.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "racio_pct", rotulo: "Rácio de custos do plantel", papel: "tinta", cores: coresCondicao(v => v > 70) },
    ], { unidade: "pct", legenda: false, min: 0 }), [{ valor: 70, rotulo: "Limite de 70%" }]),
    conclusao: rows => `Acima de 70% em ${contar(rows, r => r.racio_pct > 70)} de ${rows.length} épocas` +
      (rows.length ? `; em ${ultimo(rows).epoca}, ${pct(ultimo(rows).racio_pct)}.` : "."),
    nota: "Aproximação ao regulamento da UEFA (rácio de custos do plantel), sem as comissões de intermediários. Nas duas primeiras épocas, a média das mais-valias usa menos de três épocas.",
  },
  {
    id: "funcionarios", seccao: "custos", consulta: 31, largo: true, temporal: true,
    pergunta: "A estrutura cresceu mais depressa do que a equipa?",
    descricao: "Funcionários da SAD (média anual) por categoria.",
    construir: rows => temporal(rows, [
      { col: "jogadores", rotulo: "Jogadores", papel: "tinta" },
      { col: "treinadores", rotulo: "Treinadores", papel: "cinza-escuro" },
      { col: "staff", rotulo: "Apoio e outro pessoal", papel: "cinza" },
    ], { empilhado: true, unidade: "int", tooltipUnidade: "int" }),
    conclusao: rows => {
      if (rows.length < 2) return "";
      const a = rows[0], b = ultimo(rows);
      return `De ${a.epoca} para ${b.epoca}: jogadores ${inteiro(a.jogadores)} → ${inteiro(b.jogadores)}; ` +
        `treinadores e restante pessoal ${inteiro(a.treinadores + a.staff)} → ${inteiro(b.treinadores + b.staff)}.`;
    },
  },
  {
    id: "nao-jogadores", seccao: "custos", consulta: 33, temporal: true,
    pergunta: "Quantos não-jogadores há por cada jogador?",
    descricao: "Treinadores, pessoal de apoio e restante pessoal por cada jogador.",
    construir: rows => comReferencias(temporal(rows, [{ col: "nao_jogadores_por_jogador", rotulo: "Não-jogadores por jogador", papel: "tinta" }],
      { tipo: "line", unidade: "rat", legenda: false, min: 0 }), [{ valor: 1, rotulo: "1 por jogador" }]),
    conclusao: rows => rows.length > 1 ? `Passou de ${decimal(rows[0].nao_jogadores_por_jogador)} para ${decimal(ultimo(rows).nao_jogadores_por_jogador)} não-jogadores por jogador.` : "",
  },
  {
    id: "remuneracoes", seccao: "custos", consulta: 32, temporal: true, largo: true,
    pergunta: "Qual é o gasto médio com cada jogador e com cada funcionário?",
    descricao: "Remuneração média anual por jogador e gasto médio com pessoal por funcionário.",
    construir: rows => temporal(rows, [
      { col: "remuneracao_media_jogador", rotulo: "Por jogador", papel: "tinta" },
      { col: "custo_por_funcionario", rotulo: "Por funcionário", papel: "cinza-escuro", oca: true },
    ], { tipo: "line", min: 0 }),
    conclusao: rows => {
      const j = com(rows, "remuneracao_media_jogador");
      if (!j.length) return "";
      const max = j.reduce((a, b) => (b.remuneracao_media_jogador > a.remuneracao_media_jogador ? b : a));
      return `A remuneração média por jogador atingiu ${euros(max.remuneracao_media_jogador)} em ${max.epoca}; em ${ultimo(j).epoca} foi ${euros(ultimo(j).remuneracao_media_jogador)}.`;
    },
  },

  /* ---------------- Balanço e dívida ---------------- */
  {
    id: "balanco", seccao: "divida", grupo: "estrutura", consulta: 7, largo: true, temporal: true,
    pergunta: "O passivo da SAD supera o ativo?",
    descricao: "Ativo e passivo a 30 de junho. A área a vermelho corresponde aos capitais próprios negativos (passivo superior ao ativo).",
    construir: rows => {
      const cfg = temporal(rows, [
        { col: "passivo_total", rotulo: "Passivo", papel: "tinta", fill: areaAcima(1) },
        { col: "ativo_total", rotulo: "Ativo", papel: "cinza-escuro", oca: true },
      ], { tipo: "line", min: 0 });
      cfg.options.plugins.tooltip.callbacks.footer = i => `Capitais próprios: ${euros(rows[i[0].dataIndex].capital_proprio)}`;
      return cfg;
    },
    ficha: {
      mede: "A evolução da posição financeira: o que a SAD detém (ativo), o que deve (passivo) e a diferença entre ambos (capitais próprios).",
      formula: "Capitais próprios = Ativo − Passivo",
      dados: "Consulta 7, sobre a tabela balanco (valores dos Relatórios e Contas a 30 de junho).",
      limitacoes: "O plantel está registado ao custo de aquisição: os jogadores formados no clube têm valor contabilístico quase nulo, pelo que o ativo subestima o valor de mercado.",
    },
    conclusao: rows => `Capitais próprios negativos em ${contar(rows, r => r.capital_proprio < 0)} de ${rows.length} épocas` +
      (rows.length ? `; ${euros(ultimo(rows).capital_proprio)} a ${fimEpoca(ultimo(rows).epoca)}.` : "."),
  },
  {
    id: "racios", seccao: "divida", grupo: "financiamento", consulta: 29, temporal: true,
    pergunta: "A SAD consegue pagar o que deve a curto prazo?",
    descricao: "Liquidez geral: ativo corrente a dividir pelo passivo corrente, a 30 de junho.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "liquidez_geral", rotulo: "Liquidez geral", papel: "tinta", cores: coresCondicao(v => v < 1) },
    ], { unidade: "rat", legenda: false, min: 0 }), [{ valor: 1, rotulo: "Limiar = 1" }]),
    conclusao: rows => `Liquidez geral abaixo de 1 em ${contar(rows, r => r.liquidez_geral < 1)} de ${rows.length} épocas` +
      (rows.length ? `; ${racio(ultimo(rows).liquidez_geral)} em ${ultimo(rows).epoca}.` : "."),
    ficha: {
      mede: "Se os ativos que se convertem em meios líquidos no prazo de um ano chegam para pagar as dívidas que vencem no mesmo prazo.",
      formula: "Ativo corrente ÷ Passivo corrente",
      dados: "Tabela balanco_sad_rc (Relatórios e Contas da SAD).",
      limitacoes: "O ativo corrente inclui valores a receber de vendas de jogadores, cuja cobrança pode ser antecipada (factoring) e já estar comprometida.",
    },
  },
  {
    id: "divida-financeira", seccao: "divida", consulta: 27, temporal: true,
    pergunta: "Quanto cresceu a dívida financeira?",
    descricao: "Dívida financeira da SAD a 30 de junho (empréstimos, factoring, locações).",
    construir: rows => temporal(rows, [{ col: "financiamentos", rotulo: "Dívida financeira", papel: "tinta" }], { legenda: false }),
    conclusao: rows => {
      const v = com(rows, "financiamentos");
      if (v.length < 2) return "";
      const min = v.reduce((a, b) => (b.financiamentos < a.financiamentos ? b : a));
      if (min === ultimo(v)) return `Mínimo do intervalo em ${min.epoca}: ${euros(min.financiamentos)}.`;
      const f = dividir(ultimo(v).financiamentos, min.financiamentos);
      return `Do mínimo de ${euros(min.financiamentos)} (${min.epoca}) para ${euros(ultimo(v).financiamentos)} (${ultimo(v).epoca})` +
        (f >= 1.5 ? `: multiplicou-se por ${decimal(Math.round(10 * f) / 10)}.` : ".");
    },
  },
  {
    id: "taxas", seccao: "divida", consulta: 52, temporal: true,
    pergunta: "O Vitória paga juros acima do mercado?",
    descricao: "Taxa de juro implícita da dívida da SAD contra referências de mercado (%).",
    construir: rows => temporal(rows, [
      { col: "vitoria_implicita", rotulo: "Vitória (taxa implícita)", papel: "tinta" },
      { col: "euribor_12m", rotulo: "Euribor a 12 meses", papel: "cinza-escuro", oca: true },
      { col: "ot_portugal_10a", rotulo: "Obrigações do Tesouro a 10 anos", papel: "cinza", tracejada: true },
    ], { tipo: "line", unidade: "pct" }),
    conclusao: rows => {
      const v = com(rows, "vitoria_implicita");
      if (!v.length) return "";
      const u = ultimo(v), s = u.spread_vs_euribor;
      return `Em ${u.epoca}, a taxa implícita foi de ${pct(u.vitoria_implicita)}: ${pct(Math.abs(s)).replace("%", " p.p.")} ${s >= 0 ? "acima" : "abaixo"} da Euribor a 12 meses e ${vezes(u.vezes_estado_portugues)} a taxa das Obrigações do Tesouro a 10 anos.`;
    },
    nota: "Taxa implícita = juros dos financiamentos ÷ dívida financeira média.",
  },
  {
    id: "juros-receitas", seccao: "divida", consulta: 27, temporal: true,
    pergunta: "Que parte das vendas e serviços prestados é absorvida pelos juros?",
    descricao: "Juros dos financiamentos em percentagem das vendas e serviços prestados.",
    construir: rows => temporal(rows, [{ col: "juros_em_pct_receitas", rotulo: "Juros / vendas", papel: "tinta" }], { unidade: "pct", legenda: false, min: 0 }),
    conclusao: rows => rows.length ? `Em ${ultimo(rows).epoca}, os juros dos financiamentos (${euros(ultimo(rows).juros)}) corresponderam a ${pct(ultimo(rows).juros_em_pct_receitas)} das vendas e serviços prestados.` : "",
    nota: "Juros dos financiamentos (notas do Relatório e Contas). A rubrica «juros e gastos similares» da demonstração de resultados, usada nas consultas 8 e 30, é um valor diferente.",
  },
  {
    id: "curto-prazo", seccao: "divida", consulta: 28, temporal: true,
    pergunta: "Que parte da dívida vence em menos de um ano?",
    descricao: "Dívida financeira de curto prazo em percentagem do total.",
    construir: rows => temporal(rows, [{ col: "pct_curto_prazo", rotulo: "Curto prazo", papel: "tinta", cores: coresCondicao(v => v > 50, "amarelo") }],
      { unidade: "pct", legenda: false, min: 0, max: 100 }),
    conclusao: rows => rows.length ? `A ${fimEpoca(ultimo(rows).epoca)}, ${pct(ultimo(rows).pct_curto_prazo)} da dívida vencia em menos de um ano; a caixa era de ${euros(ultimo(rows).caixa)}.` : "",
  },
  {
    id: "instrumentos", seccao: "divida", consulta: 39,
    pergunta: "Com que instrumentos se financia a SAD?",
    descricao: "Dívida financeira por instrumento, nas três datas com detalhe nos Relatórios e Contas.",
    construir: rows => {
      const datas = [...new Set(rows.map(r => r.data_ref))];
      const grupo = i => (/^Empréstimos/.test(i) ? "Empréstimos" : /^Antecipação/.test(i) ? "Antecipação de direitos de TV" : i);
      const grupos = [...new Set(rows.map(r => grupo(r.instrumento)))];
      const papeis = ["tinta", "cinza-escuro", "cinza", "cinza-claro"];
      const datasets = grupos.map((g, k) => barras(g, datas.map(d => soma(rows.filter(r => r.data_ref === d && grupo(r.instrumento) === g).map(r => r.total)) || null), papeis[k % papeis.length]));
      const labels = datas.map(d => d.split("-").reverse().join("/"));
      return { type: "bar", data: { labels, datasets }, options: opcoes({ empilhado: true }) };
    },
    conclusao: rows => {
      const d = ultimo([...new Set(rows.map(r => r.data_ref))]);
      const ult = rows.filter(r => r.data_ref === d);
      const total = soma(ult.map(r => r.total));
      return `A ${d.split("-").reverse().join("/")}, a dívida financeira por instrumento somava ${euros(total)}; os empréstimos pesavam ${pct(soma(ult.filter(r => /^Empréstimos/.test(r.instrumento)).map(r => r.pct_da_divida)))}.`;
    },
    nota: "Usa a consulta 39 e não a 14, porque a consulta 14 mistura as datas de 30/06/2025 e 30/06/2026 sob o mesmo título.",
  },
  {
    id: "fluxos-caixa", seccao: "divida", consulta: 15, largo: true, temporal: true,
    pergunta: "Como se financiou cada época?",
    descricao: "Fluxos de caixa da SAD: operacional, de investimento (inclui vendas de passes) e de financiamento.",
    construir: rows => temporal(rows, [
      { col: "operacional", rotulo: "Operacional", papel: "tinta" },
      { col: "investimento", rotulo: "Investimento", papel: "cinza-escuro" },
      { col: "financiamento", rotulo: "Financiamento", papel: "cinza" },
    ]),
    conclusao: rows => `A operação consumiu caixa em ${contar(rows, r => r.operacional < 0)} de ${rows.length} épocas; ` +
      `a necessidade de tesouraria foi coberta com financiamento em ${contar(rows, r => /financiamento/.test(r.leitura))} e com vendas de passes ou desinvestimento em ${contar(rows, r => /vendas/.test(r.leitura))}.`,
    nota: "2024/25 com os valores originalmente publicados. O Relatório e Contas de 2025/26 reexpressou esses fluxos, com alterações de sinal (consulta 36).",
  },
  {
    id: "fundo-maneio", seccao: "divida", consulta: 38, temporal: true,
    pergunta: "O ativo corrente cobre o passivo corrente?",
    descricao: "Fundo de maneio: ativo corrente menos passivo corrente, a 30 de junho.",
    construir: rows => temporal(rows, [{ col: "fundo_maneio", rotulo: "Fundo de maneio", papel: "tinta", cores: coresSinal }], { legenda: false }),
    conclusao: rows => `Fundo de maneio negativo em ${contar(rows, r => r.fundo_maneio < 0)} de ${rows.length} épocas` +
      (rows.length ? `; ${euros(ultimo(rows).fundo_maneio)} em ${ultimo(rows).epoca}.` : "."),
  },
  {
    id: "divida-ebitda", seccao: "divida", consulta: 37, temporal: true,
    pergunta: "Quantos anos de EBITDA pagariam a dívida?",
    descricao: "Dívida financeira líquida ÷ EBITDA. As épocas com EBITDA negativo ficam sem barra, porque o rácio não tem significado.",
    construir: rows => comReferencias(temporal(rows, [{ col: "divida_liq_ebitda", rotulo: "Dívida líquida / EBITDA", papel: "tinta", cores: coresCondicao(v => v > 3) }],
      { unidade: "x", legenda: false }), [{ valor: 3, rotulo: "Referência: 3" }]),
    conclusao: rows => `EBITDA negativo em ${contar(rows, r => r.ebitda < 0)} de ${rows.length} épocas` +
      (!rows.length ? "." : ultimo(rows).divida_liq_ebitda === null
        ? `; em ${ultimo(rows).epoca}, o EBITDA foi negativo e o rácio não tem leitura.`
        : `; em ${ultimo(rows).epoca}, a dívida líquida equivalia a ${vezes(ultimo(rows).divida_liq_ebitda)} o EBITDA.`),
  },
  {
    id: "cobertura-juros", seccao: "divida", consulta: 30, tabela: true, temporal: true,
    pergunta: "O EBITDA chega para pagar os juros?",
    descricao: "Quantas vezes o EBITDA cobre os juros e gastos similares da demonstração de resultados. Abaixo de 3 vezes, a cobertura é considerada fraca (referência habitual em análise de crédito).",
    conclusao: rows => {
      const u = ultimo(rows);
      if (!u) return "";
      return `EBITDA negativo em ${contar(rows, r => r.ebitda < 0)} de ${rows.length} épocas; em ${u.epoca}, ` +
        (u.ebitda < 0 ? "o EBITDA foi negativo e não cobriu os juros." : `o EBITDA cobriu ${vezes(u.cobertura)} os juros e gastos similares.`);
    },
  },
  {
    id: "artigo-35", seccao: "divida", consulta: 43, tabela: true, temporal: true,
    pergunta: "A SAD perdeu metade do capital social?",
    descricao: "Artigo 35.º do Código das Sociedades Comerciais e parecer do auditor sobre a continuidade.",
    conclusao: rows => `Metade do capital perdida em ${contar(rows, r => r.metade_do_capital_perdida === "sim")} de ${rows.length} épocas; ` +
      `incerteza material sobre a continuidade em ${contar(rows, r => /Incerteza material/.test(r.parecer_auditor))}.`,
  },
  {
    id: "reexpressao", seccao: "divida", consulta: 36, tabela: true, largo: true,
    pergunta: "O que mudou com a reexpressão de 2024/25?",
    descricao: "Valores de 2024/25 no Relatório e Contas original e no de 2025/26 (aplicação do custo amortizado e correções).",
    conclusao: rows => {
      const fo = rows.find(r => r.indicador === "Fluxo de caixa operacional"), cp = rows.find(r => r.indicador === "Capital próprio" || r.indicador === "Capitais próprios");
      return fo && cp ? `O fluxo operacional passou de ${euros(fo.valor_original)} para ${euros(fo.valor_reexpresso)}; os capitais próprios, de ${euros(cp.valor_original)} para ${euros(cp.valor_reexpresso)}.` : "";
    },
  },

  {
    id: "painel-indicadores", seccao: "divida", grupo: "estrutura", consulta: 51, tabela: true, largo: true, temporal: true,
    pergunta: "Quadro de indicadores financeiros da SAD",
    descricao: "Margens, rentabilidade e rotação do ativo, peso dos fornecimentos e serviços externos, dívida face às vendas e fluxo de caixa operacional.",
    conclusao: rows => `A margem corrente sem vendas foi negativa em ${contar(rows, r => r.margem_corrente_sem_vendas_pct < 0)} de ${rows.length} épocas.`,
  },
  /* ---------------- Futebol ---------------- */
  {
    id: "classificacoes", seccao: "desporto", consulta: 20, largo: true, temporal: true,
    pergunta: "Como evoluiu a classificação na Liga?",
    descricao: "Lugar final na Liga em cada época (o 1.º lugar fica no topo). As épocas com competições europeias e troféus aparecem na dica.",
    construir: rows => {
      const cfg = temporal(rows, [{ col: "lugar", rotulo: "Lugar na Liga", papel: "tinta", tipo: "line" }],
        { tipo: "line", unidade: "lugar", tooltipUnidade: "lugar", legenda: false, inverter: true, min: 1, max: 18 });
      Object.assign(cfg.options.scales.y.ticks, { stepSize: 1, autoSkip: false, maxTicksLimit: 18 });
      cfg.options.scales.y.ticks.callback = v => (v === 1 || v % 3 === 0 ? `${v}.º` : "");
      cfg.data.datasets[0].pointRadius = 5;
      cfg.options.plugins.tooltip.callbacks.label = c => ` ${lugar(c.raw)} lugar`;
      cfg.options.plugins.tooltip.callbacks.footer = i => {
        const r = rows[i[0].dataIndex];
        return [r.europa && r.europa !== "—" ? r.europa : "Sem competições europeias", r.trofeu ? `Vencedor da ${r.trofeu}` : null].filter(Boolean);
      };
      cfg.options.plugins.valoresNasBarras = { formatar: v => `${v}.º` };
      return cfg;
    },
    conclusao: rows => {
      const v = com(rows, "lugar");
      if (!v.length) return "";
      const melhor = v.reduce((a, b) => (b.lugar < a.lugar ? b : a)), pior = v.reduce((a, b) => (b.lugar > a.lugar ? b : a));
      return `Melhor classificação: ${lugar(melhor.lugar)} lugar (${melhor.epoca}); pior: ${lugar(pior.lugar)} (${pior.epoca}). ` +
        `Lugar médio no intervalo: ${decimal(Math.round(10 * media(col(v, "lugar"))) / 10)}.º; ${plural(contar(v, r => r.europa && r.europa !== "—"), "época", "épocas")} com competições europeias.`;
    },
  },
  {
    id: "regressao", seccao: "desporto", consulta: 53, largo: true, temporal: true,
    pergunta: "Gastos de estrutura da SAD e classificação na Liga",
    descricao: "Gastos de estrutura (gastos com pessoal, fornecimentos e serviços externos, depreciações e amortizações) e classificação na Liga, com a reta de regressão linear. O 1.º lugar fica no topo.",
    construir: (rows, todas, ctx) => {
      const r0 = todas[0];
      const xs = numeros(col(todas, "despesas_m"));
      const xMin = Math.min(...xs), xMax = Math.max(...xs);
      const reta = [xMin, xMax].map(x => ({ x, y: r0.a_ordenada + r0.b_declive_por_m * x }));
      const pontos = rows.map(r => ({ x: r.despesas_m, y: r.lugar, epoca: r.epoca, prev: r.lugar_previsto }));
      const destaque = p => p.epoca === ctx.epoca;
      const op = opcoes({ unidade: "milhoes", legenda: true, indice: false });
      op.scales.y = { reverse: true, min: 1, max: 12, ticks: { stepSize: 1, callback: v => `${v}.º`, color: cor("suave") },
        title: { display: true, text: "Classificação na Liga", color: cor("suave") }, grid: { color: cor("grelha") }, border: { display: false } };
      op.scales.x.title = { display: true, text: "Gastos de estrutura (M€)", color: cor("suave") };
      op.scales.x.grid = { color: cor("grelha") };
      op.plugins.tooltip.callbacks = {
        title: i => i[0].raw.epoca ?? "Reta de regressão",
        label: c => (c.raw.epoca ? [` ${lugar(c.raw.y)} lugar`, ` Gastos de estrutura: ${milhoes(c.raw.x)}`, ` Previsto pela reta: ${decimal(c.raw.prev)}.º`] : ` ${decimal(c.raw.y)}.º previsto com ${milhoes(c.raw.x)}`),
      };
      return {
        type: "scatter",
        data: {
          datasets: [
            { label: "Épocas", data: pontos, backgroundColor: pontos.map(p => (destaque(p) ? cor("tinta") : cor("cinza-escuro"))),
              borderColor: pontos.map(p => (destaque(p) ? cor("fundo") : cor("cartao"))), borderWidth: pontos.map(p => (destaque(p) ? 3 : 1.5)),
              pointRadius: pontos.map(p => (destaque(p) ? 9 : 6.5)), pointHoverRadius: 9 },
            { label: "Reta de regressão", data: reta, type: "line", borderColor: cor("cinza-escuro"), borderDash: [6, 4], borderWidth: 2, pointRadius: 0, pointHoverRadius: 0 },
          ],
        },
        options: op,
        plugins: [rotulosPontos],
      };
    },
    conclusao: (rows, todas) => {
      const r = todas[0];
      const incluiZero = r.ic95_inferior <= 0 && r.ic95_superior >= 0;
      const lugares = Math.abs(r.b_declive_por_m * 10);
      return `R² = ${decimal(r.r_quadrado)} em ${r.n} épocas: a reta só acompanha ${pct(100 * r.r_quadrado)} da variação da classificação. ` +
        `Na reta, mais 10 M€ de gastos estão associados a ${decimal(lugares)} lugares ${r.b_declive_por_m < 0 ? "acima" : "abaixo"} na tabela, mas o intervalo de confiança a 95% do declive (${decimal(r.ic95_inferior)} a ${decimal(r.ic95_superior)})` +
        `${incluiZero ? " inclui o zero: não há evidência de associação" : " não inclui o zero"}.`;
    },
    nota: "A regressão usa as 13 épocas, independentemente do filtro, que apenas oculta pontos. Trata-se de uma associação, não de uma relação de causa e efeito.",
  },
  {
    id: "custo-ponto", seccao: "desporto", consulta: 49, temporal: true,
    pergunta: "Quanto custou cada ponto na Liga?",
    descricao: "Gastos com pessoal da SAD a dividir pelos pontos conquistados na Liga.",
    construir: rows => {
      const cfg = temporal(rows, [{ col: "custo_por_ponto", rotulo: "Gastos com pessoal por ponto", papel: "tinta" }], { legenda: false });
      cfg.options.plugins.tooltip.callbacks.footer = i => `${rows[i[0].dataIndex].pontos} pontos · ${lugar(rows[i[0].dataIndex].lugar)} lugar`;
      return cfg;
    },
    conclusao: rows => {
      if (!rows.length) return "";
      const max = rows.reduce((a, b) => (b.custo_por_ponto > a.custo_por_ponto ? b : a));
      const min = rows.reduce((a, b) => (b.custo_por_ponto < a.custo_por_ponto ? b : a));
      return `O ponto mais caro foi em ${max.epoca} (${euros(max.custo_por_ponto)}); o mais barato em ${min.epoca} (${euros(min.custo_por_ponto)}).`;
    },
  },
  {
    id: "espectadores", seccao: "desporto", consulta: 34, temporal: true,
    pergunta: "Quantos espectadores vão ao estádio?",
    descricao: "Média de espectadores por jogo em casa, na Liga.",
    construir: rows => {
      const cfg = temporal(rows, [{ col: "espectadores", rotulo: "Espectadores (média)", papel: "cinza-escuro" }], { unidade: "int", tooltipUnidade: "int", legenda: false, min: 0 });
      cfg.options.plugins.tooltip.callbacks.footer = i => {
        const r = rows[i[0].dataIndex];
        return r.espectadores === 0 ? "Jogos à porta fechada" : `Pessoal por espectador: ${euros(r.gasto_pessoal_por_espectador)}`;
      };
      return cfg;
    },
    conclusao: rows => {
      const v = rows.filter(r => r.espectadores > 0);
      if (!v.length) return "";
      const max = v.reduce((a, b) => (b.espectadores > a.espectadores ? b : a));
      const fechados = rows.filter(r => r.espectadores === 0).map(r => r.epoca);
      return `Máximo de ${inteiro(max.espectadores)} espectadores em ${max.epoca}.` + (fechados.length ? ` Em ${fechados.join(", ")}, os jogos foram à porta fechada.` : "");
    },
  },
  {
    id: "treinadores", seccao: "desporto", consulta: 50, factos: true, largo: true,
    pergunta: "Quantas vezes mudou o treinador?",
    descricao: "Rotação de treinadores da equipa principal desde 2015.",
    factos: rows => {
      const r = rows[0];
      return [
        { rotulo: "Mudanças de treinador", valor: inteiro(r.mudancas_desde_2015) },
        { rotulo: "Treinadores diferentes", valor: inteiro(r.treinadores_diferentes) },
        { rotulo: "Interinos", valor: inteiro(r.interinos) },
        { rotulo: "Mudanças por época", valor: decimal(r.media_por_epoca_2015_16_a_2025_26) },
      ];
    },
  },

  {
    id: "epocas-desporto", seccao: "desporto", consulta: 20, tabela: true, largo: true, temporal: true,
    pergunta: "Finanças e resultados desportivos, época a época",
    descricao: "Classificação, competições europeias, troféus, vendas e serviços prestados, gastos com pessoal e resultado líquido da SAD.",
    conclusao: rows => `No intervalo: ${plural(contar(rows, r => r.europa && r.europa !== "—"), "época", "épocas")} com competições europeias e ${plural(contar(rows, r => r.trofeu), "troféu", "troféus")}.`,
  },
  /* ---------------- Cenários ---------------- */
  {
    id: "equilibrio", seccao: "cenarios", consulta: 25, factos: true, largo: true,
    pergunta: "Quanto teria de render a venda de jogadores para a SAD atingir o equilíbrio?",
    descricao: "Ponto de equilíbrio de 2025/26, a partir do resultado com direitos de atletas e do resultado líquido.",
    factos: rows => {
      const r = rows[0];
      return [
        { rotulo: "Resultado com direitos de atletas 2025/26", valor: euros(r.resultado_com_jogadores_2025_26) },
        { rotulo: "Resultado líquido 2025/26", valor: euros(r.resultado_liquido_2025_26) },
        { rotulo: "Necessário para o equilíbrio", valor: euros(r.necessario_para_equilibrio), forte: true },
        { rotulo: "Em falta para o equilíbrio", valor: euros(r.falta_face_a_2025_26) },
      ];
    },
  },
  {
    id: "centralizacao", seccao: "cenarios", consulta: 55, largo: true,
    pergunta: "A centralização dos direitos de TV elimina o défice?",
    descricao: "Parte do défice antes de vendas (média de 2023/24 a 2025/26) que os direitos de TV centralizados cobririam, por valor do contrato e lugar na Liga. 100% significaria eliminar o défice sem vender jogadores.",
    construir: rows => {
      const contratos = [...new Set(rows.map(r => r.contrato))], lugares = [...new Set(rows.map(r => r.lugar))];
      const papeis = ["tinta", "cinza-escuro", "cinza"];
      const datasets = lugares.map((l, k) => barras(`${l} lugar`, contratos.map(c => rows.find(r => r.contrato === c && r.lugar === l)?.pct_do_defice_coberto ?? null), papeis[k % 3], { maxBarThickness: 22 }));
      const cfg = { type: "bar", data: { labels: contratos.map(c => `Contrato de ${c}`), datasets }, options: opcoes({ horizontal: true, unidade: "pct", min: 0, max: 100 }) };
      cfg.options.plugins.valoresNasBarras = { formatar: v => pct(v) };
      // Em ecrãs estreitos, o rótulo da linha sobrepunha-se às barras: fica só a marca de 100% no eixo
      cfg.options.plugins.referencias = { linhas: [{ valor: 100, rotulo: innerWidth < 640 ? "" : "100% = défice eliminado" }] };
      cfg.options.plugins.tooltip.callbacks.afterLabel = c => {
        const r = rows.find(x => `Contrato de ${x.contrato}` === c.label && `${x.lugar} lugar` === c.dataset.label);
        return r ? `   Ganho face à situação atual: ${euros(r.ganho_vs_atual)}\n   Mais-valias ainda necessárias: ${euros(r.mais_valias_necessarias)}` : "";
      };
      cfg.options.layout.padding.right = 12;
      return cfg;
    },
    conclusao: rows => {
      const max = rows.reduce((a, b) => (b.pct_do_defice_coberto > a.pct_do_defice_coberto ? b : a));
      return `Défice antes de vendas: ${euros(rows[0].defice_antes_vendas)} por época. No melhor cenário (${max.contrato}, ${max.lugar} lugar), a centralização cobre ${pct(max.pct_do_defice_coberto)}; ` +
        `seriam ainda necessários ${euros(max.mais_valias_necessarias)} de mais-valias.`;
    },
    nota: "Simulação ilustrativa: o modelo de repartição dos direitos de TV centralizados ainda não está definido.",
  },
  {
    id: "tv-por-lugar", seccao: "cenarios", consulta: 48,
    pergunta: "Quanto receberia o Vitória com os direitos de TV centralizados?",
    descricao: "Contrato de 250 M€: parte igual e parte por mérito (ilustrativa), por classificação na Liga, sem a componente de audiências.",
    construir: rows => {
      const labels = rows.map(r => lugar(r.lugar));
      const atual = rows[0].total_sem_audiencias - rows[0].vs_tv_atual;
      const cfg = {
        type: "bar",
        data: { labels, datasets: [
          barras("Parte igual", col(rows, "parte_igual"), "tinta", { stack: "tv" }),
          barras("Mérito (ilustrativo)", col(rows, "merito_ilustrativo"), "cinza", { stack: "tv" }),
        ] },
        options: opcoes({ empilhado: true }),
      };
      cfg.options.plugins.referencias = { linhas: [{ valor: atual, rotulo: `Direitos de TV atuais: ${euros(atual)}` }] };
      return cfg;
    },
    conclusao: rows => `Em qualquer posição entre o ${lugar(rows[0].lugar)} e o ${lugar(ultimo(rows).lugar)} lugar, o valor ficaria acima dos direitos de TV atuais: entre mais ${euros(ultimo(rows).vs_tv_atual)} e mais ${euros(rows[0].vs_tv_atual)}.`,
    nota: "Simulação ilustrativa da consulta 48.",
  },
  {
    id: "parte-igual", seccao: "cenarios", consulta: 26, tabela: true,
    pergunta: "Quanto vale a parte igual por clube?",
    descricao: "Parte igual estimada por clube para três valores do contrato centralizado (2028/29), face aos direitos de TV do Vitória em 2024/25.",
    conclusao: rows => `Só a parte igual valeria entre ${pct(rows[0].parte_igual_em_pct_do_atual)} e ${pct(ultimo(rows).parte_igual_em_pct_do_atual)} dos direitos de TV atuais.`,
  },

  /* ---------------- Evolução previsível da sociedade ---------------- */
  {
    id: "previsao-orcamento", seccao: "previsao", largo: true, fonteTexto: "Relatório e Contas 2025/26",
    dados: () => ORCAMENTO.map(r => ({ ...r, variacao: r.previsao_2026_27 - r.fecho_2025_26 })),
    pergunta: "O que muda do fecho de 2025/26 para o orçamento de 2026/27?",
    descricao: "Principais rubricas do orçamento para 2026/27, comparadas com os valores de fecho de 2025/26.",
    construir: rows => {
      const cfg = {
        type: "bar",
        data: { labels: col(rows, "rubrica"), datasets: [
          barras("Fecho 2025/26", col(rows, "fecho_2025_26"), "cinza", { maxBarThickness: 16 }),
          barras("Orçamento 2026/27", col(rows, "previsao_2026_27"), "tinta", { maxBarThickness: 16 }),
        ] },
        options: opcoes({ horizontal: true }),
      };
      cfg.options.scales.y.ticks.autoSkip = false;
      cfg.options.plugins.tooltip.callbacks.footer = i => `Variação: ${variacaoEuros(rows[i[0].dataIndex].variacao)}`;
      return cfg;
    },
    conclusao: rows => {
      const rai = rows.find(r => /antes de impostos/.test(r.rubrica)), g = rows.find(r => /Gastos operacionais/.test(r.rubrica)), a = rows.find(r => /atletas/.test(r.rubrica));
      return `O orçamento prevê um resultado antes de impostos de ${euros(rai.previsao_2026_27)}, contra ${euros(rai.fecho_2025_26)} em 2025/26: ` +
        `${euros(-g.variacao)} menos de gastos operacionais e ${euros(a.previsao_2026_27)} de resultado das operações com atletas.`;
    },
    nota: "Fonte: Relatório e Contas da SAD 2025/26 (orçamento da época 2026/27). Os rendimentos operacionais excluem as transferências, ao contrário do indicador homónimo do painel, que inclui as mais-valias.",
  },
  {
    id: "previsao-transferencias", seccao: "previsao", largo: true, fonteTexto: "Relatório e Contas 2025/26",
    dados: () => SALDO_ATLETAS,
    pergunta: "O valor previsto com a venda de jogadores é realista?",
    descricao: "Saldo de transações e empréstimos de atletas nas cinco épocas anteriores e valor do orçamento para 2026/27, com a média 2021/22–2025/26.",
    construir: rows => {
      const ds = barras("Saldo de transações e empréstimos", col(rows, "saldo"), "tinta", { maxBarThickness: 46 });
      ds.backgroundColor = rows.map(r => (r.previsto ? cor("amarelo") : cor("tinta")));
      ds.borderColor = rows.map(r => (r.previsto ? cor("contorno") : cor("tinta")));
      ds.borderWidth = rows.map(r => (r.previsto ? 1.5 : 0));
      const cfg = { type: "bar", data: { labels: col(rows, "epoca"), datasets: [ds] }, options: opcoes({ legenda: false, min: 0 }) };
      cfg.options.plugins.valoresNasBarras = { formatar: v => euros(v) };
      cfg.options.plugins.referencias = { linhas: [{ valor: mediaHistorica(), rotulo: `Média: ${euros(mediaHistorica())}` }] };
      return cfg;
    },
    conclusao: rows => {
      const prev = rows.find(r => r.previsto), hist = rows.filter(r => !r.previsto);
      const acima = hist.filter(r => r.saldo > prev.saldo);
      return `O orçamento conta com ${euros(prev.saldo)}, acima da média de ${euros(mediaHistorica())} das cinco épocas anteriores` +
        (acima.length ? `; só ${acima.map(r => `${r.epoca} (${euros(r.saldo)})`).join(" e ")} ${acima.length === 1 ? "superou" : "superaram"} esse valor.` : "; nenhuma época anterior atingiu esse valor.");
    },
    nota: "A amarelo, o valor orçamentado (previsão, não resultado). Fonte: Relatório e Contas da SAD 2025/26 (relatório de gestão).",
  },

  /* ---------------- Visão geral: estrutura acionista ---------------- */
  {
    id: "acionistas", seccao: "geral", bloco: "acionistas", fonteTexto: "Relatório e Contas 2025/26",
    dados: () => ACIONISTAS.atual,
    pergunta: "Quem são os acionistas da SAD?",
    descricao: "Repartição do capital social a 30 de junho de 2026 (900 000 ações). As ações da categoria A pertencem ao Vitória Sport Clube.",
    construir: rows => circular(rows),
    conclusao: () => `O Vitória Sport Clube detém ${pct(PCT_CLUBE)} do capital e a V Sports 29%; os restantes ${pct(100 - PCT_CLUBE - 29)} estão dispersos por outros acionistas.`,
    nota: "Fonte: Relatório e Contas da SAD 2025/26 (nota 1 e relatório de gestão). A parte dos outros acionistas é calculada por diferença.",
  },
  {
    id: "acionistas-operacao", seccao: "geral", bloco: "acionistas", fonteTexto: "Relatório e Contas 2025/26",
    dados: () => ACIONISTAS.operacao,
    pergunta: "E depois da operação com a V Sports?",
    descricao: "Repartição prevista se for aprovada a venda à V Sports, pelo Clube, de ações representativas de 17% do capital.",
    construir: rows => circular(rows),
    conclusao: () => `A V Sports passaria a deter 46% e o Clube ${pct(PCT_CLUBE - 17)}, mantendo a maioria do capital.`,
    nota: "Operação sujeita a aprovação das assembleias gerais e das entidades reguladoras. Não inclui o efeito da conversão em capital das entradas de 3,8 M€ previstas.",
  },

  /* ---------------- Visão geral: evolução ---------------- */
  {
    id: "geral-receitas-gastos", seccao: "geral", consultas: [103, 58], temporal: true,
    dados: () => {
      const g = new Map(linhas(58).map(r => [r.epoca, r.total_gastos]));
      return linhas(103).map(r => ({ epoca: r.epoca, rendimentos_operacionais: r.rendimentos_operacionais, vendas_servicos: r.vendas_servicos, gastos_operacionais: g.get(r.epoca) ?? null }));
    },
    pergunta: "Os rendimentos operacionais cobrem os gastos operacionais?",
    descricao: "Rendimentos operacionais (incluem as mais-valias com jogadores), vendas e serviços prestados e gastos operacionais, por época.",
    construir: rows => temporal(rows, [
      { col: "rendimentos_operacionais", rotulo: "Rendimentos operacionais", papel: "tinta" },
      { col: "gastos_operacionais", rotulo: "Gastos operacionais", papel: "cinza-escuro", oca: true },
      { col: "vendas_servicos", rotulo: "Vendas e serviços prestados", papel: "cinza", tracejada: true },
    ], { tipo: "line", min: 0 }),
    conclusao: rows => {
      const g = com(rows, "gastos_operacionais");
      if (!g.length) return "";
      const acima = contar(g, r => r.gastos_operacionais > r.rendimentos_operacionais);
      return `Os gastos superaram os rendimentos operacionais em ${acima} de ${g.length} épocas; ` +
        `passaram de ${euros(g[0].gastos_operacionais)} em ${g[0].epoca} para ${euros(ultimo(g).gastos_operacionais)} em ${ultimo(g).epoca}.`;
    },
  },
  {
    id: "geral-resultados", seccao: "geral", consulta: 102, temporal: true,
    pergunta: "Em que épocas a SAD teve lucro?",
    descricao: "Resultado líquido (barras: verde quando positivo, vermelho quando negativo) e resultado operacional (linha).",
    construir: rows => temporal(rows, [
      { col: "resultado_liquido", rotulo: "Resultado líquido", papel: "tinta", cores: coresSinal },
      { col: "resultado_operacional", rotulo: "Resultado operacional", papel: "tinta", tipo: "line", oca: true },
    ]),
    conclusao: rows => rows.length ? `Lucro em ${contar(rows, r => r.resultado_liquido > 0)} de ${rows.length} épocas; resultado líquido acumulado de ${euros(soma(col(rows, "resultado_liquido")))} em ${intervaloTexto(rows)}.` : "",
  },
  {
    id: "geral-estrutura", seccao: "geral", consulta: 101, temporal: true,
    pergunta: "O passivo é superior ao ativo?",
    descricao: "Ativo e passivo a 30 de junho (linhas) e capitais próprios (barras: vermelho quando negativos).",
    construir: rows => temporal(rows, [
      { col: "capital_proprio", rotulo: "Capitais próprios", papel: "tinta", cores: coresSinal },
      { col: "passivo_total", rotulo: "Passivo", papel: "tinta", tipo: "line" },
      { col: "ativo_total", rotulo: "Ativo", papel: "cinza-escuro", tipo: "line", oca: true },
    ]),
    conclusao: rows => rows.length ? `Capitais próprios negativos em ${contar(rows, r => r.capital_proprio < 0)} de ${rows.length} épocas; o passivo passou de ${euros(rows[0].passivo_total)} (${rows[0].epoca}) para ${euros(ultimo(rows).passivo_total)} (${ultimo(rows).epoca}).` : "",
  },
  {
    id: "geral-divida", seccao: "geral", consulta: 27, temporal: true,
    pergunta: "Quanto cresceu a dívida financeira?",
    descricao: "Dívida financeira a 30 de junho (empréstimos, factoring, antecipações de receitas e locações). Série disponível desde 2016/17.",
    construir: rows => temporal(rows, [{ col: "financiamentos", rotulo: "Dívida financeira", papel: "tinta" }], { legenda: false }),
    conclusao: rows => rows.length > 1 ? `De ${euros(rows[0].financiamentos)} em ${rows[0].epoca} para ${euros(ultimo(rows).financiamentos)} em ${ultimo(rows).epoca}; os juros dos financiamentos atingiram ${euros(ultimo(rows).juros)} na última época.` : "",
  },

  /* ---------------- Rentabilidade ---------------- */
  {
    id: "resultado-operacional", seccao: "rentabilidade", consulta: 102, temporal: true,
    pergunta: "A atividade operacional gera lucro sem a venda de jogadores?",
    descricao: "Resultado operacional da SAD, com e sem as mais-valias líquidas da alienação de passes.",
    construir: rows => temporal(rows, [
      { col: "resultado_operacional", rotulo: "Resultado operacional", papel: "tinta", cores: coresSinal },
      { col: "ro_sem_mais_valias", rotulo: "Sem mais-valias", papel: "cinza" },
    ]),
    conclusao: rows => {
      const s = com(rows, "ro_sem_mais_valias");
      return `Resultado operacional negativo em ${contar(rows, r => r.resultado_operacional < 0)} de ${rows.length} épocas; sem mais-valias, negativo em ${contar(s, r => r.ro_sem_mais_valias < 0)} de ${s.length}.`;
    },
    ficha: {
      mede: "O resultado da atividade antes de juros e impostos, separando o que vem da venda de jogadores.",
      formula: "Resultado operacional sem mais-valias = Resultado operacional − Mais-valias líquidas",
      dados: "Vista v_dr (rubrica resultado_operacional) e tabela transferencias. Consulta complementar D2.",
      limitacoes: "Os dados das mais-valias só existem desde 2017/18. É um resultado contabilístico: inclui amortizações e não mede a caixa gerada.",
    },
  },
  {
    id: "pessoal-rendimentos", seccao: "custos", consulta: 103, temporal: true,
    pergunta: "Que parte dos rendimentos é absorvida pelos gastos com pessoal?",
    descricao: "Gastos com pessoal em percentagem das vendas e serviços prestados e dos rendimentos operacionais (que incluem as mais-valias). A vermelho, as épocas acima de 100% das vendas.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "pessoal_sobre_vendas_pct", rotulo: "Sobre as vendas e serviços prestados", papel: "tinta", pontosCor: v => (v > 100 ? cor("vermelho") : cor("tinta")) },
      { col: "pessoal_sobre_rendimentos_pct", rotulo: "Sobre os rendimentos operacionais", papel: "cinza-escuro", oca: true },
    ], { tipo: "line", unidade: "pct", min: 0 }), [{ valor: 100, rotulo: "100%" }]),
    conclusao: rows => rows.length ? `Os gastos com pessoal superaram as vendas e serviços prestados em ${contar(rows, r => r.pessoal_sobre_vendas_pct > 100)} de ${rows.length} épocas. Em ${ultimo(rows).epoca}, corresponderam a ${pct(ultimo(rows).pessoal_sobre_vendas_pct)} das vendas e serviços prestados, mas a ${pct(ultimo(rows).pessoal_sobre_rendimentos_pct)} dos rendimentos operacionais; a diferença resulta das mais-valias e de outros rendimentos.` : "",
    ficha: {
      mede: "O peso dos gastos com pessoal face às vendas e serviços prestados e face à totalidade dos rendimentos operacionais.",
      formula: "Gastos com pessoal ÷ Vendas e serviços prestados · Gastos com pessoal ÷ (Vendas e serviços prestados + Subsídios à exploração + Outros rendimentos)",
      dados: "Tabela demonstracao_resultados (SAD). Consulta complementar D3; o primeiro rácio é também calculado pela consulta 3.",
      limitacoes: "A rubrica agregada de rendimentos operacionais só existe numa época; por isso, somam-se as componentes, como na consulta 57. «Outros rendimentos» inclui ganhos irregulares.",
    },
  },
  {
    id: "dependencia-extraordinarias", seccao: "rentabilidade", consulta: 54, temporal: true, largo: true,
    pergunta: "Quanto dependem as contas de receitas não recorrentes?",
    descricao: "Peso das mais-valias com jogadores no total formado pelas receitas da atividade corrente e pelas mais-valias.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "peso_mais_valias_no_total_pct", rotulo: "Peso das mais-valias", papel: "tinta", cores: coresCondicao(v => v > 50, "amarelo") },
    ], { unidade: "pct", legenda: false, min: 0, max: 100 }), [{ valor: 50, rotulo: "Metade" }]),
    conclusao: rows => `As mais-valias valeram mais de metade das receitas em ${contar(rows, r => r.peso_mais_valias_no_total_pct > 50)} de ${rows.length} épocas` +
      (rows.length ? `; ${pct(ultimo(rows).peso_mais_valias_no_total_pct)} em ${ultimo(rows).epoca}.` : "."),
    ficha: {
      mede: "A dependência de uma receita irregular: a venda de jogadores varia muito de época para época.",
      formula: "Mais-valias líquidas ÷ (Vendas e serviços prestados + Mais-valias líquidas)",
      dados: "Consulta 54 (vendas e serviços da SAD e tabela transferencias).",
      limitacoes: "Trata todas as mais-valias como não recorrentes; na prática, a venda de jogadores faz parte do modelo de negócio de muitos clubes portugueses.",
    },
  },

  /* ---------------- Endividamento: estrutura financeira ---------------- */
  {
    id: "autonomia", seccao: "divida", grupo: "estrutura", consulta: 101, temporal: true,
    pergunta: "Que parte do ativo é financiada por capitais próprios?",
    descricao: "Autonomia financeira da SAD. A vermelho, as épocas com capitais próprios negativos.",
    construir: rows => temporal(rows, [
      { col: "autonomia_pct", rotulo: "Autonomia financeira", papel: "tinta", cores: coresCondicao(v => v < 0) },
    ], { unidade: "pct", legenda: false }),
    conclusao: rows => `Autonomia negativa em ${contar(rows, r => r.autonomia_pct < 0)} de ${rows.length} épocas` +
      (rows.length ? `; ${pct(ultimo(rows).autonomia_pct)} em ${ultimo(rows).epoca}.` : "."),
    ficha: {
      mede: "A parte do ativo financiada pelos acionistas e não por terceiros. Abaixo de zero, o passivo é superior ao ativo.",
      formula: "Capitais próprios ÷ Ativo",
      dados: "Tabela balanco (SAD). Consulta complementar D1, confirmada pela coluna autonomia_pct da consulta 29.",
      limitacoes: "Depende do valor contabilístico do ativo, que subestima o valor de mercado do plantel.",
    },
  },
  {
    id: "solvabilidade", seccao: "divida", grupo: "estrutura", consulta: 101, temporal: true,
    pergunta: "Que parte do passivo está coberta por capitais próprios?",
    descricao: "Solvabilidade da SAD: capitais próprios em percentagem do passivo. A vermelho, as épocas com valores negativos.",
    construir: rows => temporal(rows, [
      { col: "solvabilidade_pct", rotulo: "Solvabilidade", papel: "tinta", cores: coresCondicao(v => v < 0) },
    ], { unidade: "pct", legenda: false }),
    conclusao: rows => {
      if (!rows.length) return "";
      const max = rows.reduce((a, b) => (b.solvabilidade_pct > a.solvabilidade_pct ? b : a));
      return `Máximo de ${pct(max.solvabilidade_pct)} em ${max.epoca}; ${pct(ultimo(rows).solvabilidade_pct)} em ${ultimo(rows).epoca}.`;
    },
    ficha: {
      mede: "Quantos euros de capitais próprios existem por cada euro de passivo. Valores negativos indicam capitais próprios negativos: o passivo é superior ao ativo.",
      formula: "Capitais próprios ÷ Passivo",
      dados: "Tabela balanco. Consulta complementar D1.",
      limitacoes: "Mede a solvabilidade contabilística, não a capacidade de cumprir os pagamentos a tempo (medida pela liquidez).",
    },
  },
  {
    id: "endividamento", seccao: "divida", grupo: "estrutura", consulta: 101, temporal: true, largo: true,
    pergunta: "Que parte do ativo é financiada por terceiros?",
    descricao: "Endividamento da SAD: passivo a dividir pelo ativo. Acima de 1, o passivo é superior ao ativo.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "endividamento", rotulo: "Endividamento", papel: "tinta" },
    ], { tipo: "line", unidade: "rat", legenda: false, min: 0 }), [{ valor: 1, rotulo: "Passivo = ativo" }]),
    conclusao: rows => {
      if (!rows.length) return "";
      const max = rows.reduce((a, b) => (b.endividamento > a.endividamento ? b : a));
      return `Acima de 1 em ${contar(rows, r => r.endividamento > 1)} de ${rows.length} épocas; máximo de ${racio(max.endividamento)} em ${max.epoca}.`;
    },
    ficha: {
      mede: "O peso do passivo face ao total do ativo.",
      formula: "Passivo ÷ Ativo",
      dados: "Tabela balanco. Consulta complementar D1 (confirmada pela consulta 29).",
      limitacoes: "Não distingue a dívida financeira (remunerada) de outras dívidas, como fornecedores ou adiantamentos.",
    },
  },

  /* ---------------- Rentabilidade: margens (D6) ---------------- */
  {
    id: "resultados-dr", seccao: "rentabilidade", consulta: 106, temporal: true, largo: true,
    pergunta: "Do resultado operacional ao resultado líquido: quanto pesam os juros e os impostos?",
    descricao: "Resultado operacional, resultado antes de impostos e resultado líquido da SAD, por época.",
    construir: rows => temporal(rows, [
      { col: "resultado_operacional", rotulo: "Resultado operacional", papel: "tinta" },
      { col: "resultado_antes_impostos", rotulo: "Resultado antes de impostos", papel: "cinza-escuro" },
      { col: "resultado_liquido", rotulo: "Resultado líquido", papel: "cinza" },
    ]),
    conclusao: rows => {
      const r = ultimo(rows);
      return r ? `Em ${r.epoca}, a passagem do resultado operacional (${euros(r.resultado_operacional)}) para o resultado antes de impostos (${euros(r.resultado_antes_impostos)}) reflete ${euros(r.resultado_antes_impostos - r.resultado_operacional)} de resultados financeiros, sobretudo juros.` : "";
    },
    ficha: {
      mede: "O efeito dos resultados financeiros (juros) e do imposto sobre o resultado da atividade.",
      formula: "Resultado antes de impostos = Resultado líquido − Imposto sobre o rendimento",
      dados: "Tabela demonstracao_resultados (SAD). Consulta complementar D6, conferida com v_kpis e D2.",
      limitacoes: "Em algumas épocas, a rubrica de juros é apresentada líquida dos juros obtidos.",
    },
  },
  {
    id: "margens", seccao: "rentabilidade", consulta: 106, temporal: true,
    pergunta: "Que margem fica por cada euro de rendimentos?",
    descricao: "Margem operacional e margem líquida sobre os rendimentos operacionais (que incluem as mais-valias).",
    construir: rows => comReferencias(temporal(rows, [
      { col: "margem_operacional_pct", rotulo: "Margem operacional", papel: "tinta" },
      { col: "margem_liquida_pct", rotulo: "Margem líquida", papel: "cinza-escuro", oca: true },
    ], { tipo: "line", unidade: "pct" }), [{ valor: 0, rotulo: "" }]),
    conclusao: rows => rows.length ? `Margem líquida negativa em ${contar(rows, r => r.margem_liquida_pct < 0)} de ${rows.length} épocas; ${pct(ultimo(rows).margem_liquida_pct)} em ${ultimo(rows).epoca}.` : "",
    ficha: {
      mede: "A parte dos rendimentos operacionais que se converte em resultado, antes (operacional) e depois (líquido) de juros e impostos.",
      formula: "Resultado operacional ÷ Rendimentos operacionais · Resultado líquido ÷ Rendimentos operacionais",
      dados: "Tabela demonstracao_resultados (SAD). Consulta complementar D6.",
      limitacoes: "Os rendimentos operacionais incluem as mais-valias com jogadores, muito irregulares: uma margem positiva pode depender de uma única venda.",
    },
  },

  /* ---------------- Composição (detalhe das notas do R&C 2025/26) ---------------- */
  {
    id: "composicao-vendas", seccao: "receitas", consulta: 59, largo: true,
    filtrar: rows => rows.filter(r => r.grupo === "Vendas e serviços prestados"),
    pergunta: "De onde vêm as vendas e serviços prestados?",
    descricao: "Composição das vendas e serviços prestados em 2024/25 e 2025/26 (nota 15 do Relatório e Contas de 2025/26). Só existe detalhe para estas duas épocas.",
    construir: rows => composicao(rows),
    conclusao: rows => {
      const tv = rows.find(r => /televisivos/.test(r.rubrica)), premios = rows.find(r => /^Prémios/.test(r.rubrica));
      const total = soma(col(rows, "valor_2025_26")), total24 = soma(col(rows, "valor_2024_25"));
      return tv ? `Os direitos de TV são a maior fonte: ${euros(tv.valor_2025_26)}, ${pct(100 * dividir(tv.valor_2025_26, total))} das vendas em 2025/26 (${pct(100 * dividir(tv.valor_2024_25, total24))} em 2024/25)` +
        (premios ? `. Os prémios de competições passaram de ${euros(premios.valor_2024_25)} para ${euros(premios.valor_2025_26)}.` : ".") : "";
    },
  },
  {
    id: "composicao-fse", seccao: "custos", consulta: 59,
    filtrar: rows => rows.filter(r => r.grupo === "Fornecimentos e serviços externos"),
    pergunta: "Em que se gastam os fornecimentos e serviços externos?",
    descricao: "Principais rubricas de fornecimentos e serviços externos em 2024/25 e 2025/26 (nota 17 do Relatório e Contas de 2025/26).",
    construir: rows => composicao(rows),
    conclusao: rows => {
      const maior = rows.reduce((a, b) => (b.valor_2025_26 > a.valor_2025_26 ? b : a));
      return `A maior rubrica em 2025/26 foi «${maior.rubrica}» (${euros(maior.valor_2025_26)}).`;
    },
  },
];

/** Escreve a época junto a cada ponto da dispersão (a época em destaque sempre; as outras se couberem) */
const rotulosPontos = {
  id: "rotulosPontos",
  afterDatasetsDraw(chart) {
    const meta = chart.getDatasetMeta(0), dados = chart.data.datasets[0].data;
    const raios = chart.data.datasets[0].pointRadius;
    const ctx = chart.ctx;
    const ocupados = meta.data.map(p => ({ x: p.x - 7, y: p.y - 7, w: 14, h: 14 }));
    const sobrepoe = (r, k) => ocupados.some((o, j) => j !== k && r.x < o.x + o.w && r.x + r.w > o.x && r.y < o.y + o.h && r.y + r.h > o.y);
    const ordem = meta.data.map((_, i) => i).sort((a, b) => (raios[b] > 8) - (raios[a] > 8));
    ctx.save();
    ctx.textBaseline = "middle";
    ordem.forEach(i => {
      const p = meta.data[i], forte = raios[i] > 8;
      ctx.font = letra(forte ? 600 : 400, 11.5);
      ctx.fillStyle = forte ? cor("texto") : cor("suave");
      const larg = ctx.measureText(dados[i].epoca).width;
      const direita = p.x + 12 + larg < chart.chartArea.right;
      const x = direita ? p.x + 11 : p.x - 11 - larg;
      const caixa = { x, y: p.y - 7, w: larg, h: 14 };
      if (!forte && sobrepoe(caixa, i)) return;
      ocupados.push(caixa);
      ctx.textAlign = "left";
      ctx.fillText(dados[i].epoca, x, p.y);
    });
    ctx.restore();
  },
};

/** Ordem de apresentação dentro de cada secção (pares lado a lado; os largos ocupam a linha toda) */
export const ORDEM = {
  geral: ["geral-receitas-gastos", "geral-resultados", "geral-estrutura", "geral-divida"],
  receitas: ["rendimentos", "composicao-vendas", "vendas-por-euro", "valor-europa", "mais-valias", "reservas-ocultas", "custo-vendas", "passes"],
  custos: ["gastos-rubricas", "custos-fixos", "composicao-fse", "pessoal-rendimentos", "gastos-vs-receitas", "uefa", "nao-jogadores", "funcionarios", "remuneracoes"],
  desporto: ["classificacoes", "regressao", "custo-ponto", "espectadores", "treinadores", "epocas-desporto"],
  cenarios: ["centralizacao", "tv-por-lugar", "parte-igual", "equilibrio"],
  previsao: ["previsao-orcamento", "previsao-transferencias"],
  rentabilidade: ["dependencia-vendas", "resultados-dr", "resultado-operacional", "margens", "dependencia-extraordinarias"],
  divida: ["balanco", "autonomia", "solvabilidade", "endividamento", "painel-indicadores",
    "divida-financeira", "juros-receitas", "taxas", "curto-prazo", "fluxos-caixa", "instrumentos", "fundo-maneio", "divida-ebitda", "racios",
    "cobertura-juros", "artigo-35", "reexpressao"],
};

/* =====================================================================
   SOLUÇÕES (propostas do autor)
   O diagnóstico, os indicadores e a prioridade são calculados a partir das consultas;
   as medidas são propostas, não dados. Usa-se sempre a última época disponível.
   ===================================================================== */

const rubrica59 = (q, grupo) => q(59).filter(r => r.grupo === grupo);

export const SOLUCOES = [
  {
    n: 1, area: "custos", titulo: "Ajustar os gastos de estrutura às receitas recorrentes", consultas: [42, 59],
    alta: ({ q }) => ultimo(q(42)).cobertura_pct < 100,
    diagnostico: ({ q }) => {
      const f = ultimo(q(42));
      return `Em ${f.epoca}, as vendas e serviços prestados (${euros(f.receitas)}) cobriram apenas ${pct(f.cobertura_pct)} dos gastos de estrutura (${euros(f.custos_fixos)}). ` +
        `O défice antes de vendas de jogadores foi de ${euros(f.defice_antes_de_vendas)}.`;
    },
    medidas: ({ q }) => {
      const fse = rubrica59(q, "Fornecimentos e serviços externos");
      const maior = fse.length ? fse.reduce((a, b) => (b.valor_2025_26 > a.valor_2025_26 ? b : a)) : null;
      return [
        "Definir um orçamento plurianual de gastos de estrutura indexado às vendas e serviços prestados, e não às mais-valias esperadas.",
        maior ? `Rever as rubricas de fornecimentos e serviços externos com maior peso, a começar por «${maior.rubrica}» (${euros(maior.valor_2025_26)} em 2025/26).` : "Rever as rubricas de fornecimentos e serviços externos com maior peso.",
      ];
    },
    indicadores: ({ q }) => {
      const f = ultimo(q(42));
      return [{ rotulo: "Vendas / gastos de estrutura", valor: pct(f.cobertura_pct), referencia: "100%" }];
    },
  },
  {
    n: 2, area: "custos", titulo: "Conter a massa salarial", consultas: [103, 45, 31],
    alta: ({ q }) => ultimo(q(103)).pessoal_sobre_vendas_pct > 100,
    diagnostico: ({ q }) => {
      const d = ultimo(q(103)), u = ultimo(q(45));
      return `Em ${d.epoca}, os gastos com pessoal (${euros(d.pessoal)}) corresponderam a ${pct(d.pessoal_sobre_vendas_pct)} das vendas e serviços prestados. ` +
        `O rácio de custos do plantel da UEFA foi de ${pct(u.racio_pct)}, ${u.racio_pct > 70 ? "acima" : "abaixo"} do limite de 70% (este rácio soma às receitas a média das mais-valias).`;
    },
    medidas: ({ q }) => {
      const f = q(31), a = f[f.length - 2], b = ultimo(f);
      return [
        "Fixar um teto para os gastos com pessoal em função das receitas recorrentes, com margem face ao limite de 70% da UEFA.",
        "Reforçar a componente variável dos contratos, ligada a objetivos desportivos e financeiros.",
        a && b ? `Rever o crescimento do quadro de pessoal: ${inteiro(a.funcionarios)} funcionários em ${a.epoca} e ${inteiro(b.funcionarios)} em ${b.epoca}.` : null,
      ].filter(Boolean);
    },
    indicadores: ({ q }) => [
      { rotulo: "Gastos com pessoal / vendas", valor: pct(ultimo(q(103)).pessoal_sobre_vendas_pct), referencia: "abaixo de 100%" },
      { rotulo: "Rácio de custos do plantel (UEFA)", valor: pct(ultimo(q(45)).racio_pct), referencia: "até 70%" },
    ],
  },
  {
    n: 3, area: "divida", titulo: "Reestruturar a dívida financeira", consultas: [52, 28, 27],
    alta: ({ q }) => ultimo(q(28)).pct_curto_prazo > 50 || ultimo(q(27)).juros_em_pct_receitas > 20,
    diagnostico: ({ q }) => {
      const t = ultimo(com(q(52), "vitoria_implicita")), c = ultimo(q(28)), j = ultimo(q(27));
      return `A dívida financeira era de ${euros(c.divida_financeira)} a ${fimEpoca(c.epoca)}, com ${pct(c.pct_curto_prazo)} a vencer em menos de um ano. ` +
        `A taxa de juro implícita foi de ${pct(t.vitoria_implicita)} (Euribor a 12 meses: ${pct(t.euribor_12m)}) e os juros absorveram ${pct(j.juros_em_pct_receitas)} das vendas e serviços prestados.`;
    },
    medidas: () => [
      "Negociar o alongamento dos prazos, para reduzir a parte da dívida que vence no próprio ano.",
      "Substituir, sempre que possível, o factoring e as antecipações de receitas por instrumentos de menor custo.",
      "Fixar um teto para os juros em percentagem das vendas e serviços prestados.",
    ],
    indicadores: ({ q }) => [
      { rotulo: "Taxa de juro implícita", valor: pct(ultimo(com(q(52), "vitoria_implicita")).vitoria_implicita), referencia: "aproximar das taxas de mercado" },
      { rotulo: "Dívida a menos de um ano", valor: pct(ultimo(q(28)).pct_curto_prazo), referencia: "até 50%" },
      { rotulo: "Juros / vendas", valor: pct(ultimo(q(27)).juros_em_pct_receitas), referencia: "até 20%" },
    ],
  },
  {
    n: 4, area: "divida", titulo: "Recapitalizar a SAD", consultas: [101, 43],
    alta: ({ q }) => ultimo(q(101)).capital_proprio < 0,
    diagnostico: ({ q }) => {
      const d = ultimo(q(101)), a = ultimo(q(43));
      return `A ${fimEpoca(d.epoca)}, os capitais próprios eram de ${euros(d.capital_proprio)} (autonomia financeira de ${pct(d.autonomia_pct)}). ` +
        (a.metade_do_capital_perdida === "sim" ? "Mais de metade do capital social está perdida (artigo 35.º do Código das Sociedades Comerciais)" : "Metade do capital social não está perdida") +
        (/Incerteza material/.test(a.parecer_auditor) ? " e o auditor assinala incerteza material sobre a continuidade." : ".");
    },
    medidas: () => [
      "Aumento de capital ou conversão de dívida em capital, para repor os capitais próprios acima de metade do capital social.",
      "Reservar parte dos resultados das épocas com mais-valias elevadas para reforçar os capitais próprios.",
    ],
    indicadores: ({ q }) => [
      { rotulo: "Capitais próprios", valor: euros(ultimo(q(101)).capital_proprio), referencia: `acima de ${euros(ultimo(q(43)).metade_capital_social)}` },
      { rotulo: "Autonomia financeira", valor: pct(ultimo(q(101)).autonomia_pct), referencia: "positiva" },
    ],
  },
  {
    n: 5, area: "divida", titulo: "Reforçar a tesouraria", consultas: [15, 29, 38],
    alta: ({ q }) => ultimo(q(29)).liquidez_geral < 1,
    diagnostico: ({ q }) => {
      const f = ultimo(q(15)), l = ultimo(q(29)), m = ultimo(q(38));
      return `Em ${f.epoca}, a atividade operacional ${f.operacional < 0 ? `consumiu ${euros(-f.operacional)}` : `gerou ${euros(f.operacional)}`} de caixa. ` +
        `A liquidez geral foi de ${racio(l.liquidez_geral)} e o prazo médio de recebimentos de ${inteiro(m.pmr_dias)} dias.`;
    },
    medidas: () => [
      "Manter um plano de tesouraria a 12 meses que antecipe os pagamentos de curto prazo.",
      "Reduzir o prazo de recebimento dos valores a receber, sobretudo das vendas de jogadores, sem recorrer a factoring caro.",
    ],
    indicadores: ({ q }) => [
      { rotulo: "Liquidez geral", valor: racio(ultimo(q(29)).liquidez_geral), referencia: "1 ou mais" },
      { rotulo: "Fluxo de caixa operacional", valor: euros(ultimo(q(15)).operacional), referencia: "positivo" },
      { rotulo: "Prazo médio de recebimentos", valor: `${inteiro(ultimo(q(38)).pmr_dias)} dias`, referencia: "a reduzir" },
    ],
  },
  {
    n: 6, area: "receitas", titulo: "Diversificar as receitas recorrentes", consultas: [59, 55],
    alta: () => false,
    diagnostico: ({ q }) => {
      const v = rubrica59(q, "Vendas e serviços prestados"), total = soma(col(v, "valor_2025_26"));
      const tv = v.find(r => /televisivos/.test(r.rubrica)), pr = v.find(r => /^Prémios/.test(r.rubrica)), bi = v.find(r => /^Bilheteira/.test(r.rubrica));
      return `Em 2025/26, os direitos de TV valeram ${pct(100 * dividir(tv.valor_2025_26, total))} das vendas e serviços prestados. ` +
        `Face a 2024/25, os prémios de competições ${pr.variacao_pct < 0 ? "caíram" : "subiram"} ${pct(Math.abs(pr.variacao_pct))} e a bilheteira, quotização e pack-sócio ${bi.variacao_pct < 0 ? "caíram" : "subiram"} ${pct(Math.abs(bi.variacao_pct))}.`;
    },
    medidas: ({ q }) => {
      const max = q(55).reduce((a, b) => (b.pct_do_defice_coberto > a.pct_do_defice_coberto ? b : a));
      return [
        "Reforçar as receitas comerciais menos dependentes dos resultados desportivos: patrocínios, bilheteira e venda de mercadorias.",
        `Preparar a centralização dos direitos de TV sem contar com ela para equilibrar as contas: no melhor cenário simulado cobre ${pct(max.pct_do_defice_coberto)} do défice antes de vendas.`,
      ];
    },
    indicadores: ({ q }) => {
      const v = rubrica59(q, "Vendas e serviços prestados"), tv = v.find(r => /televisivos/.test(r.rubrica));
      return [
        { rotulo: "Peso dos direitos de TV nas vendas", valor: pct(100 * dividir(tv.valor_2025_26, soma(col(v, "valor_2025_26")))), referencia: "a reduzir" },
        { rotulo: "Vendas e serviços prestados", valor: euros(soma(col(v, "valor_2025_26"))), referencia: "a aumentar" },
      ];
    },
  },
  {
    n: 7, area: "receitas", titulo: "Tornar a venda de jogadores mais eficiente", consultas: [46, 2, 41],
    alta: () => false,
    diagnostico: ({ q }) => {
      const c = ultimo(q(46).filter(r => /^\d{4}\/\d{2}$/.test(r.epoca))), r = q(2);
      return `Em ${c.epoca}, ${pct(c.custo_vendas_pct)} das vendas de jogadores foram para intermediários e terceiros. ` +
        `Sem mais-valias, o resultado foi negativo em ${contar(r, x => x.rl_sem_mais_valias < 0)} de ${r.length} épocas: a venda de jogadores fecha as contas todos os anos.`;
    },
    medidas: () => [
      "Reduzir o peso das comissões e dos direitos de terceiros nas vendas.",
      "Valorizar a formação: os jogadores formados no clube têm valor contabilístico quase nulo, pelo que a sua venda gera mais-valias quase integrais.",
      "Planear as vendas para que não sejam necessárias para pagar a estrutura de cada época.",
    ],
    indicadores: ({ q }) => {
      const c = ultimo(q(46).filter(r => /^\d{4}\/\d{2}$/.test(r.epoca))), m = ultimo(q(41));
      return [
        { rotulo: "Custo das vendas / vendas", valor: pct(c.custo_vendas_pct), referencia: "a reduzir" },
        { rotulo: "Múltiplo de venda", valor: `${decimal(m.multiplo_de_venda)}×`, referencia: "acima de 1" },
      ];
    },
  },
];
