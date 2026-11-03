// Definição de cada visualização: a pergunta a que responde, a consulta SQL de onde vem,
// como se desenha e a conclusão, calculada a partir dos dados filtrados.
// Nenhum valor é inventado aqui: tudo sai das linhas das consultas.

import { barras, linha, areaAcima, opcoes, cor } from "./graficos.js";
import { euros, pct, razao, vezes, racio, inteiro, decimal, lugar, milhoes, pp } from "./formato.js";
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
  { id: "geral", nome: "Visão geral", intro: "A situação financeira da SAD na época em destaque e a sua evolução: indicadores principais, leitura da época, tendências e pontos de entrada para a análise." },
  { id: "perguntas", nome: "Cinco perguntas", intro: "As perguntas de investigação do projeto, cada uma com o contexto, a resposta, os indicadores que a fundamentam, os gráficos e as limitações." },
  { id: "receitas", nome: "Receitas", intro: "A origem das receitas: a atividade corrente, a composição das vendas (incluindo os direitos de TV), as competições europeias e a venda de jogadores." },
  { id: "custos", nome: "Gastos", intro: "A evolução e a composição dos gastos operacionais: pessoal, fornecimentos e serviços externos, amortizações e outros gastos." },
  { id: "rentabilidade", nome: "Rentabilidade", intro: "Do resultado operacional ao resultado líquido: margens e peso das mais-valias nos resultados." },
  { id: "divida", nome: "Endividamento", intro: "Estrutura financeira (ativo, passivo e capitais próprios) e dívida financeira, encargos financeiros, fluxos de caixa e liquidez." },
  { id: "desporto", nome: "Desporto", intro: "A relação entre os gastos e os resultados desportivos." },
  { id: "cenarios", nome: "Cenários", intro: "Simulações do projeto SQL. São ilustrativas: dependem de pressupostos sobre contratos e classificações." },
  { id: "sql", nome: "Consultas SQL", intro: "As consultas do projeto SQL sobre as contas da SAD e as consultas complementares do painel: objetivo, código, técnicas e resultado." },
  { id: "metodologia", nome: "Metodologia e fontes", intro: "Fontes, tratamento dos dados, critérios de comparação, convenções e limitações." },
];

