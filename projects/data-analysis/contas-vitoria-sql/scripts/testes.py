"""Testes de qualidade, integridade e reconciliação da base vsc_contas.db.

Corre todos os testes e grava o relatório em testes.md. Termina com código 1
se algum teste falhar (os avisos não contam como falhas), para poder ser usado
em integração contínua.

Uso (a partir da raiz do projeto, depois de build_db.py):
    python scripts/testes.py
"""
import platform
import re
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "vsc_contas.db"
SQL = RAIZ / "sql" / "04_analises.sql"
SAIDA = RAIZ / "testes.md"

# Funções que o SQLite do Python tem, mas o sql.js (consola do browser) não.
FUNCOES_NAO_PORTATEIS = r"\b(ln|log|log2|log10|pow)\s*\("

# Números citados no README e nos relatórios, verificados contra a base.
# (descrição, consulta que devolve um valor, valor publicado, tolerância)
RECONCILIACAO = [
    ("Resultado líquido da SAD 2024/25 (M€)",
     "SELECT resultado_liquido / 1e6 FROM v_kpis WHERE entidade_id='SAD' AND epoca_id='2024/25'", 7.6, 0.05),
    ("Resultado sem mais-valias 2024/25 (M€)",
     "SELECT rl_sem_mais_valias / 1e6 FROM v_kpis WHERE entidade_id='SAD' AND epoca_id='2024/25'", -19.9, 0.05),
    ("Resultado sem mais-valias 2023/24 (M€)",
     "SELECT rl_sem_mais_valias / 1e6 FROM v_kpis WHERE entidade_id='SAD' AND epoca_id='2023/24'", -21.4, 0.05),
    ("Mais-valias 2024/25 (M€)",
     "SELECT mais_valias_liquidas / 1e6 FROM v_kpis WHERE entidade_id='SAD' AND epoca_id='2024/25'", 27.5, 0.05),
    ("Resultado líquido da SAD 2025/26 (M€)",
     "SELECT resultado_liquido / 1e6 FROM v_dr WHERE entidade_id='SAD' AND epoca_id='2025/26'", -11.1, 0.05),
    ("Capital próprio da SAD a 30/06/2026 (M€)",
     "SELECT capital_proprio / 1e6 FROM balanco WHERE entidade_id='SAD' AND epoca_id='2025/26'", -36.8, 0.05),
    ("Passivo da SAD a 30/06/2026 (M€)",
     "SELECT passivo_total / 1e6 FROM balanco WHERE entidade_id='SAD' AND epoca_id='2025/26'", 85.3, 0.05),
    ("Rácio de endividamento 2023/24",
     "SELECT 1.0 * passivo_total / ativo_total FROM balanco_sad_rc WHERE epoca_id='2023/24'", 1.87, 0.005),
    ("Dívida financeira a 30/06/2025 (M€)",
     "SELECT (financiamentos_nc + financiamentos_c) / 1e6 FROM balanco_sad_rc WHERE epoca_id='2024/25'", 34.6, 0.05),
    ("Juros suportados 2024/25 (M€)",
     "SELECT juros_suportados / 1e6 FROM balanco_sad_rc WHERE epoca_id='2024/25'", 5.0, 0.05),
    ("Taxa de juro implícita 2024/25 (%)",
     "SELECT vitoria_implicita FROM v_taxas_epoca WHERE epoca_id='2024/25'", 14.6, 0.05),
    ("Euribor a 12 meses, média 2024/25 (%)",
     "SELECT euribor_12m FROM v_taxas_epoca WHERE epoca_id='2024/25'", 2.6, 0.05),
    ("Funcionários da SAD 2024/25",
     "SELECT funcionarios FROM pessoal_sad WHERE epoca_id='2024/25'", 229, 0),
    ("Vendas brutas por euro de receita 2024/25",
     "SELECT 1.0 * t.vendas_brutas / d.vendas_servicos FROM transferencias t JOIN v_dr d "
     "ON d.epoca_id = t.epoca_id AND d.entidade_id = 'SAD' WHERE t.entidade_id='SAD' AND t.epoca_id='2024/25'",
     2.19, 0.005),
    ("Défice antes de vendas, média 2022/23–2024/25 (M€)",
     "SELECT AVG(rl_sem_mais_valias) / 1e6 FROM v_kpis WHERE entidade_id='SAD' "
     "AND epoca_id BETWEEN '2022/23' AND '2024/25'", -20.9, 0.05),
    ("Rácio UEFA de custos do plantel 2024/25 (%) · consulta 45", ("q45", "2024/25", "racio_pct"), 44.7, 0.05),
    ("R² da regressão despesas vs. lugar · consulta 53", ("q53", "2024/25", "r_quadrado"), 0.09, 0.005),
]


