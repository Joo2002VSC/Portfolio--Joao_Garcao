"""Secções «Sentimento e emoções» e «Género literário» do painel de cada livro (gráficos 2D e blocos de texto)."""
from __future__ import annotations

import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import tema
from .emocoes import EMOCOES, NOMES, TONS

TINTA, SUAVE, GRELHA, CASTANHO, OCRE, AREIA = "#1E1915", "#6E5E4E", "#E2D6C2", "#7A4E2D", "#B8893E", "#D9C7A3"
CORES_EMO = {"alegria": OCRE, "confianca": "#9C6B45", "antecipacao": "#C9A66B", "surpresa": AREIA,
             "tristeza": TINTA, "medo": "#5C4A3A", "raiva": "#A0583A", "aversao": "#8A8466"}
TONS_COR = {"positivo": OCRE, "negativo": TINTA, "neutro": AREIA, "misto": CASTANHO, "indeterminado": "#B9AC98"}
e = html.escape


def _n(v, casas=1) -> str:
    return tema.num(v, casas) if v is not None and v == v else "—"


# ---------------------------------------------------------------------------
# Sentimento e emoções
# ---------------------------------------------------------------------------

def bloco_tonalidade(r: dict) -> str:
    """Cartão com a classificação da tonalidade, as razões, os indicadores de suporte e as limitações."""
    t = r.get("tonalidade") or {}
    i = r["indicadores"]
    tom = t.get("tom", "indeterminado")
    ic = t.get("ic") or [None, None]
    razoes = "".join(f"<li>{e(x[:1].upper() + x[1:])}</li>" for x in t.get("razoes", []))
    emo = r.get("emocoes") or {}
    dominante = NOMES.get(emo.get("dominante") or "", "—")
    linhas = [
        ("Polaridade média dos capítulos", _n(t.get("media"), 3), "−1 a +1"),
        ("Intervalo de confiança a 95 %", f"[{_n(ic[0], 3)}; {_n(ic[1], 3)}]", "bootstrap por capítulos"),
        ("Intensidade da polaridade", _n(t.get("intensidade"), 3), "média de |polaridade|"),
        ("Oscilação entre capítulos", _n(t.get("variabilidade"), 3), "desvio-padrão"),
        ("Frases fortemente positivas / negativas",
         f"{_n(t.get('fortes_positivas_pct'))} % / {_n(t.get('fortes_negativas_pct'))} %", "|polaridade| ≥ 0,5"),
        ("Razão alegria / tristeza (NRC)", _n(i.get("alegria_tristeza_razao"), 2), "> 1: mais alegria"),
        ("Emoção mais frequente (NRC)", dominante, "por ocorrências"),
        ("Diversidade emocional", _n(i.get("emocoes_entropia"), 3), "0 a 1 (entropia)"),
        ("Concordância entre léxicos", _n(i.get("concordancia_lexicos"), 2), "ρ de Spearman, sentimento vs. NRC"),
    ]
    tabela = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in linhas)
    experimental = (" Em português e em francês, o léxico de emoções é uma tradução automática: resultados "
                    "experimentais." if r.get("lingua") in ("pt", "fr") else "")
    return f"""
<div class="tom tom-{e(tom)}">
 <div class="tom-veredicto"><span>Tonalidade emocional</span><b>{e(TONS.get(tom, tom))}</b>
  <small>Classificação interpretativa e experimental, calculada a partir dos dados abaixo.</small></div>
 <div class="tom-corpo">
  <h3>Porquê esta classificação</h3><ul>{razoes}</ul>
  <table class="tom-tabela"><tbody>{tabela}</tbody></table>
  <details class="tom-metodo"><summary>Como se classifica e o que isto não mede</summary>
   <p>A polaridade de cada frase vem do método de sentimento do projeto (VADER e adaptações). Calcula-se a média por
   capítulo e o intervalo de confiança a 95 % dessa média por reamostragem dos capítulos (bootstrap). O livro é
   <b>positivo</b> ou <b>negativo</b> se o intervalo inteiro fica acima de +0,05 ou abaixo de −0,05; <b>misto</b> se
   tem pelo menos 10 % de frases fortemente positivas e 10 % fortemente negativas; <b>neutro</b> se o intervalo fica
   entre −0,05 e +0,05; e <b>indeterminado</b> se os dados não permitem concluir (poucas frases, cobertura baixa do
   léxico ou intervalo que atravessa o limiar).</p>
   <p>Mede-se o vocabulário, não o tom narrativo: a ironia, as metáforas e o discurso indireto livre não são
   detetados, e nada disto diz o que o autor sentiu ou o que o leitor vai sentir. A classificação não foi validada
   com anotação humana.{experimental}</p></details>
 </div>
</div>"""


