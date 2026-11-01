// Formatação de números em português (Portugal).
// Valores na base de dados em euros; no ecrã aparecem em milhões ou milhares.

const Formato = (() => {
  const milhoes = new Intl.NumberFormat("pt-PT", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const inteiro = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0 });
  const MENOS = "−"; // sinal de menos tipográfico

  /** 14723467 → "14,7 M€"; −489000 → "−489 mil €" */
  function euros(v) {
    if (v === null || v === undefined) return "—";
    const sinal = v < 0 ? MENOS : "";
    const a = Math.abs(v);
    if (a >= 1e6) return `${sinal}${milhoes.format(a / 1e6)} M€`;
    if (a >= 1e3) return `${sinal}${inteiro.format(a / 1e3)} mil €`;
    return `${sinal}${inteiro.format(a)} €`;
  }

  /** Para os eixos: só o número em milhões ("−15", "20") */
  function eixo(v) {
    const s = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1 }).format(Math.abs(v) / 1e6);
    return (v < 0 ? MENOS : "") + s;
  }

  /** Variação com sinal explícito: "+2,3 M€" / "−1,1 M€" */
  function variacao(v) {
    if (v === null || v === undefined) return "";
    return (v > 0 ? "+" : "") + euros(v);
  }

  function percentagem(v) {
    if (v === null || v === undefined) return "—";
    return `${milhoes.format(v)}%`;
  }

  function numero(v) {
    return v === null || v === undefined ? "—" : inteiro.format(v);
  }

  return { euros, eixo, variacao, percentagem, numero };
})();
