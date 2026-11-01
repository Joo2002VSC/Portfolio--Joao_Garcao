"""Gera o relatório "Rendimentos, gastos e transferências" em PDF.

Lê vsc_contas.db, desenha os gráficos (SVG, letra Archivo), monta um HTML com
páginas A4 e imprime-o em PDF com o Chromium (Playwright).

Saídas, na pasta relatorio/:
    rendimentos-gastos-transferencias.pdf   o relatório
    rendimentos-gastos-transferencias.html  a fonte do PDF
    graficos/*.svg e *.png                  os gráficos (PNG para o README)

Uso (a partir da raiz do projeto, depois de build_db.py):
    pip install matplotlib playwright
    python scripts/relatorio_pdf.py
"""
import datetime as dt
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "vsc_contas.db"
PASTA = RAIZ / "relatorio"
GRAF = PASTA / "graficos"
NOME = "rendimentos-gastos-transferencias"

AMARELO, PRETO, CINZA_ESCURO, CINZA, CINZA_CLARO = "#F5D510", "#111111", "#6F6D6E", "#A9A7A8", "#E4E3E3"
TEXTO_2 = "#4A4949"

for f in (RAIZ / "fontes").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
plt.rcParams.update({
    "font.family": "Archivo", "font.size": 9, "svg.fonttype": "path",
    "axes.edgecolor": CINZA_CLARO, "axes.labelcolor": TEXTO_2, "text.color": PRETO,
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": CINZA_CLARO, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "legend.frameon": False,
    "xtick.major.size": 0, "ytick.major.size": 0,
})


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------
def m(v, casas=1, parenteses=True):
    """Valor em M€, negativos entre parênteses (convenção das demonstrações)."""
    if v is None:
        return "—"
    txt = f"{abs(v) / 1e6:,.{casas}f}".replace(",", " ").replace(".", ",")
    return f"({txt})" if v < 0 and parenteses else txt


def pct(v, casas=0):
    return "—" if v is None else f"{v:.{casas}f}%".replace(".", ",")


eixo = FuncFormatter(lambda v, _: "0" if v == 0 else m(v, 0 if v % 1e6 == 0 else 1) + " M€")


def q(con, sql):
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def consulta(con, numero):
    """Corre a consulta N de sql/04_analises.sql e devolve as linhas como dicionários."""
    texto = (RAIZ / "sql" / "04_analises.sql").read_text(encoding="utf-8")
    bloco = texto.split(f"-- @q {numero}.")[1].split("\n-- @q ")[0]
    return q(con, bloco.split("\n", 1)[1])


EMBLEMA = PASTA / "assets" / "emblema-vitoria-sc-pequeno.png"


def emblema(ax, altura=0.36):
    """Emblema no canto superior direito, por cima da área do gráfico (linha da legenda)."""
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    img = plt.imread(EMBLEMA)
    caixa = OffsetImage(img, zoom=altura * 72 / img.shape[0])  # dpi_cor: 72 pontos por polegada
    topo = 1
    legenda = ax.get_legend()
    if legenda is not None:  # se a legenda estiver por cima do gráfico, o emblema fica acima dela
        ax.figure.canvas.draw()
        caixa_leg = legenda.get_window_extent().transformed(ax.transAxes.inverted())
        if caixa_leg.y0 >= 0.95:
            topo = caixa_leg.y1
    ax.add_artist(AnnotationBbox(caixa, (1, topo), xycoords="axes fraction", box_alignment=(1, 0),
                                 xybox=(0, 4), boxcoords="offset points", frameon=False, pad=0,
                                 annotation_clip=False))