def itens_emocoes(r: dict, extra: dict, item) -> list[dict]:
    itens = []
    emo = extra.get("emocoes") or {}
    i = r["indicadores"]
    # 1. Distribuição da polaridade das frases (histograma)
    frases = extra.get("frases")
    if frases is not None and "sentimento" in frases and frases.sentimento.notna().sum() >= 30:
        s = frases.sentimento.dropna()
        f = go.Figure(go.Histogram(x=s, xbins=dict(start=-1, end=1.0001, size=0.1), marker=dict(color=CASTANHO,
                      line=dict(color="#F4EEE3", width=1)), hovertemplate="%{x}: %{y} frases<extra></extra>"))
        f.add_vrect(x0=-0.05, x1=0.05, fillcolor=GRELHA, opacity=0.6, line_width=0, layer="below")
        f.update_xaxes(title="polaridade da frase (−1 a +1)", range=[-1.02, 1.02])
        f.update_yaxes(title="frases")
        itens.append(item("emocoes", _lay(f, "Distribuição da polaridade das frases<br><sup>A faixa central "
                                             "(−0,05 a +0,05) corresponde às frases neutras ou sem palavras do léxico"
                                             "</sup>", 420), largo=False))
    if emo.get("estado") != "valido":
        return itens
    # 2. Intensidade das oito emoções (barras horizontais)
    vals = [(NOMES[k], i.get(f"emocao_{k}_por_1000"), (r.get("emocoes") or {}).get("presenca_pct", {}).get(k), k)
            for k in EMOCOES]
    vals = sorted([x for x in vals if x[1] is not None], key=lambda x: x[1])
    f = go.Figure(go.Bar(x=[v for _, v, _, _ in vals], y=[n for n, _, _, _ in vals], orientation="h",
                         marker=dict(color=[CORES_EMO[k] for *_, k in vals]),
                         customdata=[p for _, _, p, _ in vals],
                         hovertemplate="<b>%{y}</b><br>%{x:.1f} ocorrências por 1000 palavras<br>"
                                       "presente em %{customdata:.1f} % das frases<extra></extra>"))
    f.update_xaxes(title="ocorrências por 1000 palavras")
    itens.append(item("emocoes", _lay(f, "Emoções do vocabulário<br><sup>Intensidade (ocorrências por 1000 palavras); a "
                                         "presença (% de frases) aparece ao passar o rato · léxico NRC</sup>", 420),
                      largo=False))
    # 3. Trajetória: polaridade por capítulo, com as mudanças expressivas
    seg = emo.get("segmentos")
    if seg is not None and len(seg) >= 3:
        rot = [f"{k}. {x}" for k, x in zip(seg.index, seg.rotulo)]
        f = go.Figure()
        f.add_hrect(y0=-0.05, y1=0.05, fillcolor=GRELHA, opacity=0.6, line_width=0, layer="below")
        f.add_scatter(x=list(seg.index), y=seg.polaridade, mode="lines+markers", line=dict(color=CASTANHO, width=3),
                      marker=dict(size=8, color=CASTANHO), text=rot, name="polaridade média",
                      customdata=[NOMES.get(d, "—") if isinstance(d, str) else "—" for d in seg.dominante],
                      hovertemplate="<b>%{text}</b><br>polaridade média: %{y:.3f}<br>emoção mais frequente: "
                                    "%{customdata}<extra></extra>")
        for m in emo.get("mudancas", []):
            f.add_annotation(x=m["segmento"], y=seg.polaridade.get(m["segmento"]), text="mudança", showarrow=True,
                             arrowhead=2, arrowcolor=OCRE, font=dict(color=OCRE, size=12), ay=-32)
        f.update_xaxes(title="capítulo ou bloco (início → fim)", dtick=1 if len(seg) <= 30 else None)
        f.update_yaxes(title="polaridade média (−1 a +1)", zeroline=True, zerolinecolor=SUAVE)
        nota = ("Uma descida da polaridade indica mais vocabulário negativo nesse capítulo, não necessariamente uma "
                "deterioração da narrativa. «Mudança» assinala variações entre capítulos consecutivos maiores do que "
                "duas vezes o desvio-padrão dessas variações.")
        itens.append(item("emocoes", _lay(f, "Trajetória da polaridade<br><sup>Média por capítulo (ou bloco) · "
                                             "faixa cinzenta = neutro</sup>", 440, nota=nota)))
        f = go.Figure()
        for k, cor, traco in (("alegria", OCRE, "solid"), ("tristeza", TINTA, "solid"), ("medo", "#5C4A3A", "dot"),
                              ("confianca", "#9C6B45", "dot")):
            f.add_scatter(x=list(seg.index), y=seg[k], mode="lines+markers", name=NOMES[k], text=rot,
                          line=dict(color=cor, width=3 if traco == "solid" else 2, dash=traco), marker=dict(size=6),
                          hovertemplate=f"<b>%{{text}}</b><br>{NOMES[k]}: %{{y:.1f}} por 1000 palavras<extra></extra>")
        f.update_xaxes(title="capítulo ou bloco (início → fim)", dtick=1 if len(seg) <= 30 else None)
        f.update_yaxes(title="ocorrências por 1000 palavras")
        itens.append(item("emocoes", _lay(f, "Alegria e tristeza ao longo do livro<br><sup>Com o medo e a confiança "
                                             "a tracejado · léxico NRC</sup>", 440,
                                          legend=dict(orientation="h", y=1.08, x=0))))
    # 4. Narração e discurso direto
    can = emo.get("canais")
    if can is not None and len(can) == 2 and can.frases.min() >= 30:
        f = go.Figure()
        for canal, cor in (("narração", CASTANHO), ("discurso direto", OCRE)):
            if canal in can.index:
                f.add_bar(y=[NOMES[k] for k in EMOCOES], x=[can.loc[canal, k] for k in EMOCOES], orientation="h",
                          name=canal.capitalize(), marker=dict(color=cor),
                          hovertemplate=f"<b>%{{y}}</b> · {canal}: %{{x:.1f}} por 1000 palavras<extra></extra>")
        f.update_layout(barmode="group")
        f.update_xaxes(title="ocorrências por 1000 palavras")
        nota = ("O discurso direto é detetado pela tipografia (travessões e aspas). Separa as falas das personagens da "
                "narração, mas não o discurso indireto livre.")
        n_n = int(can.loc["narração", "frases"]) if "narração" in can.index else 0
        n_d = int(can.loc["discurso direto", "frases"]) if "discurso direto" in can.index else 0
        itens.append(item("emocoes", _lay(f, "Narração e discurso direto<br><sup>Emoções do vocabulário em cada canal · "
                                             f"{n_n} frases de narração, {n_d} de discurso direto</sup>", 460, nota=nota, legend=dict(orientation="h", y=1.08, x=0)),
                          largo=False))
    return itens


