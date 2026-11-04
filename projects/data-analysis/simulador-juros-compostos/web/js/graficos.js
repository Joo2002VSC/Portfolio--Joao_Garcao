/* CJR — gráficos em canvas, sem bibliotecas. Todas as cores vêm dos tokens CSS (temas claro e escuro). */
const CJRGraficos = (function () {
  "use strict";
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const FONTE = '12px Outfit, system-ui, sans-serif';

  function preparar(cv) {
    const r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1;
    cv.width = Math.max(1, Math.round(r.width * d)); cv.height = Math.max(1, Math.round(r.height * d));
    const x = cv.getContext("2d"); x.setTransform(d, 0, 0, d, 0, 0);
    return { x, w: r.width, h: r.height };
  }
  /* Máximo "redondo" e nº de divisões que dão marcas legíveis (1, 2, 2,5 ou 5 × 10^k). */
  function escala(v) {
    if (!(v > 0)) return { max: 1, div: 4 };
    const e = Math.pow(10, Math.floor(Math.log10(v))), f = v / e;
    let max = 10 * e; for (const s of [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]) if (f <= s) { max = s * e; break; }
    const boa = t => { const ee = Math.pow(10, Math.floor(Math.log10(t))), ff = +(t / ee).toFixed(6); return [1, 2, 2.5, 5, 10].includes(ff); };
    const div = [5, 4, 6, 3].find(k => boa(max / k)) || 4;
    return { max, div };
  }

  /*
   * Gráfico em leque. d = { anos, p10, p25, p50, p75, p90, investido, objetivo (array|null), classica, curto(fn) }
   * Devolve a geometria para a tooltip.
   */
  function leque(cv, d, hover) {
    const { x, w, h } = preparar(cv), n = d.anos.length, Y = n - 1;
    const L = 60, R = 14, T = 16, B = 28, pw = Math.max(10, w - L - R), ph = Math.max(10, h - T - B);
    let topo = Math.max(...d.p90, ...d.investido, ...d.classica);
    if (d.objetivo) topo = Math.max(topo, ...d.objetivo);
    const { max, div } = escala(topo * 1.03);
    const X = i => L + pw * (Y ? i / Y : 0), Yp = v => T + ph * (1 - Math.min(v, max * 1.05) / max);
    const muted = css("--muted"), line = css("--line");
    x.font = FONTE; x.textBaseline = "middle";
    for (let k = 0; k <= div; k++) {
      const v = max * k / div, yy = Math.round(Yp(v)) + .5;
      x.strokeStyle = line; x.lineWidth = 1; x.beginPath(); x.moveTo(L, yy); x.lineTo(w - R, yy); x.stroke();
      x.fillStyle = muted; x.textAlign = "right"; x.fillText(d.curto(v), L - 8, yy);
    }
    x.textBaseline = "top";
    const maxLbl = Math.max(1, Math.floor(pw / 46)); let passo = 1;
    for (const s of [1, 2, 5, 10, 20]) { passo = s; if (Y / s <= maxLbl) break; }
    for (let i = 0; i <= Y; i += passo) {
      const px = X(i); x.fillStyle = muted;
      x.textAlign = px + 20 > w ? "right" : px - 20 < 0 ? "left" : "center";
      x.fillText(d.anos[i], Math.min(px, w - 2), h - B + 9);
    }
    const banda = (lo, hi, cor) => {
      x.beginPath(); for (let i = 0; i <= Y; i++) x.lineTo(X(i), Yp(hi[i]));
      for (let i = Y; i >= 0; i--) x.lineTo(X(i), Yp(lo[i])); x.closePath(); x.fillStyle = cor; x.fill();
    };
    banda(d.p10, d.p90, css("--good-band")); banda(d.p25, d.p75, css("--good-band-2"));
    const linha = (arr, cor, larg, tr) => {
      x.beginPath(); arr.forEach((v, i) => x.lineTo(X(i), Yp(v)));
      x.strokeStyle = cor; x.lineWidth = larg; x.setLineDash(tr); x.lineJoin = "round"; x.stroke(); x.setLineDash([]);
    };
    linha(d.investido, muted, 1.5, [5, 4]);
    if (d.objetivo) {
      linha(d.objetivo, css("--warn"), 1.6, [6, 4]);
      const yl = Yp(d.objetivo[0]);
      x.fillStyle = css("--warn-ink"); x.textAlign = "left"; x.textBaseline = "bottom";
      x.font = '600 12px Outfit, system-ui, sans-serif'; x.fillText("Objetivo", L + 6, yl - 4); x.font = FONTE;
    }
    linha(d.classica, css("--brand"), 1.3, [2, 3]);
    linha(d.p50, css("--good"), 2.8, []);
    x.fillStyle = css("--good"); x.beginPath(); x.arc(X(Y), Yp(d.p50[Y]), 4.5, 0, 7); x.fill();
    if (hover != null) {
      const hx = Math.round(X(hover)) + .5;
      x.strokeStyle = css("--line-2"); x.lineWidth = 1; x.beginPath(); x.moveTo(hx, T); x.lineTo(hx, T + ph); x.stroke();
      x.fillStyle = css("--card"); x.strokeStyle = css("--good"); x.lineWidth = 2;
      x.beginPath(); x.arc(X(hover), Yp(d.p50[hover]), 4.5, 0, 7); x.fill(); x.stroke();
    }
    return { X, Yp, L, pw, Y };
  }

  /*
   * Histograma do valor final com barra de excesso. d = { ordenados, investido, objetivo, curto(fn) }
   * As barras são coloridas pela posição face ao capital investido e ao objetivo.
   */
  function histograma(cv, d, hover) {
    const { x, w, h } = preparar(cv), s = d.ordenados, n = s.length;
    const muted = css("--muted");
    if (!n) return null;
    const lo = 0, cauda = s[Math.floor((n - 1) * 0.98)];
    const hi = Math.max(cauda, d.objetivo * 1.08, d.investido * 1.08);
    const span = hi - lo, bins = 30, B = 46, T = 34, bw = w / (bins + 1.4);
    if (!(span > 0)) {
      x.fillStyle = muted; x.font = "13px Outfit, system-ui, sans-serif"; x.textAlign = "center"; x.textBaseline = "middle";
      x.fillText("Todos os cenários terminam em " + d.curto(s[0]), w / 2, h / 2); return null;
    }
    const cont = new Array(bins + 1).fill(0);
    for (let i = 0; i < n; i++) { const v = s[i]; cont[v >= hi ? bins : Math.max(0, Math.floor((v - lo) / span * bins))]++; }
    const mx = Math.max(...cont, 1), base = h - B;
    const px = v => (Math.min(v, hi) - lo) / span * bins * bw;
    const cor = c => c >= d.objetivo ? css("--good") : c >= d.investido ? css("--warn") : css("--bad-bar");
    for (let k = 0; k <= bins; k++) {
      const x0 = k < bins ? k * bw : bins * bw + bw * 0.4, larg = bw - 2;
      const meio = k < bins ? lo + span * (k + .5) / bins : hi;
      const bh = (base - T) * cont[k] / mx;
      x.globalAlpha = hover == null || hover === k ? 1 : .5;
      x.fillStyle = cor(meio); x.fillRect(x0 + 1, base - bh, larg, bh);
    }
    x.globalAlpha = 1;
    const ocupados = [];
    const marca = (v, corL, rotulo, alinh) => {
      const gx = Math.round(px(v)) + .5; x.strokeStyle = corL; x.lineWidth = 1.5; x.setLineDash([4, 3]);
      x.beginPath(); x.moveTo(gx, T - 18); x.lineTo(gx, base); x.stroke(); x.setLineDash([]);
      x.fillStyle = corL; x.font = '600 11.5px Outfit, system-ui, sans-serif'; x.textBaseline = "bottom";
      const lw = x.measureText(rotulo).width;
      if (alinh === "right" && gx - 4 - lw < 0) alinh = "left";
      if (alinh === "left" && gx + 4 + lw > w) alinh = "right";
      const x0 = alinh === "left" ? gx + 4 : gx - 4 - lw;
      const sobrepoe = ocupados.some(([a, b]) => x0 < b + 6 && x0 + lw > a - 6);
      ocupados.push([x0, x0 + lw]);
      x.textAlign = alinh; x.fillText(rotulo, gx + (alinh === "left" ? 4 : -4), T - (sobrepoe ? 20 : 6)); x.font = FONTE;
    };
    const ladoInv = px(d.investido) < px(d.objetivo) ? "right" : "left";
    marca(d.investido, muted, "Investido", ladoInv);
    if (d.objetivo > 0) marca(d.objetivo, css("--warn-ink"), "Objetivo", ladoInv === "right" ? "left" : "right");
    // faixa de percentis por baixo do eixo: P10–P90, P25–P75, mediana e média
    const yb = base + 10, q = d.quantis;
    x.strokeStyle = css("--strong"); x.lineWidth = 1.2;
    x.beginPath(); x.moveTo(px(q.p10), yb + 5); x.lineTo(px(q.p90), yb + 5); x.stroke();
    for (const v of [q.p10, q.p90]) { x.beginPath(); x.moveTo(px(v), yb + 1); x.lineTo(px(v), yb + 9); x.stroke(); }
    x.fillStyle = css("--good-band-2"); x.fillRect(px(q.p25), yb, px(q.p75) - px(q.p25), 10);
    x.strokeRect(px(q.p25) + .5, yb + .5, px(q.p75) - px(q.p25), 9);
    x.lineWidth = 2.5; x.strokeStyle = css("--good"); x.beginPath(); x.moveTo(px(q.p50), yb - 2); x.lineTo(px(q.p50), yb + 12); x.stroke();
    const mxp = px(q.media); x.fillStyle = css("--strong"); x.beginPath(); x.moveTo(mxp, yb); x.lineTo(mxp + 5, yb + 5); x.lineTo(mxp, yb + 10); x.lineTo(mxp - 5, yb + 5); x.closePath(); x.fill();
    x.fillStyle = muted; x.font = FONTE; x.textBaseline = "top";
    x.textAlign = "left"; x.fillText("0 €", 0, yb + 16);
    x.textAlign = "right"; x.fillText("≥ " + d.curto(hi), w, yb + 16);
    x.textAlign = "center"; x.fillText(d.curto(hi / 2), px(hi / 2), yb + 16);
    return { bw, bins, lo, span, hi, cont, n };
  }

  return { preparar, escala, leque, histograma, css };
})();