def guardar(fig, nome):
    emblema(fig.axes[0], altura=0.3 if fig.get_size_inches()[0] < 4 else 0.36)
    GRAF.mkdir(parents=True, exist_ok=True)
    fig.savefig(GRAF / f"{nome}.svg", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(GRAF / f"{nome}.png", dpi=200, bbox_inches="tight", pad_inches=0.1, facecolor="white")
    plt.close(fig)
    return f"graficos/{nome}.svg"


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def grafico_saldo(linhas):
    ep = [l["epoca"] for l in linhas]
    x = range(len(ep))
    fig, ax = plt.subplots(figsize=(7.1, 3.6))
    w = 0.36
    ax.bar([i - w / 2 for i in x], [l["gastos_operacionais"] for l in linhas], width=w,
           color=PRETO, label="Gastos operacionais")
    ax.bar([i + w / 2 for i in x], [l["receitas_transferencias"] for l in linhas], width=w,
           color=AMARELO, edgecolor=PRETO, linewidth=0.5, label="Receitas de transferências (mais-valias)")
    ax.plot(list(x), [l["saldo"] for l in linhas], color=CINZA_ESCURO, linewidth=1.6, marker="o",
            markersize=5, markerfacecolor="white", markeredgecolor=PRETO, markeredgewidth=1.2,
            label="Saldo (transferências − gastos)")
    for i, l in enumerate(linhas):
        ax.annotate(m(l["saldo"]), (i, l["saldo"]), xytext=(0, -13), textcoords="offset points",
                    ha="center", fontsize=7.2, color=PRETO, fontweight="bold")
        ax.text(i - w / 2, l["gastos_operacionais"] + 0.6e6, m(l["gastos_operacionais"], 0),
                ha="center", fontsize=6.6, color=TEXTO_2)
    ax.axhline(0, color=PRETO, linewidth=0.9)
    ax.set_xticks(list(x), ep, fontsize=7.8)
    ax.yaxis.set_major_formatter(eixo)
    ax.set_ylim(-32e6, 46e6)
    ax.legend(loc="upper left", fontsize=7.6, ncol=3, bbox_to_anchor=(0, 1.08))
    return guardar(fig, "01_gastos_transferencias_saldo")


def grafico_rendimentos(linhas):
    ep = [l["epoca"][2:] for l in linhas]
    x = range(len(ep))
    vs = [l["vendas_servicos"] for l in linhas]
    sb = [l["subsidios"] or 0 for l in linhas]
    ot = [l["outros_rendimentos"] for l in linhas]
    fig, ax = plt.subplots(figsize=(7.1, 3.3))
    ax.bar(x, vs, color=PRETO, width=0.66, label="Vendas e serviços prestados")
    ax.bar(x, sb, bottom=vs, color=CINZA, width=0.66, label="Subsídios à exploração")
    ax.bar(x, ot, bottom=[a + b for a, b in zip(vs, sb)], color=AMARELO, edgecolor=PRETO,
           linewidth=0.5, width=0.66, label="Outros rendimentos (inclui mais-valias com jogadores)")
    for i, l in enumerate(linhas):
        ax.text(i, l["total_rendimentos"] + 0.7e6, m(l["total_rendimentos"]), ha="center",
                fontsize=7, fontweight="bold")
    ax.set_xticks(list(x), ep, fontsize=7.8)
    ax.yaxis.set_major_formatter(eixo)
    ax.set_ylim(0, 58e6)
    ax.legend(loc="upper left", fontsize=7.6, ncol=3, bbox_to_anchor=(0, 1.1))
    return guardar(fig, "02_rubricas_rendimentos")


def grafico_gastos(linhas):
    ep = [l["epoca"][2:] for l in linhas]
    x = range(len(ep))
    series = [
        ("Gastos com pessoal", [l["pessoal"] for l in linhas], PRETO, None),
        ("Fornecimentos e serviços externos", [l["fse"] for l in linhas], CINZA_ESCURO, None),
        ("Depreciações e amortizações (inclui passes)", [l["depreciacoes"] for l in linhas], CINZA, None),
        ("Mercadorias, outros gastos, imparidades e provisões",
         [l["mercadorias"] + l["outros_gastos"] + l["imparidades_provisoes"] for l in linhas], AMARELO, PRETO),
    ]
    fig, ax = plt.subplots(figsize=(7.1, 3.3))
    base = [0] * len(linhas)
    for nome, vals, cor, borda in series:
        ax.bar(x, vals, bottom=base, color=cor, width=0.66, label=nome,
               edgecolor=borda or cor, linewidth=0.5)
        base = [a + b for a, b in zip(base, vals)]
    for i, l in enumerate(linhas):
        ax.text(i, l["total_gastos"] + 0.6e6, m(l["total_gastos"]), ha="center", fontsize=7, fontweight="bold")
    ax.set_xticks(list(x), ep, fontsize=7.8)
    ax.yaxis.set_major_formatter(eixo)
    ax.set_ylim(0, 46e6)
    ax.legend(loc="upper left", fontsize=7.4, ncol=2, bbox_to_anchor=(0, 1.16))
    return guardar(fig, "03_rubricas_gastos")


def grafico_detalhe(linhas, nota, nome, titulo_cor=AMARELO):
    sel = [l for l in linhas if l["nota"] == nota]
    sel.sort(key=lambda l: max(l["valor_2025_26"], l["valor_2024_25"]))
    y = range(len(sel))
    fig, ax = plt.subplots(figsize=(3.3, 0.3 * len(sel) + 0.55))
    h = 0.38
    ax.barh([i + h / 2 for i in y], [l["valor_2024_25"] for l in sel], height=h, color=CINZA_CLARO,
            label="2024/25")
    ax.barh([i - h / 2 for i in y], [l["valor_2025_26"] for l in sel], height=h, color=titulo_cor,
            edgecolor=PRETO, linewidth=0.5, label="2025/26")
    for i, l in enumerate(sel):
        ax.text(l["valor_2025_26"] + 0.12e6, i - h / 2, m(l["valor_2025_26"]), va="center", fontsize=8,
                fontweight="bold")
    rotulo = lambda s: s if len(s) < 26 else s[:s.rfind(" ", 0, 26)] + "\n" + s[s.rfind(" ", 0, 26) + 1:]
    ax.set_yticks(list(y), [rotulo(l["rubrica"]) for l in sel], fontsize=8, linespacing=1.0)
    ax.xaxis.set_major_formatter(eixo)
    ax.tick_params(axis="x", labelsize=7.4)
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(max(l["valor_2024_25"], l["valor_2025_26"]) for l in sel) * 1.22)
    ax.legend(loc="lower right", fontsize=7.6)
    return guardar(fig, nome)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------
