"""Gera dicionario-dados.md a partir do esquema e da base de dados.

Para cada tabela e vista: descrição (comentário que a precede em 01_schema.sql
ou 03_vistas.sql), número de linhas, épocas cobertas e, para cada coluna, tipo,
chave, se aceita NULL, quantos valores estão em falta e o comentário da coluna.

Uso (a partir da raiz do projeto, depois de build_db.py):
    python scripts/dicionario.py
"""
import re
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "vsc_contas.db"
SAIDA = RAIZ / "dicionario-dados.md"

CONVENCOES = """## Convenções

| Tema | Regra |
|:---|:---|
| Dialeto | SQLite 3 (testado com 3.45). As consultas só usam funções que também existem no sql.js do browser. |
| Unidades | Valores monetários em **euros inteiros** (arredondados ao euro na carga). Taxas de juro em **percentagem** (2,5 = 2,5%). |
| Sinais | Gastos com sinal **negativo**, como nas demonstrações de resultados. Em `v_kpis`, `gastos_pessoal` e `juros` passam a positivos. |
| Épocas | Texto `AAAA/AA` (por exemplo `2024/25`). O exercício fecha a 30 de junho do segundo ano. |
| Entidades | `SAD` (Vitória SC – Futebol, SAD), `CLUBE` (associação) e `CONSOLIDADO` (Grupo). |
| Em falta | `NULL` = dado não disponível na fonte. Nunca se usa 0 para "desconhecido". |
| Proveniência | Coluna `documento` (relatório e nota de origem) nas tabelas verificadas nos R&C; tabela `fonte` para as restantes; `divergencia` regista os valores das fontes secundárias que foram substituídos. |
"""


def comentarios(caminho):
    """Devolve {tabela: (descrição, {coluna: comentário})} lendo o SQL."""
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    resultado = {}
    for i, linha in enumerate(linhas):
        m = re.match(r"CREATE (?:TABLE|VIEW) (\w+)", linha)
        if not m:
            continue
        acima, j = [], i - 1
        while j >= 0 and linhas[j].startswith("--"):
            texto = linhas[j].lstrip("-").strip()
            if texto and not set(texto) <= set("=-"):
                acima.insert(0, texto)
            j -= 1
        cols, k = {}, i + 1
        while k < len(linhas) and not linhas[k].startswith(");") and not linhas[k].startswith("CREATE"):
            c = re.match(r"\s*(\w+)\s+[A-Z]+.*?--\s*(.+)$", linhas[k])
            if c:
                cols[c.group(1)] = c.group(2).strip()
            k += 1
        resultado[m.group(1)] = (" ".join(acima), cols)
    return resultado