class Relatorio:
    def __init__(self):
        self.linhas, self.falhas, self.avisos, self.ok = [], 0, 0, 0

    def secao(self, titulo):
        self.linhas += ["", f"## {titulo}", "", "| Resultado | Teste | Detalhe |", "|:---:|:---|:---|"]

    def registar(self, estado, teste, detalhe=""):
        simbolo = {"ok": "✓", "falha": "✗", "aviso": "⚠"}[estado]
        if estado == "ok":
            self.ok += 1
        elif estado == "falha":
            self.falhas += 1
        else:
            self.avisos += 1
        self.linhas.append(f"| {simbolo} | {teste} | {detalhe} |")
        print(f"  {simbolo} {teste}" + (f" · {detalhe}" if detalhe and estado != "ok" else ""))


def valor(con, sql):
    linha = con.execute(sql).fetchone()
    return None if linha is None else linha[0]


def da_consulta(con, consulta, epoca, coluna):
    """Corre a consulta N de 04_analises.sql e devolve uma coluna da linha de uma época."""
    numero = consulta[1:]
    bloco = SQL.read_text(encoding="utf-8").split(f"-- @q {numero}.")[1]
    bloco = re.split(r"^-- @q ", bloco, flags=re.M)[0].split("\n", 1)[1]
    cur = con.execute(bloco)
    nomes = [d[0] for d in cur.description]
    for linha in cur.fetchall():
        if linha[0] == epoca:
            return linha[nomes.index(coluna)]
    return None


