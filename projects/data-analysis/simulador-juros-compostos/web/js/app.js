/* CJR — interface: formulário, execução no Web Worker e apresentação dos resultados. */
(function () {
  "use strict";
  const M = cjrFabricaModelo(), G = CJRGraficos;
  const $ = id => document.getElementById(id);
  const ANO0 = M.ANO_INICIAL;
  const NOMES_CEN = { base: "Base", pessimista: "Pessimista", otimista: "Otimista", estagflacao: "Estagflação" };

  /* ---------------------------------------------------------------- formatação (pt-PT) */
  const eur = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
  const num = (v, c = 0) => new Intl.NumberFormat("pt-PT", { minimumFractionDigits: c, maximumFractionDigits: c }).format(v);
  const pct = (v, c = 1) => v == null || !isFinite(v) ? "—" : num(v * 100, c) + " %";
  const sinal = v => v > 0 ? "+" : v < 0 ? "−" : "";
  const eurS = v => v == null || !isFinite(v) ? "—" : sinal(Math.round(v)) + eur.format(Math.abs(v));
  const pctS = (v, c = 1) => v == null || !isFinite(v) ? "—" : sinal(v) + pct(Math.abs(v), c);
  function curto(v) {
    const a = Math.abs(v);
    if (a >= 1e6) return num(v / 1e6, a >= 1e7 ? 0 : 1) + " M€";
    if (a >= 1e3) return num(v / 1e3, 0) + " k€";
    return num(v, 0) + " €";
  }
  const nivel = p => p >= .7 ? "good" : p >= .4 ? "warn" : "bad";
  const ICON = {
    good: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="currentColor" opacity=".18"/><path d="M4.8 8.3l2.1 2.1 4.3-4.6" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    warn: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.8l6.6 11.7H1.4z" fill="currentColor" opacity=".2"/><path d="M8 6v3.6M8 11.6v.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    bad: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="currentColor" opacity=".18"/><path d="M5.6 5.6l4.8 4.8M10.4 5.6l-4.8 4.8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    neutral: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
  };
  const TXT_NIVEL = { good: "Provável", warn: "Incerto", bad: "Improvável", neutral: "Sem objetivo" };

  /* ---------------------------------------------------------------- estado */
  const estado = { cenario: "base", unidade: "real", linhas: "marcos", cmp: "cenarios", R: null, lotes: {}, job: 0 };
  const CAMPOS = Object.keys(M.PADRAO).filter(k => $(k));

  /* ---------------------------------------------------------------- formulário */
  const ehPct = el => el.hasAttribute("data-pct");
  const arred = v => Math.round(v * 1e6) / 1e6;
  function encher(p) {
    for (const k of CAMPOS) {
      const el = $(k), v = p[k];
      if (el.type === "checkbox") el.checked = !!v;
      else el.value = ehPct(el) ? arred(v * 100) : v;
    }
    atualizarAux();
  }
  function ler() {
    const p = Object.assign({}, M.PADRAO), invalidos = {};
    for (const k of CAMPOS) {
      const el = $(k);
      if (el.type === "checkbox") p[k] = el.checked;
      else if (el.tagName === "SELECT") p[k] = k === "n_cenarios" ? +el.value : el.value;
      else {
        const v = parseFloat(String(el.value).replace(",", "."));
        if (!isFinite(v)) { invalidos[k] = true; continue; }
        p[k] = ehPct(el) ? v / 100 : v;
      }
    }
    p.ano_alvo = Math.round(p.ano_alvo); p.graus_liberdade = Math.round(p.graus_liberdade); p.semente = Math.round(p.semente);
    const erros = Object.assign(M.validar(p), invalidos);
    mostrarErros(erros);
    return { p, ok: !Object.keys(erros).length };
  }
  function mostrarErros(erros) {
    for (const k of CAMPOS) {
      const el = $(k), f = el.closest(".f"); if (!f) continue;
      let msg = f.querySelector(".msg");
      const err = erros[k];
      f.classList.toggle("err", !!err); el.setAttribute("aria-invalid", err ? "true" : "false");
      if (err) {
        if (!msg) { msg = document.createElement("p"); msg.className = "msg"; msg.id = "msg-" + k; f.appendChild(msg); }
        const desc = (el.getAttribute("aria-describedby") || "").split(" ").filter(Boolean);
        if (!desc.includes(msg.id)) el.setAttribute("aria-describedby", desc.concat(msg.id).join(" "));
        if (Array.isArray(err)) {
          const f2 = v => ehPct(el) ? num(v * 100, 2).replace(/,?0+$/, "") : num(v, 0);
          msg.textContent = `Indique um valor entre ${f2(err[0])} e ${f2(err[1])}.`;
        } else msg.textContent = "Indique um número.";
      } else if (msg) msg.textContent = "";
    }
  }
  function atualizarAux() {
    const c = +$("peso_cripto").value;
    $("barA").style.width = (100 - c) + "%"; $("barC").style.width = c + "%";
    $("lblA").textContent = "Ações " + (100 - c) + "%"; $("lblC").textContent = "Criptoativos " + c + "%";
    $("peso_cripto").setAttribute("aria-valuetext", `${100 - c}% ações, ${c}% criptoativos`);
    const y = Math.round(+$("ano_alvo").value) - ANO0;
    $("horHelp").textContent = y > 0 ? `${y} ${y === 1 ? "ano" : "anos"} (${ANO0}–${ANO0 + y})` : "";
    $("fNu").hidden = $("distribuicao").value !== "t";
    for (const b of document.querySelectorAll("#segCenario button")) b.setAttribute("aria-pressed", String(b.dataset.cen === estado.cenario));
    $("cenHelp").textContent = estado.cenario ? "Define os pressupostos de mercado. O seu plano mantém-se." : "Pressupostos personalizados na configuração avançada.";
    const { p, ok } = ler(); if (ok) renderImplicito(p);
  }

  /* ---------------------------------------------------------------- execução (Web Worker) */
  let fonteWorker = null;
  function novoWorker() {
    try {
      if (!fonteWorker) fonteWorker = URL.createObjectURL(new Blob(
        [`const M=(${cjrFabricaModelo.toString()})();(${cjrCorpoWorker.toString()})(M);`], { type: "text/javascript" }));
      return new Worker(fonteWorker);
    } catch (_) { return null; }
  }
  const workers = { principal: null, aux: null };
  function pedir(canal, msg, aoProgresso) {
    if (workers[canal]) { workers[canal].terminate(); workers[canal] = null; }
    return new Promise((resolve, reject) => {
      const w = novoWorker();
      if (!w) {  // sem Web Workers: corre na própria página
        setTimeout(() => {
          try {
            if (msg.tipo === "simular") resolve(M.simular(msg.params, { progresso: aoProgresso }));
            else resolve(msg.lista.map(it => ({ chave: it.chave, resumo: M.simular(it.params, { leve: true }).resumo })));
          } catch (e) { reject(e); }
        }, 20);
        return;
      }
      workers[canal] = w;
      w.onmessage = ev => {
        const d = ev.data;
        if (d.tipo === "progresso") { if (aoProgresso) aoProgresso(d.f); return; }
        w.terminate(); if (workers[canal] === w) workers[canal] = null;
        if (d.tipo === "erro") reject(new Error(d.mensagem));
        else resolve(d.tipo === "resultado" ? d.res : d.linhas);
      };
      w.onerror = e => { w.terminate(); reject(e); };
      w.postMessage(msg);
    });
  }

  let temporizador = null;
  function agendar(atraso = 250) { clearTimeout(temporizador); temporizador = setTimeout(executar, atraso); }
  async function executar() {
    const { p, ok } = ler();
    if (!ok) { mostrarInvalido(); return; }
    const job = ++estado.job;
    const main = $("main"), barra = $("barra");
    const tLento = setTimeout(() => { if (job === estado.job) { main.setAttribute("aria-busy", "true"); barra.style.width = "4%"; $("statusMeta").textContent = `A simular ${num(p.n_cenarios)} cenários…`; } }, 150);
    try {
      const R = await pedir("principal", { tipo: "simular", params: p }, f => { if (job === estado.job) barra.style.width = Math.max(4, f * 100) + "%"; });
      if (job !== estado.job) return;
      estado.R = R; estado.lotes = {};
      renderTudo();
      calcularLotes(job);
    } catch (e) {
      if (job === estado.job) { $("statusText").textContent = "Não foi possível simular: " + e.message; }
    } finally {
      clearTimeout(tLento);
      if (job === estado.job) { main.setAttribute("aria-busy", "false"); barra.style.width = "0"; }
    }
  }
  function mostrarInvalido() {
    const pill = $("statusPill"); pill.className = "pill bad"; pill.innerHTML = ICON.bad + "Dados inválidos";
    $("statusText").textContent = "Corrija os campos assinalados no painel de parâmetros. Os resultados abaixo correspondem à última simulação válida.";
    $("main").setAttribute("aria-busy", "true");
  }

  /* Comparação de cenários/estratégias e sensibilidade: corridas mais leves, depois do resultado principal. */
  const N_LOTE = p => Math.min(p.n_cenarios, 10000);
  const VARIACOES = [
    ["retorno_acoes", "Rentabilidade das ações", 0.01, "±1 p.p."],
    ["retorno_cripto", "Rentabilidade da cripto", 0.05, "±5 p.p."],
    ["vol_acoes", "Volatilidade das ações", 0.04, "±4 p.p."],
    ["vol_cripto", "Volatilidade da cripto", 0.15, "±15 p.p."],
    ["inflacao", "Inflação média", 0.01, "±1 p.p."],
    ["custos", "Custos de gestão", 0.0025, "±0,25 p.p."],
    ["aporte", "Aporte periódico", "x0.2", "±20 %"],
    ["p_crise", "Probabilidade de crise", 0.03, "±3 p.p."],
    ["peso_cripto", "Peso da cripto", 0.10, "±10 p.p."]
  ];
  function listaCenarios(p) {
    const plano = {}; for (const k in p) if (!M.CAMPOS_MERCADO.includes(k)) plano[k] = p[k];
    plano.n_cenarios = N_LOTE(p);
    const base = {}; for (const k of M.CAMPOS_MERCADO) base[k] = M.PADRAO[k];
    const l = Object.keys(M.CENARIOS).map(c => ({ chave: c, params: Object.assign({}, base, plano, M.CENARIOS[c]) }));
    if (!estado.cenario) l.push({ chave: "atual", params: Object.assign({}, p, { n_cenarios: N_LOTE(p) }) });
    return l;
  }
  function listaEstrategias(p) {
    const l = [{ chave: "atual", params: Object.assign({}, p, { n_cenarios: N_LOTE(p) }) }];
    guardadas().forEach((g, i) => l.push({ chave: "g" + i, params: Object.assign({}, M.PADRAO, g.params, { n_cenarios: N_LOTE(p), semente: p.semente }) }));
    return l;
  }
  function listaSensibilidade(p) {
    const b = Object.assign({}, p, { n_cenarios: 2000 }), l = [{ chave: "base", params: b }];
    for (const [k, , d] of VARIACOES) {
      for (const s of [-1, 1]) {
        const v = typeof d === "string" ? b[k] * (1 + s * parseFloat(d.slice(1))) : b[k] + s * d;
        const lim = M.LIMITES[k], vv = Math.min(lim[1], Math.max(lim[0], v));
        if (Math.abs(vv - b[k]) > 1e-12) l.push({ chave: k + (s < 0 ? ":-" : ":+"), params: Object.assign({}, b, { [k]: vv }) });
      }
    }
    return l;
  }
  async function calcularLotes(job) {
    const p = estado.R.parametros;
    const ordem = estado.cmp === "cenarios" ? ["cenarios", "sens", "estrategias"] : ["estrategias", "sens", "cenarios"];
    renderCmp(); renderTornado();
    for (const qual of ordem) {
      if (qual === "estrategias" && !guardadas().length) { estado.lotes.estrategias = []; renderCmp(); continue; }
      const lista = qual === "cenarios" ? listaCenarios(p) : qual === "estrategias" ? listaEstrategias(p) : listaSensibilidade(p);
      try {
        const linhas = await pedir("aux", { tipo: "lote", lista });
        if (job !== estado.job) return;
        estado.lotes[qual] = linhas;
        if (qual === "sens") renderTornado(); else renderCmp();
      } catch (e) { if (job !== estado.job) return; }
    }
  }

  /* ---------------------------------------------------------------- apresentação */
  function renderTudo() {
    renderStatus(); renderKpis(); renderLeque(); renderDist(); renderTabela(); renderRisco();
    renderPressupostos(); renderPrecisao(); renderImplicito(estado.R.parametros);
  }
  function renderStatus() {
    const R = estado.R, s = R.resumo, p = R.parametros, pill = $("statusPill");
    const semInv = p.capital_inicial === 0 && p.aporte === 0;
    const lv = semInv || p.objetivo_real <= 0 ? "neutral" : nivel(s.prob_objetivo);
    pill.className = "pill " + lv; pill.innerHTML = ICON[lv] + (semInv ? "Sem investimento" : TXT_NIVEL[lv]);
    if (semInv) $("statusText").textContent = "Indique um capital inicial ou um aporte periódico para simular o crescimento do património.";
    else if (p.objetivo_real <= 0) $("statusText").innerHTML = `Valor mediano em ${p.ano_alvo}: <b>${eur.format(s.mediana_real)}</b> em poder de compra de hoje. Defina um objetivo para ver a probabilidade de o atingir.`;
    else $("statusText").innerHTML = `Em <b>${pct(s.prob_objetivo, 0)}</b> dos cenários o património chega a <b>${eur.format(p.objetivo_real)}</b> em poder de compra de hoje até <b>${p.ano_alvo}</b>. Valor mediano: <b>${eur.format(s.mediana_real)}</b> (€ de hoje).`;
    const meia = (s.ic95_mediana_real[1] - s.ic95_mediana_real[0]) / 2;
    $("statusMeta").textContent = `${estado.cenario ? "Cenário " + NOMES_CEN[estado.cenario] : "Pressupostos personalizados"} · ${num(R.N)} cenários · mediana ±${curto(meia)}`;
  }
  function renderKpis() {
    const R = estado.R, s = R.resumo, p = R.parametros;
    $("kMedLbl").innerHTML = `Património mediano <span class="base">€ de ${p.ano_alvo}</span>`;
    $("kMed").textContent = eur.format(s.mediana_nominal);
    $("kMedS").textContent = `Metade dos cenários termina acima deste valor, em euros nominais de ${p.ano_alvo}.`;
    $("kReal").textContent = eur.format(s.mediana_real);
    $("kRealS").textContent = `O mesmo valor descontada a inflação de cada cenário (média de ${pct(p.inflacao)} ao ano).`;
    if (p.objetivo_real > 0) {
      $("kObj").textContent = pct(s.prob_objetivo, 0);
      $("kObjS").textContent = `Cenários com pelo menos ${eur.format(p.objetivo_real)} de hoje em ${p.ano_alvo} (margem ±${num(1.96 * s.erro_prob_objetivo * 100, 1)} p.p.).`;
    } else { $("kObj").textContent = "—"; $("kObjS").textContent = "Defina um objetivo para ver esta probabilidade."; }
    $("kRange").textContent = `${curto(s.p10_real)} – ${curto(s.p90_real)}`;
    $("kInv").textContent = eur.format(s.investido_medio);
    $("kInvS").textContent = `Capital inicial mais aportes (média dos cenários). Em € de hoje: ${eur.format(s.investido_real_medio)}.`;
    const cls = (el, v) => { el.classList.toggle("pos", v > 0); el.classList.toggle("neg", v < 0); };
    $("kGN").textContent = eurS(s.ganho_nominal_mediano); cls($("kGN"), s.ganho_nominal_mediano);
    $("kGR").textContent = eurS(s.ganho_real_mediano); cls($("kGR"), s.ganho_real_mediano);
    $("kAcum").textContent = pctS(s.rentab_acumulada_mediana, 0); cls($("kAcum"), s.rentab_acumulada_mediana);
    const tn = s.tir_nominal[50], tr = s.tir_real[50];
    $("kTir").textContent = tn == null ? "—" : pctS(tn) + "/ano";
    $("kTirS").textContent = tn == null ? "Sem capital investido." :
      `Nominal, no cenário mediano. Real: ${pctS(tr)}/ano (P10 a P90: ${pctS(s.tir_real[10])} a ${pctS(s.tir_real[90])}).`;
    $("kPerda").textContent = pct(s.prob_perda_real, 0);
    $("kPerdaS").textContent = `Cenários que terminam abaixo do capital investido, em poder de compra (em euros nominais: ${pct(s.prob_perda_nominal, 0)}).`;
  }

  /* séries por ano na unidade escolhida */
  function series(un) {
    const R = estado.R, p = R.parametros, ix = q => R.percentis.indexOf(q);
    const src = un === "real" ? R.anoPct.real : R.anoPct.nominal;
    const infl = y => Math.pow(1 + p.inflacao, y);
    return {
      anos: R.anos, p10: src[ix(10)], p25: src[ix(25)], p50: src[ix(50)], p75: src[ix(75)], p90: src[ix(90)],
      investido: Array.from(un === "real" ? R.investidoRealMedio : R.investidoMedio),
      objetivo: p.objetivo_real > 0 ? R.anos.map((_, y) => un === "real" ? p.objetivo_real : p.objetivo_real * infl(y)) : null,
      classica: R.deterministico.map((v, y) => un === "real" ? v / infl(y) : v), curto
    };
  }
  let geoLeque = null, dadosLeque = null;
  function renderLeque(hover) {
    if (!estado.R) return;
    const p = estado.R.parametros;
    dadosLeque = series(estado.unidade);
    geoLeque = G.leque($("chart"), dadosLeque, hover);
    const Y = dadosLeque.anos.length - 1;
    $("chart").setAttribute("aria-label", `Gráfico em leque, ${estado.unidade === "real" ? "em € de hoje" : "em euros nominais"}: em ${p.ano_alvo} a mediana é ${eur.format(dadosLeque.p50[Y])}, com 80 % dos cenários entre ${eur.format(dadosLeque.p10[Y])} e ${eur.format(dadosLeque.p90[Y])}.`);
    $("evoSub").textContent = estado.unidade === "real"
      ? "Em € de hoje. A mediana está a cheio; as bandas mostram onde ficam 50 % e 80 % dos cenários."
      : `Em euros nominais de cada ano. O objetivo cresce com a inflação média (${pct(p.inflacao)}).`;
  }
  function renderDist(hover) {
    const R = estado.R, s = R.resumo, p = R.parametros;
    const ord = M.ordenar(R.finalReal);
    const q = { p10: s.p10_real, p25: s.p25_real, p50: s.mediana_real, p75: s.p75_real, p90: s.p90_real, media: s.media_real };
    estado.geoHist = G.histograma($("hist"), { ordenados: ord, investido: s.investido_real_medio, objetivo: p.objetivo_real, quantis: q, curto }, hover);
    $("hist").setAttribute("aria-label", `Histograma do valor final em € de hoje: mediana ${eur.format(s.mediana_real)}, média ${eur.format(s.media_real)}, ${pct(s.prob_perda_real, 0)} abaixo do investido e ${pct(s.prob_objetivo, 0)} acima do objetivo.`);
    $("distSub").textContent = `Valor em ${p.ano_alvo}, em € de hoje, nos ${num(R.N)} cenários. Por baixo: caixa P25–P75, bigodes P10–P90, traço verde na mediana e losango na média.` +
      (s.media_real > s.mediana_real * 1.05 ? " A média fica acima da mediana porque poucos cenários muito favoráveis a puxam para cima." : "");
    const linhas = [
      ["Média", eur.format(s.media_real)], ["Mediana", eur.format(s.mediana_real)],
      ["P10", eur.format(s.p10_real)], ["P25", eur.format(s.p25_real)], ["P75", eur.format(s.p75_real)], ["P90", eur.format(s.p90_real)],
      null,
      ["Capital investido", eur.format(s.investido_real_medio)],
      ["Probabilidade de perda", pct(s.prob_perda_real, 1)],
      ["Probabilidade de atingir o objetivo", p.objetivo_real > 0 ? pct(s.prob_objetivo, 1) : "—"]
    ];
    $("distStats").innerHTML = linhas.map(l => l ? `<dt>${l[0]}</dt><dd>${l[1]}</dd>` : '<span class="sep" role="presentation"></span>').join("");
  }
  function renderTabela() {
    const R = estado.R, d = series(estado.unidade), Y = d.anos.length - 1;
    const passo = estado.linhas === "todos" ? 1 : (Y > 30 ? 5 : Y > 12 ? 2 : 1), out = [];
    for (let y = 0; y <= Y; y++) {
      if (y % passo && y !== Y) continue;
      const inv = d.investido[y], abaixo = d.p10[y] < inv - 1e-9, r = inv > 0 ? d.p50[y] / inv : null;
      out.push(`<tr class="${y === Y ? "tgt" : ""}"><td>${d.anos[y]}</td><td>${eur.format(inv)}</td><td class="${abaixo ? "neg" : ""}">${abaixo ? '<span class="ar" aria-hidden="true">▼</span><span class="sr-only">abaixo do investido: </span>' : ""}${eur.format(d.p10[y])}</td><td class="med">${eur.format(d.p50[y])}</td><td>${eur.format(d.p90[y])}</td><td>${r == null ? "—" : num(r, 2) + "×"}</td><td>${eur.format(d.classica[y])}</td></tr>`);
    }
    $("tbody").innerHTML = out.join("");
    $("tblSub").textContent = (estado.unidade === "real" ? "Em € de hoje" : "Em euros nominais") + ", a mesma base do gráfico de evolução. ▼ assinala anos em que o P10 fica abaixo do capital investido.";
  }
  function renderRisco() {
    const R = estado.R, s = R.resumo, p = R.parametros, Y = R.Y;
    const perdaAnual = s.var95_anual < 0;
    $("rcards").innerHTML = `
      <div class="rcard"><h3>Queda máxima pelo caminho</h3><span class="v">${pct(s.drawdown_mediano, 0)} <small>mediana · pior 10 %: ${pct(s.drawdown_p90, 0)}</small></span>
        <p>Maior descida, do pico ao mínimo, do valor de cada euro investido (sem contar novos aportes). É a perda temporária que teria de aguentar sem vender.</p></div>
      <div class="rcard"><h3>Perda num mau ano (VaR 95 %)</h3><span class="v">${perdaAnual ? "−" + pct(-s.var95_anual, 0) : "Sem perda"} <small>média dos 5 % piores anos (CVaR): ${s.cvar95_anual < 0 ? "−" + pct(-s.cvar95_anual, 0) : pct(s.cvar95_anual, 0)}</small></span>
        <p>${perdaAnual ? `Em 1 de cada 20 anos, a carteira pode cair ${pct(-s.var95_anual, 0)} ou mais.` : "Mesmo nos 5 % piores anos, a carteira não desce."} Calculado sobre todos os anos de todos os cenários.</p></div>
      <div class="rcard"><h3>Cauda no fim do horizonte</h3><span class="v">${eur.format(s.p5_real)} <small>média dos 5 % piores: ${eur.format(s.cvar5_real)}</small></span>
        <p>Em 5 % dos cenários o património em ${p.ano_alvo} fica abaixo deste valor (€ de hoje). Capital investido: ${eur.format(s.investido_real_medio)}.</p></div>
      <div class="rcard"><h3>Pelo menos uma crise de mercado</h3><span class="v">${pct(s.prob_crise, 0)}</span>
        <p>Probabilidade de haver pelo menos uma crise em ${Y} anos, com ${pct(p.p_crise, 0)} por ano.</p></div>`;
  }
  function renderTornado() {
    const el = $("tornado"), L = estado.lotes.sens;
    if (!L) { el.innerHTML = '<p class="cmp-empty">A calcular a sensibilidade…</p>'; return; }
    const val = Object.fromEntries(L.map(l => [l.chave, l.resumo.mediana_real]));
    const base = val.base;
    const rows = VARIACOES.map(([k, nome, , tag]) => ({ k, nome, tag, lo: val[k + ":-"], hi: val[k + ":+"] }))
      .filter(r => r.lo != null || r.hi != null)
      .map(r => Object.assign(r, { amp: Math.abs((r.hi ?? base) - (r.lo ?? base)) }))
      .sort((a, b) => b.amp - a.amp);
    let mn = base, mx = base; for (const r of rows) for (const v of [r.lo, r.hi]) if (v != null) { mn = Math.min(mn, v); mx = Math.max(mx, v); }
    const pad = (mx - mn) * .04 || 1; mn -= pad; mx += pad;
    const X = v => (v - mn) / (mx - mn) * 100, cx = X(base);
    const seg = v => { if (v == null) return ""; const a = Math.min(X(v), cx), b = Math.max(X(v), cx); return `<i class="${v < base ? "lo" : "hi"}" style="left:${a}%;width:${Math.max(.4, b - a)}%"></i>`; };
    const desc = r => [r.lo != null ? `menos: ${curto(r.lo)}` : null, r.hi != null ? `mais: ${curto(r.hi)}` : null].filter(Boolean).join(" · ");
    el.innerHTML = rows.map(r => `<div class="tr"><span class="nm">${r.nome} ${r.tag}<small>${desc(r)}</small></span><div class="trk" role="img" aria-label="${r.nome}: ${desc(r)}; base ${curto(base)}">${seg(r.lo)}${seg(r.hi)}<span class="c" style="left:${cx}%"></span></div></div>`).join("");
    $("sensSub").textContent = `Mediana em € de hoje (base ${curto(base)}) quando cada pressuposto muda e os restantes se mantêm. Vermelho: pior do que a base; verde: melhor. 2 000 cenários com os mesmos números aleatórios, para isolar o efeito de cada parâmetro.`;
  }
  function renderCmp() {
    const el = $("cmp"), modo = estado.cmp, L = estado.lotes[modo], p = estado.R && estado.R.parametros;
    for (const b of document.querySelectorAll("[data-cmp]")) b.setAttribute("aria-pressed", String(b.dataset.cmp === modo));
    if (!p) return;
    $("cmpSub").textContent = modo === "cenarios"
      ? `O seu plano nos quatro cenários de mercado, com a mesma semente e ${num(N_LOTE(p))} cenários cada: as diferenças vêm só dos pressupostos de mercado. Valores em € de hoje.`
      : `As configurações guardadas, cada uma com os seus parâmetros, a mesma semente e ${num(N_LOTE(p))} cenários. Valores em € de hoje, no ano final de cada estratégia.`;
    if (modo === "estrategias" && !guardadas().length) {
      el.innerHTML = '<p class="cmp-empty">Ainda não guardou nenhuma configuração. Abra «Configurações guardadas» no painel, dê um nome ao plano atual e carregue em Guardar. Depois altere o plano e compare aqui.</p>'; return;
    }
    if (!L) { el.innerHTML = '<p class="cmp-empty">A calcular a comparação…</p>'; return; }
    const g = guardadas();
    const nome = c => c === "atual" ? (modo === "cenarios" ? "Personalizado" : "Plano atual") : modo === "cenarios" ? NOMES_CEN[c] : g[+c.slice(1)] ? g[+c.slice(1)].nome : c;
    const sub = (c, s) => {
      if (modo === "cenarios") {
        const m = Object.assign({}, M.PADRAO, M.CENARIOS[c] || {}, c === "atual" ? p : {});
        return `ações ${pct(m.retorno_acoes, 1)} · cripto ${pct(m.retorno_cripto, 0)} · inflação ${pct(m.inflacao, 1)}`;
      }
      const q = c === "atual" ? p : Object.assign({}, M.PADRAO, g[+c.slice(1)].params);
      return `${eur.format(q.aporte)} ${q.frequencia === "mensal" ? "/mês" : q.frequencia === "semanal" ? "/semana" : "/ano"} · ${pct(q.peso_cripto, 0)} cripto · ${q.ano_alvo}`;
    };
    let mx = 0; for (const l of L) mx = Math.max(mx, l.resumo.p90_real); if (p.objetivo_real > 0 && modo === "cenarios") mx = Math.max(mx, p.objetivo_real);
    mx *= 1.05;
    const X = v => Math.max(0, Math.min(100, v / mx * 100));
    const atual = modo === "cenarios" ? (estado.cenario || "atual") : "atual";
    el.innerHTML = `<div class="hd"><span>${modo === "cenarios" ? "Cenário" : "Estratégia"}</span><span>P10 – mediana – P90 (0 a ${curto(mx)})</span><span class="num">Mediana</span><span class="num">Objetivo</span><span class="num">Perda real</span></div>` +
      L.map(l => {
        const s = l.resumo, cur = l.chave === atual;
        return `<div class="rw${cur ? " cur" : ""}"><span class="nm">${nome(l.chave)}${cur ? ' <span class="sr-only">(selecionado)</span>' : ""}<small>${sub(l.chave, s)}</small></span>
          <div class="rng" role="img" aria-label="${nome(l.chave)}: P10 ${eur.format(s.p10_real)}, mediana ${eur.format(s.mediana_real)}, P90 ${eur.format(s.p90_real)}"><span class="ax"></span><span class="bar" style="left:${X(s.p10_real)}%;width:${X(s.p90_real) - X(s.p10_real)}%"></span>${modo === "cenarios" && p.objetivo_real > 0 ? `<span class="goal" style="left:${X(p.objetivo_real)}%" title="Objetivo"></span>` : ""}<span class="med" style="left:${X(s.mediana_real)}%"></span></div>
          <span class="num md">${curto(s.mediana_real)}</span><span class="num po" title="Probabilidade de atingir o objetivo">${pct(s.prob_objetivo, 0)}</span><span class="num pp" title="Probabilidade de perda real">${pct(s.prob_perda_real, 0)}</span></div>`;
      }).join("");
  }
  function renderImplicito(p) {
    const r = M.rentabilidadeImplicita(p), s = estado.R && estado.R.resumo;
    const ma = v => v == null ? '<span title="Com a Student-t a média aritmética teórica não está definida">n.d.</span>' : pct(v, 1);
    $("implicito").innerHTML = `<table><caption class="sr-only">Rentabilidades anuais implícitas nos pressupostos</caption>
      <thead><tr><th scope="col">Implícito</th><th scope="col">Mediana</th><th scope="col">Média aritm.</th><th scope="col">Efetiva</th></tr></thead>
      <tbody><tr><td>Ações</td><td>${pct(r.acoes.mediana, 1)}</td><td>${ma(r.acoes.media_aritm)}</td><td>${pct(r.acoes.efetiva, 1)}</td></tr>
      <tr><td>Cripto</td><td>${pct(r.cripto.mediana, 1)}</td><td>${ma(r.cripto.media_aritm)}</td><td>${pct(r.cripto.efetiva, 1)}</td></tr></tbody></table>
      <p>Efetiva = crescimento composto esperado depois de crises, regulação e custos.${s && s.tir_nominal[50] != null && estado.R.parametros === p ? ` Carteira simulada: TIR nominal mediana de ${pct(s.tir_nominal[50], 1)}.` : ""}</p>`;
  }
  function renderPressupostos() {
    const p = estado.R.parametros;
    const itens = [
      ["Cenário de mercado", estado.cenario ? NOMES_CEN[estado.cenario] : "Personalizado"],
      ["Capital inicial", eur.format(p.capital_inicial)], ["Aporte", `${eur.format(p.aporte)} (${p.frequencia})`],
      ["Aumento anual do aporte", pct(p.crescimento_aporte, 1)], ["Horizonte", `${ANO0}–${p.ano_alvo}`],
      ["Objetivo", eur.format(p.objetivo_real) + " de hoje"], ["Composição", `${pct(1 - p.peso_cripto, 0)} ações · ${pct(p.peso_cripto, 0)} cripto`],
      ["Rentab. mediana ações / cripto", `${pct(p.retorno_acoes, 1)} / ${pct(p.retorno_cripto, 1)}`],
      ["Volatilidade ações / cripto", `${pct(p.vol_acoes, 0)} / ${pct(p.vol_cripto, 0)}`], ["Correlação", num(p.correlacao, 2)],
      ["Distribuição", p.distribuicao === "t" ? `Student-t (ν = ${p.graus_liberdade})` : "Log-normal"],
      ["Custos de gestão", pct(p.custos, 2) + "/ano"], ["Rebalanceamento", p.rebalancear ? "Anual" : "Não"],
      ["Inflação", `${pct(p.inflacao, 1)} ± ${num(p.vol_inflacao * 100, 1)} p.p.`], ["Aportes indexados", p.indexar_inflacao ? "Sim" : "Não"],
      ["Crise de mercado", `${pct(p.p_crise, 0)}/ano (−${pct(p.queda_crise_acoes, 0)} / −${pct(p.queda_crise_cripto, 0)})`],
      ["Regulação cripto", `${pct(p.p_regulacao, 0)}/ano (−${pct(p.queda_regulacao, 0)})`],
      ["Choque de inflação", `${pct(p.p_choque_inflacao, 0)}/ano (+${num(p.choque_inflacao * 100, 1)} p.p.)`],
      ["Pausa nos aportes", `${pct(p.p_pausa, 0)}/ano`], ["Cenários / semente", `${num(p.n_cenarios)} / ${p.semente}`]
    ];
    $("pressupostos").innerHTML = itens.map(([a, b]) => `<div><dt>${a}</dt><dd>${b}</dd></div>`).join("");
  }
  function renderPrecisao() {
    const R = estado.R, s = R.resumo, meia = (s.ic95_mediana_real[1] - s.ic95_mediana_real[0]) / 2;
    $("precisao").innerHTML = `Com <b>${num(R.N)}</b> cenários, a mediana em € de hoje tem uma margem de erro de cerca de <b>±${eur.format(meia)}</b> (intervalo de confiança de 95 %, pelas estatísticas de ordem)` +
      (R.parametros.objetivo_real > 0 ? ` e a probabilidade de atingir o objetivo de <b>±${num(1.96 * s.erro_prob_objetivo * 100, 1)} p.p.</b>` : "") +
      `. Para reduzir a margem a metade são precisos quatro vezes mais cenários. Este erro é só de amostragem: não mede o erro dos pressupostos, que normalmente é muito maior.`;
  }

  /* ---------------------------------------------------------------- tooltips */
  const tip = $("tip"), cbox = $("cbox");
  function moverLeque(e) {
    if (!geoLeque) return;
    const r = cbox.getBoundingClientRect(), y = Math.round((e.clientX - r.left - geoLeque.L) / geoLeque.pw * geoLeque.Y);
    if (y < 0 || y > geoLeque.Y) { esconderLeque(); return; }
    const d = dadosLeque, linha = (a, b, f) => `<div class="row"><span>${a}</span><span${f ? ' style="font-weight:700;color:var(--strong)"' : ""}>${b}</span></div>`;
    tip.hidden = false;
    tip.innerHTML = `<b>${d.anos[y]}</b>` + linha("P90", eur.format(d.p90[y])) + linha("P75", eur.format(d.p75[y])) + linha("Mediana", eur.format(d.p50[y]), true) +
      linha("P25", eur.format(d.p25[y])) + linha("P10", eur.format(d.p10[y])) + linha("Capital investido", eur.format(d.investido[y])) +
      (d.objetivo ? linha("Objetivo", eur.format(d.objetivo[y])) : "") + linha("Calc. clássica", eur.format(d.classica[y]));
    const tx = geoLeque.X(y), tw = tip.offsetWidth, th = tip.offsetHeight;
    tip.style.left = (tx + 14 + tw > r.width ? Math.max(4, tx - tw - 14) : tx + 14) + "px";
    tip.style.top = Math.max(4, Math.min(r.height - th - 4, geoLeque.Yp(d.p50[y]) - th / 2)) + "px";
    renderLeque(y);
  }
  function esconderLeque() { tip.hidden = true; if (estado.R) renderLeque(); }
  cbox.addEventListener("pointermove", moverLeque); cbox.addEventListener("pointerdown", moverLeque); cbox.addEventListener("pointerleave", esconderLeque);
  const htip = $("htip"), hbox = $("hbox");
  hbox.addEventListener("pointermove", e => {
    const g = estado.geoHist; if (!g) return;
    const r = hbox.getBoundingClientRect(), px = e.clientX - r.left;
    let k = px < g.bins * g.bw ? Math.floor(px / g.bw) : (px >= g.bins * g.bw + g.bw * .4 ? g.bins : -1);
    if (k < 0 || k > g.bins) { htip.hidden = true; return; }
    const a = g.lo + g.span * k / g.bins, b = a + g.span / g.bins;
    htip.hidden = false;
    htip.innerHTML = `<b>${k === g.bins ? "≥ " + curto(g.hi) : curto(a) + " – " + curto(b)}</b><div class="row"><span>Cenários</span><span>${pct(g.cont[k] / g.n, 1)}</span></div>`;
    const tw = htip.offsetWidth; htip.style.left = Math.min(r.width - tw - 4, Math.max(4, px - tw / 2)) + "px"; htip.style.top = "4px";
    renderDist(k);
  });
  hbox.addEventListener("pointerleave", () => { htip.hidden = true; if (estado.R) renderDist(); });

  /* ---------------------------------------------------------------- configurações guardadas (localStorage) */
  const CHAVE = "cjr.configuracoes.v1";
  function guardadas() { try { const v = JSON.parse(localStorage.getItem(CHAVE) || "[]"); return Array.isArray(v) ? v : []; } catch (_) { return []; } }
  function gravar(lista) { try { localStorage.setItem(CHAVE, JSON.stringify(lista)); return true; } catch (_) { return false; } }
  function renderGuardadas() {
    const g = guardadas(), el = $("listaGuardadas");
    el.innerHTML = g.length ? g.map((c, i) => `<div class="row"><b title="${c.nome.replace(/"/g, "&quot;")}">${c.nome.replace(/</g, "&lt;")}</b><span><button class="linkbtn" type="button" data-carregar="${i}">Carregar</button><button class="linkbtn" type="button" data-apagar="${i}" aria-label="Apagar ${c.nome.replace(/"/g, "&quot;")}">Apagar</button></span></div>`).join("")
      : '<p class="help" style="margin:0;font-size:12.5px;color:var(--muted)">Ainda não há configurações guardadas neste navegador.</p>';
  }
  $("guardar").addEventListener("click", () => {
    const nome = $("nomeConfig").value.trim(), msg = $("guardarMsg");
    const { p, ok } = ler();
    msg.hidden = false;
    if (!nome) { msg.textContent = "Indique um nome para a configuração."; $("nomeConfig").focus(); return; }
    if (!ok) { msg.textContent = "Corrija os campos assinalados antes de guardar."; return; }
    const g = guardadas().filter(c => c.nome !== nome);
    g.push({ nome, params: p, data: new Date().toISOString() });
    if (g.length > 12) g.shift();
    if (!gravar(g)) { msg.textContent = "Este navegador não permite guardar configurações nesta janela."; return; }
    msg.hidden = true; $("nomeConfig").value = ""; renderGuardadas();
    if (estado.R) { estado.lotes.estrategias = null; calcularLotes(estado.job); }
  });
  $("listaGuardadas").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    const g = guardadas();
    if (b.dataset.carregar != null) {
      const c = g[+b.dataset.carregar]; if (!c) return;
      const p = Object.assign({}, M.PADRAO, c.params);
      estado.cenario = Object.keys(M.CENARIOS).find(k => M.CAMPOS_MERCADO.every(f => Math.abs(p[f] - (M.CENARIOS[k][f] ?? M.PADRAO[f])) < 1e-12)) || null;
      encher(p); executar();
    } else if (b.dataset.apagar != null) {
      g.splice(+b.dataset.apagar, 1); gravar(g); renderGuardadas();
      if (estado.R) { estado.lotes.estrategias = null; calcularLotes(estado.job); }
    }
  });

  /* ---------------------------------------------------------------- exportar */
  $("csv").addEventListener("click", () => {
    const R = estado.R; if (!R) return;
    const p = R.parametros, nr = v => num(v, 2).replace(/\s/g, ""), ix = q => R.percentis.indexOf(q);
    const L = ["CJR — Calculador de Juros Compostos;Simulação de Monte Carlo", "Gerado em;" + new Date().toLocaleString("pt-PT"),
      "Aviso;Simulação ilustrativa, não é aconselhamento financeiro", ""];
    L.push("Parâmetro;Valor"); for (const k of Object.keys(M.PADRAO)) L.push(`${k};${typeof p[k] === "number" ? nr(p[k]).replace(/,00$/, "") : p[k]}`);
    L.push("", "Ano;Investido (nominal);P10 (nominal);P25 (nominal);Mediana (nominal);P75 (nominal);P90 (nominal);Investido (€ de hoje);P10 (€ de hoje);P25 (€ de hoje);Mediana (€ de hoje);P75 (€ de hoje);P90 (€ de hoje);Calculadora clássica (nominal)");
    for (let y = 0; y <= R.Y; y++) {
      const v = [R.anos[y], nr(R.investidoMedio[y]), ...[10, 25, 50, 75, 90].map(q => nr(R.anoPct.nominal[ix(q)][y])), nr(R.investidoRealMedio[y]),
        ...[10, 25, 50, 75, 90].map(q => nr(R.anoPct.real[ix(q)][y])), nr(R.deterministico[y])];
      L.push(v.join(";"));
    }
    const blob = new Blob(["﻿" + L.join("\r\n")], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `cjr-simulacao-${p.ano_alvo}.csv`;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  $("imprimir").addEventListener("click", () => window.print());

  /* ---------------------------------------------------------------- eventos do formulário */
  for (const k of CAMPOS) {
    $(k).addEventListener("input", () => {
      if (M.CAMPOS_MERCADO.includes(k)) estado.cenario = null;
      atualizarAux(); agendar(k === "n_cenarios" ? 0 : 250);
    });
  }
  $("segCenario").addEventListener("click", e => {
    const b = e.target.closest("button[data-cen]"); if (!b) return;
    const { p } = ler(); const novo = Object.assign({}, p);
    for (const k of M.CAMPOS_MERCADO) novo[k] = M.PADRAO[k];
    Object.assign(novo, M.CENARIOS[b.dataset.cen]);
    estado.cenario = b.dataset.cen; encher(novo); agendar(0);
  });
  $("repor").addEventListener("click", () => { estado.cenario = "base"; encher(M.PADRAO); agendar(0); });
  for (const b of document.querySelectorAll("[data-u]")) b.addEventListener("click", () => {
    estado.unidade = b.dataset.u; for (const o of document.querySelectorAll("[data-u]")) o.setAttribute("aria-pressed", String(o === b));
    if (estado.R) { renderLeque(); renderTabela(); }
  });
  for (const b of document.querySelectorAll("[data-r]")) b.addEventListener("click", () => {
    estado.linhas = b.dataset.r; for (const o of document.querySelectorAll("[data-r]")) o.setAttribute("aria-pressed", String(o === b));
    if (estado.R) renderTabela();
  });
  for (const b of document.querySelectorAll("[data-cmp]")) b.addEventListener("click", () => {
    estado.cmp = b.dataset.cmp; renderCmp();
  });
  let rz; window.addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(() => { if (estado.R) { renderLeque(); renderDist(); } }, 80); });
  const redesenhar = () => { if (estado.R) { renderLeque(); renderDist(); } };
  if (window.matchMedia) { const mq = window.matchMedia("(prefers-color-scheme: dark)"); if (mq.addEventListener) mq.addEventListener("change", redesenhar); }
  new MutationObserver(redesenhar).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(redesenhar);

  encher(M.PADRAO); renderGuardadas(); executar();
})();