def bloco_fases(extra: dict) -> str:
    fases = (extra.get("emocoes") or {}).get("fases")
    if fases is None or not len(fases):
        return ""
    cab = "".join(f"<th>{e(str(f).capitalize())}</th>" for f in fases.index)
    linhas = [("Polaridade média", "polaridade", 3)] + [(NOMES[k], k, 1) for k in ("alegria", "tristeza", "medo",
                                                                                    "confianca")]
    corpo = "".join(f"<tr><th>{e(n)}</th>" + "".join(f"<td>{_n(fases.loc[f, c], d)}</td>" for f in fases.index)
                    + "</tr>" for n, c, d in linhas)
    return (f'<div class="fases"><h3>Início, Desenvolvimento e Conclusão</h3><table><thead><tr><th></th>{cab}</tr>'
            f'</thead><tbody>{corpo}</tbody></table><p class="nota">Início = primeiros 20 % das palavras; conclusão = '
            "últimos 20 %. Emoções em ocorrências por 1000 palavras.</p></div>")


# ---------------------------------------------------------------------------
# Género literário
# ---------------------------------------------------------------------------

def bloco_genero(r: dict) -> str:
    g = r.get("genero")
    if not g:
        return ""
    bib = g.get("bibliografico")
    if bib:
        estado = "confirmado manualmente" if bib.get("estado") == "confirmado" else "proposto, por confirmar"
        conc = {True: "concorda com a inferência", False: "diverge da inferência", None: "sem comparação possível"}[
            bib.get("concorda")]
        nota = f'<p class="nota">{e(bib["nota"])}</p>' if bib.get("nota") else ""
        bib_html = (f'<div class="gen-cartao"><span>Género bibliográfico</span><b>{e(bib["genero"])}</b>'
                    f'<small>{e(estado)} · {e(conc)}</small><small>Fonte: {e(bib.get("fonte") or "—")}</small>{nota}</div>')
    else:
        bib_html = ('<div class="gen-cartao"><span>Género bibliográfico</span><b>—</b><small>Sem informação em '
                    'metadados.csv</small></div>')
    tracos = "".join(f"<li>{e(t)}</li>" for t in g.get("tracos", []))
    criterios = ""
    for bloco, titulo in (("formas", "Forma"), ("generos", "Género")):
        linhas = ""
        for c in g[bloco]:
            if c["pontuacao"] in (None, 0) and bloco == "generos":
                continue
            itens = "".join(f'<li class="{"ok" if x["cumprido"] else ("nao" if x["cumprido"] is False else "na")}">'
                            f'{"✓" if x["cumprido"] else ("✗" if x["cumprido"] is False else "–")} {e(x["criterio"])}</li>'
                            for x in c["criterios"])
            linhas += f'<div><h4>{e(c["nome"])} <small>{_n(c["pontuacao"], 2)}</small></h4><ul>{itens}</ul></div>'
        criterios += f'<div class="gen-crit"><h3>{titulo}: Critérios das Categorias Pontuadas</h3>{linhas}</div>'
    return f"""
<div class="genero">
 <div class="gen-topo">
  <div class="gen-cartao principal"><span>Género inferido pelo conteúdo</span><b>{e(g.get("principal") or "Sem categoria clara")}</b>
   <small>Forma: {e(g.get("forma_principal") or "—")} · {e(g.get("metodo", ""))}</small></div>
  {bib_html}
 </div>
 {f'<ul class="gen-tracos">{tracos}</ul>' if tracos else ''}
 {criterios}
 <details class="tom-metodo"><summary>Inferência computacional e classificação bibliográfica</summary>
  <p>O género <b>inferido</b> resulta de regras explícitas sobre indicadores do texto (forma, extensão, pessoa da
  narração, discurso direto, personagens). A pontuação é a fração dos critérios cumpridos, não uma probabilidade. O
  género <b>bibliográfico</b> vem de catálogos (indicados como fonte) e nunca entra no cálculo: serve para comparar. Os
  limiares de extensão de romance, novela e conto seguem a convenção das regras dos prémios Nebula (SFWA). Não são
  inferidos nesta versão: {e(", ".join(g.get("nao_inferidos", [])).lower())}.</p></details>
</div>"""


