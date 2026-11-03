// Conclusões automáticas da visão geral (dimensão D).
// Cada regra lê uma consulta SQL, aplica um limiar explícito e devolve uma frase com a fonte.
// Os nomes dos indicadores em SENTIDO têm de coincidir com os da consulta complementar D4.

import { linhas } from "./dados.js";
import { euros, pct, racio, vezes, inteiro, variacaoEuros } from "./formato.js";

const naEpoca = (n, epoca) => linhas(n).find(r => r.epoca === epoca) ?? null;

/** Indicadores em que "subir" é favorável (+1) ou desfavorável (−1), para classificar as variações de D4.
    O ativo fica de fora: o seu aumento não é bom nem mau por si (pode ser financiado por dívida). */
export const SENTIDO = {
  "Resultado líquido": 1, "Capitais próprios": 1, "Vendas e serviços prestados": 1, "Mais-valias com jogadores": 1,
  "Passivo": -1, "Gastos com pessoal": -1,
};

/** Época cujas contas foram reexpressas no Relatório e Contas seguinte (consulta 36) */
export const EPOCA_REEXPRESSA = "2024/25";

/** Riscos: limiares de referência habituais na análise financeira, explicitados em cada frase */
const RISCOS = [
  { n: 7, teste: r => r.capital_proprio < 0, frase: r => `Capitais próprios negativos: ${euros(r.capital_proprio)} (o passivo supera o ativo).` },
  { n: 29, teste: r => r.liquidez_geral < 1, frase: r => `Liquidez geral de ${racio(r.liquidez_geral)}: o ativo corrente não cobre o passivo corrente (limiar: 1).` },
  { n: 28, teste: r => r.pct_curto_prazo > 50, frase: r => `${pct(r.pct_curto_prazo)} da dívida financeira vence em menos de um ano (limiar do painel: 50%).` },
  { n: 27, teste: r => r.juros_em_pct_receitas > 20, frase: r => `Os juros dos financiamentos absorvem ${pct(r.juros_em_pct_receitas)} das vendas e serviços prestados (limiar do painel: 20%).` },
  { n: 30, teste: r => r.cobertura !== null && r.cobertura < 3, frase: r => (r.ebitda < 0 ? "EBITDA negativo: não cobre os juros e gastos similares." : `O EBITDA cobre apenas ${vezes(r.cobertura)} os juros e gastos similares (referência: 3 vezes).`) },
  { n: 43, teste: r => /Incerteza material/.test(r.parecer_auditor ?? ""), frase: () => "O auditor assinala incerteza material sobre a continuidade." },
];

const ATENCAO = [
  { n: 2, teste: r => r.rl_sem_mais_valias < 0, frase: r => `Sem mais-valias, o resultado líquido seria de ${euros(r.rl_sem_mais_valias)} (aproximação, sem efeito fiscal).` },
  { n: 3, teste: r => r.pct > 100, frase: r => `Os gastos com pessoal correspondem a ${pct(r.pct)} das vendas e serviços prestados (acima de 100%).` },
  { n: 54, teste: r => r.peso_mais_valias_no_total_pct > 50, frase: r => `As mais-valias representam ${pct(r.peso_mais_valias_no_total_pct)} da soma das vendas e serviços prestados com as mais-valias (acima de metade).` },
  { n: 45, teste: r => r.racio_pct > 70, frase: r => `Rácio de custos do plantel de ${pct(r.racio_pct)}, acima do limite de 70% da UEFA.` },
];

export function conclusoes(epoca) {
  const melhorias = [], riscos = [], atencao = [], estruturais = [];

  // Evolução face à época anterior (consulta complementar D4): favoráveis primeiro, depois desfavoráveis
  const variacoes = linhas(104).filter(r => r.epoca === epoca && r.variacao !== null && r.variacao !== 0 && SENTIDO[r.indicador]);
  [true, false].forEach(favoravel => variacoes
    .filter(r => (Math.sign(r.variacao) === SENTIDO[r.indicador]) === favoravel)
    .forEach(r => melhorias.push({ texto: `${r.indicador}: ${variacaoEuros(r.variacao)} face a ${r.epoca_anterior}.`, n: 104, sentido: favoravel ? "favoravel" : "desfavoravel" })));

  RISCOS.forEach(({ n, teste, frase }) => { const r = naEpoca(n, epoca); if (r && teste(r)) riscos.push({ texto: frase(r), n }); });
  ATENCAO.forEach(({ n, teste, frase }) => { const r = naEpoca(n, epoca); if (r && teste(r)) atencao.push({ texto: frase(r), n }); });

  // Alterações estruturais: pessoal, dívida financeira e reexpressão
  const f = naEpoca(31, epoca);
  if (f?.variacao) estruturais.push({ texto: `Funcionários: ${inteiro(f.funcionarios)} (${f.variacao > 0 ? "+" : "−"}${inteiro(Math.abs(f.variacao))} face à época anterior); ${pct(f.pct_jogadores)} são jogadores.`, n: 31 });
  const d = linhas(27), i = d.findIndex(r => r.epoca === epoca);
  if (i > 0 && d[i].financiamentos !== null && d[i - 1].financiamentos) {
    estruturais.push({ texto: `Dívida financeira de ${euros(d[i].financiamentos)}, ${variacaoEuros(d[i].financiamentos - d[i - 1].financiamentos)} face a ${d[i - 1].epoca}.`, n: 27 });
  }
  // A reexpressão e a aprovação pendente são assinaladas junto ao título da síntese (selos), sem repetir aqui
  return { melhorias, riscos, atencao, estruturais };
}
