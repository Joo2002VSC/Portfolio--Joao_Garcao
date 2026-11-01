// Definição de cada visualização: a pergunta a que responde, a consulta SQL de onde vem,
// como se desenha e a conclusão, calculada a partir dos dados filtrados.
// Nenhum valor é inventado aqui: tudo sai das linhas das consultas.

import { barras, linha, areaAcima, opcoes, cor } from "./graficos.js";
import { euros, pct, razao, inteiro, decimal, lugar, milhoes, pp } from "./formato.js";
import { media, soma, dividir, ultimo, numeros } from "./dados.js";

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
    return ds;
  });
  return { type: tipo, data: { labels: epocasDe(rows), datasets }, options: opcoes(op) };
}

const comReferencias = (config, linhas) => { config.options.plugins.referencias = { linhas }; return config; };

/** Barras de uma só série com destaque a amarelo para os valores que cumprem uma condição */
const coresCondicao = cond => (v => (v !== null && cond(v) ? cor("amarelo") : cor("tinta")));

/* =====================================================================
   SECÇÕES
   ===================================================================== */

export const SECCOES = [
  { id: "geral", nome: "Visão geral", intro: "Os indicadores principais da época em destaque e as respostas às cinco perguntas do projeto." },
  { id: "receitas", nome: "Receitas e transferências", intro: "De onde vem o dinheiro: a operação corrente, a Europa e a venda de jogadores." },
  { id: "custos", nome: "Custos e pessoal", intro: "Quanto custa a estrutura e se as receitas da operação a conseguem pagar." },
  { id: "divida", nome: "Balanço e dívida", intro: "Património, endividamento, custo da dívida e liquidez da SAD." },
  { id: "desporto", nome: "Desporto", intro: "A relação entre o dinheiro gasto e os resultados em campo." },
  { id: "cenarios", nome: "Cenários", intro: "Simulações do projeto SQL. São ilustrativas: dependem de pressupostos sobre contratos e classificações." },
  { id: "sql", nome: "Consultas SQL", intro: "As 59 consultas do projeto, com o código e o resultado. Pesquisa, ordena e exporta." },
];

/* =====================================================================
   VISUALIZAÇÕES
   Campos: id, seccao, consulta, pergunta, descricao, nota, largo, construir(rows), conclusao(rows),
           temporal (true = filtra pelo intervalo de épocas), tabela (true = mostra como tabela)
   ===================================================================== */