def itens_genero(r: dict, item) -> list[dict]:
    g = r.get("genero")
    if not g:
        return []
    cats = [c for c in g["formas"] + g["generos"] if c["pontuacao"] is not None]
    cats = sorted(cats, key=lambda c: c["pontuacao"])
    f = go.Figure(go.Bar(x=[c["pontuacao"] for c in cats], y=[c["nome"] for c in cats], orientation="h",
                         marker=dict(color=[OCRE if c["pontuacao"] == 1 else (CASTANHO if c["pontuacao"] >= 0.5 else AREIA)
                                            for c in cats]),
                         hovertemplate="<b>%{y}</b>: %{x:.2f} dos critérios cumpridos<extra></extra>"))
    f.update_xaxes(title="pontuação de regras (fração dos critérios cumpridos; não é probabilidade)", range=[0, 1.05])
    return [item("genero", _lay(f, "Perfil de género literário<br><sup>Formas e géneros avaliados pelas regras; "
                                   "0 quando falha um critério essencial (forma ou extensão)</sup>",
                                120 + 34 * len(cats)), largo=False)]


def _lay(f: go.Figure, titulo: str, altura: int, nota: str = "", **extra) -> go.Figure:
    from .interativo import _layout
    return _layout(f, titulo, altura=altura, nota=nota, **extra)


