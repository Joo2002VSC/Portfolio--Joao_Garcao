/*
 * Testes do motor JavaScript (web/js/modelo.js), com os mesmos casos A–G do Python.
 *
 * Uso:  node scripts/testes_web.js                 corre os testes
 *       node scripts/testes_web.js --resumo '{...}' imprime o resumo em JSON (usado por testes.py
 *                                                   para comparar os dois motores)
 */
"use strict";
const path = require("path");
const M = require(path.join(__dirname, "..", "web", "js", "modelo.js"));

if (process.argv[2] === "--resumo") {
  const r = M.simular(JSON.parse(process.argv[3] || "{}"));
  process.stdout.write(JSON.stringify(r.resumo));
  process.exit(0);
}

const SEM_RISCO = { vol_acoes: 0, vol_cripto: 0, vol_inflacao: 0, p_crise: 0, p_regulacao: 0, p_choque_inflacao: 0,
  p_pausa: 0, custos: 0, crescimento_aporte: 0, inflacao: 0, peso_cripto: 0, n_cenarios: 20 };
const com = (base, extra) => Object.assign({}, base, extra);
const perto = (a, b, rel = 1e-10) => Math.abs(a - b) <= rel * Math.max(1, Math.abs(b));
const todos = (arr, f) => Array.prototype.every.call(arr, f);
function assert(c, msg) { if (!c) throw new Error(msg || "falhou"); }
function formulaClassica(cap, a, taxa, anos) {
  const q = Math.pow(1 + taxa, 1 / 12), n = anos * 12;
  return q === 1 ? cap + a * n : cap * Math.pow(q, n) + a * q * (Math.pow(q, n) - 1) / (q - 1);
}

