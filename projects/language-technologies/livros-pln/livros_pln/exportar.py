"""Exportação para Excel: uma folha por tabela, com os indicadores acompanhados da definição e do estado."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import catalogo, qualidade


def _folha(escritor, df: pd.DataFrame, nome: str):
    df.to_excel(escritor, sheet_name=nome[:31], index=False)
    folha = escritor.sheets[nome[:31]]
    folha.freeze_panes = "A2"
    for i, col in enumerate(df.columns, start=1):
        largura = max([len(str(col))] + [len(str(v)) for v in df[col].head(200)]) + 2
        folha.column_dimensions[folha.cell(row=1, column=i).column_letter].width = min(largura, 70)


def tabela_indicadores(registo: dict) -> pd.DataFrame:
    i, e = registo["indicadores"], registo.get("estados", {})
    linhas = []
    for k, ind in catalogo.INDICADORES.items():
        if k not in i and k not in e:
            continue
        estado = e.get(k, {})
        linhas.append({"grupo": ind.grupo, "indicador": ind.nome, "chave": k, "valor": i.get(k), "unidade": ind.unidade,
                       "estado": qualidade.ROTULOS.get(estado.get("estado"), "válido"), "motivo": estado.get("motivo"),
                       "definição": ind.definicao, "fórmula": ind.formula or None,
                       "comparável entre línguas": "sim" if ind.entre_linguas else "não"})
    return pd.DataFrame(linhas)


def livro(registo: dict, tabelas: dict[str, pd.DataFrame], destino: Path):
    m = registo["metadados"]
    meta = {"Título": m.get("titulo") or registo["titulo"], "Autor": m.get("autor"), "Ano": m.get("ano"),
            "Idioma": m.get("idioma"), "Fonte": m.get("fonte")}
    tec = {"Ficheiro": registo["ficheiro"], "Formato": registo["formato"],
           "Personagens (método)": registo.get("metodo_personagens"),
           "Sentimento (método)": registo.get("metodo_sentimento")}
    tec.update({f"Processamento: {k}": v for k, v in registo["processamento"].items()})
    tec.update({f"Parâmetro: {k}": v for k, v in registo.get("parametros", {}).items()})
    amb = registo.get("ambiente", {})
    if amb:
        tec["Ambiente: Python"] = amb.get("python")
        tec.update({f"Ambiente: {k}": v for k, v in amb.get("bibliotecas", {}).items()})
        tec["Modelo spaCy"] = f"{amb['modelo']['nome']} {amb['modelo']['versao']}"
        tec.update({f"Modelo: exatidão {k}": v for k, v in amb["modelo"].get("exatidao", {}).items()})
    with pd.ExcelWriter(destino, engine="openpyxl") as w:
        _folha(w, pd.DataFrame(list(meta.items()), columns=["campo", "valor"]), "Metadados")
        _folha(w, pd.DataFrame(list(tec.items()), columns=["campo", "valor"]), "Processamento")
        _folha(w, tabela_indicadores(registo), "Indicadores")
        if registo.get("qualidade"):
            _folha(w, pd.DataFrame(registo["qualidade"]), "Qualidade")
        for nome, df in tabelas.items():
            if df is not None and not df.empty:
                _folha(w, df, nome)


def corpus(tabela: pd.DataFrame, destino: Path):
    dicionario = pd.DataFrame([{"chave": k, "indicador": i.nome, "grupo": i.grupo, "unidade": i.unidade,
                                "definição": i.definicao, "comparável entre línguas": "sim" if i.entre_linguas else "não"}
                               for k, i in catalogo.INDICADORES.items()])
    with pd.ExcelWriter(destino, engine="openpyxl") as w:
        _folha(w, tabela, "Livros")
        _folha(w, dicionario, "Dicionário de indicadores")