# Descrições das colunas. Chave "coluna" vale para todas as tabelas;
# "tabela.coluna" sobrepõe-se. Os comentários do próprio esquema têm prioridade.
COLUNAS = {
    "epoca_id": "Época desportiva, `AAAA/AA`",
    "entidade_id": "`SAD`, `CLUBE` ou `CONSOLIDADO`",
    "ano_inicio": "Ano em que a época começa (1 de julho)",
    "ano_fim": "Ano em que a época termina (30 de junho)",
    "nome": "Nome legível",
    "descricao": "Texto descritivo",
    "documento": "Documento e nota de origem (Relatório e Contas)",
    "documentos": "Documentos de origem",
    "nota": "Observação sobre o valor ou a época",
    "valor": "Valor em euros",
    "categoria": "Categoria da receita ou do gasto",
    "tipo": "Tipo de registo",
    "estado": "Estado dos dados nesta fonte",
    "fonte": "Origem do valor",
    "indicador": "Nome do indicador",
    "rubrica_id": "Identificador da rubrica da demonstração de resultados",
    "rubrica.natureza": "`rendimento`, `gasto` ou `resultado`",
    "rubrica.ordem": "Ordem de apresentação na demonstração de resultados",
    "ativo_total": "Ativo total a 30/06 (€)",
    "ativo_corrente": "Ativo corrente (€)",
    "ativo_nao_corrente": "Ativo não corrente (€)",
    "passivo_total": "Passivo total a 30/06 (€)",
    "passivo_corrente": "Passivo corrente, a menos de um ano (€)",
    "passivo_nao_corrente": "Passivo não corrente (€)",
    "capital_proprio": "Capital próprio = ativo − passivo (€); no Clube, fundos patrimoniais",
    "caixa": "Caixa e depósitos bancários a 30/06 (€)",
    "financiamentos_nc": "Financiamentos obtidos não correntes (€)",
    "financiamentos_c": "Financiamentos obtidos correntes (€)",
    "juros_suportados": "Juros e gastos similares suportados, brutos (€)",
    "juros_obtidos": "Juros obtidos (€)",
    "operacional": "Fluxo de caixa das atividades operacionais (€)",
    "investimento": "Fluxo de caixa das atividades de investimento (€)",
    "financiamento": "Fluxo de caixa das atividades de financiamento (€)",
    "vendas_brutas": "Valor bruto das vendas de passes de jogadores (€)",
    "custo_vendas": "Comissões, partes de terceiros e solidariedade pagas nas vendas (€)",
    "mais_valias_liquidas": "Preço de venda − valor contabilístico − custos da venda (€)",
    "jogador": "Nome do jogador",
    "clube": "Clube de destino ou de origem",
    "operacao_id": "Identificador da operação",
    "credor": "Entidade credora",
    "total": "Montante total em dívida (€)",
    "menos_1_ano": "Parte que vence em menos de um ano (€)",
    "entre_1_3_anos": "Parte que vence entre um e três anos (€)",
    "mais_3_anos": "Parte que vence a mais de três anos (€)",
    "data_ref": "Data de referência (AAAA-MM-DD)",
    "instrumento": "Empréstimos, factoring, Apollo ou locações financeiras",
    "posicao_liga": "Lugar final na I Liga",
    "pontos": "Pontos na I Liga",
    "media_espectadores": "Média de espectadores em casa na Liga (0 = jogos sem público)",
    "competicao_europeia": "Competição europeia disputada (NULL = nenhuma)",
    "fase_europeia": "Fase mais avançada atingida na Europa",
    "trofeu": "Troféu conquistado na época",
    "funcionarios": "Número médio de funcionários da SAD",
    "jogadores": "Número médio de jogadores",
    "treinadores_profissional": "Treinadores e staff técnico do futebol profissional",
    "treinadores_formacao": "Treinadores da formação",
    "apoio_futebol_profissional": "Pessoal de apoio ao futebol profissional (categoria criada em 2021/22)",
    "outro_pessoal": "Restante pessoal (administrativo e outros)",
    "rem_administracao": "Remunerações dos órgãos sociais (€)",
    "rem_pessoal_administrativo": "Remunerações do pessoal administrativo (€)",
    "rem_treinadores": "Remunerações dos treinadores (€)",
    "rem_jogadores": "Remunerações dos jogadores (€)",
    "rem_apoio_futebol": "Remunerações do pessoal de apoio ao futebol (€)",
    "encargos_remuneracoes": "Encargos sociais sobre remunerações (€)",
    "seguro_acidentes": "Seguros de acidentes de trabalho (€)",
    "outros_gastos": "Outros gastos com pessoal (€)",
    "total_gastos_pessoal": "Total de gastos com pessoal (€)",
    "valor_liquido_inicio": "Valor contabilístico do plantel no início da época (€)",
    "valor_liquido_fim": "Valor contabilístico do plantel no fim da época (€)",
    "aquisicoes": "Passes adquiridos na época (€)",
    "amortizacoes": "Amortizações dos passes na época (€)",
    "valor_bruto_alienado": "Custo de aquisição dos passes vendidos (€)",
    "amort_acumuladas_alienadas": "Amortizações acumuladas dos passes vendidos (€)",
    "rescisoes_bruto": "Custo de aquisição dos contratos rescindidos (€)",
    "rescisoes_amort_acumuladas": "Amortizações acumuladas dos contratos rescindidos (€)",
    "lado": "`ativo` ou `passivo`",
    "prazo": "`corrente` ou `nao_corrente`",
    "rubrica": "Rubrica do balanço ou da transação",
    "sentido": "`receita da SAD`, `gasto da SAD` ou `saldo`",
    "parecer_auditor": "Tipo de opinião e ênfases da certificação legal de contas",
    "artigo_35_no_relatorio": "1 se o relatório refere o artigo 35.º do CSC",
    "valor_original": "Valor publicado no R&C da própria época",
    "valor_reexpresso": "Valor reexpresso no ano seguinte",
    "valor_fonte": "Valor na fonte secundária",
    "valor_rc": "Valor nos Relatórios e Contas",
    "diferenca": "valor_fonte − valor_rc",
    "divergencia_id": "Identificador",
    "evento_id": "Identificador",
    "treinador_id": "Identificador",
    "periodo": "Período no cargo (texto)",
    "data": "Mês da observação (AAAA-MM-01)",
    "taxa_pct": "Taxa em percentagem",
    "data_efeito": "Data a partir da qual a taxa vigora",
    "facilidade_deposito": "Taxa da facilidade permanente de depósito do BCE (%)",
    "refinanciamento": "Taxa das operações principais de refinanciamento do BCE (%)",
    "vendas_servicos": "Vendas e prestações de serviços: receitas da operação (€)",
    "rendimentos_operacionais": "Rendimentos operacionais sem operações com jogadores (€; 2025/26)",
    "outros_rendimentos": "Outros rendimentos, incluindo mais-valias com jogadores (€)",
    "fse": "Fornecimentos e serviços externos (€, negativo)",
    "gastos_pessoal": "Gastos com pessoal (€; negativo em `v_dr`, positivo em `v_kpis`)",
    "depreciacoes": "Depreciações e amortizações, incluindo passes (€, negativo)",
    "ebitda": "Resultado antes de juros, impostos, depreciações e amortizações (€)",
    "ebitda_sem_transferencias": "EBITDA sem operações com jogadores (€)",
    "resultado_operacional": "Resultado operacional (€)",
    "juros": "Juros (€; nalgumas épocas líquidos dos juros obtidos, ver `balanco_sad_rc`)",
    "resultado_liquido": "Resultado líquido do período (€)",
    "rl_sem_mais_valias": "Resultado líquido − mais-valias com jogadores (€)",
    "pct_pessoal_receitas": "Gastos com pessoal em % das vendas e serviços",
    "rl_sad": "Resultado líquido da SAD (€)",
    "rl_clube": "Resultado líquido do Clube (€)",
    "rl_consolidado": "Resultado líquido do Grupo (€)",
    "bce_deposito": "Taxa de depósito do BCE, média da época ponderada pelos dias (%)",
    "euribor_12m": "Euribor a 12 meses, média da época (%)",
    "ot_portugal_10a": "Obrigações do Estado português a 10 anos, média da época (%)",
    "credito_empresas_pt": "Crédito novo a empresas em Portugal, média dos meses disponíveis (%)",
    "vitoria_implicita": "Juros suportados ÷ dívida financeira média da SAD (%)",
    "meses_euribor": "Número de observações mensais da Euribor na época",
}


