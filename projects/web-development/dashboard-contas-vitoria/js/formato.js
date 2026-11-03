// Formatação em português europeu, com as convenções das demonstrações financeiras:
// valores monetários negativos entre parênteses; percentagens e rácios com sinal de menos;
// vírgula decimal; espaço inseparável como separador de milhares (também em números de 4 algarismos).

const MENOS = "\u2212";
const ESPACO = "\u00A0";

/** Formatador pt-PT com separador de milhares sempre presente (o Intl de pt-PT não agrupa "5000") */
function nf(min, max) {
  const base = new Intl.NumberFormat("pt-PT", { minimumFractionDigits: min, maximumFractionDigits: max, useGrouping: false });
  return {
    format(v) {
      const [inteira, dec] = base.format(v).split(",");
      const agrupada = inteira.replace(/\B(?=(\d{3})+(?!\d))/g, ESPACO).replace("-", MENOS);
      return dec === undefined ? agrupada : `${agrupada},${dec}`;
    },
  };
}
const F0 = nf(0, 0), F1 = nf(1, 1), F2 = nf(2, 2), F01 = nf(0, 1), F02 = nf(0, 2), F03 = nf(0, 3);

export const vazio = v => v === null || v === undefined || (typeof v === "number" && !Number.isFinite(v));

function euroAbs(a) {
  if (a >= 1e6) return `${F1.format(a / 1e6)} M€`;
  if (a >= 1e3) return `${F0.format(a / 1e3)} mil €`;
  return `${F0.format(a)} €`;
}

/** 14 723 467 → "14,7 M€"; negativo → "(14,7 M€)" */
export function euros(v) {
  if (vazio(v)) return "—";
  return v < 0 ? `(${euroAbs(-v)})` : euroAbs(v);
}

/** Variação com sinal explícito: "+2,3 M€" / "−1,1 M€" */
export function variacaoEuros(v) {
  if (vazio(v)) return "—";
  if (v === 0) return "0 €";
  return (v > 0 ? "+" : MENOS) + euroAbs(Math.abs(v));
}

export const pct = v => (vazio(v) ? "—" : `${F1.format(v)}%`);
export const pp = v => (vazio(v) ? "—" : `${v > 0 ? "+" : ""}${F1.format(v)} p.p.`);
/** Múltiplo (quantas vezes), em tabelas e indicadores: "2,07×" */
export const razao = v => (vazio(v) ? "—" : `${F2.format(v)}×`);
/** Múltiplo em texto corrido: "4,7 vezes" */
export const vezes = v => (vazio(v) ? "—" : `${(Math.abs(v) < 10 ? F02 : F01).format(v)} ${Math.abs(v) === 1 ? "vez" : "vezes"}`);
/** Rácio sem unidade (liquidez, endividamento): "0,27" */
export const racio = v => (vazio(v) ? "—" : F2.format(v));
export const inteiro = v => (vazio(v) ? "—" : F0.format(v));
export const decimal = v => (vazio(v) ? "—" : F03.format(v));
export const dias = v => (vazio(v) ? "—" : `${F0.format(v)} dias`);
export const milhoes = v => (vazio(v) ? "—" : `${F1.format(v)} M€`);
export const lugar = v => (vazio(v) ? "—" : `${F0.format(v)}.º`);

/** Marcas dos eixos (compactas) por unidade */
export const eixo = {
  eur: v => {
    if (v === 0) return "0";
    const a = Math.abs(v), s = a >= 1e6 ? `${F01.format(a / 1e6)} M€` : `${F0.format(a / 1e3)} mil €`;
    return v < 0 ? `(${s})` : s;
  },
  pct: v => `${F0.format(v)}%`,
  x: v => `${F01.format(v)}×`,
  rat: v => F01.format(v),
  int: v => F0.format(v),
  dias: v => F0.format(v),
  milhoes: v => `${F0.format(v)} M€`,
  lugar: v => `${F0.format(v)}.º`,
};