/** Subgrupos dentro de uma secção: [chave, título, texto]. Os painéis sem grupo ficam no último. */
export const GRUPOS = {
  divida: [
    ["estrutura", "Estrutura financeira", "O que a SAD detém, o que deve e a diferença entre ambos: capitais próprios, autonomia, solvabilidade e endividamento."],
    ["financiamento", "Dívida, encargos financeiros e liquidez", "A parte remunerada do passivo, o seu custo, os instrumentos utilizados e a capacidade de cumprir os compromissos."],
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
    id: "dependencia-vendas", seccao: "perguntas", questao: 1, consulta: 2, largo: true, temporal: true,
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
    id: "valor-europa", seccao: "perguntas", questao: 2, consulta: 21,
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
    id: "vendas-por-euro", seccao: "perguntas", questao: 2, consulta: 54, temporal: true,
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
    id: "custos-fixos", seccao: "perguntas", questao: 1, largo: true, consulta: 42, temporal: true,
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
    id: "taxas", seccao: "perguntas", questao: 3, consulta: 52, temporal: true,
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
    id: "curto-prazo", seccao: "perguntas", questao: 3, consulta: 28, temporal: true,
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
    descricao: "Margens, rendibilidade e rotação do ativo, peso dos fornecimentos e serviços externos, dívida face às vendas e fluxo de caixa operacional.",
    conclusao: rows => `A margem corrente sem vendas foi negativa em ${contar(rows, r => r.margem_corrente_sem_vendas_pct < 0)} de ${rows.length} épocas.`,
  },
  /* ---------------- Desporto ---------------- */
  {
    id: "regressao", seccao: "perguntas", questao: 4, consulta: 53, largo: true, temporal: true,
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
    id: "centralizacao", seccao: "perguntas", questao: 5, consulta: 55, matriz: true, largo: true,
    pergunta: "A centralização dos direitos de TV elimina o défice?",
    descricao: "Percentagem do défice antes de vendas (média de 2023/24 a 2025/26) coberta pelos direitos de TV centralizados, por valor do contrato e classificação na Liga.",
    matriz: rows => ({
      linhas: [...new Set(rows.map(r => r.contrato))],
      colunas: [...new Set(rows.map(r => r.lugar))],
      celula: (l, c) => rows.find(r => r.contrato === l && r.lugar === c),
      valor: r => r.pct_do_defice_coberto,
      texto: r => pct(r.pct_do_defice_coberto),
      detalhe: r => `Ganho face à situação atual: ${euros(r.ganho_vs_atual)} · mais-valias ainda necessárias: ${euros(r.mais_valias_necessarias)}`,
      rotuloLinhas: "Contrato", rotuloColunas: "Lugar",
    }),
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
      ctx.font = `${forte ? 700 : 400} 11.5px "Archivo", sans-serif`;
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
  receitas: ["rendimentos", "composicao-vendas", "mais-valias", "reservas-ocultas", "custo-vendas", "passes"],
  custos: ["gastos-rubricas", "composicao-fse", "pessoal-rendimentos", "gastos-vs-receitas", "uefa", "nao-jogadores", "funcionarios", "remuneracoes"],
  rentabilidade: ["resultados-dr", "resultado-operacional", "margens", "dependencia-extraordinarias"],
  divida: ["balanco", "autonomia", "solvabilidade", "endividamento", "painel-indicadores",
    "divida-financeira", "juros-receitas", "fluxos-caixa", "instrumentos", "fundo-maneio", "divida-ebitda", "racios",
    "cobertura-juros", "artigo-35", "reexpressao"],
};

/* =====================================================================
   PERGUNTAS DE INVESTIGAÇÃO (Visão geral)
   As respostas são calculadas a partir das consultas indicadas.
   ===================================================================== */

export const PERGUNTAS = [
  {
    n: 1, contexto: "Os clubes portugueses vendem jogadores com regularidade, mas essas receitas variam muito. Interessa saber se a operação corrente (bilheteira, direitos de TV, patrocínios, prémios) chega para pagar a estrutura.",
    pergunta: "A atividade corrente cobre os gastos de estrutura?", consultas: [2, 42],
    resposta: ({ q }) => {
      const r = q(2), ult3 = r.slice(-3);
      return `Não. Sem as mais-valias com jogadores, o resultado da SAD foi negativo em ${contar(r, x => x.rl_sem_mais_valias < 0)} de ${r.length} épocas; ` +
        `em média faltaram ${euros(-media(col(ult3, "rl_sem_mais_valias")))} por época (${ult3[0].epoca}–${ultimo(ult3).epoca}).`;
    },
    indicadores: ({ q }) => {
      const r = q(2), f = ultimo(q(42));
      return [
        { rotulo: "Épocas com resultado sem mais-valias negativo", valor: `${contar(r, x => x.rl_sem_mais_valias < 0)} de ${r.length}` },
        { rotulo: `Resultado sem mais-valias (${ultimo(r).epoca})`, valor: euros(ultimo(r).rl_sem_mais_valias) },
        { rotulo: `Vendas / gastos de estrutura (${f.epoca})`, valor: pct(f.cobertura_pct) },
      ];
    },
    limitacoes: "Os dados de transferências só existem desde 2017/18. O resultado sem mais-valias é uma aproximação: subtrai as mais-valias ao resultado líquido, sem ajustar o imposto nem outros efeitos. Cada época usa os valores do seu próprio Relatório e Contas (2024/25 sem a reexpressão).",
  },
  {
    n: 2, contexto: "As mais-valias com jogadores e as receitas das competições da UEFA são as duas fontes de receita mais irregulares. Mede-se o seu peso face às vendas e serviços prestados.",
    pergunta: "Quanto pesam as vendas de jogadores e a Europa?", consultas: [54, 21],
    resposta: ({ q }) => {
      const v = ultimo(q(54)), g = q(21), fase = g[0], sem = ultimo(g);
      return `As vendas de jogadores superaram as receitas da atividade corrente em ${contar(q(54), x => x.vendas_por_euro_de_receita > 1)} de ${q(54).length} épocas (${racio(v.vendas_por_euro_de_receita)} € por cada euro de receita em ${v.epoca}). ` +
        `Nas épocas com fase de grupos europeia, as vendas e serviços prestados foram em média de ${euros(fase.receita_media)}, contra ${euros(sem.receita_media)} nas épocas sem competições europeias.`;
    },
    indicadores: ({ q }) => {
      const v = ultimo(q(54)), g = q(21);
      return [
        { rotulo: `Vendas por euro de receita (${v.epoca})`, valor: `${racio(v.vendas_por_euro_de_receita)} €` },
        { rotulo: `Peso das mais-valias (${v.epoca})`, valor: pct(v.peso_mais_valias_no_total_pct) },
        { rotulo: "Resultado médio da SAD com fase de grupos", valor: euros(g[0].rl_medio) },
        { rotulo: "Resultado médio sem competições europeias", valor: euros(ultimo(g).rl_medio) },
      ];
    },
    limitacoes: "A comparação europeia assenta em médias de poucas épocas (3 a 6 por grupo) e não isola outros fatores, como as vendas de jogadores na mesma época.",
  },
  {
    n: 3, contexto: "O passivo da SAD cresceu desde 2020/21. A sustentabilidade depende do montante da dívida financeira, do seu custo e do prazo de vencimento.",
    pergunta: "A dívida é sustentável e a que custo?", consultas: [52, 28, 27],
    resposta: ({ q }) => {
      const t = ultimo(com(q(52), "vitoria_implicita")), c = ultimo(q(28));
      return `É cara e de curto prazo: taxa implícita de ${pct(t.vitoria_implicita)} em ${t.epoca} (${pp(t.spread_vs_euribor)} face à Euribor) ` +
        `e ${pct(c.pct_curto_prazo)} da dívida financeira a vencer em menos de um ano.`;
    },
    indicadores: ({ q }) => {
      const t = ultimo(com(q(52), "vitoria_implicita")), c = ultimo(q(28)), j = ultimo(q(27));
      return [
        { rotulo: `Dívida financeira (${c.epoca})`, valor: euros(c.divida_financeira) },
        { rotulo: "Taxa de juro implícita", valor: pct(t.vitoria_implicita) },
        { rotulo: "Juros / vendas", valor: pct(j.juros_em_pct_receitas) },
        { rotulo: "Dívida a menos de um ano", valor: pct(c.pct_curto_prazo) },
      ];
    },
    limitacoes: "A taxa implícita inclui comissões de factoring e de antecipação de receitas, pelo que não é diretamente comparável a uma taxa nominal de mercado.",
  },
  {
    n: 4, contexto: "Os gastos com o plantel são a principal alavanca desportiva. Testa-se, com uma regressão linear, se as épocas com mais despesa tiveram melhores classificações.",
    pergunta: "Gastar mais traz melhores classificações?", consultas: [53],
    resposta: ({ q }) => {
      const r = q(53)[0];
      const zero = r.ic95_inferior <= 0 && r.ic95_superior >= 0;
      return `${zero ? "Os dados não o demonstram" : "Há uma associação estatística, mas não uma prova de causa"}: a reta só acompanha ${pct(100 * r.r_quadrado)} da variação da classificação (R² = ${decimal(r.r_quadrado)}, ${r.n} épocas) ` +
        `e o intervalo de confiança do declive ${zero ? "inclui o zero" : "não inclui o zero"}.`;
    },
    indicadores: ({ q }) => {
      const r = q(53)[0];
      return [
        { rotulo: "R²", valor: decimal(r.r_quadrado) },
        { rotulo: "Declive (lugares por M€ de gastos)", valor: decimal(r.b_declive_por_m) },
        { rotulo: "IC 95% do declive", valor: `${decimal(r.ic95_inferior)} a ${decimal(r.ic95_superior)}` },
        { rotulo: "Épocas", valor: inteiro(r.n) },
      ];
    },
    limitacoes: "Treze observações conferem pouca potência estatística. Trata-se de uma associação, não de uma relação de causa e efeito: a classificação depende de muitos fatores não medidos.",
  },
  {
    n: 5, contexto: "A centralização dos direitos de TV, prevista para 2028/29, pode alterar as receitas da SAD. Simula-se quanto do défice antes de vendas ficaria coberto.",
    pergunta: "Que combinação reduz a dependência das vendas?", consultas: [55, 48],
    resposta: ({ q }) => {
      const r = q(55), max = r.reduce((a, b) => (b.pct_do_defice_coberto > a.pct_do_defice_coberto ? b : a));
      return `A centralização dos direitos de TV, por si só, cobriria no máximo ${pct(max.pct_do_defice_coberto)} do défice antes de vendas (${max.contrato}, ${max.lugar} lugar). ` +
        `O restante teria de ser coberto por outras vias: menos gastos, dívida mais barata ou venda de jogadores.`;
    },
    indicadores: ({ q }) => {
      const r = q(55), central = r.find(x => x.contrato === "250 M€" && x.lugar === "6.º");
      return [
        { rotulo: "Défice antes de vendas (média de 3 épocas)", valor: euros(r[0].defice_antes_vendas) },
        { rotulo: "Cenário central (250 M€, 6.º lugar): ganho", valor: euros(central?.ganho_vs_atual) },
        { rotulo: "Cenário central: défice coberto", valor: pct(central?.pct_do_defice_coberto) },
        { rotulo: "Mais-valias ainda necessárias", valor: euros(central?.mais_valias_necessarias) },
      ];
    },
    limitacoes: "Simulação ilustrativa: o modelo de repartição dos direitos centralizados ainda não está definido; a componente de mérito é linear e ignora as audiências.",
  },
];
