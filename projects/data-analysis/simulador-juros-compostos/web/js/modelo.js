/*
 * CJR — motor de simulação Monte Carlo (versão JavaScript).
 *
 * Implementa o mesmo algoritmo de simulador/modelo.py e simulador/risco.py. Os números
 * não coincidem ao cêntimo (geradores aleatórios diferentes), mas as distribuições são as
 * mesmas: scripts/testes_web.js verifica as propriedades exatas e compara os dois motores.
 *
 * O código está dentro de uma função-fábrica para poder correr em três sítios sem alterações:
 * na página, num Web Worker (criado a partir do texto da fábrica) e em Node (testes).
 */
function cjrFabricaModelo() {
  "use strict";

  const ANO_INICIAL = 2026, ANO_MAXIMO = 2086, MESES_PAUSA = 6, INFLACAO_MINIMA = -0.05;
  const PERCENTIS = [5, 10, 25, 50, 75, 90, 95];

  const PADRAO = {
    capital_inicial: 2000, ano_alvo: 2046, aporte: 200, frequencia: "mensal", crescimento_aporte: 0.02,
    indexar_inflacao: false, peso_cripto: 0.20, rebalancear: true, objetivo_real: 100000,
    retorno_acoes: 0.07, vol_acoes: 0.16, retorno_cripto: 0.15, vol_cripto: 0.65, correlacao: 0.35,
    custos: 0.0025, distribuicao: "normal", graus_liberdade: 5,
    inflacao: 0.022, vol_inflacao: 0.01,
    p_crise: 0.06, queda_crise_acoes: 0.25, queda_crise_cripto: 0.50, p_regulacao: 0.03,
    queda_regulacao: 0.40, p_choque_inflacao: 0.05, choque_inflacao: 0.05, p_pausa: 0.05,
    n_cenarios: 2000, semente: 20261103
  };

  /* Cenários de mercado: só alteram pressupostos de mercado, nunca o plano. */
  const CENARIOS = {
    base: {},
    pessimista: { retorno_acoes: 0.045, vol_acoes: 0.18, retorno_cripto: 0.05, vol_cripto: 0.75, correlacao: 0.5,
      inflacao: 0.03, vol_inflacao: 0.015, p_crise: 0.10, queda_crise_acoes: 0.35, queda_crise_cripto: 0.65,
      p_regulacao: 0.06, queda_regulacao: 0.50, p_choque_inflacao: 0.08, choque_inflacao: 0.06, p_pausa: 0.08 },
    otimista: { retorno_acoes: 0.09, vol_acoes: 0.15, retorno_cripto: 0.25, vol_cripto: 0.60, correlacao: 0.3,
      inflacao: 0.02, vol_inflacao: 0.007, p_crise: 0.04, queda_crise_acoes: 0.20, queda_crise_cripto: 0.40,
      p_regulacao: 0.01, queda_regulacao: 0.30, p_choque_inflacao: 0.03, choque_inflacao: 0.04, p_pausa: 0.03 },
    estagflacao: { retorno_acoes: 0.03, vol_acoes: 0.19, retorno_cripto: 0.04, vol_cripto: 0.70, correlacao: 0.45,
      inflacao: 0.05, vol_inflacao: 0.02, p_crise: 0.09, queda_crise_acoes: 0.30, queda_crise_cripto: 0.55,
      p_regulacao: 0.04, queda_regulacao: 0.40, p_choque_inflacao: 0.15, choque_inflacao: 0.07, p_pausa: 0.10 }
  };
  const CAMPOS_MERCADO = Object.keys(CENARIOS.pessimista);

  /* ---------------------------------------------------------------- validação */
  const LIMITES = {
    ano_alvo: [ANO_INICIAL + 1, ANO_MAXIMO], capital_inicial: [0, 1e9], aporte: [0, 1e8],
    crescimento_aporte: [-0.5, 0.5], peso_cripto: [0, 1], retorno_acoes: [-0.5, 1], retorno_cripto: [-0.9, 3],
    vol_acoes: [0, 1.5], vol_cripto: [0, 3], correlacao: [-1, 1], custos: [0, 0.05], inflacao: [-0.05, 0.5],
    vol_inflacao: [0, 0.2], p_crise: [0, 1], p_regulacao: [0, 1], p_choque_inflacao: [0, 1], p_pausa: [0, 1],
    queda_crise_acoes: [0, 0.95], queda_crise_cripto: [0, 0.95], queda_regulacao: [0, 0.95],
    choque_inflacao: [0, 0.5], objetivo_real: [0, 1e10], graus_liberdade: [3, 30]
  };
  function validar(p) {
    const erros = {};
    for (const k in LIMITES) {
      if (k === "graus_liberdade" && p.distribuicao !== "t") continue;
      const v = p[k], [lo, hi] = LIMITES[k];
      if (typeof v !== "number" || !isFinite(v) || v < lo || v > hi) erros[k] = [lo, hi];
    }
    if (!["semanal", "mensal", "anual"].includes(p.frequencia)) erros.frequencia = true;
    if (!["normal", "t"].includes(p.distribuicao)) erros.distribuicao = true;
    if (!(p.n_cenarios >= 1)) erros.n_cenarios = true;
    return erros;
  }

  /* ---------------------------------------------------------------- utilitários */
  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  const probMensal = pAnual => 1 - Math.pow(1 - pAnual, 1 / 12);
  function aporteDoMes(base, freq, mes) {
    if (freq === "semanal") return base * 52 / 12;
    if (freq === "mensal") return base;
    return mes === 0 ? base : 0;
  }
  /* Percentil com interpolação linear entre estatísticas de ordem (= numpy.percentile por defeito). */
  function percentilOrdenado(s, q) {
    const n = s.length; if (!n) return NaN;
    const h = (n - 1) * q / 100, lo = Math.floor(h), hi = Math.min(n - 1, lo + 1);
    return s[lo] + (h - lo) * (s[hi] - s[lo]);
  }
  const ordenar = a => Float64Array.from(a).sort();
  function mediana(a) { return percentilOrdenado(ordenar(a), 50); }

  function taxaClassica(p) {
    const bruta = (1 - p.peso_cripto) * p.retorno_acoes + p.peso_cripto * p.retorno_cripto;
    return (1 + bruta) * (1 - p.custos) - 1;
  }
  function valorDeterministico(p) {
    const Y = p.ano_alvo - ANO_INICIAL, f = Math.pow(1 + taxaClassica(p), 1 / 12);
    let v = p.capital_inicial; const serie = [v];
    for (let y = 0; y < Y; y++) {
      let base = p.aporte * Math.pow(1 + p.crescimento_aporte, y);
      if (p.indexar_inflacao) base *= Math.pow(1 + p.inflacao, y);
      for (let m = 0; m < 12; m++) v = (v + aporteDoMes(base, p.frequencia, m)) * f;
      serie.push(v);
    }
    return serie;
  }

  function rentabilidadeImplicita(p) {
    const ef = (r, quedas) => {
      let lg = Math.log(1 + r) + Math.log(1 - p.custos);
      for (const [prob, q] of quedas) lg += 12 * probMensal(prob) * Math.log(1 - q);
      return Math.exp(lg) - 1;
    };
    const arit = (r, s) => p.distribuicao === "normal" ? (1 + r) * Math.exp(s * s / 2) - 1 : null;
    return {
      acoes: { mediana: p.retorno_acoes, media_aritm: arit(p.retorno_acoes, p.vol_acoes),
        efetiva: ef(p.retorno_acoes, [[p.p_crise, p.queda_crise_acoes]]) },
      cripto: { mediana: p.retorno_cripto, media_aritm: arit(p.retorno_cripto, p.vol_cripto),
        efetiva: ef(p.retorno_cripto, [[p.p_crise, p.queda_crise_cripto], [p.p_regulacao, p.queda_regulacao]]) }
    };
  }

  /* TIR anualizada: Σ a_t (1+r)^(T−t) = valor final; aportes no início do mês t. */
  function tirAnual(aportes, valorFinal) {
    const T = aportes.length;
    let soma = 0; for (let t = 0; t < T; t++) soma += aportes[t];
    if (!(soma > 0) || !(valorFinal > 0)) return null;
    const vf = r => { const l = Math.log1p(r); let s = 0; for (let t = 0; t < T; t++) if (aportes[t]) s += aportes[t] * Math.exp(l * (T - t)); return s; };
    let lo = -0.99, hi = 1.0;
    if (vf(lo) > valorFinal || vf(hi) < valorFinal) return null;
    for (let i = 0; i < 200 && hi - lo > 1e-13; i++) { const mid = (lo + hi) / 2; if (vf(mid) < valorFinal) lo = mid; else hi = mid; }
    return Math.pow(1 + (lo + hi) / 2, 12) - 1;
  }

  /* ---------------------------------------------------------------- simulação */
  /*
   * opcoes.leve = true: só calcula o que a comparação e a sensibilidade precisam (valores finais).
   * opcoes.progresso(f): chamado no fim de cada ano com a fração concluída.
   */
  function simular(entrada, opcoes) {
    const o = opcoes || {};
    const p = Object.assign({}, PADRAO, entrada);
    const erros = validar(p);
    if (Object.keys(erros).length) throw new Error("Parâmetros inválidos: " + Object.keys(erros).join(", "));

    const N = Math.round(p.n_cenarios), Y = p.ano_alvo - ANO_INICIAL, M = Y * 12;
    const rng = mulberry32(p.semente);
    let spare = null;
    const gauss = () => {
      if (spare !== null) { const s = spare; spare = null; return s; }
      let u = 0; while (u === 0) u = rng();
      const v = rng(), r = Math.sqrt(-2 * Math.log(u));
      spare = r * Math.sin(2 * Math.PI * v);
      return r * Math.cos(2 * Math.PI * v);
    };
    const ehT = p.distribuicao === "t", nu = Math.round(p.graus_liberdade);
    const chi2 = () => { let s = 0; for (let k = 0; k < nu; k++) { const z = gauss(); s += z * z; } return s; };

    const wc = p.peso_cripto, wa = 1 - wc;
    const muA = Math.log(1 + p.retorno_acoes) / 12, sA = p.vol_acoes / Math.sqrt(12);
    const muC = Math.log(1 + p.retorno_cripto) / 12, sC = p.vol_cripto / Math.sqrt(12);
    const rho = p.correlacao, rr = Math.sqrt(1 - rho * rho);
    const pmCrise = probMensal(p.p_crise), pmReg = probMensal(p.p_regulacao);
    const fCustos = Math.pow(1 - p.custos, 1 / 12);
    const kCA = 1 - p.queda_crise_acoes, kCC = 1 - p.queda_crise_cripto, kR = 1 - p.queda_regulacao;
    const cap = p.capital_inicial;

    const A = new Float64Array(N).fill(cap * wa), C = new Float64Array(N).fill(cap * wc);
    const preco = new Float64Array(N).fill(1), pago = new Float64Array(N).fill(cap), pagoReal = new Float64Array(N).fill(cap);
    const pausa = new Int32Array(N), crises = new Int32Array(N);
    const unid = new Float64Array(N).fill(1), pico = new Float64Array(N).fill(1), ddMax = new Float64Array(N);
    const unidIni = new Float64Array(N);

    const anoPct = o.leve ? null : { nominal: PERCENTIS.map(() => new Float64Array(Y + 1)), real: PERCENTIS.map(() => new Float64Array(Y + 1)) };
    const investidoMedio = new Float64Array(Y + 1), investidoRealMedio = new Float64Array(Y + 1);
    const retAnuais = o.leve ? null : new Float32Array(N * Y);
    const aportesM = new Float64Array(Math.max(M, 1)), aportesMR = new Float64Array(Math.max(M, 1));
    if (anoPct) for (let k = 0; k < PERCENTIS.length; k++) { anoPct.nominal[k][0] = cap; anoPct.real[k][0] = cap; }
    investidoMedio[0] = investidoRealMedio[0] = cap;

    for (let y = 0; y < Y; y++) {
      const baseAno = p.aporte * Math.pow(1 + p.crescimento_aporte, y);
      for (let i = 0; i < N; i++) {
        let inf = p.inflacao + p.vol_inflacao * gauss();
        if (rng() < p.p_choque_inflacao) inf += p.choque_inflacao;
        const fInf = Math.pow(1 + Math.max(inf, INFLACAO_MINIMA), 1 / 12);
        if (rng() < p.p_pausa) pausa[i] += MESES_PAUSA;
        const base = p.indexar_inflacao ? baseAno * preco[i] : baseAno;
        let a_ = A[i], c_ = C[i], pr = preco[i], u = unid[i], pk = pico[i], dd = ddMax[i];
        unidIni[i] = u;
        for (let m = 0; m < 12; m++) {
          let ap = aporteDoMes(base, p.frequencia, m);
          if (pausa[i] > 0) { ap = 0; pausa[i]--; }
          if (ap) {
            a_ += ap * wa; c_ += ap * wc; pago[i] += ap; pagoReal[i] += ap / pr;
            aportesM[y * 12 + m] += ap / N; aportesMR[y * 12 + m] += ap / pr / N;
          }
          const antes = a_ + c_;
          let z1 = gauss(), z2 = rho * z1 + rr * gauss();
          if (ehT) { const e = Math.sqrt((nu - 2) / chi2()); z1 *= e; z2 *= e; }
          a_ *= Math.exp(muA + sA * z1);
          c_ *= Math.exp(muC + sC * z2);
          if (rng() < pmCrise) { a_ *= kCA; c_ *= kCC; crises[i]++; }
          if (rng() < pmReg) c_ *= kR;
          a_ *= fCustos; c_ *= fCustos; pr *= fInf;
          if (antes > 0) u *= (a_ + c_) / antes;
          if (u > pk) pk = u;
          const d = 1 - u / pk; if (d > dd) dd = d;
        }
        if (p.rebalancear) { const t = a_ + c_; a_ = t * wa; c_ = t * wc; }
        A[i] = a_; C[i] = c_; preco[i] = pr; unid[i] = u; pico[i] = pk; ddMax[i] = dd;
        if (retAnuais) retAnuais[y * N + i] = u / unidIni[i] - 1;
      }
      let sInv = 0, sInvR = 0; for (let i = 0; i < N; i++) { sInv += pago[i]; sInvR += pagoReal[i]; }
      investidoMedio[y + 1] = sInv / N; investidoRealMedio[y + 1] = sInvR / N;
      if (anoPct) {
        const nom = new Float64Array(N), rea = new Float64Array(N);
        for (let i = 0; i < N; i++) { nom[i] = A[i] + C[i]; rea[i] = nom[i] / preco[i]; }
        nom.sort(); rea.sort();
        for (let k = 0; k < PERCENTIS.length; k++) {
          anoPct.nominal[k][y + 1] = percentilOrdenado(nom, PERCENTIS[k]);
          anoPct.real[k][y + 1] = percentilOrdenado(rea, PERCENTIS[k]);
        }
      }
      if (o.progresso) o.progresso((y + 1) / Y);
    }
    if (M > 0) { aportesM[0] += cap; aportesMR[0] += cap; }

    const finalNom = new Float64Array(N), finalReal = new Float64Array(N);
    for (let i = 0; i < N; i++) { finalNom[i] = A[i] + C[i]; finalReal[i] = finalNom[i] / preco[i]; }

    const res = {
      parametros: p, N, Y, anos: Array.from({ length: Y + 1 }, (_, k) => ANO_INICIAL + k),
      investidoMedio, investidoRealMedio, finalNom, finalReal, pago, pagoReal, ddMax, crises,
      aportesMensais: aportesM, aportesMensaisReais: aportesMR,
      deterministico: valorDeterministico(p), percentis: PERCENTIS, anoPct, retAnuais
    };
    res.resumo = resumir(res);
    return res;
  }

  /* ---------------------------------------------------------------- indicadores */
  function resumir(r) {
    const p = r.parametros, N = r.N;
    const nomS = ordenar(r.finalNom), realS = ordenar(r.finalReal);
    const pct = (s, q) => percentilOrdenado(s, q);
    const ganhoN = new Float64Array(N), ganhoR = new Float64Array(N), acum = [];
    let perdaN = 0, perdaR = 0, obj = 0, comCrise = 0, somaReal = 0;
    for (let i = 0; i < N; i++) {
      ganhoN[i] = r.finalNom[i] - r.pago[i];
      ganhoR[i] = r.finalReal[i] - r.pagoReal[i];
      if (r.pago[i] > 0) acum.push(r.finalNom[i] / r.pago[i] - 1);
      if (r.finalNom[i] < r.pago[i]) perdaN++;
      if (r.finalReal[i] < r.pagoReal[i]) perdaR++;
      if (r.finalReal[i] >= p.objetivo_real) obj++;
      if (r.crises[i] > 0) comCrise++;
      somaReal += r.finalReal[i];
    }
    const pObj = obj / N;
    const k = 1.96 * Math.sqrt(N) / 2;
    const ic = [nomS[Math.max(0, Math.floor(N / 2 - k))], nomS[Math.min(N - 1, Math.ceil(N / 2 + k))]];
    const icR = [realS[Math.max(0, Math.floor(N / 2 - k))], realS[Math.min(N - 1, Math.ceil(N / 2 + k))]];
    let invM = 0, invRM = 0; for (let i = 0; i < N; i++) { invM += r.pago[i]; invRM += r.pagoReal[i]; }

    const s = {
      n: N,
      mediana_nominal: pct(nomS, 50), mediana_real: pct(realS, 50), media_real: somaReal / N,
      p5_real: pct(realS, 5), p10_real: pct(realS, 10), p25_real: pct(realS, 25), p75_real: pct(realS, 75), p90_real: pct(realS, 90),
      p10_nominal: pct(nomS, 10), p90_nominal: pct(nomS, 90),
      investido_medio: invM / N, investido_real_medio: invRM / N,
      ganho_nominal_mediano: mediana(ganhoN), ganho_real_mediano: mediana(ganhoR),
      rentab_acumulada_mediana: acum.length ? mediana(acum) : null,
      prob_objetivo: pObj, erro_prob_objetivo: Math.sqrt(pObj * (1 - pObj) / N),
      prob_perda_nominal: perdaN / N, prob_perda_real: perdaR / N,
      ic95_mediana_nominal: ic, ic95_mediana_real: icR,
      prob_crise: comCrise / N,
      deterministico: r.deterministico[r.deterministico.length - 1]
    };
    s.tir_nominal = { 10: tirAnual(r.aportesMensais, s.p10_nominal), 50: tirAnual(r.aportesMensais, s.mediana_nominal), 90: tirAnual(r.aportesMensais, s.p90_nominal) };
    s.tir_real = { 10: tirAnual(r.aportesMensaisReais, s.p10_real), 50: tirAnual(r.aportesMensaisReais, s.mediana_real), 90: tirAnual(r.aportesMensaisReais, s.p90_real) };
    if (r.ddMax) { const d = ordenar(r.ddMax); s.drawdown_mediano = pct(d, 50); s.drawdown_p90 = pct(d, 90); }
    if (r.retAnuais && r.retAnuais.length) {
      const ra = ordenar(r.retAnuais), v = pct(ra, 5);
      let sm = 0, c = 0; for (let i = 0; i < ra.length && ra[i] <= v; i++) { sm += ra[i]; c++; }
      s.var95_anual = v; s.cvar95_anual = c ? sm / c : v;
    }
    { const v = s.p5_real; let sm = 0, c = 0; for (let i = 0; i < N && realS[i] <= v; i++) { sm += realS[i]; c++; } s.cvar5_real = c ? sm / c : v; }
    return s;
  }

  return { ANO_INICIAL, ANO_MAXIMO, PADRAO, CENARIOS, CAMPOS_MERCADO, LIMITES, PERCENTIS,
    validar, simular, resumir, tirAnual, taxaClassica, valorDeterministico, rentabilidadeImplicita,
    probMensal, percentilOrdenado, ordenar };
}

/* Código do Web Worker: recebe pedidos e devolve resultados sem bloquear a página. */
function cjrCorpoWorker(M) {
  self.onmessage = function (ev) {
    const pedido = ev.data;
    try {
      if (pedido.tipo === "simular") {
        let ultimo = 0;
        const res = M.simular(pedido.params, { progresso: f => { if (f - ultimo >= 0.05 || f === 1) { ultimo = f; self.postMessage({ tipo: "progresso", id: pedido.id, f }); } } });
        self.postMessage({ tipo: "resultado", id: pedido.id, res });
      } else if (pedido.tipo === "lote") {
        const linhas = pedido.lista.map(item => {
          const r = M.simular(item.params, { leve: true });
          return { chave: item.chave, resumo: r.resumo };
        });
        self.postMessage({ tipo: "lote", id: pedido.id, linhas });
      }
    } catch (e) {
      self.postMessage({ tipo: "erro", id: pedido.id, mensagem: String(e && e.message || e) });
    }
  };
}

if (typeof module !== "undefined" && module.exports) module.exports = cjrFabricaModelo();
