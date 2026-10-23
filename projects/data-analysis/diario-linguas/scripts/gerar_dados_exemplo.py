"""
Gera uma base de dados de EXEMPLO para o Diário de Aprendizagem de Línguas.

Os dados são simulados (mas realistas): seis meses de estudo de neerlandês,
francês e italiano, com vocabulário real. Serve para testar as consultas e os
gráficos antes de começar a registar os teus próprios dados com `registar.py`.

Uso:
    python scripts/gerar_dados_exemplo.py
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BD = RAIZ / "dados" / "diario.db"
ESQUEMA = RAIZ / "sql" / "01_schema.sql"

random.seed(42)

INICIO = date(2026, 5, 4)
FIM = date(2026, 10, 22)

IDIOMAS = [
    # id, código, nome, nível, objetivo
    (1, "nl", "Neerlandês", "A2", "Chegar a B1"),
    (2, "fr", "Francês", "B2", "Manter o nível"),
    (3, "it", "Italiano", "A2", "Consolidar o A2"),
]

# (termo, tradução, classe, tema, dificuldade 0–1)
VOCAB = {
    "nl": [
        ("hallo", "olá", "expressão", "saudações", .05),
        ("goedemorgen", "bom dia", "expressão", "saudações", .10),
        ("tot ziens", "adeus", "expressão", "saudações", .10),
        ("dank je wel", "muito obrigado", "expressão", "saudações", .08),
        ("alsjeblieft", "por favor / aqui tens", "expressão", "saudações", .35),
        ("graag gedaan", "de nada", "expressão", "saudações", .25),
        ("hoe gaat het?", "como estás?", "expressão", "saudações", .12),
        ("het huis", "a casa", "nome", "casa", .20),
        ("de keuken", "a cozinha", "nome", "casa", .30),
        ("de slaapkamer", "o quarto", "nome", "casa", .28),
        ("het raam", "a janela", "nome", "casa", .40),
        ("de deur", "a porta", "nome", "casa", .18),
        ("het brood", "o pão", "nome", "comida", .15),
        ("de kaas", "o queijo", "nome", "comida", .10),
        ("de groente", "os legumes", "nome", "comida", .38),
        ("het vlees", "a carne", "nome", "comida", .30),
        ("de ui", "a cebola", "nome", "comida", .55),
        ("de aardappel", "a batata", "nome", "comida", .35),
        ("lekker", "saboroso", "adjetivo", "comida", .10),
        ("de rekening", "a conta", "nome", "comida", .42),
        ("werken", "trabalhar", "verbo", "trabalho", .12),
        ("de vergadering", "a reunião", "nome", "trabalho", .60),
        ("de collega", "o colega", "nome", "trabalho", .10),
        ("het kantoor", "o escritório", "nome", "trabalho", .35),
        ("verdienen", "ganhar (dinheiro)", "verbo", "trabalho", .45),
        ("de werkgever", "o empregador", "nome", "trabalho", .40),
        ("lopen", "andar / caminhar", "verbo", "dia a dia", .25),
        ("fietsen", "andar de bicicleta", "verbo", "dia a dia", .15),
        ("boodschappen doen", "fazer compras", "expressão", "dia a dia", .50),
        ("gezellig", "acolhedor / agradável", "adjetivo", "dia a dia", .45),
        ("eigenlijk", "na verdade", "advérbio", "dia a dia", .55),
        ("misschien", "talvez", "advérbio", "dia a dia", .30),
        ("zeker", "certamente", "advérbio", "dia a dia", .22),
        ("meestal", "geralmente", "advérbio", "dia a dia", .48),
        ("binnenkort", "em breve", "advérbio", "dia a dia", .52),
        ("het station", "a estação", "nome", "viagens", .08),
        ("de trein", "o comboio", "nome", "viagens", .12),
        ("het kaartje", "o bilhete", "nome", "viagens", .35),
        ("vertrekken", "partir", "verbo", "viagens", .40),
        ("aankomen", "chegar", "verbo", "viagens", .50),
        ("de vertraging", "o atraso", "nome", "viagens", .62),
        ("overstappen", "mudar (de transporte)", "verbo", "viagens", .58),
        ("het boek", "o livro", "nome", "cultura", .30),
        ("lezen", "ler", "verbo", "cultura", .10),
        ("de voorstelling", "o espetáculo", "nome", "cultura", .55),
        ("het verhaal", "a história", "nome", "cultura", .40),
        ("schrijven", "escrever", "verbo", "cultura", .15),
        ("de wedstrijd", "o jogo / a partida", "nome", "desporto", .45),
        ("winnen", "ganhar", "verbo", "desporto", .12),
        ("verliezen", "perder", "verbo", "desporto", .30),
        ("de supporter", "o adepto", "nome", "desporto", .08),
        ("het weer", "o tempo (meteorologia)", "nome", "tempo", .20),
        ("regenen", "chover", "verbo", "tempo", .18),
        ("bewolkt", "nublado", "adjetivo", "tempo", .50),
        ("de wind", "o vento", "nome", "tempo", .05),
        ("koud", "frio", "adjetivo", "tempo", .10),
        ("begrijpen", "compreender", "verbo", "aprendizagem", .45),
        ("onthouden", "lembrar-se / memorizar", "verbo", "aprendizagem", .58),
        ("de uitspraak", "a pronúncia", "nome", "aprendizagem", .55),
        ("herhalen", "repetir", "verbo", "aprendizagem", .42),
        ("de zin", "a frase / a vontade", "nome", "aprendizagem", .50),
        ("moeilijk", "difícil", "adjetivo", "aprendizagem", .25),
        ("makkelijk", "fácil", "adjetivo", "aprendizagem", .22),
        ("de bibliotheek", "a biblioteca", "nome", "cultura", .35),
        ("lenen", "pedir emprestado", "verbo", "cultura", .52),
        ("de schrijver", "o escritor", "nome", "cultura", .30),
        ("de krant", "o jornal", "nome", "cultura", .28),
        ("de stad", "a cidade", "nome", "viagens", .15),
        ("de straat", "a rua", "nome", "viagens", .18),
        ("links", "à esquerda", "advérbio", "viagens", .20),
        ("rechtdoor", "sempre em frente", "advérbio", "viagens", .48),
        ("de haven", "o porto", "nome", "viagens", .35),
        ("de rivier", "o rio", "nome", "viagens", .25),
        ("het geld", "o dinheiro", "nome", "trabalho", .30),
        ("de schuld", "a dívida / a culpa", "nome", "trabalho", .55),
        ("de belasting", "o imposto", "nome", "trabalho", .62),
        ("sparen", "poupar", "verbo", "trabalho", .35),
        ("duur", "caro", "adjetivo", "dia a dia", .25),
        ("goedkoop", "barato", "adjetivo", "dia a dia", .38),
        ("het ontbijt", "o pequeno-almoço", "nome", "comida", .45),
        ("de lunch", "o almoço", "nome", "comida", .05),
        ("het avondeten", "o jantar", "nome", "comida", .40),
        ("het bestek", "os talheres", "nome", "comida", .60),
        ("de vriend", "o amigo / namorado", "nome", "pessoas", .15),
        ("de vriendin", "a amiga / namorada", "nome", "pessoas", .18),
        ("de buurman", "o vizinho", "nome", "pessoas", .45),
        ("de ouders", "os pais", "nome", "pessoas", .30),
        ("de broer", "o irmão", "nome", "pessoas", .22),
        ("de zus", "a irmã", "nome", "pessoas", .28),
        ("de verjaardag", "o aniversário", "nome", "pessoas", .50),
        ("vieren", "celebrar", "verbo", "pessoas", .48),
        ("de keeper", "o guarda-redes", "nome", "desporto", .10),
        ("scoren", "marcar golo", "verbo", "desporto", .08),
        ("het doelpunt", "o golo", "nome", "desporto", .58),
        ("de scheidsrechter", "o árbitro", "nome", "desporto", .68),
        ("het ijs", "o gelo / o gelado", "nome", "tempo", .35),
        ("zonnig", "soalheiro", "adjetivo", "tempo", .20),
        ("de herfst", "o outono", "nome", "tempo", .45),
    ],
    "fr": [
        ("néanmoins", "no entanto", "advérbio", "discurso", .30),
        ("d'ailleurs", "aliás", "advérbio", "discurso", .25),
        ("en revanche", "em contrapartida", "expressão", "discurso", .28),
        ("quant à", "quanto a", "expressão", "discurso", .20),
        ("à mon sens", "a meu ver", "expressão", "discurso", .18),
        ("le chantier", "a obra (construção)", "nome", "dia a dia", .35),
        ("la boîte", "a caixa / a empresa (fam.)", "nome", "dia a dia", .30),
        ("bosser", "trabalhar (fam.)", "verbo", "dia a dia", .40),
        ("le boulot", "o trabalho (fam.)", "nome", "dia a dia", .12),
        ("se débrouiller", "desenrascar-se", "verbo", "dia a dia", .38),
        ("avoir du mal à", "ter dificuldade em", "expressão", "dia a dia", .22),
        ("la fac", "a faculdade", "nome", "universidade", .08),
        ("le mémoire", "a dissertação", "nome", "universidade", .55),
        ("la soutenance", "a defesa (tese)", "nome", "universidade", .50),
        ("le directeur de thèse", "o orientador", "expressão", "universidade", .30),
        ("la bourse", "a bolsa", "nome", "universidade", .25),
        ("le dépouillement", "o levantamento (de fontes)", "nome", "universidade", .70),
        ("la dette souveraine", "a dívida soberana", "expressão", "economia", .20),
        ("le taux d'intérêt", "a taxa de juro", "expressão", "economia", .15),
        ("l'endettement", "o endividamento", "nome", "economia", .35),
        ("la croissance", "o crescimento", "nome", "economia", .12),
        ("le chômage", "o desemprego", "nome", "economia", .25),
        ("le bilan", "o balanço", "nome", "economia", .32),
        ("l'actionnaire", "o acionista", "nome", "economia", .30),
        ("le règlement", "o regulamento", "nome", "política", .40),
        ("le trilogue", "o trílogo", "nome", "política", .35),
        ("la vie privée", "a privacidade", "expressão", "política", .15),
        ("le chiffrement", "a encriptação", "nome", "política", .55),
        ("la surveillance", "a vigilância", "nome", "política", .10),
        ("éventuellement", "possivelmente (falso amigo)", "advérbio", "falsos amigos", .65),
        ("actuellement", "atualmente", "advérbio", "falsos amigos", .30),
        ("la marmelade", "a compota", "nome", "falsos amigos", .60),
        ("le chandail", "a camisola", "nome", "falsos amigos", .58),
        ("rester", "ficar", "verbo", "falsos amigos", .50),
        ("le compromis", "o acordo / compromisso", "nome", "falsos amigos", .45),
        ("la librairie", "a livraria", "nome", "falsos amigos", .40),
        ("le roman", "o romance", "nome", "cultura", .10),
        ("le recueil", "a coletânea", "nome", "cultura", .52),
        ("le dénouement", "o desfecho", "nome", "cultura", .60),
        ("feuilleter", "folhear", "verbo", "cultura", .48),
        ("l'écrivain", "o escritor", "nome", "cultura", .08),
    ],
    "it": [
        ("ciao", "olá / adeus", "expressão", "saudações", .02),
        ("buongiorno", "bom dia", "expressão", "saudações", .05),
        ("arrivederci", "adeus", "expressão", "saudações", .15),
        ("grazie mille", "muito obrigado", "expressão", "saudações", .05),
        ("prego", "de nada / faz favor", "expressão", "saudações", .28),
        ("piacere", "muito prazer", "expressão", "saudações", .20),
        ("la colazione", "o pequeno-almoço", "nome", "comida", .40),
        ("il pranzo", "o almoço", "nome", "comida", .35),
        ("la cena", "o jantar", "nome", "comida", .20),
        ("il conto", "a conta", "nome", "comida", .18),
        ("squisito", "delicioso", "adjetivo", "comida", .48),
        ("il formaggio", "o queijo", "nome", "comida", .32),
        ("la stazione", "a estação", "nome", "viagens", .05),
        ("il biglietto", "o bilhete", "nome", "viagens", .25),
        ("il binario", "a linha / plataforma", "nome", "viagens", .55),
        ("in ritardo", "atrasado", "expressão", "viagens", .30),
        ("l'albergo", "o hotel", "nome", "viagens", .45),
        ("andare", "ir", "verbo", "dia a dia", .10),
        ("rimanere", "ficar", "verbo", "dia a dia", .50),
        ("la settimana", "a semana", "nome", "dia a dia", .25),
        ("domani", "amanhã", "advérbio", "dia a dia", .15),
        ("ieri", "ontem", "advérbio", "dia a dia", .28),
        ("adesso", "agora", "advérbio", "dia a dia", .32),
        ("sempre", "sempre", "advérbio", "dia a dia", .05),
        ("spesso", "frequentemente", "advérbio", "dia a dia", .42),
        ("il libro", "o livro", "nome", "cultura", .05),
        ("leggere", "ler", "verbo", "cultura", .25),
        ("il racconto", "o conto", "nome", "cultura", .38),
        ("la partita", "o jogo (futebol)", "nome", "desporto", .45),
        ("la squadra", "a equipa", "nome", "desporto", .50),
        ("il tifoso", "o adepto", "nome", "desporto", .55),
        ("caldo", "quente", "adjetivo", "tempo", .40),
        ("piovere", "chover", "verbo", "tempo", .35),
        ("imparare", "aprender", "verbo", "aprendizagem", .30),
        ("capire", "compreender", "verbo", "aprendizagem", .20),
        ("sbagliare", "errar", "verbo", "aprendizagem", .48),
        ("la parola", "a palavra", "nome", "aprendizagem", .22),
    ],
}

RECURSOS = {
    "nl": ["Duolingo", "Anki", "Nederlands in gang", "podcast Echt Gebeurd", "série na NPO"],
    "fr": ["conversa com o Claude", "Le Monde", "France Culture", "romance", "Anki"],
    "it": ["Duolingo", "Anki", "podcast Coffee Break Italian", "YouTube"],
}

TIPOS_POR_IDIOMA = {
    "nl": (["vocabulário", "gramática", "áudio/vídeo", "leitura"], [5, 3, 2, 1]),
    "fr": (["conversa", "leitura", "áudio/vídeo", "vocabulário"], [4, 3, 2, 1]),
    "it": (["vocabulário", "gramática", "áudio/vídeo"], [5, 2, 2]),
}


def prob_sessao(codigo: str, d: date) -> float:
    """Probabilidade de haver sessão num dado dia — define o 'perfil' de cada língua."""
    fim_de_semana = d.weekday() >= 5
    if codigo == "nl":          # cada vez mais regular
        base = 0.40 + 0.25 * (d - INICIO).days / (FIM - INICIO).days
        return base * (0.7 if fim_de_semana else 1)
    if codigo == "fr":          # constante, mais ao fim de semana
        return 0.40 if fim_de_semana else 0.22
    if codigo == "it":          # entusiasmo inicial, depois abandono
        if d < date(2026, 7, 1):
            return 0.45
        if d < date(2026, 8, 15):
            return 0.15
        if d < date(2026, 9, 20):
            return 0.06
        return 0.0
    return 0.0


def main() -> None:
    BD.parent.mkdir(parents=True, exist_ok=True)
    if BD.exists():
        BD.unlink()

    con = sqlite3.connect(BD)
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))
    con.executemany("INSERT INTO idiomas VALUES (?,?,?,?,?)", IDIOMAS)
    id_idioma = {c: i for i, c, *_ in IDIOMAS}

    por_aprender = {c: list(v) for c, v in VOCAB.items()}
    for lista in por_aprender.values():
        random.shuffle(lista)
    aprendidas = {c: [] for c in VOCAB}      # (palavra_id, dificuldade, nº revisões)
    proximo_id = 1

    d = INICIO
    while d <= FIM:
        for codigo in ("nl", "fr", "it"):
            if random.random() > prob_sessao(codigo, d):
                continue
            tipos, pesos = TIPOS_POR_IDIOMA[codigo]
            tipo = random.choices(tipos, pesos)[0]
            duracao = max(10, int(random.gauss(35 if tipo == "conversa" else 25, 10)))
            cur = con.execute(
                "INSERT INTO sessoes (idioma_id, data, duracao_min, tipo, recurso) VALUES (?,?,?,?,?)",
                (id_idioma[codigo], d.isoformat(), duracao, tipo, random.choice(RECURSOS[codigo])),
            )
            sessao_id = cur.lastrowid

            # palavras novas (sobretudo em sessões de vocabulário)
            if codigo == "fr":                      # nível B2: menos palavras, mais finas
                n_novas = random.randint(0, 2)
            else:
                n_novas = random.randint(1, 3) if tipo == "vocabulário" else random.randint(0, 1)
            for _ in range(n_novas):
                if not por_aprender[codigo]:
                    break
                termo, trad, classe, tema, dif = por_aprender[codigo].pop()
                con.execute(
                    "INSERT INTO palavras VALUES (?,?,?,?,?,?,?)",
                    (proximo_id, id_idioma[codigo], termo, trad, classe, tema, d.isoformat()),
                )
                aprendidas[codigo].append([proximo_id, dif, 0])
                proximo_id += 1

            # revisões de palavras já aprendidas
            if aprendidas[codigo]:
                k = min(len(aprendidas[codigo]), random.randint(4, 10))
                for item in random.sample(aprendidas[codigo], k):
                    pid, dif, n = item
                    p_erro = dif * (0.88 ** n)      # erra menos à medida que revê
                    acertou = 0 if random.random() < p_erro else 1
                    con.execute(
                        "INSERT INTO revisoes (palavra_id, sessao_id, data, acertou) VALUES (?,?,?,?)",
                        (pid, sessao_id, d.isoformat(), acertou),
                    )
                    item[2] += 1
        d += timedelta(days=1)

    con.commit()
    totais = con.execute(
        "SELECT (SELECT COUNT(*) FROM palavras), (SELECT COUNT(*) FROM sessoes), (SELECT COUNT(*) FROM revisoes)"
    ).fetchone()
    con.close()
    print(f"Base de dados criada em {BD.relative_to(RAIZ)}")
    print(f"  {totais[0]} palavras · {totais[1]} sessões · {totais[2]} revisões")


if __name__ == "__main__":
    main()