def main():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    r = Relatorio()

    # 1. Integridade ------------------------------------------------------
    print("Integridade")
    r.secao("1. Integridade da base de dados")
    estado = valor(con, "PRAGMA integrity_check")
    r.registar("ok" if estado == "ok" else "falha", "Ficheiro SQLite íntegro (`PRAGMA integrity_check`)", estado)
    erros_fk = con.execute("PRAGMA foreign_key_check").fetchall()
    r.registar("ok" if not erros_fk else "falha", "Chaves estrangeiras válidas (`PRAGMA foreign_key_check`)",
               f"{len(erros_fk)} referências inválidas" if erros_fk else "0 referências inválidas")
    epocas = [e for (e,) in con.execute("SELECT epoca_id FROM epoca ORDER BY epoca_id")]
    esperadas = [f"{a}/{str(a + 1)[2:]}" for a in range(2012, 2026)]
    r.registar("ok" if epocas == esperadas else "falha", "Épocas contínuas de 2012/13 a 2025/26",
               f"{len(epocas)} épocas")
    orfas = valor(con, """SELECT COUNT(*) FROM demonstracao_resultados d
                          LEFT JOIN rubrica r ON r.rubrica_id = d.rubrica_id WHERE r.rubrica_id IS NULL""")
    r.registar("ok" if orfas == 0 else "falha", "Todas as linhas da DR têm rubrica conhecida", f"{orfas} sem correspondência")

    # 2. Coerência contabilística ------------------------------------------
    print("Coerência contabilística")
    r.secao("2. Coerência contabilística")
    erros = con.execute("""SELECT entidade_id || ' ' || epoca_id FROM balanco
                           WHERE ABS(ativo_total - passivo_total - capital_proprio) > 1""").fetchall()
    r.registar("ok" if not erros else "falha", "Ativo = passivo + capital próprio (todas as entidades e épocas)",
               ", ".join(e for (e,) in erros) or "diferença ≤ 1 € em todas")
    erros = con.execute("""SELECT epoca_id FROM balanco_sad_rc
                           WHERE ABS(ativo_corrente + ativo_nao_corrente - ativo_total) > 1
                              OR ABS(passivo_corrente + passivo_nao_corrente - passivo_total) > 1""").fetchall()
    r.registar("ok" if not erros else "falha", "Corrente + não corrente = total (balanço dos R&C)",
               ", ".join(e for (e,) in erros) or "13 épocas")
    erros = con.execute("""SELECT r.epoca_id FROM balanco_sad_rc r JOIN balanco b
                           ON b.epoca_id = r.epoca_id AND b.entidade_id = 'SAD'
                           WHERE ABS(r.ativo_total - b.ativo_total) > 1
                              OR ABS(r.capital_proprio - b.capital_proprio) > 1""").fetchall()
    r.registar("ok" if not erros else "falha", "Tabela `balanco` (SAD) igual ao balanço dos R&C",
               ", ".join(e for (e,) in erros) or "sem diferenças")
    erros = con.execute("""SELECT epoca_id FROM pessoal_sad
                           WHERE jogadores + treinadores_profissional + treinadores_formacao
                                 + COALESCE(apoio_futebol_profissional, 0) + outro_pessoal != funcionarios""").fetchall()
    r.registar("ok" if not erros else "falha", "Soma das categorias de pessoal = nº de funcionários",
               ", ".join(e for (e,) in erros) or "todas as épocas")
    erros = con.execute("""SELECT epoca_id FROM pessoal_sad
                           WHERE ABS(COALESCE(rem_administracao,0) + COALESCE(rem_pessoal_administrativo,0)
                                   + COALESCE(rem_treinadores,0) + COALESCE(rem_jogadores,0)
                                   + COALESCE(rem_apoio_futebol,0) + COALESCE(encargos_remuneracoes,0)
                                   + COALESCE(seguro_acidentes,0) + COALESCE(outros_gastos,0)
                                   - total_gastos_pessoal) > 1
                             AND rem_jogadores IS NOT NULL""").fetchall()
    r.registar("ok" if not erros else "falha", "Soma das rubricas de gastos com pessoal = total",
               ", ".join(e for (e,) in erros) or "épocas com remunerações decompostas (2016/17 em diante)")
    sem = [e for (e,) in con.execute("SELECT epoca_id FROM pessoal_sad WHERE rem_jogadores IS NULL")]
    if sem:
        r.registar("aviso", "Remunerações sem decomposição por categoria",
                   ", ".join(sem) + ": os R&C dessas épocas só dão o total")
    erros = con.execute("""SELECT epoca_id FROM passes_jogadores
                           WHERE ABS(valor_liquido_inicio + aquisicoes - amortizacoes
                                     - (valor_bruto_alienado - amort_acumuladas_alienadas)
                                     - (rescisoes_bruto - rescisoes_amort_acumuladas)
                                     - valor_liquido_fim) > 4""").fetchall()
    r.registar("ok" if not erros else "falha",
               "Passes: valor inicial + aquisições − amortizações − saídas = valor final",
               ", ".join(e for (e,) in erros) or "todas as épocas (tolerância de 4 €: oito valores arredondados ao euro)")
    erros = con.execute("""SELECT a.epoca_id FROM passes_jogadores a JOIN passes_jogadores b
                           ON b.epoca_id = (SELECT MIN(epoca_id) FROM passes_jogadores WHERE epoca_id > a.epoca_id)
                           WHERE ABS(a.valor_liquido_fim - b.valor_liquido_inicio) > 1""").fetchall()
    r.registar("ok" if not erros else "falha", "Passes: valor final de uma época = valor inicial da seguinte",
               ", ".join(e for (e,) in erros) or "sem quebras")
    erros = con.execute("""SELECT epoca_id FROM v_kpis WHERE entidade_id = 'SAD'
                           AND mais_valias_liquidas IS NOT NULL
                           AND rl_sem_mais_valias != resultado_liquido - mais_valias_liquidas""").fetchall()
    r.registar("ok" if not erros else "falha", "Resultado sem mais-valias = resultado líquido − mais-valias",
               ", ".join(e for (e,) in erros) or "todas as épocas")
    erros = con.execute("""SELECT data_ref || ' ' || instrumento FROM financiamento_detalhe
                           WHERE menos_1_ano > total OR total < 0""").fetchall()
    r.registar("ok" if not erros else "falha", "Dívida por instrumento: parte de curto prazo ≤ total",
               ", ".join(e for (e,) in erros) or "sem incoerências")

    # 2025/26: as linhas do comunicado somam o resultado líquido.
    obs = dict(con.execute("SELECT descricao, valor FROM evento WHERE epoca_id = '2025/26' "
                           "AND tipo = 'observacao'").fetchall())
    rend, imp, rl, ebitda = con.execute(
        """SELECT MAX(CASE WHEN rubrica_id='rendimentos_operacionais' THEN valor END),
                  MAX(CASE WHEN rubrica_id='imposto' THEN valor END),
                  MAX(CASE WHEN rubrica_id='resultado_liquido' THEN valor END),
                  MAX(CASE WHEN rubrica_id='ebitda_sem_transferencias' THEN valor END)
           FROM demonstracao_resultados WHERE entidade_id='SAD' AND epoca_id='2025/26'""").fetchone()
    soma = (rend + obs["Gastos operacionais (excluindo operações com atletas)"]
            + obs["Resultado com direitos de atletas (após custos e amortizações)"]
            + obs["Resultados financeiros"] + imp)
    dif = abs(soma - rl)
    estado = "ok" if dif <= 2 else "aviso" if dif <= 5000 else "falha"
    r.registar(estado, "`rec_2025_26`: linhas do comunicado somam o resultado líquido",
               f"{soma:,.0f} € vs {rl:,.0f} € · diferença de {dif:,.0f} € não discriminada no comunicado".replace(",", " "))
    implicita = rend + obs["Gastos operacionais (excluindo operações com atletas)"] - ebitda
    r.registar("aviso", "`rec_2025_26`: EBITDA publicado ≠ rendimentos − gastos",
               f"diferença de {abs(implicita) / 1e6:.2f} M€: depreciações de ativos não desportivos (deduzida)".replace(".", ","))

    # 3. Reconciliação com os relatórios -----------------------------------
    print("Reconciliação")
    r.secao("3. Reconciliação: números citados nos relatórios vs. base de dados")
    for descricao, sql, publicado, tol in RECONCILIACAO:
        if isinstance(sql, tuple):  # valor lido do resultado de uma consulta do projeto
            calc = da_consulta(con, *sql)
        else:
            calc = valor(con, sql)
        ok = calc is not None and abs(calc - publicado) <= tol + 1e-9
        r.registar("ok" if ok else "falha", descricao,
                   f"publicado {publicado:g} · calculado {calc:.3f}".replace(".", ","))

    # 4. Consultas -------------------------------------------------------------
    print("Consultas")
    r.secao("4. Consultas de análise")
    texto = SQL.read_text(encoding="utf-8")
    blocos = re.split(r"^-- @q ", texto, flags=re.M)[1:]
    vazias, erros_sql, nao_portateis = [], [], []
    for bloco in blocos:
        titulo, _, corpo = bloco.partition("\n")
        numero = titulo.split(".")[0]
        codigo = "\n".join(l for l in corpo.splitlines() if not l.strip().startswith("--"))
        if re.search(FUNCOES_NAO_PORTATEIS, codigo, re.I):
            nao_portateis.append(numero)
        try:
            if not con.execute(corpo).fetchall():
                vazias.append(numero)
        except sqlite3.Error as e:
            erros_sql.append(f"{numero} ({e})")
    r.registar("ok" if not erros_sql else "falha", f"As {len(blocos)} consultas correm sem erros",
               "; ".join(erros_sql) or "")
    r.registar("ok" if not vazias else "falha", "Todas as consultas devolvem pelo menos uma linha",
               ", ".join(vazias) or "")
    r.registar("ok" if not nao_portateis else "falha",
               "Nenhuma consulta usa funções que não existem no SQLite do browser (ln, log, pow)",
               ", ".join(nao_portateis) or "")

    # 5. Avisos de qualidade ----------------------------------------------------
    print("Avisos")
    r.secao("5. Avisos de qualidade (não bloqueiam)")
    for categoria, v, n in con.execute(
            """SELECT categoria, valor, COUNT(*) FROM receitas_composicao
               GROUP BY categoria, valor HAVING COUNT(*) >= 3"""):
        r.registar("aviso", f"Valor repetido em {n} épocas: {categoria}", f"{v:,} €".replace(",", " "))
    for epoca, in con.execute("""SELECT epoca_id FROM transferencias WHERE entidade_id='SAD'
                                 AND vendas_brutas = mais_valias_liquidas"""):
        r.registar("aviso", f"Vendas brutas = mais-valias em {epoca}",
                   "a fonte só indica as mais-valias; o rácio de mais-valias sobre vendas dá 100%")
    em_falta = [e for (e,) in con.execute(
        """SELECT e.epoca_id FROM epoca e LEFT JOIN v_dr d ON d.epoca_id = e.epoca_id AND d.entidade_id = 'SAD'
           WHERE d.vendas_servicos IS NULL ORDER BY 1""")]
    r.registar("aviso", "Épocas da SAD sem receitas detalhadas", ", ".join(em_falta))

    con.close()
    cabecalho = [
        "# Testes de qualidade e reconciliação", "",
        "Gerado por `scripts/testes.py`. Corre-o depois de `build_db.py`.", "",
        f"**{r.ok} testes aprovados · {r.falhas} falhados · {r.avisos} avisos**", "",
        f"Python {platform.python_version()} · SQLite {sqlite3.sqlite_version} · {platform.system()}",
    ]
    SAIDA.write_text("\n".join(cabecalho + r.linhas) + "\n", encoding="utf-8")
    print(f"\n{r.ok} aprovados, {r.falhas} falhados, {r.avisos} avisos · relatório em {SAIDA.name}")
    sys.exit(1 if r.falhas else 0)


if __name__ == "__main__":
    main()