/** Formatação de um valor pela sua unidade */
export const porUnidade = {
  eur: euros, pct, pp, x: razao, rat: racio, int: inteiro, dias, milhoes, lugar, num: decimal,
  txt: v => (vazio(v) ? "—" : String(v)),
};
export const formatar = (unidade, v) => (porUnidade[unidade] ?? decimal)(v);

/* ---------- Metadados das colunas das consultas SQL ----------
   Rótulo legível e unidade de cada coluna. As exceções por consulta resolvem nomes
   iguais com significados diferentes (ex.: "variacao" em euros na consulta 1, em pessoas na 31). */

const COLUNAS = {
  epoca: ["Época", "txt"], lugar: ["Lugar", "lugar"], posicao_liga: ["Lugar", "lugar"], pontos: ["Pontos", "int"],
  rl: ["Resultado líquido", "eur"], variacao: ["Variação", "eur"], sinal: ["Sinal", "txt"], leitura: ["Leitura", "txt"],
  mais_valias: ["Mais-valias", "eur"], rl_sem_mais_valias: ["Resultado sem mais-valias", "eur"],
  receitas: ["Vendas e serviços prestados", "eur"], pessoal: ["Gastos com pessoal", "eur"], pct: ["Gastos com pessoal / vendas", "pct"], ranking_pior: ["Posição (pior = 1)", "int"],
  ebitda_sem_transferencias: ["EBITDA sem transferências", "eur"], ebitda: ["EBITDA", "eur"],
  tv: ["Direitos de TV", "pct"], competicoes: ["Prémios de competições", "pct"], socios: ["Sócios e camarotes", "pct"],
  patrocinios: ["Patrocínios", "pct"], bilhetica: ["Bilheteira", "pct"], outras: ["Outras", "pct"],
  grupo: ["Grupo", "txt"], tipo: ["Tipo de época", "txt"], epocas: ["Épocas", "int"], lista: ["Lista", "txt"],
  receita_media: ["Receita média", "eur"], rl_medio: ["Resultado médio", "eur"],
  ativo_total: ["Ativo", "eur"], passivo_total: ["Passivo", "eur"], capital_proprio: ["Capital próprio", "eur"],
  situacao: ["Situação", "txt"], epocas_negativas_acumuladas: ["Épocas negativas (acumuladas)", "int"], passivo_sobre_ativo: ["Passivo / ativo", "rat"],
  juros_pagos: ["Juros suportados", "eur"], pct_juros_sobre_receitas: ["Juros / vendas", "pct"],
  juros_2019_20: ["Juros 2019/20", "eur"], juros_2024_25: ["Juros 2024/25", "eur"], multiplicador: ["Multiplicador", "x"], crescimento_anual_pct: ["Crescimento anual", "pct"],
  vendas_brutas: ["Vendas brutas", "eur"], custo_vendas: ["Custo das vendas", "eur"], mais_valias_liquidas: ["Mais-valias líquidas", "eur"],
  mais_valias_sobre_vendas_pct: ["Mais-valias / vendas", "pct"], media_movel_3_epocas: ["Média móvel (3 épocas)", "eur"],
  atletas: ["Atletas", "eur"], total: ["Total", "eur"], pct_atletas: ["Peso dos atletas", "pct"], indice_vs_2017_18: ["Índice (2017/18 = 1)", "x"],
  credor: ["Credor", "txt"], menos_1_ano: ["Menos de 1 ano", "eur"], pct_curto_prazo: ["Curto prazo", "pct"],
  operacional: ["Operacional", "eur"], investimento: ["Investimento", "eur"], financiamento: ["Financiamento", "eur"], caixa_final: ["Caixa no fim", "eur"],
  categoria: ["Categoria", "txt"], valor: ["Valor", "eur"], n_epocas: ["N.º de épocas", "int"], diferenca: ["Diferença", "eur"],
  europa: ["Europa", "txt"], trofeu: ["Troféu", "txt"],
  correlacao: ["Correlação", "num"], pessoal_medio: ["Pessoal médio", "eur"], lugar_medio: ["Classificação média", "num"],
  ranking_gasto: ["Posição nos gastos", "int"], ranking_lugar: ["Posição na classificação", "int"],
  custos_plantel: ["Custos do plantel", "eur"], receitas_relevantes: ["Receitas relevantes", "eur"], racio_pct: ["Rácio", "pct"], racio_sem_vendas_pct: ["Rácio sem vendas", "pct"],
  resultado_com_jogadores_2025_26: ["Resultado com direitos de atletas 2025/26", "eur"], resultado_liquido_2025_26: ["Resultado líquido 2025/26", "eur"],
  necessario_para_equilibrio: ["Necessário para o equilíbrio", "eur"], falta_face_a_2025_26: ["Em falta para o equilíbrio (2025/26)", "eur"],
  valor_total_contrato: ["Contrato total", "eur"], parte_igual_por_clube: ["Parte igual por clube", "eur"], tv_vitoria_2024_25: ["Direitos de TV do Vitória 2024/25", "eur"], parte_igual_em_pct_do_atual: ["Parte igual / direitos de TV atuais", "pct"],
  financiamentos: ["Dívida financeira", "eur"], juros: ["Juros", "eur"], taxa_implicita_pct: ["Taxa implícita", "pct"], juros_em_pct_receitas: ["Juros / vendas", "pct"],
  divida_financeira: ["Dívida financeira", "eur"], caixa: ["Caixa", "eur"], divida_financeira_liquida: ["Dívida financeira líquida", "eur"], outro_passivo: ["Outro passivo", "eur"],
  endividamento: ["Endividamento (passivo / ativo)", "rat"], autonomia_pct: ["Autonomia financeira", "pct"], liquidez_geral: ["Liquidez geral", "rat"], liquidez_imediata_pct: ["Liquidez imediata", "pct"], ranking_endividamento: ["Posição (mais endividada = 1)", "int"],
  cobertura: ["Cobertura dos juros pelo EBITDA", "x"],
  funcionarios: ["Funcionários", "int"], jogadores: ["Jogadores", "int"], treinadores: ["Treinadores", "int"], staff: ["Apoio e outro pessoal", "int"], pct_jogadores: ["Peso dos jogadores", "pct"],
  custo_por_funcionario: ["Custo por funcionário", "eur"], remuneracao_media_jogador: ["Remuneração média por jogador", "eur"], remuneracao_media_treinador: ["Remuneração média por treinador", "eur"], indice_gastos: ["Índice de gastos com pessoal", "rat"],
  nao_jogadores: ["Não-jogadores", "int"], nao_jogadores_por_jogador: ["Não-jogadores por jogador", "rat"],
  espectadores: ["Espectadores (média)", "int"], gastos_pessoal: ["Gastos com pessoal", "eur"], gasto_pessoal_por_espectador: ["Pessoal por espectador", "eur"],
  fonte: ["Fonte", "txt"], divergencias: ["Divergências", "int"], epocas_afetadas: ["Épocas afetadas", "int"], maior_diferenca: ["Maior diferença", "eur"],
  indicador: ["Indicador", "txt"], valor_original: ["Valor original", "eur"], valor_reexpresso: ["Valor reexpresso", "eur"], variacao_pct: ["Variação", "pct"],
  divida_liquida: ["Dívida líquida", "eur"], divida_liq_ebitda: ["Dívida líquida / EBITDA", "x"],
  fundo_maneio: ["Fundo de maneio", "eur"], clientes: ["Clientes", "eur"], pmr_dias: ["Prazo médio de recebimento", "dias"], pmp_dias: ["Prazo médio de pagamento", "dias"],
  outras_contas_pagar: ["Outras contas a pagar", "eur"], outras_contas_pagar_pct_passivo: ["Outras contas a pagar / passivo", "pct"],
  data_ref: ["Data", "txt"], instrumento: ["Instrumento", "txt"], pct_da_divida: ["Peso na dívida", "pct"],
  aquisicoes: ["Aquisições", "eur"], amortizacoes: ["Amortizações", "eur"], investimento_liquido: ["Investimento líquido", "eur"], perda_em_rescisoes: ["Perda em rescisões", "eur"],
  valor_contabilistico_plantel: ["Plantel no balanço", "eur"], taxa_amortizacao_pct: ["Taxa de amortização", "pct"],
  valor_contabilistico_vendido: ["Valor contabilístico vendido", "eur"], reserva_oculta_realizada: ["Reserva oculta realizada", "eur"], multiplo_de_venda: ["Múltiplo de venda", "x"], plantel_no_balanco: ["Plantel no balanço", "eur"],
  custos_fixos: ["Custos fixos", "eur"], cobertura_pct: ["Receitas / custos fixos", "pct"], defice_antes_de_vendas: ["Défice antes de vendas", "eur"],
  metade_capital_social: ["Metade do capital social", "eur"], metade_do_capital_perdida: ["Metade do capital perdida?", "txt"], parecer_auditor: ["Parecer do auditor", "txt"],
  sad_cobra_quotas_e_lugares: ["Cobrado pela SAD (quotas e lugares)", "eur"], rendas_pagas_ao_clube: ["Rendas pagas ao Clube", "eur"], cedencia_pessoal: ["Cedência de pessoal", "eur"], clube_deve_a_sad: ["Saldo devido pelo Clube à SAD", "eur"],
  custo_vendas_pct: ["Custo das vendas / vendas", "pct"],
  solidariedade: ["Solidariedade e formação", "eur"], pct_do_total_do_periodo: ["Peso no período", "pct"], acumulado: ["Acumulado", "eur"],
  parte_igual: ["Parte igual", "eur"], merito_ilustrativo: ["Mérito (ilustrativo)", "eur"], total_sem_audiencias: ["Total (sem audiências)", "eur"], vs_tv_atual: ["Diferença face aos direitos de TV atuais", "eur"],
  custo_por_ponto: ["Custo por ponto", "eur"], ranking_eficiencia: ["Posição em eficiência", "int"],
  mudancas_desde_2015: ["Mudanças desde 2015", "int"], interinos: ["Interinos", "int"], treinadores_diferentes: ["Treinadores diferentes", "int"], media_por_epoca_2015_16_a_2025_26: ["Média por época", "num"],
  margem_corrente_sem_vendas_pct: ["Margem corrente sem vendas", "pct"], margem_operacional_com_vendas_pct: ["Margem operacional com vendas", "pct"],
  rendibilidade_ativo_pct: ["Rendibilidade do ativo", "pct"], rotacao_ativo: ["Rotação do ativo", "rat"], fse_receitas_pct: ["FSE / vendas", "pct"],
  divida_fin_receitas: ["Dívida financeira / vendas", "rat"], cash_flow_operacional_pct: ["Fluxo de caixa operacional / vendas", "pct"],
  bce_deposito: ["BCE (facilidade de depósito)", "pct"], euribor_12m: ["Euribor a 12 meses", "pct"], ot_portugal_10a: ["Obrigações do Tesouro a 10 anos", "pct"], credito_empresas_pt: ["Crédito a empresas em Portugal", "pct"],
  vitoria_implicita: ["Vitória (taxa implícita)", "pct"], spread_vs_euribor: ["Diferencial face à Euribor", "pp"], spread_vs_estado_portugues: ["Diferencial face às OT", "pp"], vezes_estado_portugues: ["Múltiplo da taxa das OT", "x"],
  despesas_m: ["Despesas", "milhoes"], lugar_previsto: ["Lugar previsto", "num"], residuo: ["Resíduo", "num"], a_ordenada: ["Ordenada na origem", "num"],
  b_declive_por_m: ["Declive (lugares por M€)", "num"], erro_padrao_b: ["Erro-padrão do declive", "num"], ic95_inferior: ["IC 95% inferior", "num"], ic95_superior: ["IC 95% superior", "num"],
  r_quadrado: ["R²", "num"], n: ["N.º de épocas", "int"],
  receitas_operacao: ["Receitas da operação", "eur"], vendas_por_euro_de_receita: ["Vendas por euro de receita", "x"], peso_mais_valias_no_total_pct: ["Peso das mais-valias", "pct"],
  contrato: ["Contrato", "txt"], tv_centralizada: ["Direitos de TV centralizados", "eur"], ganho_vs_atual: ["Ganho face ao atual", "eur"], defice_antes_vendas: ["Défice antes de vendas", "eur"],
  mais_valias_necessarias: ["Mais-valias necessárias", "eur"], pct_do_defice_coberto: ["Défice coberto", "pct"],
  gastos_operacionais: ["Gastos operacionais", "eur"], receitas_transferencias: ["Receitas de transferências", "eur"], saldo: ["Saldo", "eur"],
  transferencias_cobrem_pct: ["Cobertura pelas mais-valias", "pct"], saldo_com_receitas_operacao: ["Saldo com receitas da operação", "eur"],
  vendas_servicos: ["Vendas e serviços prestados", "eur"], subsidios: ["Subsídios à exploração", "eur"], outros_rendimentos: ["Outros rendimentos", "eur"], total_rendimentos: ["Total de rendimentos", "eur"], outros_rendimentos_pct: ["Peso de outros rendimentos", "pct"],
  fse: ["Fornecimentos e serviços externos", "eur"], depreciacoes: ["Depreciações e amortizações", "eur"], mercadorias: ["Mercadorias", "eur"], outros_gastos: ["Outros gastos", "eur"],
  imparidades_provisoes: ["Imparidades e provisões", "eur"], total_gastos: ["Total de gastos", "eur"], pessoal_pct: ["Peso do pessoal", "pct"],
  nota: ["Nota", "txt"], rubrica: ["Rubrica", "txt"],
  solvabilidade_pct: ["Solvabilidade", "pct"],
  resultado_operacional: ["Resultado operacional", "eur"], resultado_liquido: ["Resultado líquido", "eur"],
  ro_sem_mais_valias: ["Resultado operacional sem mais-valias", "eur"], financeiro_e_impostos: ["Resultado financeiro e impostos", "eur"],
  rendimentos_operacionais: ["Rendimentos operacionais", "eur"], pessoal_sobre_vendas_pct: ["Gastos com pessoal / vendas", "pct"],
  pessoal_sobre_rendimentos_pct: ["Gastos com pessoal / rendimentos operacionais", "pct"], anterior: ["Época anterior (valor)", "eur"],
  epoca_anterior: ["Época anterior", "txt"], epoca_maximo: ["Época do máximo", "txt"], maximo: ["Máximo", "eur"],
  epoca_minimo: ["Época do mínimo", "txt"], minimo: ["Mínimo", "eur"], estado: ["Estado dos dados", "txt"], documentos: ["Documentos", "txt"], valor_2024_25: ["2024/25", "eur"], valor_2025_26: ["2025/26", "eur"],
};

const EXCECOES = {
  6: { epocas: ["N.º de épocas", "int"] },
  21: { epocas: ["N.º de épocas", "int"] },
  22: { epocas: ["N.º de épocas", "int"] },
  31: { variacao: ["Variação", "int"] },
  54: { media_movel_3_epocas: ["Média móvel (3 épocas)", "x"] },
};

/** Rótulo e unidade de uma coluna (com alternativa pelo padrão do nome e pelo valor) */
export function coluna(nome, consulta, exemplo) {
  const m = EXCECOES[consulta]?.[nome] ?? COLUNAS[nome];
  if (m) return { rotulo: m[0], unidade: m[1] };
  const rotulo = nome.replace(/_/g, " ").replace(/^./, c => c.toUpperCase());
  if (/_pct$|^pct/.test(nome)) return { rotulo, unidade: "pct" };
  if (typeof exemplo === "string") return { rotulo, unidade: "txt" };
  if (typeof exemplo === "number" && Math.abs(exemplo) >= 1000) return { rotulo, unidade: "eur" };
  return { rotulo, unidade: "num" };
}
