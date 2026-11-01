// Animações do dashboard
// - entrada: cada gráfico anima-se na primeira vez que aparece no ecrã
//   (barras a crescer da linha do zero, linhas a subir ponto a ponto, pontos a "saltar")
// - transição: quando um filtro muda, os gráficos transformam-se em vez de redesenhar
// - contagem: os números dos indicadores contam até ao valor novo
// Tudo é desligado se o sistema operativo pedir menos movimento.

const Animacoes = (() => {
  const reduzido = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const suave = "easeOutQuart";

  /** Atraso em escada: ponto a ponto e, dentro de cada época, série a série */
  const escada = (passo, porSerie) => ctx =>
    ctx.type === "data" && ctx.mode === "default" ? ctx.dataIndex * passo + ctx.datasetIndex * porSerie : 0;

  /** Opções de animação para a primeira vez que o gráfico é desenhado */
  function entrada(tipo) {
    if (reduzido) return false;
    if (tipo === "bar") return { duration: 750, easing: suave, delay: escada(45, 110) };
    if (tipo === "hbar") return { duration: 700, easing: suave, delay: escada(70, 0) };
    if (tipo === "line") {
      // Cada ponto sobe a partir do fundo do gráfico, da esquerda para a direita
      return {
        duration: 650, easing: suave, delay: escada(55, 140),
        y: { from: ctx => (ctx.type === "data" ? ctx.chart.chartArea?.bottom : undefined) },
      };
    }
    if (tipo === "scatter") {
      return {
        duration: 600, easing: "easeOutBack", delay: escada(50, 0),
        radius: { from: 0 },
      };
    }
    return { duration: 600, easing: suave };
  }

  /** Opções de animação para as atualizações (mudança de filtros) */
  function transicao() {
    return reduzido ? false : { duration: 550, easing: "easeInOutCubic" };
  }

  /** Conta de um número até outro, escrevendo-o formatado em cada frame */
  function contar(el, de, para, formatar, duracao = 700) {
    if (reduzido || de === null || para === null || de === para) { el.textContent = formatar(para); return; }
    const t0 = performance.now();
    const passo = agora => {
      const t = Math.min(1, (agora - t0) / duracao);
      const e = 1 - Math.pow(1 - t, 3); // easeOutCubic
      el.textContent = formatar(de + (para - de) * e);
      if (t < 1) requestAnimationFrame(passo);
    };
    requestAnimationFrame(passo);
  }

  /** Chama `aoVer(elemento)` uma única vez, quando o elemento entra no ecrã */
  function observar(elementos, aoVer) {
    if (reduzido || !("IntersectionObserver" in window)) { elementos.forEach(aoVer); return; }
    const io = new IntersectionObserver(entradas => {
      entradas.forEach(e => {
        if (e.isIntersecting) { io.unobserve(e.target); aoVer(e.target); }
      });
    }, { threshold: 0.18, rootMargin: "0px 0px -40px 0px" });
    elementos.forEach(el => io.observe(el));
  }

  return { reduzido, entrada, transicao, contar, observar };
})();