CSS = """
.tom{display:grid;grid-template-columns:minmax(220px,300px) 1fr;gap:28px;border-top:3px solid var(--tinta,#1E1915);
 padding:22px 0 8px;margin:0 0 26px}
.tom-veredicto span,.gen-cartao span{display:block;font-family:var(--ui);font-size:12px;letter-spacing:.1em;
 text-transform:uppercase;color:#6E5E4E}
.tom-veredicto b{display:block;font-family:var(--display);font-size:clamp(28px,3.2vw,40px);line-height:1.08;margin:8px 0}
.tom-veredicto small,.gen-cartao small{display:block;font-family:var(--ui);font-size:13.5px;color:#6E5E4E;margin-top:4px}
.tom-positivo .tom-veredicto b{color:#B8893E}.tom-negativo .tom-veredicto b{color:#1E1915}
.tom-misto .tom-veredicto b{color:#7A4E2D}.tom-neutro .tom-veredicto b,.tom-indeterminado .tom-veredicto b{color:#6E5E4E}
.tom-corpo h3,.gen-crit h3,.fases h3{font-family:var(--display);font-size:20px;margin:0 0 8px}
.tom-corpo ul{margin:0 0 14px;padding-left:18px;font-size:15.5px}
.tom-tabela,.fases table{border-collapse:collapse;width:100%;font-family:var(--ui);font-size:14.5px}
.tom-tabela th,.tom-tabela td,.fases th,.fases td{padding:7px 8px;border-bottom:1px solid #E2D6C2;text-align:left}
.tom-tabela td:nth-child(2){font-variant-numeric:tabular-nums;font-weight:600}
.tom-tabela td:nth-child(3){color:#6E5E4E}
.tom-metodo{margin-top:14px;font-size:15px}.tom-metodo summary{cursor:pointer;font-family:var(--ui);font-weight:600}
.fases{margin:8px 0 24px}.fases td{font-variant-numeric:tabular-nums}
.genero{margin:0 0 26px}.gen-topo{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:18px}
.gen-cartao{border-top:3px solid #7A4E2D;padding:16px 0}.gen-cartao.principal{border-top-color:#B8893E}
.gen-cartao b{display:block;font-family:var(--display);font-size:clamp(24px,2.6vw,32px);margin:6px 0}
.gen-tracos{font-size:15.5px;padding-left:18px}
.gen-crit{margin-top:14px}.gen-crit>div{display:inline-block;vertical-align:top;width:min(100%,360px);margin:0 18px 12px 0}
.gen-crit h4{font-family:var(--ui);font-size:15px;margin:6px 0}.gen-crit h4 small{color:#6E5E4E;font-weight:400}
.gen-crit ul{list-style:none;padding:0;margin:0;font-family:var(--ui);font-size:14px}
.gen-crit li{padding:3px 0}.gen-crit li.ok{color:#1E1915}.gen-crit li.nao{color:#A0583A}.gen-crit li.na{color:#8A8466}
.tom-corpo,.fases{min-width:0;overflow-x:auto}
@media(max-width:760px){.tom{grid-template-columns:1fr}.tom-tabela,.fases table{font-size:13px}
 .tom-tabela th,.tom-tabela td,.fases th,.fases td{padding:6px 5px}}
"""