def main():
    con = sqlite3.connect(DB)
    notas = {**comentarios(RAIZ / "sql" / "01_schema.sql"), **comentarios(RAIZ / "sql" / "03_vistas.sql")}
    objetos = con.execute("""SELECT name, type FROM sqlite_master
                             WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'
                             ORDER BY type, name""").fetchall()
    linhas = ["# Dicionário de dados", "",
              "Gerado por `scripts/dicionario.py` a partir de `vsc_contas.db` e dos comentários do esquema.", "",
              CONVENCOES, "## Índice", ""]
    linhas.append(" · ".join(f"[`{n}`](#{n})" for n, _ in objetos))
    for nome, tipo in objetos:
        desc, cols_nota = notas.get(nome, ("", {}))
        n = con.execute(f"SELECT COUNT(*) FROM {nome}").fetchone()[0]
        info = con.execute(f"PRAGMA table_info({nome})").fetchall()
        fks = {f[3]: f"{f[2]}.{f[4]}" for f in con.execute(f"PRAGMA foreign_key_list({nome})")}
        nomes = [c[1] for c in info]
        cobertura = ""
        if "epoca_id" in nomes:
            a, b = con.execute(f"SELECT MIN(epoca_id), MAX(epoca_id) FROM {nome}").fetchone()
            cobertura = f" · épocas {a} a {b}" if a else ""
        linhas += ["", f"## `{nome}`", "",
                   f"*{'Vista' if tipo == 'view' else 'Tabela'} · {n} linhas{cobertura}*", ""]
        if desc:
            linhas += [desc, ""]
        linhas += ["| Coluna | Tipo | Chave | Em falta | Descrição |", "|:---|:---|:---|---:|:---|"]
        for _, col, tipo_col, notnull, _, pk in info:
            chave = " · ".join(filter(None, ["PK" if pk else "", f"FK → `{fks[col]}`" if col in fks else ""]))
            nulos = con.execute(f"SELECT COUNT(*) FROM {nome} WHERE {col} IS NULL").fetchone()[0]
            texto = cols_nota.get(col) or COLUNAS.get(f"{nome}.{col}") or COLUNAS.get(col, "")
            linhas.append(f"| `{col}` | {tipo_col or '—'} | {chave} | {nulos if nulos else ''} | {texto} |")
    SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Dicionário gravado em {SAIDA.name} ({len(objetos)} tabelas e vistas)")


if __name__ == "__main__":
    main()