export const PAINEIS = [
  /* ---------------- Visão geral ---------------- */
  {
    id: "resultado-entidades", seccao: "geral", consulta: 10, largo: true, temporal: true,
    pergunta: "Que entidade dá lucro e qual dá prejuízo?",
    descricao: "Resultado líquido por época (exercício a 30 de junho). Clica na legenda para esconder uma entidade.",
    construir: rows => temporal(rows, [
      { col: "rl_sad", rotulo: "SAD", papel: "tinta" },
      { col: "rl_consolidado", rotulo: "Grupo consolidado", papel: "cinza" },
      { col: "rl_clube", rotulo: "Clube", papel: "amarelo" },
    ]),
    conclusao: rows => {
      const sad = com(rows, "rl_sad"), clube = com(rows, "rl_clube");
      const partes = [`A SAD teve prejuízo em ${contar(sad, r => r.rl_sad < 0)} de ${sad.length} épocas`];
      if (clube.length) partes.push(`o Clube em ${contar(clube, r => r.rl_clube < 0)} de ${clube.length}`);
      return partes.join("; ") + ".";
    },
    nota: "Clube e Grupo consolidado ainda sem contas de 2025/26.",
  },
  {
    id: "dependencia-vendas", seccao: "geral", consulta: 2, largo: true, temporal: true,
    pergunta: "A SAD consegue ter lucro sem vender jogadores?",
    descricao: "Resultado líquido com e sem as mais-valias líquidas da venda de jogadores.",
    construir: rows => temporal(rows, [
      { col: "rl", rotulo: "Resultado líquido", papel: "tinta" },
      { col: "rl_sem_mais_valias", rotulo: "Sem mais-valias", papel: "cinza" },
    ]),
    conclusao: rows => {
      const neg = contar(rows, r => r.rl_sem_mais_valias < 0);
      const graças = contar(rows, r => r.leitura);
      return `Sem mais-valias, o resultado seria negativo em ${neg} de ${rows.length} épocas. ` +
        `Em ${plural(graças, "época", "épocas")}, o lucro só existiu graças às vendas.`;
    },
  },

  /* ---------------- Receitas e transferências ---------------- */
  {
    id: "rendimentos", seccao: "receitas", consulta: 57, largo: true, temporal: true,
    pergunta: "Quanto dos rendimentos vem de fora da operação corrente?",
    descricao: "Rendimentos operacionais da SAD por rubrica. \"Outros rendimentos\" inclui os ganhos com a venda de passes.",
    construir: rows => temporal(rows, [
      { col: "vendas_servicos", rotulo: "Vendas e serviços", papel: "tinta" },
      { col: "outros_rendimentos", rotulo: "Outros rendimentos", papel: "amarelo" },
      { col: "subsidios", rotulo: "Subsídios", papel: "cinza" },
    ], { empilhado: true }),
    conclusao: rows => {
      const u = ultimo(rows);
      return `Em média, ${pct(media(col(rows, "outros_rendimentos_pct")))} dos rendimentos vieram de outros rendimentos` +
        (u ? `; em ${u.epoca}, ${pct(u.outros_rendimentos_pct)}.` : ".");
    },
  },
  {
    id: "composicao-receitas", seccao: "receitas", consulta: 5, temporal: true,
    pergunta: "Que fontes pesam mais nas receitas do grupo?",
    descricao: "Peso de cada fonte nas receitas operacionais do Grupo consolidado (%).",
    construir: rows => temporal(rows, [
      { col: "tv", rotulo: "Direitos TV", papel: "tinta" },
      { col: "competicoes", rotulo: "Competições", papel: "amarelo" },
      { col: "socios", rotulo: "Sócios e camarotes", papel: "cinza-escuro" },
      { col: "patrocinios", rotulo: "Patrocínios", papel: "cinza" },
      { calcular: r => (r.bilhetica ?? 0) + (r.outras ?? 0), rotulo: "Bilhética e outras", papel: "amarelo-claro" },
    ], { empilhado: true, unidade: "pct", max: 100 }),
    conclusao: rows => {
      if (!rows.length) return "";
      const maxComp = rows.reduce((a, b) => (b.competicoes > a.competicoes ? b : a));
      return `Os direitos TV foram a maior fonte em ${contar(rows, r => r.tv >= Math.max(r.competicoes, r.socios, r.patrocinios))} de ${rows.length} épocas. ` +
        `As competições chegaram a ${pct(maxComp.competicoes)} em ${maxComp.epoca}.`;
    },
    nota: "\"Outras\" junta merchandising, mecanismo de solidariedade, subsídios e outros.",
  },
  {
    id: "valor-europa", seccao: "receitas", consulta: 21,
    pergunta: "Quanto vale uma época europeia?",
    descricao: "Receitas e resultado médios da SAD por tipo de época (2013/14 a 2025/26).",
    construir: rows => {
      const labels = rows.map(r => r.tipo.replace(/^\d+\.\s*/, ""));
      const cfg = {
        type: "bar",
        data: { labels, datasets: [barras("Receita média", col(rows, "receita_media"), "tinta"), barras("Resultado médio", col(rows, "rl_medio"), "cinza")] },
        options: opcoes(),
      };
      cfg.options.plugins.tooltip.callbacks.footer = i => `${plural(rows[i[0].dataIndex].epocas, "época", "épocas")}: ${rows[i[0].dataIndex].lista}`;
      return cfg;
    },
    conclusao: rows => {
      const g = rows[0], s = ultimo(rows);
      return `Com fase de grupos, a receita média foi ${euros(g.receita_media)}, contra ${euros(s.receita_media)} sem Europa; ` +
        `o resultado médio passou de ${euros(s.rl_medio)} para ${euros(g.rl_medio)}.`;
    },
    nota: "Não depende do intervalo de épocas: cada grupo junta todas as épocas desse tipo.",
  },
  {
    id: "vendas-por-euro", seccao: "receitas", consulta: 54, temporal: true,
    pergunta: "A SAD vende mais em jogadores do que fatura na operação?",
    descricao: "Vendas brutas de jogadores por cada euro de receita da operação (TV, bilheteira, patrocínios, sócios).",
    construir: rows => comReferencias(temporal(rows, [
      { col: "vendas_por_euro_de_receita", rotulo: "Vendas por € de receita", papel: "cinza" },
      { col: "media_movel_3_epocas", rotulo: "Média móvel (3 épocas)", papel: "tinta", tipo: "line" },
    ], { unidade: "x", min: 0 }), [{ valor: 1, rotulo: "Vendas = receitas" }]),
    conclusao: rows => `As vendas superaram as receitas da operação em ${contar(rows, r => r.vendas_por_euro_de_receita > 1)} de ${rows.length} épocas` +
      (rows.length ? `; em ${ultimo(rows).epoca} foram ${razao(ultimo(rows).vendas_por_euro_de_receita)} por cada euro.` : "."),
  },
  {
    id: "mais-valias", seccao: "receitas", consulta: 12, temporal: true,
    pergunta: "Quanto das vendas de jogadores se transforma em mais-valia?",
    descricao: "Vendas brutas e mais-valias líquidas (depois do valor contabilístico e dos custos da venda).",
    construir: rows => {
      const cfg = temporal(rows, [
        { col: "vendas_brutas", rotulo: "Vendas brutas", papel: "tinta" },
        { col: "mais_valias_liquidas", rotulo: "Mais-valias líquidas", papel: "amarelo" },
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
      return `No conjunto de ${intervaloTexto(rows)}, os jogadores vendidos renderam ${razao(dividir(v, c))} o valor que tinham no balanço.`;
    },
    nota: "O balanço regista os passes ao custo de aquisição: os jogadores da formação valem quase zero.",
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
      return `O peso subiu de ${pct(rows[0]?.custo_vendas_pct)} para ${pct(ultimo(rows)?.custo_vendas_pct)}` +
        (ud ? `. A dívida a intermediários desportivos era de ${euros(ud.custo_vendas)} (${ud.epoca.replace("dívida ", "")}).` : ".");
    },
  },
  {
    id: "passes", seccao: "receitas", consulta: 40, temporal: true,
    pergunta: "A SAD investe mais em passes do que amortiza?",
    descricao: "Aquisições e amortizações de passes, e valor do plantel no balanço.",
    construir: rows => temporal(rows, [
      { col: "aquisicoes", rotulo: "Aquisições", papel: "tinta" },
      { col: "amortizacoes", rotulo: "Amortizações", papel: "cinza" },
      { col: "valor_contabilistico_plantel", rotulo: "Plantel no balanço", papel: "amarelo", tipo: "line" },
    ]),
    conclusao: rows => `Investimento líquido em ${intervaloTexto(rows)}: ${euros(soma(col(rows, "investimento_liquido")))}. ` +
      `O plantel valia ${euros(ultimo(rows)?.valor_contabilistico_plantel)} no balanço em ${ultimo(rows)?.epoca}.`,
  },
  {
    id: "solidariedade", seccao: "receitas", consulta: 47, temporal: true,
    pergunta: "Quanto rende a formação de jogadores vendidos por outros clubes?",
    descricao: "Mecanismo de solidariedade e compensação por formação (FIFA).",
    construir: rows => temporal(rows, [{ col: "solidariedade", rotulo: "Solidariedade e formação", papel: "cinza-escuro" }], { legenda: false }),
    conclusao: rows => `Total em ${intervaloTexto(rows)}: ${euros(soma(col(rows, "solidariedade")))}, um valor irregular de época para época.`,
  },

  /* ---------------- Custos e pessoal ---------------- */
  {
    id: "gastos-rubricas", seccao: "custos", consulta: 58, largo: true, temporal: true,
    pergunta: "Que gastos cresceram mais?",
    descricao: "Gastos operacionais da SAD por rubrica.",
    construir: rows => temporal(rows, [
      { col: "pessoal", rotulo: "Pessoal", papel: "tinta" },
      { col: "fse", rotulo: "FSE", papel: "cinza-escuro" },
      { col: "depreciacoes", rotulo: "Depreciações e amortizações", papel: "cinza" },
      { calcular: r => (r.mercadorias ?? 0) + (r.outros_gastos ?? 0) + (r.imparidades_provisoes ?? 0), rotulo: "Outros", papel: "amarelo-claro" },
    ], { empilhado: true }),
    conclusao: rows => {
      if (rows.length < 2) return "";
      const a = rows[0], b = ultimo(rows);
      return `Os gastos operacionais passaram de ${euros(a.total_gastos)} (${a.epoca}) para ${euros(b.total_gastos)} (${b.epoca}), ` +
        `${razao(dividir(b.total_gastos, a.total_gastos))}. O pessoal pesa ${pct(b.pessoal_pct)} do total.`;
    },
    nota: "\"Outros\" junta mercadorias, outros gastos, imparidades e provisões.",
  },
  {
    id: "gastos-vs-receitas", seccao: "custos", consulta: 56, largo: true, temporal: true,
    pergunta: "Receitas e vendas de jogadores chegam para pagar os gastos?",
    descricao: "Gastos operacionais (à esquerda) contra receitas da operação mais mais-valias com jogadores (à direita).",
    construir: rows => {
      const cfg = temporal(rows, [
        { col: "gastos_operacionais", rotulo: "Gastos operacionais", papel: "tinta", stack: "gastos" },
        { col: "receitas_operacao", rotulo: "Receitas da operação", papel: "cinza", stack: "receitas" },
        { col: "receitas_transferencias", rotulo: "Mais-valias com jogadores", papel: "amarelo", stack: "receitas" },
      ], { empilhado: true });
      cfg.options.plugins.tooltip.callbacks.footer = i => `Saldo: ${euros(rows[i[0].dataIndex].saldo_com_receitas_operacao)}`;
      return cfg;
    },
    conclusao: rows => `Mesmo somando as vendas, faltou dinheiro em ${contar(rows, r => r.saldo_com_receitas_operacao < 0)} de ${rows.length} épocas. ` +
      `As mais-valias cobriram entre ${pct(Math.min(...numeros(col(rows, "transferencias_cobrem_pct"))))} e ${pct(Math.max(...numeros(col(rows, "transferencias_cobrem_pct"))))} dos gastos.`,
  },
  {
    id: "pessoal-receitas", seccao: "custos", consulta: 3, temporal: true,
    pergunta: "Os salários cabem nas receitas?",
    descricao: "Gastos com pessoal em percentagem das vendas e serviços. A amarelo, as épocas acima de 100%.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "pct", rotulo: "Pessoal / receitas", papel: "tinta", cores: coresCondicao(v => v > 100) },
    ], { unidade: "pct", legenda: false, min: 0 }), [{ valor: 100, rotulo: "100%" }]),
    conclusao: rows => `Os gastos com pessoal superaram as receitas em ${contar(rows, r => r.pct > 100)} de ${rows.length} épocas; o máximo foi ${pct(Math.max(...numeros(col(rows, "pct"))))}.`,
  },
  {
    id: "custos-fixos", seccao: "custos", consulta: 42, temporal: true,
    pergunta: "As receitas cobrem os custos fixos?",
    descricao: "Vendas e serviços em percentagem dos custos fixos (pessoal, FSE e depreciações).",
    construir: rows => comReferencias(temporal(rows, [
      { col: "cobertura_pct", rotulo: "Receitas / custos fixos", papel: "cinza-escuro" },
    ], { unidade: "pct", legenda: false, min: 0, max: 120 }), [{ valor: 100, rotulo: "Cobertura total" }]),
    conclusao: rows => (contar(rows, r => r.cobertura_pct >= 100) === 0
      ? `As receitas nunca cobriram os custos fixos (${plural(rows.length, "época", "épocas")}). `
      : `As receitas cobriram os custos fixos em ${contar(rows, r => r.cobertura_pct >= 100)} de ${rows.length} épocas. `) +
      `Défice médio antes de vendas: ${euros(media(col(rows, "defice_antes_de_vendas")))} por época.`,
  },
  {
    id: "uefa", seccao: "custos", consulta: 45, temporal: true,
    pergunta: "A SAD cumpriria o limite de custos do plantel da UEFA?",
    descricao: "Remunerações do plantel e amortizações de passes, em % das receitas mais a média de 3 épocas das mais-valias.",
    construir: rows => comReferencias(temporal(rows, [
      { col: "racio_pct", rotulo: "Rácio de custos do plantel", papel: "tinta", cores: coresCondicao(v => v > 70) },
    ], { unidade: "pct", legenda: false, min: 0 }), [{ valor: 70, rotulo: "Limite de 70%" }]),
    conclusao: rows => `Acima de 70% em ${contar(rows, r => r.racio_pct > 70)} de ${rows.length} épocas` +
      (rows.length ? `; em ${ultimo(rows).epoca}, ${pct(ultimo(rows).racio_pct)}.` : "."),
    nota: "Aproximação ao regulamento. Nas duas primeiras épocas, a média das mais-valias usa menos de 3 épocas. A consulta 24 tem uma versão mais simples.",
  },
  {
    id: "funcionarios", seccao: "custos", consulta: 31, temporal: true,
    pergunta: "A estrutura cresceu mais depressa do que a equipa?",
    descricao: "Funcionários da SAD (média anual) por categoria.",
    construir: rows => temporal(rows, [
      { col: "jogadores", rotulo: "Jogadores", papel: "tinta" },
      { col: "treinadores", rotulo: "Treinadores", papel: "cinza" },
      { col: "staff", rotulo: "Staff e apoio", papel: "amarelo" },
    ], { empilhado: true, unidade: "int", tooltipUnidade: "int" }),
    conclusao: rows => {
      if (rows.length < 2) return "";
      const a = rows[0], b = ultimo(rows);
      return `De ${a.epoca} para ${b.epoca}: jogadores ${inteiro(a.jogadores)} → ${inteiro(b.jogadores)}; ` +
        `treinadores e staff ${inteiro(a.treinadores + a.staff)} → ${inteiro(b.treinadores + b.staff)}.`;
    },
  },
  {
    id: "nao-jogadores", seccao: "custos", consulta: 33, temporal: true,
    pergunta: "Quantos não-jogadores há por cada jogador?",
    descricao: "Treinadores, staff e apoio por cada jogador.",
    construir: rows => comReferencias(temporal(rows, [{ col: "nao_jogadores_por_jogador", rotulo: "Não-jogadores por jogador", papel: "tinta" }],
      { tipo: "line", unidade: "x", legenda: false, min: 0 }), [{ valor: 1, rotulo: "1 por jogador" }]),
    conclusao: rows => rows.length > 1 ? `Passou de ${decimal(rows[0].nao_jogadores_por_jogador)} para ${decimal(ultimo(rows).nao_jogadores_por_jogador)} não-jogadores por jogador.` : "",
  },
  {
    id: "remuneracoes", seccao: "custos", consulta: 32, temporal: true,
    pergunta: "Quanto custa, em média, cada jogador e cada funcionário?",
    descricao: "Remuneração média anual por jogador e custo médio por funcionário.",
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
    id: "balanco", seccao: "divida", consulta: 7, largo: true, temporal: true,
    pergunta: "O passivo da SAD supera o ativo?",
    descricao: "Ativo e passivo a 30 de junho. A área amarela é o capital próprio negativo.",
    construir: rows => {
      const cfg = temporal(rows, [
        { col: "passivo_total", rotulo: "Passivo", papel: "tinta", fill: areaAcima(1) },
        { col: "ativo_total", rotulo: "Ativo", papel: "cinza-escuro", oca: true },
      ], { tipo: "line", min: 0 });
      cfg.options.plugins.tooltip.callbacks.footer = i => `Capital próprio: ${euros(rows[i[0].dataIndex].capital_proprio)}`;
      return cfg;
    },
    conclusao: rows => `Capital próprio negativo em ${contar(rows, r => r.capital_proprio < 0)} de ${rows.length} épocas` +
      (rows.length ? `; ${euros(ultimo(rows).capital_proprio)} a ${fimEpoca(ultimo(rows).epoca)}.` : "."),
  },
  {
    id: "racios", seccao: "divida", consulta: 29, temporal: true,
    pergunta: "A SAD consegue pagar o que deve a curto prazo?",
    descricao: "Endividamento (passivo / ativo) e liquidez geral (ativo corrente / passivo corrente).",
    construir: rows => comReferencias(temporal(rows, [
      { col: "endividamento", rotulo: "Endividamento", papel: "tinta" },
      { col: "liquidez_geral", rotulo: "Liquidez geral", papel: "cinza-escuro", oca: true },
    ], { tipo: "line", unidade: "x", min: 0 }), [{ valor: 1, rotulo: "Limiar = 1" }]),
    conclusao: rows => `Liquidez geral abaixo de 1 em ${contar(rows, r => r.liquidez_geral < 1)} de ${rows.length} épocas` +
      (rows.length ? `; em ${ultimo(rows).epoca}, ${razao(ultimo(rows).liquidez_geral)} e endividamento de ${razao(ultimo(rows).endividamento)}.` : "."),
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
      return `De ${euros(min.financiamentos)} (${min.epoca}) para ${euros(ultimo(v).financiamentos)} (${ultimo(v).epoca}): ${razao(dividir(ultimo(v).financiamentos, min.financiamentos))}.`;
    },
  },
  {
    id: "taxas", seccao: "divida", consulta: 52, temporal: true,
    pergunta: "O Vitória paga juros acima do mercado?",
    descricao: "Taxa de juro implícita da dívida da SAD contra referências de mercado (%).",
    construir: rows => temporal(rows, [
      { col: "vitoria_implicita", rotulo: "Vitória (implícita)", papel: "tinta" },
      { col: "euribor_12m", rotulo: "Euribor 12 meses", papel: "cinza-escuro", oca: true },
      { col: "ot_portugal_10a", rotulo: "OT Portugal 10 anos", papel: "amarelo" },
    ], { tipo: "line", unidade: "pct" }),
    conclusao: rows => {
      const v = com(rows, "vitoria_implicita");
      return v.length ? `Em ${ultimo(v).epoca}, a taxa implícita foi ${pct(ultimo(v).vitoria_implicita)}: ${pp(ultimo(v).spread_vs_euribor)} acima da Euribor e ${razao(ultimo(v).vezes_estado_portugues)} a taxa do Estado.` : "";
    },
    nota: "Taxa implícita = juros dos financiamentos / dívida financeira média.",
  },
  {
    id: "juros-receitas", seccao: "divida", consulta: 27, temporal: true,
    pergunta: "Quanto das receitas vai para juros?",
    descricao: "Juros dos financiamentos em percentagem das vendas e serviços.",
    construir: rows => temporal(rows, [{ col: "juros_em_pct_receitas", rotulo: "Juros / receitas", papel: "tinta" }], { unidade: "pct", legenda: false, min: 0 }),
    conclusao: rows => rows.length ? `Em ${ultimo(rows).epoca}, os juros consumiram ${pct(ultimo(rows).juros_em_pct_receitas)} das receitas (${euros(ultimo(rows).juros)}).` : "",
    nota: "Juros dos financiamentos. A consulta 8 usa os juros suportados líquidos, um valor diferente.",
  },
  {
    id: "curto-prazo", seccao: "divida", consulta: 28, temporal: true,
    pergunta: "Que parte da dívida vence em menos de um ano?",
    descricao: "Dívida financeira de curto prazo em percentagem do total.",
    construir: rows => temporal(rows, [{ col: "pct_curto_prazo", rotulo: "Curto prazo", papel: "tinta", cores: coresCondicao(v => v > 50) }],
      { unidade: "pct", legenda: false, min: 0, max: 100 }),
    conclusao: rows => rows.length ? `A ${fimEpoca(ultimo(rows).epoca)}, ${pct(ultimo(rows).pct_curto_prazo)} da dívida vencia em menos de um ano; a caixa era de ${euros(ultimo(rows).caixa)}.` : "",
  },
  {
    id: "instrumentos", seccao: "divida", consulta: 39,
    pergunta: "Com que instrumentos se financia a SAD?",
    descricao: "Dívida financeira por instrumento, nas três datas com detalhe nos Relatórios e Contas.",
    construir: rows => {
      const datas = [...new Set(rows.map(r => r.data_ref))];
      const grupo = i => (/^Empréstimos/.test(i) ? "Empréstimos" : /^Antecipação/.test(i) ? "Antecipação de direitos TV" : i);
      const grupos = [...new Set(rows.map(r => grupo(r.instrumento)))];
      const papeis = ["tinta", "cinza-escuro", "amarelo", "cinza", "amarelo-claro"];
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
    nota: "Usa a consulta 39 e não a 14: a consulta 14 mistura as datas de 30/06/2025 e 30/06/2026 sob o mesmo título.",
  },
  {
    id: "fluxos-caixa", seccao: "divida", consulta: 15, largo: true, temporal: true,
    pergunta: "Como se financiou cada época?",
    descricao: "Fluxos de caixa da SAD: operacional, de investimento (inclui vendas de passes) e de financiamento.",
    construir: rows => temporal(rows, [
      { col: "operacional", rotulo: "Operacional", papel: "tinta" },
      { col: "investimento", rotulo: "Investimento", papel: "cinza" },
      { col: "financiamento", rotulo: "Financiamento", papel: "amarelo" },
    ]),
    conclusao: rows => `A operação consumiu caixa em ${contar(rows, r => r.operacional < 0)} de ${rows.length} épocas; ` +
      `o buraco foi tapado com financiamento em ${contar(rows, r => /financiamento/.test(r.leitura))} e com vendas ou investimento em ${contar(rows, r => /vendas/.test(r.leitura))}.`,
    nota: "2024/25 com os valores originais. O R&C de 2025/26 reexpressou esses fluxos (consulta 36).",
  },
  {
    id: "fundo-maneio", seccao: "divida", consulta: 38, temporal: true,
    pergunta: "O ativo corrente chega para o passivo corrente?",
    descricao: "Fundo de maneio: ativo corrente menos passivo corrente, a 30 de junho.",
    construir: rows => temporal(rows, [{ col: "fundo_maneio", rotulo: "Fundo de maneio", papel: "tinta" }], { legenda: false }),
    conclusao: rows => `Fundo de maneio negativo em ${contar(rows, r => r.fundo_maneio < 0)} de ${rows.length} épocas` +
      (rows.length ? `; ${euros(ultimo(rows).fundo_maneio)} em ${ultimo(rows).epoca}.` : "."),
  },
  {
    id: "divida-ebitda", seccao: "divida", consulta: 37, temporal: true,
    pergunta: "Quantos anos de EBITDA pagariam a dívida?",
    descricao: "Dívida financeira líquida / EBITDA. Sem barra nas épocas de EBITDA negativo (rácio sem leitura).",
    construir: rows => comReferencias(temporal(rows, [{ col: "divida_liq_ebitda", rotulo: "Dívida líquida / EBITDA", papel: "tinta", cores: coresCondicao(v => v > 3) }],
      { unidade: "x", legenda: false }), [{ valor: 3, rotulo: "Referência: 3×" }]),
    conclusao: rows => `EBITDA negativo em ${contar(rows, r => r.ebitda < 0)} de ${rows.length} épocas` +
      (rows.length ? `; em ${ultimo(rows).epoca}, a dívida líquida equivalia a ${razao(ultimo(rows).divida_liq_ebitda)} o EBITDA.` : "."),
  },
  {
    id: "passivo-entidades", seccao: "divida", consulta: 11, temporal: true,
    pergunta: "Onde está concentrado o passivo do grupo?",
    descricao: "Passivo do Clube e da SAD a 30 de junho.",
    construir: rows => temporal(rows, [
      { col: "passivo_sad", rotulo: "SAD", papel: "tinta" },
      { col: "passivo_clube", rotulo: "Clube", papel: "amarelo" },
    ], { tipo: "line", min: 0 }),
    conclusao: rows => rows.length ? `Em ${ultimo(rows).epoca}, a SAD tinha ${razao(ultimo(rows).passivo_sad_por_euro_do_clube)} o passivo do Clube.` : "",
  },
  {
    id: "cobertura-juros", seccao: "divida", consulta: 30, tabela: true, temporal: true,
    pergunta: "O EBITDA chega para pagar os juros?",
    descricao: "Quantas vezes o EBITDA cobre os juros. Abaixo de 3×, a cobertura é considerada fraca.",
    conclusao: rows => `EBITDA negativo em ${contar(rows, r => r.ebitda < 0)} de ${rows.length} épocas; cobertura de ${razao(ultimo(rows)?.cobertura)} em ${ultimo(rows)?.epoca}.`,
  },
  {
    id: "artigo-35", seccao: "divida", consulta: 43, tabela: true, temporal: true,
    pergunta: "A SAD perdeu metade do capital social?",
    descricao: "Artigo 35.º do Código das Sociedades Comerciais e parecer do auditor sobre a continuidade.",
    conclusao: rows => `Metade do capital perdida em ${contar(rows, r => r.metade_do_capital_perdida === "sim")} de ${rows.length} épocas; ` +
      `incerteza material sobre a continuidade em ${contar(rows, r => /Incerteza material/.test(r.parecer_auditor))}.`,
  },
  {
    id: "reexpressao", seccao: "divida", consulta: 36, tabela: true,
    pergunta: "O que mudou com a reexpressão de 2024/25?",
    descricao: "Valores de 2024/25 no R&C original e no R&C de 2025/26 (custo amortizado e correções).",
    conclusao: rows => {
      const fo = rows.find(r => r.indicador === "Fluxo de caixa operacional"), cp = rows.find(r => r.indicador === "Capital próprio");
      return fo && cp ? `O fluxo operacional passou de ${euros(fo.valor_original)} para ${euros(fo.valor_reexpresso)}; o capital próprio, de ${euros(cp.valor_original)} para ${euros(cp.valor_reexpresso)}.` : "";
    },
  },

  {
    id: "painel-indicadores", seccao: "divida", consulta: 51, tabela: true, largo: true, temporal: true,
    pergunta: "Painel de indicadores financeiros",
    descricao: "Margens, rendibilidade, rotação do ativo, peso dos FSE, dívida face às receitas e cash flow operacional.",
    conclusao: rows => `A margem corrente sem vendas foi negativa em ${contar(rows, r => r.margem_corrente_sem_vendas_pct < 0)} de ${rows.length} épocas.`,
  },
  /* ---------------- Desporto ---------------- */
  {
    id: "regressao", seccao: "desporto", consulta: 53, largo: true, temporal: true,
    pergunta: "Gastar mais dá melhores classificações?",
    descricao: "Despesas da SAD (pessoal, FSE e amortizações) e lugar na Liga, com a reta de regressão linear. O 1.º lugar fica em cima.",
    construir: (rows, todas, ctx) => {
      const r0 = todas[0];
      const xs = numeros(col(todas, "despesas_m"));
      const xMin = Math.min(...xs), xMax = Math.max(...xs);
      const reta = [xMin, xMax].map(x => ({ x, y: r0.a_ordenada + r0.b_declive_por_m * x }));
      const pontos = rows.map(r => ({ x: r.despesas_m, y: r.lugar, epoca: r.epoca, prev: r.lugar_previsto }));
      const destaque = p => p.epoca === ctx.epoca;
      const op = opcoes({ unidade: "milhoes", legenda: true, indice: false });
      op.scales.y = { reverse: true, min: 1, max: 12, ticks: { stepSize: 1, callback: v => `${v}.º`, color: cor("suave") },
        title: { display: true, text: "Lugar na Liga", color: cor("suave") }, grid: { color: cor("grelha") }, border: { display: false } };
      op.scales.x.title = { display: true, text: "Despesas da SAD", color: cor("suave") };
      op.scales.x.grid = { color: cor("grelha") };
      op.plugins.tooltip.callbacks = {
        title: i => i[0].raw.epoca ?? "Reta de regressão",
        label: c => (c.raw.epoca ? [` ${lugar(c.raw.y)} lugar`, ` Despesas: ${milhoes(c.raw.x)}`, ` Previsto pela reta: ${decimal(c.raw.prev)}.º`] : ` ${decimal(c.raw.y)}.º previsto com ${milhoes(c.raw.x)}`),
      };
      return {
        type: "scatter",
        data: {
          datasets: [
            { label: "Épocas", data: pontos, backgroundColor: pontos.map(p => (destaque(p) ? cor("amarelo") : cor("tinta"))),
              borderColor: pontos.map(p => (destaque(p) ? cor("tinta") : cor("cartao"))), borderWidth: 1.5,
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
      return `R² = ${decimal(r.r_quadrado)} em ${r.n} épocas: as despesas explicam ${pct(100 * r.r_quadrado)} das diferenças de classificação. ` +
        `Cada 10 M€ a mais valem ${decimal(Math.abs(r.b_declive_por_m * 10))} lugares (IC 95% do declive: ${decimal(r.ic95_inferior)} a ${decimal(r.ic95_superior)}${incluiZero ? ", inclui o zero" : ""}).`;
    },
    nota: "A regressão usa as 13 épocas, independentemente do filtro; o filtro só esconde pontos. É uma associação, não uma relação de causa e efeito.",
  },
  {
    id: "custo-ponto", seccao: "desporto", consulta: 49, temporal: true,
    pergunta: "Quanto custou cada ponto na Liga?",
    descricao: "Gastos com pessoal da SAD a dividir pelos pontos conquistados no campeonato.",
    construir: rows => {
      const cfg = temporal(rows, [{ col: "custo_por_ponto", rotulo: "Custo por ponto", papel: "tinta" }], { legenda: false });
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
    descricao: "Média de espectadores por jogo em casa na Liga.",
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
      return `Máximo de ${inteiro(max.espectadores)} espectadores em ${max.epoca}. Em 2020/21 os jogos foram à porta fechada.`;
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
    descricao: "Lugar, Europa, troféus, receitas, gastos com pessoal e resultado líquido da SAD.",
    conclusao: rows => `${plural(contar(rows, r => r.europa && r.europa !== "—"), "época", "épocas")} com Europa e ${plural(contar(rows, r => r.trofeu), "troféu", "troféus")} no intervalo.`,
  },
  /* ---------------- Cenários ---------------- */
  {
    id: "equilibrio", seccao: "cenarios", consulta: 25, factos: true, largo: true,
    pergunta: "Quanto teria de render a venda de jogadores para a SAD não ter prejuízo?",
    descricao: "Ponto de equilíbrio de 2025/26, a partir do resultado com direitos de atletas e do resultado líquido.",
    factos: rows => {
      const r = rows[0];
      return [
        { rotulo: "Resultado com jogadores 2025/26", valor: euros(r.resultado_com_jogadores_2025_26) },
        { rotulo: "Resultado líquido 2025/26", valor: euros(r.resultado_liquido_2025_26) },
        { rotulo: "Necessário para o equilíbrio", valor: euros(r.necessario_para_equilibrio), forte: true },
        { rotulo: "Falta face a 2025/26", valor: euros(r.falta_face_a_2025_26) },
      ];
    },
  },
  {
    id: "centralizacao", seccao: "cenarios", consulta: 55, matriz: true, largo: true,
    pergunta: "A centralização dos direitos TV resolve o défice?",
    descricao: "Percentagem do défice antes de vendas (média 2023/24–2025/26) coberta pela TV centralizada, por valor do contrato e lugar na Liga.",
    matriz: rows => ({
      linhas: [...new Set(rows.map(r => r.contrato))],
      colunas: [...new Set(rows.map(r => r.lugar))],
      celula: (l, c) => rows.find(r => r.contrato === l && r.lugar === c),
      valor: r => r.pct_do_defice_coberto,
      texto: r => pct(r.pct_do_defice_coberto),
      detalhe: r => `Ganho face ao atual: ${euros(r.ganho_vs_atual)} · mais-valias ainda necessárias: ${euros(r.mais_valias_necessarias)}`,
      rotuloLinhas: "Contrato", rotuloColunas: "Lugar",
    }),
    conclusao: rows => {
      const max = rows.reduce((a, b) => (b.pct_do_defice_coberto > a.pct_do_defice_coberto ? b : a));
      return `Défice antes de vendas: ${euros(rows[0].defice_antes_vendas)} por época. No melhor cenário (${max.contrato}, ${max.lugar} lugar), a centralização cobre ${pct(max.pct_do_defice_coberto)}; ` +
        `ainda seriam precisos ${euros(max.mais_valias_necessarias)} de mais-valias.`;
    },
    nota: "Simulação ilustrativa: o modelo de repartição dos direitos centralizados ainda não está definido.",
  },
  {
    id: "tv-por-lugar", seccao: "cenarios", consulta: 48,
    pergunta: "Quanto receberia o Vitória com a TV centralizada?",
    descricao: "Contrato de 250 M€: parte igual e parte por mérito (ilustrativa), por lugar na Liga, sem a componente de audiências.",
    construir: rows => {
      const labels = rows.map(r => lugar(r.lugar));
      const atual = rows[0].total_sem_audiencias - rows[0].vs_tv_atual;
      const cfg = {
        type: "bar",
        data: { labels, datasets: [
          barras("Parte igual", col(rows, "parte_igual"), "tinta", { stack: "tv" }),
          barras("Mérito (ilustrativo)", col(rows, "merito_ilustrativo"), "amarelo", { stack: "tv" }),
        ] },
        options: opcoes({ empilhado: true }),
      };
      cfg.options.plugins.referencias = { linhas: [{ valor: atual, rotulo: `TV atual: ${euros(atual)}` }] };
      return cfg;
    },
    conclusao: rows => `Em qualquer lugar entre o ${lugar(rows[0].lugar)} e o ${lugar(ultimo(rows).lugar)}, o valor ficaria acima da TV atual: de mais ${euros(ultimo(rows).vs_tv_atual)} a mais ${euros(rows[0].vs_tv_atual)}.`,
    nota: "Simulação ilustrativa da consulta 48.",
  },
  {
    id: "parte-igual", seccao: "cenarios", consulta: 26, tabela: true,
    pergunta: "Quanto vale a parte igual por clube?",
    descricao: "Parte igual estimada por clube para três valores do contrato centralizado (2028/29), face à TV do Vitória em 2024/25.",
    conclusao: rows => `Só a parte igual valeria entre ${pct(rows[0].parte_igual_em_pct_do_atual)} e ${pct(ultimo(rows).parte_igual_em_pct_do_atual)} da TV atual.`,
  },
];

/** Escreve a época junto a cada ponto da dispersão (a época em destaque sempre; as outras se couberem) */
const rotulosPontos = {
  id: "rotulosPontos",
  afterDatasetsDraw(chart) {
    const meta = chart.getDatasetMeta(0), dados = chart.data.datasets[0].data;
    const destaque = chart.data.datasets[0].backgroundColor;
    const ctx = chart.ctx;
    const ocupados = meta.data.map(p => ({ x: p.x - 7, y: p.y - 7, w: 14, h: 14 }));
    const sobrepoe = (r, k) => ocupados.some((o, j) => j !== k && r.x < o.x + o.w && r.x + r.w > o.x && r.y < o.y + o.h && r.y + r.h > o.y);
    const ordem = meta.data.map((_, i) => i).sort((a, b) => (destaque[b] === cor("amarelo")) - (destaque[a] === cor("amarelo")));
    ctx.save();
    ctx.textBaseline = "middle";
    ordem.forEach(i => {
      const p = meta.data[i], forte = destaque[i] === cor("amarelo");
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

/* =====================================================================
   PERGUNTAS DE INVESTIGAÇÃO (Visão geral)
   As respostas são calculadas a partir das consultas indicadas.
   ===================================================================== */

export const PERGUNTAS = [
  {
    pergunta: "A atividade corrente cobre os custos recorrentes?", consultas: [2],
    resposta: ({ q }) => {
      const r = q(2), ult3 = r.slice(-3);
      return `Não. Sem mais-valias, o resultado foi negativo em ${contar(r, x => x.rl_sem_mais_valias < 0)} de ${r.length} épocas; ` +
        `em média faltaram ${euros(-media(col(ult3, "rl_sem_mais_valias")))} por época (${ult3[0].epoca}–${ultimo(ult3).epoca}).`;
    },
  },
  {
    pergunta: "Quanto pesam as vendas de jogadores e a Europa?", consultas: [54, 6],
    resposta: ({ q }) => {
      const v = ultimo(q(54)), e = q(6);
      const grupos = e[0], resto = e.slice(1);
      const mediaResto = dividir(soma(resto.map(x => x.receita_media * x.epocas)), soma(resto.map(x => x.epocas)));
      return `Em ${v.epoca}, a SAD vendeu ${razao(v.vendas_por_euro_de_receita)} em jogadores por cada euro de receita. ` +
        `Com fase de grupos europeia, as receitas operacionais médias do grupo sobem de ${euros(mediaResto)} para ${euros(grupos.receita_media)}.`;
    },
  },
  {
    pergunta: "A dívida é sustentável e a que custo?", consultas: [52, 28],
    resposta: ({ q }) => {
      const t = ultimo(com(q(52), "vitoria_implicita")), c = ultimo(q(28));
      return `É cara e curta: taxa implícita de ${pct(t.vitoria_implicita)} em ${t.epoca} (${pp(t.spread_vs_euribor)} face à Euribor) ` +
        `e ${pct(c.pct_curto_prazo)} da dívida a vencer em menos de um ano.`;
    },
  },
  {
    pergunta: "Gastar mais traz melhores classificações?", consultas: [53],
    resposta: ({ q }) => {
      const r = q(53)[0];
      return `Não se consegue demonstrar: R² = ${decimal(r.r_quadrado)} em ${r.n} épocas e o intervalo de confiança do efeito ` +
        `(${decimal(r.ic95_inferior)} a ${decimal(r.ic95_superior)} lugares por M€) ${r.ic95_inferior <= 0 && r.ic95_superior >= 0 ? "inclui o zero" : "não inclui o zero"}.`;
    },
  },
  {
    pergunta: "Que combinação reduz a dependência das vendas?", consultas: [55],
    resposta: ({ q }) => {
      const r = q(55), max = r.reduce((a, b) => (b.pct_do_defice_coberto > a.pct_do_defice_coberto ? b : a));
      return `A centralização dos direitos TV cobriria no máximo ${pct(max.pct_do_defice_coberto)} do défice antes de vendas (${max.contrato}, ${max.lugar} lugar). ` +
        `O resto exige cortar custos, juros mais baixos ou manter as vendas.`;
    },
  },
];