def tabela(cabecalho, linhas, destaque=None, classes=None):
    alinh = classes or [""] * len(cabecalho)
    th = "".join(f'<th class="{"n" if "n" in alinh[j].split() else "t"}">{c}</th>' for j, c in enumerate(cabecalho))
    corpo = []
    for i, l in enumerate(linhas):
        cls = ' class="destaque"' if destaque and destaque(i, l) else ""
        tds = "".join(f'<td class="{(classes or [""] * len(l))[j]}">{v}</td>' for j, v in enumerate(l))
        corpo.append(f"<tr{cls}>{tds}</tr>")
    return f'<table><thead><tr>{th}</tr></thead><tbody>{"".join(corpo)}</tbody></table>'


def pagina(conteudo, n, total, capa=False):
    if capa:
        return f'<section class="pagina capa">{conteudo}</section>'
    return f"""<section class="pagina">
  <header class="cabecalho">
    <img src="assets/emblema-vitoria-sc-pequeno.png" alt="">
    <span class="titulo-curto">Rendimentos, gastos e transferências</span>
    <span class="entidade">Vitória SC – Futebol, SAD · 2013/14–2025/26</span>
  </header>
  <div class="corpo">{conteudo}</div>
  <footer class="rodape">
    <span>Análise independente de João Garção a partir dos Relatórios e Contas da SAD. Sem ligação oficial ao Vitória Sport Clube.</span>
    <span class="num">{n:02d} / {total:02d}</span>
  </footer>
</section>"""


