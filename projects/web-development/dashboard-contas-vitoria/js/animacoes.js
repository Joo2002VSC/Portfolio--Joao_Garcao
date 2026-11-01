// Animações: discretas e com função (mostram de onde vêm os valores e o que mudou).
// Tudo é desligado quando o sistema operativo pede menos movimento.

export const reduzido = matchMedia("(prefers-reduced-motion: reduce)").matches;

const escada = (passo, porSerie) => ctx =>
  ctx.type === "data" && ctx.mode === "default" ? ctx.dataIndex * passo + ctx.datasetIndex * porSerie : 0;

/** Opções Chart.js para a primeira vez que um gráfico aparece */
export function entrada(tipo) {
  if (reduzido) return { animation: false };
  switch (tipo) {
    case "bar":
      return { animation: { duration: 650, easing: "easeOutQuart", delay: escada(30, 70) } };
    case "line":
      return {
        animation: { duration: 600, easing: "easeOutQuart", delay: escada(40, 90) },
        animations: { y: { from: ctx => (ctx.type === "data" ? ctx.chart.chartArea?.bottom : undefined) } },
      };
    case "scatter":
      return { animation: { duration: 550, easing: "easeOutBack", delay: escada(35, 0) }, animations: { radius: { from: 0 } } };
    default:
      return { animation: { duration: 500, easing: "easeOutQuart" } };
  }
}

/** Opções Chart.js para atualizações (mudança de filtros) */
export const transicao = () => (reduzido ? { animation: false } : { animation: { duration: 450, easing: "easeInOutCubic" } });

/** Conta de um número até outro, escrevendo-o formatado em cada frame */
export function contar(el, de, para, formatar, duracao = 650) {
  if (reduzido || typeof de !== "number" || typeof para !== "number" || de === para) { el.textContent = formatar(para); return; }
  const t0 = performance.now();
  const passo = agora => {
    const t = Math.min(1, (agora - t0) / duracao);
    el.textContent = formatar(de + (para - de) * (1 - Math.pow(1 - t, 3)));
    if (t < 1) requestAnimationFrame(passo);
  };
  requestAnimationFrame(passo);
}

/** Chama `aoVer(elemento)` uma vez, quando o elemento entra no ecrã */
export function observar(elementos, aoVer) {
  if (reduzido || !("IntersectionObserver" in window)) { elementos.forEach(aoVer); return; }
  const io = new IntersectionObserver(entradas => entradas.forEach(e => {
    if (e.isIntersecting) { io.unobserve(e.target); aoVer(e.target); }
  }), { threshold: 0.12, rootMargin: "0px 0px -30px 0px" });
  elementos.forEach(el => io.observe(el));
}