const testes = {
  A_capitalizacao_sem_volatilidade() {
    for (const [peso, campo] of [[0, "retorno_acoes"], [1, "retorno_cripto"]]) {
      const r = M.simular(com(SEM_RISCO, { peso_cripto: peso, [campo]: 0.06, ano_alvo: 2056 }));
      const e = formulaClassica(2000, 200, 0.06, 30);
      assert(todos(r.finalNom, v => perto(v, e)), `${peso}: ${r.finalNom[0]} vs ${e}`);
      assert(perto(r.deterministico[30], e));
    }
  },
  A2_classica_igual_a_estocastica_com_custos() {
    const p = com(SEM_RISCO, { retorno_acoes: 0.05, custos: 0.008, crescimento_aporte: 0.03, frequencia: "semanal" });
    const r = M.simular(p);
    assert(perto(r.finalNom[0], r.deterministico[r.Y]), `${r.finalNom[0]} vs ${r.deterministico[r.Y]}`);
    for (let y = 0; y <= r.Y; y++) assert(perto(r.anoPct.nominal[3][y], r.deterministico[y]));
  },
  B_rentabilidade_zero() {
    const r = M.simular(com(SEM_RISCO, { retorno_acoes: 0, retorno_cripto: 0 }));
    const e = 2000 + 200 * 12 * 20;
    assert(todos(r.finalNom, v => perto(v, e)) && todos(r.pago, v => perto(v, e)));
  },
  C_sem_investimento() {
    const r = M.simular({ capital_inicial: 0, aporte: 0, n_cenarios: 300 });
    assert(todos(r.finalNom, v => v === 0) && todos(r.finalReal, v => v === 0));
    const s = r.resumo;
    assert(s.mediana_nominal === 0 && s.tir_nominal[50] === null && s.rentab_acumulada_mediana === null && s.prob_perda_nominal === 0);
  },
  D_reprodutibilidade() {
    const a = M.simular({}), b = M.simular({});
    assert(a.finalNom.every((v, i) => v === b.finalNom[i]));
    assert(!M.simular({ semente: 1 }).finalNom.every((v, i) => v === a.finalNom[i]));
    const ta = M.simular({ distribuicao: "t" }), tb = M.simular({ distribuicao: "t" });
    assert(ta.finalNom.every((v, i) => v === tb.finalNom[i]));
  },
  E_inflacao() {
    const p = com(SEM_RISCO, { inflacao: 0.03, aporte: 0 });
    const r = M.simular(p);
    const idx = Math.pow(1.03, 20);
    assert(todos(r.finalReal, (v, i) => perto(v, r.finalNom[i] / idx)), "real ≠ nominal/índice");
    assert(todos(r.pagoReal, v => perto(v, 2000)));
    const r2 = M.simular(com(SEM_RISCO, { inflacao: 0.04, capital_inicial: 0, aporte: 100, ano_alvo: 2028 }));
    const f = Math.pow(1.04, 1 / 12); let e = 0; for (let t = 0; t < 24; t++) e += 100 / Math.pow(f, t);
    assert(perto(r2.pagoReal[0], e), `${r2.pagoReal[0]} vs ${e}`);
  },
  F_aportes_crescentes() {
    const r = M.simular(com(SEM_RISCO, { capital_inicial: 0, aporte: 100, crescimento_aporte: 0.10, retorno_acoes: 0, retorno_cripto: 0 }));
    assert(perto(r.aportesMensais[11], 100) && perto(r.aportesMensais[12], 110));
    for (let y = 1; y <= r.Y; y++) assert(perto(r.investidoMedio[y] - r.investidoMedio[y - 1], 1200 * Math.pow(1.1, y - 1)));
  },
  G_custos() {
    const r = M.simular(com(SEM_RISCO, { retorno_acoes: 0, retorno_cripto: 0, custos: 0.01, aporte: 0 }));
    assert(perto(r.finalNom[0], 2000 * Math.pow(0.99, 20)));
    const r2 = M.simular(com(SEM_RISCO, { retorno_acoes: 0, retorno_cripto: 0, custos: 0.01, capital_inicial: 0, aporte: 100 }));
    let e = 0; for (let t = 0; t < 240; t++) e += 100 * Math.pow(0.99, (240 - t) / 12);
    assert(perto(r2.finalNom[0], e), `${r2.finalNom[0]} vs ${e}`);
  },
  P1_frequencias() {
    for (const [f, a] of [["semanal", 120], ["mensal", 120 * 52 / 12], ["anual", 120 * 52]]) {
      const r = M.simular(com(SEM_RISCO, { frequencia: f, aporte: a, retorno_acoes: 0, retorno_cripto: 0 }));
      assert(perto((r.pago[0] - 2000) / 20, 120 * 52), f);
    }
  },
  P5_tir_e_fisher() {
    const s = M.simular(com(SEM_RISCO, { retorno_acoes: 0.06, custos: 0.005, inflacao: 0.02 })).resumo;
    assert(Math.abs(s.tir_nominal[50] - (1.06 * 0.995 - 1)) < 1e-9, s.tir_nominal[50]);
    assert(Math.abs(s.tir_real[50] - (1.06 * 0.995 / 1.02 - 1)) < 1e-9, s.tir_real[50]);
  },
  P7_risco_nulo() {
    const s = M.simular(com(SEM_RISCO, { retorno_acoes: 0.05, custos: 0.002 })).resumo;
    assert(s.drawdown_p90 < 1e-12 && Math.abs(s.var95_anual - (1.05 * 0.998 - 1)) < 1e-6);
  },
  P11_percentil_igual_ao_numpy() {
    const s = Float64Array.from([1, 2, 3, 4, 10]);
    assert(M.percentilOrdenado(s, 10) === 1.4 && M.percentilOrdenado(s, 50) === 3 && Math.abs(M.percentilOrdenado(s, 90) - 7.6) < 1e-12);
  },
  S1_probabilidade_anual_de_crise() {
    const r = M.simular(com(SEM_RISCO, { p_crise: 0.10, ano_alvo: 2031, n_cenarios: 20000 }));
    let sem = 0; for (const c of r.crises) if (c === 0) sem++;
    const q = Math.pow(0.9, 5), se = Math.sqrt(q * (1 - q) / 20000);
    assert(Math.abs(sem / 20000 - q) < 4 * se, `${sem / 20000} vs ${q}`);
  },
  V1_validacao() {
    for (const e of [{ correlacao: 1.2 }, { peso_cripto: 1.5 }, { queda_crise_acoes: 1 }, { ano_alvo: 2026 }, { aporte: -1 }, { distribuicao: "t", graus_liberdade: 2 }]) {
      let lancou = false; try { M.simular(e); } catch (_) { lancou = true; }
      assert(lancou, JSON.stringify(e));
    }
  }
};

let falhas = 0;
const t0 = Date.now();
for (const [nome, f] of Object.entries(testes)) {
  try { f(); console.log("  ok     " + nome); } catch (e) { falhas++; console.log("  FALHOU " + nome + ": " + e.message); }
}
const t1 = Date.now(); M.simular({ n_cenarios: 50000 }); const t2 = Date.now();
console.log(`\n${Object.keys(testes).length - falhas}/${Object.keys(testes).length} testes passaram (${t1 - t0} ms). 50 000 cenários × 20 anos: ${t2 - t1} ms.`);
process.exit(falhas ? 1 : 0);