def main():
    con = sqlite3.connect(DB)
    saldo = consulta(con, 56)
    rend = consulta(con, 57)
    gast = consulta(con, 58)
    det = consulta(con, 59)
    ult = saldo[-1]
    g26 = gast[-1]
    r26 = rend[-1]
    media_cob = sum(l["transferencias_cobrem_pct"] for l in saldo) / len(saldo)
    pior = min(saldo, key=lambda l: l["saldo"])
    melhor = max(saldo, key=lambda l: l["saldo"])

    g1 = grafico_saldo(saldo)
    g2 = grafico_rendimentos(rend)
    g3 = grafico_gastos(gast)
    g4a = grafico_detalhe(det, "15", "04_detalhe_vendas_servicos")
    g4b = grafico_detalhe(det, "17", "05_detalhe_fse", titulo_cor=CINZA_ESCURO)

    hoje = dt.date.today()
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
             "setembro", "outubro", "novembro", "dezembro"]
    data_txt = f"{meses[hoje.month - 1].capitalize()} de {hoje.year}"

    # --- Capa -------------------------------------------------------------
    capa = f"""
  <div class="capa-faixa"></div>
  <div class="capa-topo">
    <img class="capa-emblema" src="assets/emblema-vitoria-sc.png" alt="Emblema do Vitória Sport Clube">
    <div class="capa-entidade">Vitória SC<br>Futebol, SAD</div>
  </div>
  <div class="capa-titulo">
    <p class="sobretitulo">Análise financeira · 2013/14 a 2025/26</p>
    <h1>Rendimentos,<br>gastos e<br>transferências</h1>
    <p class="subtitulo">Quanto custa a operação da SAD, quanto rendem as vendas de jogadores e o que fica por cobrir.</p>
  </div>
  <div class="capa-numeros">
    <div><span class="v">{m(ult["gastos_operacionais"])} M€</span><span class="l">gastos operacionais em 2025/26</span></div>
    <div><span class="v">{m(ult["receitas_transferencias"])} M€</span><span class="l">receitas de transferências em 2025/26</span></div>
    <div><span class="v">{m(ult["saldo"])} M€</span><span class="l">saldo a cobrir pela operação</span></div>
  </div>
  <div class="capa-rodape">
    <span>João Garção · Mestrado em Humanidades Digitais, Universidade do Minho</span>
    <span>{data_txt}</span>
  </div>"""

    # --- Síntese ------------------------------------------------------------
    sintese = f"""
  <p class="seccao-num">Síntese</p>
  <h2>O essencial em quatro números</h2>
  <div class="kpis">
    <div class="kpi"><span class="v">{m(ult["gastos_operacionais"])}<small> M€</small></span><span class="l">Gastos operacionais em 2025/26, o máximo da série ({pct(g26["variacao_pct"], 1)} face a 2024/25)</span></div>
    <div class="kpi"><span class="v">{m(ult["receitas_transferencias"])}<small> M€</small></span><span class="l">Mais-valias com a venda de jogadores ({m(ult["vendas_brutas"])} M€ em vendas brutas)</span></div>
    <div class="kpi escuro"><span class="v">{m(ult["saldo"])}<small> M€</small></span><span class="l">Saldo entre transferências e gastos: o que a operação teria de cobrir</span></div>
    <div class="kpi"><span class="v">{pct(ult["transferencias_cobrem_pct"])}</span><span class="l">Parte dos gastos coberta pelas transferências (média de {pct(media_cob)} desde 2017/18)</span></div>
  </div>
  <h3>Principais conclusões</h3>
  <ol class="conclusoes">
    <li><div><strong>As transferências nunca chegaram para pagar os gastos.</strong> Em nove épocas, as mais-valias cobriram entre {pct(min(l["transferencias_cobrem_pct"] for l in saldo))} e {pct(max(l["transferencias_cobrem_pct"] for l in saldo))} dos gastos operacionais. O saldo foi sempre negativo, entre {m(melhor["saldo"])} M€ ({melhor["epoca"]}) e {m(pior["saldo"])} M€ ({pior["epoca"]}).</div></li>
    <li><div><strong>Os gastos duplicaram em oito épocas.</strong> Passaram de {m(gast[4]["total_gastos"])} M€ em 2017/18 para {m(g26["total_gastos"])} M€ em 2025/26. Os gastos com pessoal são a maior rubrica: {pct(g26["pessoal_pct"])} do total em 2025/26.</div></li>
    <li><div><strong>Mais de metade dos rendimentos vem de "outros rendimentos".</strong> É aqui que entram as mais-valias com jogadores: {pct(r26["outros_rendimentos_pct"])} dos rendimentos operacionais em 2025/26, contra {pct(rend[0]["outros_rendimentos_pct"])} em 2013/14.</div></li>
    <li><div><strong>Sem Europa, as receitas da operação caem um terço.</strong> Entre 2024/25 e 2025/26, os prémios de competições passaram de 9,7 para 1,6 M€ e as vendas e serviços de 22,6 para 14,9 M€. Os gastos não acompanharam a descida: subiram 1,9 M€.</div></li>
  </ol>
  <h3>Conteúdo</h3>
  <ol class="indice">
    <li><span>Gastos operacionais vs. receitas de transferências</span><span>03</span></li>
    <li><span>Evolução das rubricas de rendimentos</span><span>04</span></li>
    <li><span>Evolução das rubricas de gastos operacionais</span><span>05</span></li>
    <li><span>2025/26 em detalhe: notas do Relatório e Contas</span><span>06</span></li>
    <li><span>Notas metodológicas e fontes</span><span>07</span></li>
  </ol>"""

    # --- 1. Saldo -------------------------------------------------------------
    t1 = tabela(
        ["Época", "Gastos operacionais", "Vendas brutas", "Receitas de transferências", "Saldo", "Cobertura", "Saldo com receitas da operação"],
        [[l["epoca"], m(-l["gastos_operacionais"]), m(l["vendas_brutas"]), m(l["receitas_transferencias"]),
          m(l["saldo"]), pct(l["transferencias_cobrem_pct"]), m(l["saldo_com_receitas_operacao"])] for l in saldo],
        destaque=lambda i, l: i == len(saldo) - 1, classes=["", "n", "n", "n", "n forte", "n", "n"])
    sec1 = f"""
  <p class="seccao-num">01</p>
  <h2>Gastos operacionais vs. receitas de transferências</h2>
  <p class="lead">As vendas de jogadores são a segunda fonte de rendimento da SAD, mas nunca cobriram os gastos operacionais. Em 2025/26 cobriram {pct(ult["transferencias_cobrem_pct"])}: ficaram por cobrir {m(-ult["saldo"])} M€, mais do que todas as receitas da operação ({m(ult["receitas_operacao"])} M€).</p>
  <figure><img src="{g1}" alt="Gastos operacionais, receitas de transferências e saldo por época"></figure>
  {t1}
  <p class="nota">Valores em M€; negativos entre parênteses. Gastos operacionais = mercadorias + FSE + pessoal + depreciações e amortizações (inclui passes) + outros gastos + imparidades + provisões. Receitas de transferências = mais-valias líquidas com a venda de passes. Cobertura = receitas de transferências ÷ gastos. Saldo com receitas da operação = saldo + vendas e serviços prestados. Consulta SQL 56. Em 2020/21, a fonte só indica as mais-valias, usadas também como vendas brutas.</p>"""

    # --- 2. Rendimentos -------------------------------------------------------
    t2 = tabela(
        ["Época", "Vendas e serviços", "Subsídios", "Outros rendimentos", "Total", "Peso de outros rendimentos"],
        [[l["epoca"], m(l["vendas_servicos"]), m(l["subsidios"], 2), m(l["outros_rendimentos"]),
          m(l["total_rendimentos"]), pct(l["outros_rendimentos_pct"])] for l in rend],
        destaque=lambda i, l: i == len(rend) - 1, classes=["", "n", "n", "n", "n forte", "n"])
    sec2 = f"""
  <p class="seccao-num">02</p>
  <h2>Evolução das rubricas de rendimentos</h2>
  <p class="lead">Os rendimentos operacionais passaram de {m(rend[0]["total_rendimentos"])} M€ em 2013/14 para {m(r26["total_rendimentos"])} M€ em 2025/26, com um máximo de {m(max(l["total_rendimentos"] for l in rend))} M€ em 2024/25. O crescimento veio sobretudo dos outros rendimentos, onde se registam as mais-valias com jogadores; as vendas e serviços dependem da Europa.</p>
  <figure><img src="{g2}" alt="Rubricas de rendimentos por época"></figure>
  {t2}
  <p class="nota">Valores em M€. Vendas e serviços prestados = direitos TV, prémios de competições, bilheteira, quotas, patrocínios, mercadorias e mecanismo de solidariedade. Outros rendimentos = sobretudo mais-valias com a alienação de passes, compensações por atletas vendidos em anos anteriores e receitas de apostas. Consulta SQL 57.</p>"""

    # --- 3. Gastos -------------------------------------------------------------
    t3 = tabela(
        ["Época", "Pessoal", "FSE", "Depreciações", "Mercadorias", "Outros gastos", "Imparid. e provisões", "Total", "Pessoal %", "Var."],
        [[l["epoca"], m(l["pessoal"]), m(l["fse"]), m(l["depreciacoes"]), m(l["mercadorias"], 2),
          m(l["outros_gastos"]), m(l["imparidades_provisoes"], 2), m(l["total_gastos"]),
          pct(l["pessoal_pct"]), "—" if l["variacao_pct"] is None else pct(l["variacao_pct"])] for l in gast],
        destaque=lambda i, l: i == len(gast) - 1,
        classes=["", "n", "n", "n", "n", "n", "n", "n forte", "n", "n"])
    sec3 = f"""
  <p class="seccao-num">03</p>
  <h2>Evolução das rubricas de gastos operacionais</h2>
  <p class="lead">Os gastos operacionais triplicaram desde 2013/14 ({m(gast[0]["total_gastos"])} → {m(g26["total_gastos"])} M€). Os gastos com pessoal multiplicaram-se por {str(round(g26["pessoal"] / gast[0]["pessoal"], 1)).replace(".", ",")} e pesam hoje mais de metade do total. Ao contrário das receitas, os gastos quase nunca descem: só caíram em {sum(1 for l in gast if (l["variacao_pct"] or 0) < 0)} das {len(gast) - 1} épocas.</p>
  <figure><img src="{g3}" alt="Rubricas de gastos operacionais por época"></figure>
  {t3}
  <p class="nota">Valores em M€; imparidades e provisões líquidas de reversões (valor negativo = reversão). Depreciações incluem a amortização dos passes de jogadores. Outros gastos incluem as menos-valias com jogadores, multas e quotizações. Consulta SQL 58.</p>"""

    # --- 4. Detalhe 2025/26 -----------------------------------------------------
    def linha_det(l):
        return [l["rubrica"], m(l["valor_2024_25"], 2), m(l["valor_2025_26"], 2), m(l["variacao"], 2)]
    det15 = [l for l in det if l["nota"] == "15"]
    det17 = [l for l in det if l["nota"] == "17"]
    det1920 = [l for l in det if l["nota"] in ("19", "20")]
    sec4 = f"""
  <p class="seccao-num">04</p>
  <h2>2025/26 em detalhe: notas do Relatório e Contas</h2>
  <p class="lead">As notas 15, 17, 19 e 20 do R&C 2025/26 decompõem as rubricas e comparam-nas com 2024/25. A queda das receitas está quase toda nos prémios de competições (−8,1 M€); nos gastos, a única descida relevante foi nas despesas com provas, também ligadas à Europa (−1,7 M€).</p>
  <div class="duas">
    <div><h4>Vendas e serviços prestados <span>nota 15</span></h4><figure><img src="{g4a}" alt="Detalhe das vendas e serviços prestados"></figure></div>
    <div><h4>Fornecimentos e serviços externos <span>nota 17</span></h4><figure><img src="{g4b}" alt="Detalhe dos fornecimentos e serviços externos"></figure></div>
  </div>
  <div class="duas tabelas-pequenas">
    <div>{tabela(["Rubrica", "2024/25", "2025/26", "Var."], [linha_det(l) for l in det15], classes=["", "n", "n", "n forte"])}</div>
    <div>{tabela(["Rubrica", "2024/25", "2025/26", "Var."], [linha_det(l) for l in det17], classes=["", "n", "n", "n forte"])}</div>
  </div>
  <h4>Outros rendimentos e outros gastos <span>notas 19 e 20</span></h4>
  <div class="compacta">{tabela(["Nota", "Rubrica", "2024/25", "2025/26", "Var."], [[l["nota"]] + linha_det(l) for l in det1920], classes=["", "", "n", "n", "n forte"])}</div>
  <p class="nota">Valores em M€. 2024/25 tal como apresentado no R&C 2025/26 (reexpresso): na nota 19, os ganhos com passes de 2024/25 são 0,45 M€ inferiores aos do R&C 2024/25, por causa da correção do custo amortizado. Consulta SQL 59 e tabela <code>detalhe_rubrica</code>.</p>"""

    # --- 5. Notas -----------------------------------------------------------------
    sec5 = """
  <p class="seccao-num">05</p>
  <h2>Notas metodológicas e fontes</h2>
  <div class="duas texto">
    <div>
      <h4>Fontes</h4>
      <p>Demonstrações de resultados e notas dos Relatórios e Contas da Vitória SC – Futebol, SAD, de 2012/13 a 2025/26, conferidas documento a documento, e dashboard VSC Contas (vitoriasempre.net) para a decomposição de épocas antigas. Todos os valores estão na base SQLite <code>vsc_contas.db</code> e são lidos pelas consultas 56 a 59 de <code>sql/04_analises.sql</code>.</p>
      <h4>Convenções</h4>
      <p>Valores em milhões de euros, arredondados a uma casa decimal; negativos entre parênteses, como nas demonstrações financeiras. Épocas de 1 de julho a 30 de junho. Cada época usa os valores do seu próprio Relatório e Contas; a reexpressão de 2024/25 feita no R&C 2025/26 está registada à parte (tabela <code>reexpressao</code>).</p>
      <h4>Definições</h4>
      <p><strong>Gastos operacionais:</strong> todos os gastos antes de juros e impostos, incluindo a amortização dos passes. <strong>Receitas de transferências:</strong> mais-valias líquidas, isto é, preço de venda menos valor contabilístico do jogador e custos da venda (comissões, partes de terceiros, solidariedade e, em 2025/26, efeito do custo amortizado). <strong>Saldo:</strong> receitas de transferências menos gastos operacionais.</p>
    </div>
    <div>
      <h4>Limitações</h4>
      <p>As mais-valias de 2020/21 e anteriores vêm do VSC Contas; as vendas brutas de 2020/21 não estão disponíveis. A decomposição das notas 15 a 20 só foi registada para 2024/25 e 2025/26. O R&C 2025/26 ainda está sujeito a aprovação da assembleia geral da SAD.</p>
      <h4>Qualidade dos dados</h4>
      <p>A base é validada por testes automáticos (<code>scripts/testes.py</code>): a soma das rubricas operacionais bate com o resultado operacional em nove épocas, e o detalhe das notas 15, 17, 19 e 20 soma o valor de cada rubrica da demonstração de resultados.</p>
      <h4>Emblema e autoria</h4>
      <p>O emblema é propriedade do Vitória Sport Clube e é usado apenas para identificar o clube analisado. Este relatório é uma análise independente, sem ligação oficial ao clube ou à SAD.</p>
      <p class="assinatura">João Garção<br><span>github.com/Joo2002VSC</span></p>
    </div>
  </div>"""

    paginas = [capa, sintese, sec1, sec2, sec3, sec4, sec5]
    total = len(paginas)
    corpo = "\n".join(pagina(c, i + 1, total, capa=(i == 0)) for i, c in enumerate(paginas))
    html = (RAIZ / "scripts" / "modelo_relatorio.html").read_text(encoding="utf-8").replace("{{PAGINAS}}", corpo)
    PASTA.mkdir(exist_ok=True)
    fonte_html = PASTA / f"{NOME}.html"
    fonte_html.write_text(html, encoding="utf-8")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = browser.new_page()
        page.goto(fonte_html.as_uri())
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(PASTA / f"{NOME}.pdf"), format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()
    print(f"Relatório gravado em relatorio/{NOME}.pdf ({total} páginas)")


if __name__ == "__main__":
    main()
