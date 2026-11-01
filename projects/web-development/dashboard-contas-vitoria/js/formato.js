// Formatação de números em português (Portugal), como nas demonstrações financeiras:
// valores negativos entre parênteses. Na base de dados os valores estão em euros.

const Formato = (() => {
  const umaCasa = new Intl.NumberFormat("pt-PT", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const inteiro = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0 });
  const MENOS = "−"; // sinal de menos tipográfico

  /** Valor absoluto em M€, mil € ou € */
  function absoluto(a) {
    if (a >= 1e6) return `${umaCasa.format(a / 1e6)} M€`;
    if (a >= 1e3) return `${inteiro.format(a / 1e3)} mil €`;
    return `${inteiro.format(a)} €`;
  }

  /** 14723467 → "14,7 M€"; −14723467 → "(14,7 M€)" */
  function euros(v) {
    if (v === null || v === undefined) return "—";
    return v < 0 ? `(${absoluto(-v)})` : absoluto(v);
  }

  /** Para os eixos: "5 M€", "(10 M€)", "0" */
  function eixo(v) {
    if (v === 0) return "0";
    const s = `${new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1 }).format(Math.abs(v) / 1e6)} M€`;
    return v < 0 ? `(${s})` : s;
  }

  /** Variação com sinal explícito: "+2,3 M€" / "−1,1 M€" */
  function variacao(v) {
    if (v === null || v === undefined) return "";
    return (v > 0 ? "+" : MENOS) + absoluto(Math.abs(v));
  }

  function percentagem(v) {
    if (v === null || v === undefined) return "—";
    return `${umaCasa.format(v)}%`;
  }

  return { euros, eixo, variacao, percentagem };
})();
