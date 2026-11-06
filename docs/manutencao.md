# Manutenção do repositório

Guia curto para manter o portefólio organizado: onde fica cada coisa, que convenções seguir e o que não se pode mover.

## Estrutura

```text
Portfolio--Joao_Garcao/
├── README.md, README.en.md, README.fr.md   apresentação do portefólio (mesma estrutura nas 3 línguas)
├── LICENSE.md                              regime de direitos e exceções
├── about/                                  CV
├── assets/                                 imagens do README principal
├── docs/                                   este guia
├── observatorio-blcs/                      página de encaminhamento (endereço antigo do Observatório)
├── .github/
│   ├── workflows/                          testes e verificação de ligações
│   └── scripts/                            scripts usados pelos workflows
└── projects/
    ├── data-analysis/                      análise de dados em SQL e Python
    ├── web-development/                    sites, dashboards e interfaces
    ├── digital-humanities/                 património, edição digital, Observatório BLCS
    ├── language-technologies/              PLN e IA
    ├── languages-and-literature/           tradução, terminologia, estudos literários
    └── business-and-innovation/            inovação e análise de negócio
```

## Convenções

- **Nomes de pastas e ficheiros:** minúsculas, palavras separadas por hífen, sem espaços nem acentos (`contas-vitoria-sql`, `captura-2023-05-26-100543.png`).
- **Áreas:** organizadas por domínio de conhecimento, não por linguagem de programação. Uma área nova só se justifica com dois ou mais projetos.
- **READMEs:** português europeu primeiro (`## 🇵🇹`), depois inglês (`## 🇬🇧`); alguns projetos têm também francês. Cada README de área lista todos os seus projetos.
- **Terminologia:** «direitos de TV» (nunca «direitos TV»).
- **Créditos e direitos:** cada projeto indica os coautores e termina com a nota de direitos que remete para `LICENSE.md`.

## Painéis do Livros-PLN

As ligações do portefólio para o Livros-PLN apontam para o GitHub Pages do próprio repositório (https://joo2002vsc.github.io/livros-pln/), que o GitHub Actions do livros-pln atualiza sempre que muda o código ou um livro. Não é preciso copiar nada para o portefólio quando sai uma versão nova.

`projects/language-technologies/livros-pln/demo/` guarda uma cópia de arquivo dos painéis da versão 3.4.1 (6 de novembro de 2026); já não é atualizada nem usada nas ligações. O `index.html` da pasta do projeto reencaminha para a página dos livros analisados.

## Acrescentar um projeto

1. Criar a pasta em `projects/<área>/<nome-do-projeto>/`.
2. Escrever o `README.md`: contexto (cadeira ou projeto pessoal), objetivos, tecnologias, ficheiros, autoria e nota de direitos.
3. Acrescentar uma linha ao README da área (PT e EN).
4. Se for um projeto de destaque, atualizar os três READMEs da raiz.
5. Correr `python .github/scripts/verificar_ligacoes.py` antes do commit.

## Caminhos que não se podem mover

O GitHub Pages publica o branch `main` a partir da raiz, por isso o endereço de cada página é o seu caminho no repositório.

| Caminho | Porquê |
| --- | --- |
| `projects/web-development/dashboard-contas-vitoria/` | Página publicada; lê dados de `data/`; o script `exportar_json.py` lê de `../../data-analysis/contas-vitoria-sql` |
| `projects/data-analysis/contas-vitoria-sql/` | Workflow `contas-vitoria-sql.yml`; fonte de dados da dashboard |
| `projects/data-analysis/simulador-juros-compostos/` | Página publicada (`web/`); workflow `simulador-juros-compostos.yml` |
| `projects/web-development/blog-literario/` | Página publicada; `leituras-sql/scripts/caminhos.py` escreve nesta pasta |
| `projects/data-analysis/leituras-sql/` | Escreve no blog através de um caminho relativo |
| `projects/digital-humanities/observatorio-blcs/` | Página publicada; o endereço antigo `observatorio-blcs/` encaminha para aqui |

Se for mesmo necessário mover uma destas pastas: atualizar os scripts e os workflows indicados, procurar o caminho antigo em todos os READMEs e deixar no lugar antigo um `index.html` de encaminhamento (ver `observatorio-blcs/index.html`).

## Verificações automáticas

| Workflow | Quando corre | O que faz |
| --- | --- | --- |
| `contas-vitoria-sql.yml` | Alterações em `contas-vitoria-sql/` | Reconstrói a base de dados, corre as consultas e os testes |
| `simulador-juros-compostos.yml` | Alterações no simulador | Testa os motores Python e JavaScript e compara-os |
| `verificar-ligacoes.yml` | Alterações em ficheiros `.md` | Confirma que todas as ligações relativas apontam para ficheiros existentes |
