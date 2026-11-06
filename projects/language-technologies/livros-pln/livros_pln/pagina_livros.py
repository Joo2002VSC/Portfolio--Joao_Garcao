"""Página «Livros analisados»: catálogo, pesquisa e filtros, comparação e explorador de indicadores.

A página só apresenta valores já calculados pelo pipeline (os `indicadores.json` de cada livro);
nada é recalculado no navegador. As definições, unidades, limitações e a comparabilidade entre
línguas vêm de `catalogo.py`. Funciona sem JavaScript (o catálogo é HTML estático); com JavaScript,
acrescenta a pesquisa, os filtros, a ordenação, a comparação e o explorador.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from . import catalogo, interativo, qualidade
from .interativo import maiusculas

# Todos os indicadores do catálogo entram na comparação, agrupados pelos temas do catálogo; cada tema
# tem uma nota metodológica.
NOTAS = {
    "Dimensão": "Valores absolutos: dependem da extensão de cada obra e não medem estilo. Versos e estrofes só se "
                "aplicam a textos em verso.",
    "Diversidade lexical": "O MTLD e o HD-D são pouco sensíveis à extensão do texto; o TTR, o vocabulário, os lemas "
                           "distintos e os hápax dependem dela. Todos dependem da tokenização de cada língua.",
    "Densidade e extensão das palavras": "Dependem da morfologia de cada língua (por exemplo, palavras mais longas "
                                         "em português do que em inglês).",
    "Extensão das frases": "A mediana e os percentis descrevem melhor a frase típica do que a média, que é puxada "
                           "pelas frases longas. Em verso, a segmentação em frases é menos fiável.",
    "Complexidade sintática": "Medida na árvore de dependências do modelo de cada língua; não confundir com a "
                              "extensão das frases.",
    "Classes gramaticais": "Frequências relativas (por 1000 palavras), já normalizadas pela extensão; as etiquetas "
                           "vêm do modelo de cada língua.",
    "Legibilidade": "Cada língua usa a sua adaptação da fórmula de Flesch, com escalas diferentes; não se aplica a "
                    "textos em verso.",
    "Pontuação": "Ocorrências por 1000 palavras. Dependem das convenções tipográficas de cada língua e de cada "
                 "edição digital (por exemplo, travessões ou aspas no diálogo).",
    "Discurso e entidades": "O diálogo é detetado pela tipografia; as entidades vêm do reconhecimento automático do "
                            "modelo de cada língua. As contagens de nomes dependem da extensão da obra.",
    "Rede de personagens": "Coocorrência no mesmo parágrafo, não uma relação narrativa comprovada. O número de "
                           "personagens depende do método (dicionário revisto ou reconhecimento automático).",
    "Tipos de frase": "Detetados pela pontuação final de cada frase.",
    "Morfologia verbal e pessoa": "Traços morfológicos (Universal Dependencies) anotados pelo modelo de cada língua; "
                                  "os tempos e os modos não têm a mesma divisão em todas as línguas.",
    "Leis do vocabulário": "Ajustes em escala logarítmica; o R² indica a qualidade do ajuste, não a qualidade do "
                           "texto. O expoente de Heaps depende da extensão e da língua.",
    "Sentimento": "Polaridade do vocabulário (positivo, negativo, neutro), não emoções nem o tom narrativo; "
                  "léxicos diferentes em cada língua, pensados para textos curtos.",
}


def _grupos() -> list[tuple[str, list[str], str]]:
    por_grupo: dict[str, list[str]] = {}
    for k, ind in catalogo.INDICADORES.items():
        por_grupo.setdefault(ind.grupo, []).append(k)
    ordem = list(catalogo.GRUPOS) + [g for g in por_grupo if g not in catalogo.GRUPOS]
    return [(g, por_grupo[g], NOTAS.get(g, "")) for g in ordem if g in por_grupo]


GRUPOS = _grupos()
# Indicadores que mudam com a extensão do texto (fora da «Dimensão», onde isso é evidente): sem barras
# comparativas quando as obras têm extensões muito diferentes.
DEPENDEM_DA_EXTENSAO = {"ttr", "vocabulario", "lemas_distintos", "hapax_pct", "frase_maxima", "entidades_pessoa",
                        "entidades_lugar", "entidades_organizacao", "heaps_k"}
# Eixos do explorador: todos os indicadores do catálogo, pela ordem dos temas
EIXOS = [k for _, ks, _ in GRUPOS for k in ks]
CLASSES_COMPOSICAO = [("NOUN", "Substantivos"), ("VERB", "Verbos"), ("ADJ", "Adjetivos"), ("ADV", "Advérbios"),
                      ("PRON", "Pronomes"), ("PROPN", "Nomes próprios")]
NOMES_LINGUAS = {"pt": "Português", "fr": "Francês", "en": "Inglês"}


def _seculo(ano) -> str | None:
    try:
        a = int(str(ano)[:4])
    except (TypeError, ValueError):
        return None
    romanos = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV",
               "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
    s = (a - 1) // 100 + 1
    return f"Século {romanos[s - 1]}" if 1 <= s <= len(romanos) else None


def _chaves() -> list[str]:
    usadas = [k for _, ks, _ in GRUPOS for k in ks] + EIXOS
    return [k for k in dict.fromkeys(usadas) if k in catalogo.INDICADORES]


def dados(registos: list[dict]) -> dict:
    """Prepara os dados embutidos na página, tal como estão nos indicadores.json (sem recalcular)."""
    chaves = _chaves()
    livros = []
    for r in registos:
        i, e = r["indicadores"], r.get("estados", {})
        livros.append({
            "id": r["id"], "titulo": r.get("titulo") or r["id"], "autor": r.get("autor"),
            "ano": str(r["ano"]) if r.get("ano") else None, "seculo": _seculo(r.get("ano")),
            "lingua": r["lingua"], "idioma": NOMES_LINGUAS.get(r["lingua"], r.get("lingua_nome")),
            "forma": r.get("forma", "prosa"), "fonte": (r.get("metadados") or {}).get("fonte"),
            "atualizado": r["processamento"].get("data"), "versao": r["processamento"].get("versao"),
            "leitura": i.get("legibilidade_leitura"), "escala": i.get("legibilidade_escala"),
            "nivel": i.get("legibilidade_nivel"), "personagem_principal": i.get("personagem_principal"),
            "personagens": (r.get("personagens_principais") or [])[:5],
            "metodo_personagens": r.get("metodo_personagens"), "metodo_sentimento": r.get("metodo_sentimento"),
            "valores": {k: i.get(k) for k in chaves},
            "estados": {k: {"rotulo": qualidade.ROTULOS.get(v.get("estado"), v.get("estado")), "motivo": v.get("motivo")}
                        for k, v in e.items() if k in chaves},
            "classes": {c: i.get(f"pos_{c.lower()}_por_1000") for c, _ in CLASSES_COMPOSICAO},
            "avisos": [a["mensagem"] for a in r.get("qualidade", [])],
            "restrito": bool(r.get("restrito")), "nota_restricao": r.get("nota_restricao"),
        })
    indicadores = {k: {"nome": maiusculas(catalogo.INDICADORES[k].nome), "unidade": catalogo.INDICADORES[k].unidade,
                       "casas": catalogo.INDICADORES[k].casas, "entre_linguas": catalogo.INDICADORES[k].entre_linguas,
                       "definicao": catalogo.INDICADORES[k].definicao,
                       "interpretacao": catalogo.INDICADORES[k].interpretacao,
                       "limitacoes": catalogo.INDICADORES[k].limitacoes,
                       "extensao": k in DEPENDEM_DA_EXTENSAO}
                   for k in chaves}
    return {"livros": livros, "indicadores": indicadores,
            "grupos": [{"nome": maiusculas(g), "chaves": [k for k in ks if k in indicadores], "nota": n}
                       for g, ks, n in GRUPOS],
            "eixos": [k for k in EIXOS if k in indicadores],
            "classes": CLASSES_COMPOSICAO}


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

def _fmt(v, casas: int = 1) -> str:
    return interativo._num(v, casas)


def _valor(livro: dict, k: str) -> str:
    """Valor formatado; os estados não aplicável/desconhecido aparecem com o motivo (atributo title)."""
    est = livro["estados"].get(k)
    if est:
        return (f'<abbr class="na" title="{html.escape(est["motivo"] or "")}">'
                f'{html.escape(est["rotulo"] or "n.a.")}</abbr>')
    v = livro["valores"].get(k)
    if v is None:
        return '<span class="na">—</span>'
    return html.escape(_fmt(v, catalogo.INDICADORES[k].casas))


def _cartao(l: dict) -> str:
    e = html.escape
    leitura = (maiusculas(l["leitura"]) if l["leitura"] else
               f'<abbr class="na" title="{e((l["estados"].get("legibilidade") or {}).get("motivo") or "")}">n.a.</abbr>')
    sent = l["valores"].get("sentimento_medio")
    meta = " · ".join(x for x in [e(l["autor"] or "Autor desconhecido"), e(l["ano"] or "sem data")])
    capa_autor = e((l["autor"] or "").upper())
    url = f'livros/{e(l["id"])}/painel.html'
    if l["restrito"]:
        capa_tag, capa_fim, titulo = '<span class="capa capa-' + e(l["lingua"]) + '" aria-hidden="true">', "</span>", e(l["titulo"])
        abrir = ('<p class="restrito" title="' + e(l["nota_restricao"] or "") + '">Só indicadores: obra protegida '
                 'por direitos de autor</p>')
        secundarias = ""
    else:
        capa_tag, capa_fim = f'<a class="capa capa-{e(l["lingua"])}" href="{url}" tabindex="-1" aria-hidden="true">', "</a>"
        titulo = f'<a href="{url}">{e(l["titulo"])}</a>'
        abrir = f'<a class="abrir" href="{url}">Abrir análise <span aria-hidden="true">→</span></a>'
        secundarias = (f'<p class="secundarias"><a href="livros/{e(l["id"])}/README.md">Relatório</a> · '
                       f'<a href="livros/{e(l["id"])}/{e(l["id"])}.xlsx">Excel</a></p>')
    return f"""<article class="livro" data-id="{e(l['id'])}" data-titulo="{e(l['titulo'].lower())}"
 data-autor="{e((l['autor'] or '').lower())}" data-lingua="{e(l['lingua'])}" data-seculo="{e(l['seculo'] or '')}"
 data-forma="{e(l['forma'])}" data-ano="{e(l['ano'] or '')}" data-palavras="{l['valores'].get('palavras') or 0}"
 data-mtld="{l['valores'].get('mtld') if l['valores'].get('mtld') is not None else ''}"
 data-frase="{l['valores'].get('frase_mediana') if l['valores'].get('frase_mediana') is not None else ''}">
 {capa_tag}
  <span class="capa-autor">{capa_autor}</span><span class="capa-titulo">{e(l['titulo'])}</span>
  <span class="capa-orn">❦</span><span class="capa-ano">{e(l['ano'] or '')}</span>{capa_fim}
 <div class="corpo">
  <p class="etiquetas"><span>{e(l['idioma'])}</span><span>{e(maiusculas(l['forma']))}</span></p>
  <h3>{titulo}</h3>
  <p class="meta">{meta}</p>
  <dl class="resumo-livro">
   <div><dt>Palavras</dt><dd>{_valor(l, 'palavras')}</dd></div>
   <div><dt>Frases</dt><dd>{_valor(l, 'frases')}</dd></div>
   <div><dt title="Diversidade lexical (MTLD)">MTLD</dt><dd>{_valor(l, 'mtld')}</dd></div>
   <div><dt>Frase mediana</dt><dd>{_valor(l, 'frase_mediana')}{' palavras' if l['valores'].get('frase_mediana') is not None else ''}</dd></div>
   <div><dt>Leitura</dt><dd>{leitura}</dd></div>
   <div><dt>Sentimento</dt><dd>{_valor(l, 'sentimento_medio') if sent is not None or 'sentimento_medio' in l['estados'] else '—'}</dd></div>
  </dl>
  <div class="acoes">
   {abrir}
   <label class="comparar"><input type="checkbox" value="{e(l['id'])}"> Comparar</label>
  </div>
  {secundarias}
 </div>
</article>"""


def _opcoes(valores: list[tuple[str, str]]) -> str:
    return "".join(f'<option value="{html.escape(v)}">{html.escape(r)}</option>' for v, r in valores)


def catalogo_html(d: dict) -> str:
    livros = d["livros"]
    linguas = sorted({(l["lingua"], l["idioma"]) for l in livros}, key=lambda x: x[1])
    autores = sorted({l["autor"] for l in livros if l["autor"]})
    seculos = sorted({l["seculo"] for l in livros if l["seculo"]},
                     key=lambda s: int(min((l["ano"] for l in livros if l["seculo"] == s and l["ano"]), default="0")[:4]))
    formas = sorted({l["forma"] for l in livros})
    cartoes = "".join(_cartao(l) for l in sorted(livros, key=lambda l: l["titulo"].lower()))
    return f"""
<form class="filtros" role="search" aria-label="Pesquisar e filtrar livros" onsubmit="return false">
 <div class="campo largo"><label for="f-texto">Pesquisar</label>
  <input id="f-texto" type="search" placeholder="Título ou autor" autocomplete="off"></div>
 <div class="campo"><label for="f-lingua">Língua</label><select id="f-lingua"><option value="">Todas</option>{_opcoes(linguas)}</select></div>
 <div class="campo"><label for="f-autor">Autor</label><select id="f-autor"><option value="">Todos</option>{_opcoes([(a.lower(), a) for a in autores])}</select></div>
 <div class="campo"><label for="f-seculo">Período</label><select id="f-seculo"><option value="">Todos</option>{_opcoes([(s, s) for s in seculos])}</select></div>
 <div class="campo"><label for="f-forma">Forma</label><select id="f-forma"><option value="">Prosa e verso</option>{_opcoes([(f, maiusculas(f)) for f in formas])}</select></div>
 <div class="campo"><label for="f-ordem">Ordenar por</label><select id="f-ordem">
  <option value="titulo">Título (A–Z)</option><option value="autor">Autor (A–Z)</option>
  <option value="ano">Ano de publicação</option><option value="palavras">Número de palavras</option>
  <option value="mtld">Diversidade lexical (MTLD)</option><option value="frase">Extensão mediana das frases</option></select></div>
 <button type="button" id="f-limpar" class="limpar">Limpar filtros</button>
</form>
<p class="contagem" id="f-contagem" aria-live="polite">{len(livros)} livros</p>
<p class="aviso-ordem" id="f-aviso" hidden></p>
<div class="catalogo" id="lista-livros">{cartoes}</div>
<p class="vazio" id="f-vazio" hidden>Nenhum livro corresponde aos filtros. <button type="button" class="limpar" data-limpar>Limpar filtros</button></p>
"""


def comparacao_html(d: dict) -> str:
    temas = "".join(f'<button type="button" class="tema" aria-pressed="true" data-grupo="{i}">'
                    f'{html.escape(g["nome"])} <small>{len(g["chaves"])}</small></button>'
                    for i, g in enumerate(d["grupos"]))
    total = sum(len(g["chaves"]) for g in d["grupos"])
    return f"""
<p class="instrucao" id="c-instrucao">Selecione dois ou mais livros no catálogo («Comparar») para os ver lado a lado.
Por omissão, comparam-se todos os livros visíveis.</p>
<div class="temas" role="group" aria-label="Temas apresentados na comparação">
 <span class="rotulo-temas">Temas</span>{temas}
 <button type="button" class="tema-todos" data-temas="todos">Todos</button>
 <button type="button" class="tema-todos" data-temas="nenhum">Nenhum</button>
</div>
<label class="so-comparaveis"><input type="checkbox" id="c-comparaveis"> Mostrar só os indicadores comparáveis entre
os livros selecionados</label>
<p class="contagem" id="c-contagem" aria-live="polite">{total} indicadores em {len(d["grupos"])} temas.</p>
<div class="comparacao" id="tabela-comparacao" aria-live="polite"></div>
"""


def explorador_html(d: dict, offline: bool) -> str:
    opcoes = "".join(
        f'<optgroup label="{html.escape(g["nome"])}">'
        + _opcoes([(k, d["indicadores"][k]["nome"]) for k in g["chaves"] if k in d["eixos"]]) + "</optgroup>"
        for g in d["grupos"])
    if offline:
        from plotly.offline import get_plotlyjs
        script = f"<script>{get_plotlyjs()}</script>"
    else:
        from plotly.offline import get_plotlyjs_version
        script = f'<script src="https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js" charset="utf-8"></script>'
    return f"""
<div class="filtros eixos" aria-label="Escolher os eixos">
 <div class="campo"><label for="e-x">Eixo horizontal</label><select id="e-x">{opcoes}</select></div>
 <div class="campo"><label for="e-y">Eixo vertical</label><select id="e-y">{opcoes}</select></div>
</div>
<p class="aviso-ordem" id="e-aviso" hidden></p>
<figure class="figura explorador"><div id="grafico-explorador" style="height:520px" role="img"
 aria-label="Gráfico de dispersão dos livros visíveis segundo os dois indicadores escolhidos"></div>
<p class="nota">Cada ponto é um livro visível no catálogo (os filtros aplicam-se aqui). Cor e forma indicam a língua.
Valores exatos ao passar o rato.</p></figure>
{script}
"""


def glossario_html(d: dict) -> str:
    blocos = []
    for g in d["grupos"]:
        itens = "".join(
            f'<details><summary>{html.escape(d["indicadores"][k]["nome"])}'
            f'<span class="unid">{html.escape(d["indicadores"][k]["unidade"])}</span></summary>'
            f'<p><b>O que mede.</b> {html.escape(d["indicadores"][k]["definicao"])}</p>'
            f'<p><b>Como ler.</b> {html.escape(d["indicadores"][k]["interpretacao"])}</p>'
            + (f'<p><b>Limitações.</b> {html.escape(d["indicadores"][k]["limitacoes"])}</p>'
               if d["indicadores"][k]["limitacoes"] else "")
            + f'<p class="comp-ling">{"Comparável entre línguas." if d["indicadores"][k]["entre_linguas"] else "Não comparável entre línguas: compare só obras na mesma língua."}</p>'
            "</details>" for k in g["chaves"])
        blocos.append(f'<div class="grupo-gloss"><h3>{html.escape(g["nome"])}</h3><p class="nota-grupo">'
                      f'{html.escape(g["nota"])}</p>{itens}</div>')
    return '<div class="glossario">' + "".join(blocos) + "</div>"


def dados_html(repositorio: str) -> str:
    return f"""
<ul class="downloads">
 <li><a href="indicadores.csv">Indicadores de todos os livros (CSV)</a><span>uma linha por livro, uma coluna por indicador</span></li>
 <li><a href="indicadores.xlsx">Indicadores de todos os livros (Excel)</a><span>inclui o dicionário de indicadores</span></li>
 <li><a href="README.md">Relatório do corpus</a><span>comparações por língua, Delta de Burrows e correlações quando há livros suficientes</span></li>
 <li><a href="{repositorio}/docs/indicadores.md">Documentação dos indicadores</a><span>fórmulas, unidades, limitações e referências bibliográficas</span></li>
</ul>
"""


JS = r"""
(()=>{
const D=JSON.parse(document.getElementById("dados-livros").textContent);
const L=Object.fromEntries(D.livros.map(l=>[l.id,l])), I=D.indicadores;
// formato português igual ao dos relatórios: espaço nos milhares (também com 4 algarismos), vírgula decimal, sinal −
const nf=(v,c)=>{if(v==null||Number.isNaN(v))return"—";const [i,d]=Math.abs(v).toFixed(c).split(".");
  return (v<0&&Number(Math.abs(v).toFixed(c))!==0?"−":"")+i.replace(/\B(?=(\d{3})+(?!\d))/g," ")+(d?","+d:"");};
const $=s=>document.querySelector(s), cat=$("#lista-livros"), cartoes=[...cat.querySelectorAll(".livro")];
const f={texto:$("#f-texto"),lingua:$("#f-lingua"),autor:$("#f-autor"),seculo:$("#f-seculo"),forma:$("#f-forma"),ordem:$("#f-ordem")};
const sem=s=>(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
function visiveis(){return cartoes.filter(c=>!c.hidden).map(c=>L[c.dataset.id]);}
function aplicar(){
  const t=sem(f.texto.value.trim());
  cartoes.forEach(c=>{const ok=(!t||sem(c.dataset.titulo).includes(t)||sem(c.dataset.autor).includes(t))
    &&(!f.lingua.value||c.dataset.lingua===f.lingua.value)&&(!f.autor.value||c.dataset.autor===f.autor.value)
    &&(!f.seculo.value||c.dataset.seculo===f.seculo.value)&&(!f.forma.value||c.dataset.forma===f.forma.value);c.hidden=!ok;});
  const o=f.ordem.value, num=(c,k)=>c.dataset[k]===""?null:parseFloat(c.dataset[k]);
  const cmp={titulo:(a,b)=>a.dataset.titulo.localeCompare(b.dataset.titulo,"pt"),autor:(a,b)=>a.dataset.autor.localeCompare(b.dataset.autor,"pt"),
    ano:(a,b)=>(num(a,"ano")??9999)-(num(b,"ano")??9999),palavras:(a,b)=>num(b,"palavras")-num(a,"palavras"),
    mtld:(a,b)=>(num(b,"mtld")??-1)-(num(a,"mtld")??-1),frase:(a,b)=>(num(b,"frase")??-1)-(num(a,"frase")??-1)}[o];
  cartoes.slice().sort(cmp).forEach(c=>cat.appendChild(c));
  const n=visiveis().length; $("#f-contagem").textContent=n===1?"1 livro encontrado":`${n} livros encontrados`;
  $("#f-vazio").hidden=n>0;
  const langs=new Set(visiveis().map(l=>l.lingua)), av=$("#f-aviso");
  if((o==="mtld"||o==="frase")&&langs.size>1){av.hidden=false;av.textContent=o==="mtld"?"Atenção: o MTLD depende da língua; a ordenação só é comparável entre livros da mesma língua.":"Atenção: a extensão das frases depende da língua e da pontuação de cada edição; compare com cautela livros em línguas diferentes.";}else av.hidden=true;
  comparar(); explorar();
}
function limpar(){f.texto.value="";["lingua","autor","seculo","forma"].forEach(k=>f[k].value="");f.ordem.value="titulo";
  document.querySelectorAll(".comparar input").forEach(i=>i.checked=false);aplicar();}
Object.values(f).forEach(el=>el.addEventListener(el.tagName==="INPUT"?"input":"change",aplicar));
document.querySelectorAll("#f-limpar,[data-limpar]").forEach(b=>b.addEventListener("click",limpar));
document.querySelectorAll(".comparar input").forEach(i=>i.addEventListener("change",comparar));

function celula(l,k){const e=l.estados[k];if(e)return `<abbr class="na" title="${e.motivo||""}">${e.rotulo}</abbr>`;
  const v=l.valores[k];return v==null?'<span class="na">—</span>':nf(v,I[k].casas);}
const TEMAS=new Set(D.grupos.map((_,i)=>i));
const texto=(nome,unid,f)=>`<tr class="sub"><th scope="row"><span class="nome">${nome}</span>${unid?`<small>${unid}</small>`:""}</th>`+
  SEL.map(l=>{const v=f(l);return `<td>${v?esc(v):'<span class="na">—</span>'}</td>`;}).join("")+"</tr>";
const esc=t=>String(t).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let SEL=[];
function comparar(){
  const marcados=[...document.querySelectorAll(".comparar input:checked")].map(i=>L[i.value]);
  const sel=marcados.length>=2?marcados:visiveis(), alvo=$("#tabela-comparacao");
  $("#c-instrucao").textContent=marcados.length>=2?`A comparar os ${sel.length} livros selecionados.`:
    (marcados.length===1?"Selecione pelo menos mais um livro para comparar. Por agora, comparam-se todos os livros visíveis.":"Selecione dois ou mais livros no catálogo («Comparar») para os ver lado a lado. Por omissão, comparam-se todos os livros visíveis.");
  SEL=sel;
  if(sel.length<1){alvo.innerHTML="";return;}
  const langs=new Set(sel.map(l=>l.lingua)), formas=new Set(sel.map(l=>l.forma));
  const pal=sel.map(l=>l.valores.palavras).filter(v=>v), razao=pal.length?Math.max(...pal)/Math.min(...pal):1;
  let h=`<div class="tabela comp"><table><caption class="sr">Comparação de indicadores entre os livros selecionados</caption><thead><tr><th scope="col">Indicador</th>`+
    sel.map(l=>`<th scope="col">${l.restrito?l.titulo:`<a href="livros/${l.id}/painel.html">${l.titulo}</a>`}<small>${l.idioma} · ${l.forma}${l.restrito?" · só indicadores":""}</small></th>`).join("")+"</tr></thead>";
  const incomparavel=k=>{const ind=I[k];
    if(!ind.entre_linguas&&langs.size>1)return "Não comparável entre línguas";
    if(ind.extensao&&razao>2)return "Depende da extensão do texto";
    return "";};
  const soComp=$("#c-comparaveis").checked;
  let nInd=0,nTemas=0;
  for(const [gi,g] of D.grupos.entries()){
    if(!TEMAS.has(gi))continue;
    const ks=g.chaves.filter(k=>sel.some(l=>l.valores[k]!=null||l.estados[k])&&!(soComp&&incomparavel(k)));
    if(!ks.length)continue;
    nInd+=ks.length;nTemas++;
    h+=`<tbody><tr class="grupo"><th colspan="${sel.length+1}" scope="rowgroup">${g.nome}<span>${g.nota}</span></th></tr>`;
    for(const k of ks){
      const ind=I[k], vals=sel.map(l=>l.estados[k]?null:l.valores[k]);
      const aviso=incomparavel(k);
      const nums=vals.filter(v=>v!=null), max=nums.length?Math.max(...nums.map(Math.abs)):0, neg=nums.some(v=>v<0);
      h+=`<tr${aviso?' class="incomparavel"':""}><th scope="row"><span class="nome" title="${ind.definicao.replace(/"/g,"&quot;")}">${ind.nome}</span><small>${ind.unidade}</small>${aviso?`<em>⚠ ${aviso}</em>`:""}</th>`;
      sel.forEach((l,j)=>{const v=vals[j];let barra="";
        if(!aviso&&v!=null&&max>0&&sel.length>1){const w=Math.abs(v)/max*100;
          barra=neg?`<span class="barra-v div"><i style="${v<0?"right:50%":"left:50%"};width:${w/2}%"></i></span>`:`<span class="barra-v"><i style="width:${w}%"></i></span>`;}
        h+=`<td>${celula(l,k)}${barra}</td>`;});
      h+="</tr>";
      if(k==="legibilidade"){h+=`<tr class="sub"><th scope="row"><span class="nome">Classificação da leitura</span></th>`+sel.map(l=>`<td>${l.leitura?l.leitura[0].toUpperCase()+l.leitura.slice(1)+(l.escala?` <small>(${l.escala})</small>`:""):'<span class="na">—</span>'}</td>`).join("")+"</tr>";}
      if(k==="personagens_na_rede"){
        h+=texto("Personagem mais central","PageRank",l=>l.personagem_principal);
        h+=texto("Personagens principais","as cinco com maior PageRank",l=>l.personagens.length?l.personagens.join(", "):null);
        h+=texto("Método de identificação","",l=>l.metodo_personagens);}
      if(k==="sentimento_medio")h+=texto("Método de sentimento","léxico e versão",l=>l.metodo_sentimento);
    }
    if(g.chaves[0]==="pos_noun_por_1000"){
      h+=`<tr class="sub"><th scope="row"><span class="nome">Composição</span><small>% das palavras</small></th>`+sel.map(l=>{
        let x=0;const partes=D.classes.map(([c,n],j)=>{const v=l.classes[c];if(v==null)return"";const w=v/10;x+=w;
          return `<i class="c${j}" style="width:${w}%" title="${n}: ${nf(w,1)} %"></i>`;}).join("");
        return `<td><span class="composicao" role="img" aria-label="Composição por classes gramaticais">${partes}<i class="resto" style="width:${Math.max(0,100-x)}%" title="Outras classes: ${nf(Math.max(0,100-x),1)} %"></i></span></td>`;}).join("")+"</tr>";
    }
    h+="</tbody>";
  }
  h+="</table></div>";
  $("#c-contagem").textContent=nInd?`${nInd} ${nInd===1?"indicador":"indicadores"} em ${nTemas} ${nTemas===1?"tema":"temas"}.`:"Nenhum indicador para mostrar: escolha pelo menos um tema.";
  if(!nInd)h="";
  h+=`<ul class="legenda-comp">`+D.classes.map(([c,n],j)=>`<li><i class="c${j}"></i>${n}</li>`).join("")+`<li><i class="resto"></i>Outras classes</li></ul>`;
  const notas=[];
  if(langs.size>1)notas.push("Os livros selecionados estão em línguas diferentes: os indicadores marcados com ⚠ dependem da língua (modelos, léxicos ou fórmulas diferentes) e não se comparam diretamente; as barras foram omitidas nessas linhas.");
  if(formas.size>1)notas.push("A seleção junta prosa e verso: a legibilidade e o diálogo não se aplicam ao verso, e a extensão das frases depende da forma.");
  if(razao>2)notas.push(`O livro mais extenso tem ${nf(razao,1)} vezes mais palavras do que o mais curto: prefira os indicadores normalizados (por 1000 palavras, percentagens, MTLD, HD-D) aos valores absolutos.`);
  if(notas.length)h=`<div class="notas-comp">${notas.map(n=>`<p>${n}</p>`).join("")}</div>`+h;
  alvo.innerHTML=h;
}
const CORES={pt:"#7A4E2D",en:"#B8893E",fr:"#1E1915"}, SIMB={pt:"circle",en:"diamond",fr:"square"};
function explorar(){
  if(!window.Plotly)return;
  const x=$("#e-x").value,y=$("#e-y").value, vis=visiveis(), langs=[...new Set(vis.map(l=>l.lingua))];
  const traces=langs.map(lg=>{const ls=vis.filter(l=>l.lingua===lg&&l.valores[x]!=null&&l.valores[y]!=null&&!l.estados[x]&&!l.estados[y]);
    return {type:"scatter",mode:"markers+text",name:ls[0]?.idioma||lg,x:ls.map(l=>l.valores[x]),y:ls.map(l=>l.valores[y]),
      text:ls.map(l=>l.titulo),textposition:"top center",textfont:{family:"Source Sans 3, Arial",size:13,color:"#1E1915"},
      marker:{size:16,color:CORES[lg]||"#6E5E4E",symbol:SIMB[lg]||"circle",line:{color:"#F4EEE3",width:2}},
      hovertemplate:`<b>%{text}</b><br>${I[x].nome}: %{x}<br>${I[y].nome}: %{y}<extra>${ls[0]?.idioma||""}</extra>`};});
  const pts=traces.flatMap(t=>t.x.map((v,i)=>[v,t.y[i]]));
  const faixa=j=>{const v=pts.map(p=>p[j]);if(!v.length)return undefined;let a=Math.min(...v),b=Math.max(...v);
    const m=(b-a)*0.18||Math.abs(a)*0.1||1;return [a-m,b+m];};   // margem para os rótulos não ficarem cortados
  const ax=(k,j)=>({range:faixa(j),title:{text:`${I[k].nome} (${I[k].unidade})`,font:{size:13,color:"#6E5E4E"}},gridcolor:"#E2D6C2",zeroline:false,tickfont:{color:"#6E5E4E"}});
  Plotly.react("grafico-explorador",traces,{paper_bgcolor:"#F4EEE3",plot_bgcolor:"#F4EEE3",font:{family:"Source Sans 3, Arial",color:"#1E1915"},
    margin:{l:70,r:20,t:20,b:60},xaxis:ax(x,0),yaxis:ax(y,1),legend:{orientation:"h",y:-0.18},separators:", ",
    hoverlabel:{bgcolor:"#1E1915",font:{color:"#F3EADB"}}},{displaylogo:false,responsive:true});
  const av=$("#e-aviso"), inc=[x,y].filter(k=>!I[k].entre_linguas).map(k=>I[k].nome);
  const falta=vis.filter(l=>l.estados[x]||l.estados[y]||l.valores[x]==null||l.valores[y]==null).map(l=>l.titulo);
  const msg=[];
  if(langs.length>1&&inc.length)msg.push(`${inc.join(" e ")} ${inc.length>1?"não são comparáveis":"não é comparável"} entre línguas: compare apenas pontos da mesma cor.`);
  if(falta.length)msg.push(`Sem valor para: ${falta.join(", ")} (não aplicável ou desconhecido).`);
  av.hidden=!msg.length;av.textContent=msg.join(" ");
}
document.querySelectorAll(".tema").forEach(b=>b.addEventListener("click",()=>{const i=+b.dataset.grupo;
  TEMAS.has(i)?TEMAS.delete(i):TEMAS.add(i);b.setAttribute("aria-pressed",TEMAS.has(i));comparar();}));
document.querySelectorAll(".tema-todos").forEach(b=>b.addEventListener("click",()=>{const todos=b.dataset.temas==="todos";
  document.querySelectorAll(".tema").forEach(t=>{const i=+t.dataset.grupo;todos?TEMAS.add(i):TEMAS.delete(i);t.setAttribute("aria-pressed",todos);});comparar();}));
$("#c-comparaveis").addEventListener("change",comparar);
$("#e-x").value="frase_mediana";$("#e-y").value="mtld";
["#e-x","#e-y"].forEach(s=>$(s).addEventListener("change",explorar));
aplicar();
})();
"""

CSS = """
.restrito{font-family:var(--ui);font-size:14px;color:var(--suave);margin:0;padding:8px 0;border-top:1px dashed var(--linha)}
.temas{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:6px 0 14px}
.rotulo-temas{font-family:var(--ui);font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--suave);margin-right:4px}
.tema,.tema-todos{font-family:var(--ui);font-size:14px;padding:6px 11px;border:1px solid var(--linha);background:transparent;color:var(--suave);cursor:pointer;border-radius:2px}
.tema small{font-size:11.5px;opacity:.75;margin-left:2px}
.tema[aria-pressed="true"]{background:#1E1915;border-color:#1E1915;color:#F4EEE3}
.tema:hover,.tema-todos:hover{border-color:#7A4E2D}
.tema:focus-visible,.tema-todos:focus-visible,.so-comparaveis input:focus-visible{outline:2px solid #B8893E;outline-offset:2px}
.tema-todos{text-decoration:underline;text-underline-offset:3px;border-color:transparent}
.so-comparaveis{display:flex;gap:8px;align-items:center;font-family:var(--ui);font-size:15px;margin:0 0 8px;cursor:pointer}
.so-comparaveis input{width:17px;height:17px;accent-color:#7A4E2D}

.introducao{max-width:820px;font-size:18px;color:var(--suave);margin:36px 0 0}
.filtros{display:flex;flex-wrap:wrap;gap:14px 18px;align-items:flex-end;margin:28px 0 0;padding:18px 0;
border-top:2px solid var(--tinta);border-bottom:1px solid var(--linha)}
.campo{display:flex;flex-direction:column;gap:6px;min-width:150px}
.campo.largo{flex:1 1 240px}
.campo label{font-family:var(--ui);font-size:12.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--suave)}
.campo input,.campo select{font-family:var(--ui);font-size:15px;color:var(--tinta);background:var(--cartao,#FBF8F2);
border:1px solid var(--linha);border-radius:2px;padding:9px 10px;min-height:42px}
.campo input:focus,.campo select:focus,.limpar:focus-visible,.comparar input:focus-visible,.abrir:focus-visible{outline:2px solid var(--ocre);outline-offset:2px}
.limpar{font-family:var(--ui);font-size:14px;font-weight:600;background:transparent;color:var(--tinta);
border:1px solid var(--tinta);padding:10px 16px;min-height:42px;cursor:pointer}
.limpar:hover{background:var(--tinta);color:var(--creme)}
.contagem{font-family:var(--ui);font-size:14px;color:var(--suave);margin:14px 0 0}
.aviso-ordem{font-family:var(--ui);font-size:13.5px;color:var(--castanho);border-left:3px solid var(--ocre);padding-left:12px;margin:10px 0 0}
.catalogo{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:28px;margin:22px 0 0}
.livro{display:grid;grid-template-rows:auto 1fr;min-width:0;background:#FBF8F2;border:1px solid var(--linha)}
.resumo-livro dd{overflow-wrap:anywhere}
.livro[hidden]{display:none}
.capa{position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:8px;
aspect-ratio:16/9;padding:22px;text-align:center;text-decoration:none;color:var(--creme);background:var(--tinta);border:0}
.capa:after{content:"";position:absolute;inset:10px;border:1px solid rgba(184,137,62,.55);pointer-events:none}
.capa-pt{background:#2A1F18}.capa-en{background:#1E1915}.capa-fr{background:#2B2620}
.capa-autor{font-family:var(--ui);font-size:11.5px;letter-spacing:.18em;color:var(--areia)}
.capa-titulo{font-family:var(--display);font-weight:700;font-size:28px;line-height:1.05;color:var(--creme);
display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.capa-orn{color:var(--ocre);font-size:15px}.capa-ano{font-family:var(--display);font-style:italic;font-size:17px;color:var(--ocre)}
.livro .corpo{display:flex;flex-direction:column;padding:18px 20px 16px}
.etiquetas{display:flex;gap:8px;margin:0 0 8px}
.etiquetas span{font-family:var(--ui);font-size:12px;font-weight:600;color:var(--castanho);border:1px solid var(--linha);padding:2px 8px}
.livro h3{font-family:var(--display);font-weight:700;font-size:27px;line-height:1.1;margin:0}
.livro h3 a{color:var(--tinta);border:0}.livro h3 a:hover{color:var(--castanho)}
.livro .meta{font-family:var(--display);font-style:italic;font-size:18px;color:var(--castanho);margin:4px 0 12px}
.resumo-livro{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:14px;margin:0 0 14px;border-top:1px solid var(--linha)}
.resumo-livro div{padding:9px 0;border-bottom:1px solid var(--linha)}
.resumo-livro dt{font-family:var(--ui);font-size:11.5px;color:var(--suave);letter-spacing:.03em}
.resumo-livro dd{margin:2px 0 0;font-family:var(--display);font-weight:700;font-size:21px;font-variant-numeric:lining-nums tabular-nums}
abbr.na,span.na{font-family:var(--ui);font-size:13px;font-weight:600;color:var(--suave);text-decoration:underline dotted;cursor:help}
span.na{text-decoration:none;cursor:default}
.acoes{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:auto}
.abrir{font-family:var(--ui);font-size:14.5px;font-weight:700;color:var(--creme);background:var(--tinta);
padding:10px 16px;border:0}
.abrir:hover{background:var(--castanho);color:#fff}
.comparar{font-family:var(--ui);font-size:14px;color:var(--tinta);display:flex;align-items:center;gap:6px;cursor:pointer}
.comparar input{width:18px;height:18px;accent-color:#7A4E2D}
.secundarias{font-family:var(--ui);font-size:13px;color:var(--suave);margin:12px 0 0}
.vazio{font-family:var(--ui);font-size:16px;padding:28px;border:1px dashed var(--linha);text-align:center;margin-top:22px}
.instrucao{font-family:var(--ui);font-size:15px;color:var(--suave);margin:20px 0 0}
.notas-comp{margin:18px 0 0;border-left:3px solid var(--ocre);padding:4px 0 4px 16px;font-family:var(--ui);font-size:14px;color:var(--castanho)}
.notas-comp p{margin:4px 0}
.comp{overflow-x:auto;margin:18px 0 0}
.comp table{min-width:640px;table-layout:fixed}
.comp thead th:first-child{width:30%}
.comp tbody th[scope=row],.comp tbody td{border-bottom:1px solid var(--linha)}
.comp thead th{vertical-align:bottom;font-size:13px;text-transform:none;letter-spacing:0}
.comp thead th a{font-family:var(--display);font-size:21px;font-weight:700;color:var(--tinta);border:0;display:block}
.comp thead th small{display:block;font-weight:400;color:var(--suave);font-size:12.5px}
.comp tr.grupo th{background:var(--papel2,#EDE4D3);font-family:var(--display);font-size:20px;font-weight:700;color:var(--tinta);
padding:12px;letter-spacing:0;text-transform:none}
.comp tr.grupo th span{display:block;font-family:var(--ui);font-size:12.5px;font-weight:400;color:var(--suave);margin-top:2px}
.comp tbody th[scope=row]{font-weight:600;color:var(--tinta);text-transform:none;letter-spacing:0;font-size:14px}
.comp tbody th small{display:block;font-weight:400;color:var(--suave);font-size:12px}
.comp tbody th em{display:block;font-style:normal;font-size:12px;color:var(--castanho);margin-top:3px}
.comp td{font-variant-numeric:tabular-nums;font-size:15px}
.comp .nome{cursor:help;border-bottom:1px dotted var(--linha)}
.barra-v{display:block;position:relative;height:6px;background:#EDE4D3;margin-top:6px}
.barra-v i{position:absolute;left:0;top:0;bottom:0;background:var(--castanho)}
.barra-v.div:before{content:"";position:absolute;left:50%;top:-2px;bottom:-2px;width:1px;background:var(--suave)}
.incomparavel td{color:var(--suave)}
.composicao{display:flex;height:18px;border:1px solid var(--linha);min-width:140px}
.composicao i,.legenda-comp i{display:block;height:100%}
.c0{background:#7A4E2D}.c1{background:#1E1915}.c2{background:#B8893E}.c3{background:#8A8466}.c4{background:#A0583A}.c5{background:#D9C7A3}
.resto{background:repeating-linear-gradient(45deg,#EDE4D3 0 4px,#F4EEE3 4px 8px)}
.legenda-comp{display:flex;flex-wrap:wrap;gap:6px 18px;list-style:none;padding:0;margin:12px 0 0;font-family:var(--ui);font-size:13px;color:var(--suave)}
.legenda-comp li{display:flex;align-items:center;gap:6px}.legenda-comp i{width:14px;height:14px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.glossario{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px 40px;margin:20px 0 0}
.grupo-gloss h3{font-family:var(--display);font-weight:700;font-size:23px;margin:14px 0 2px}
.nota-grupo{font-family:var(--ui);font-size:13px;color:var(--suave);margin:0 0 6px}
.glossario details{border-bottom:1px solid var(--linha);padding:8px 0}
.glossario summary{cursor:pointer;font-family:var(--ui);font-size:15px;font-weight:600;display:flex;justify-content:space-between;gap:12px}
.glossario summary .unid{font-weight:400;color:var(--suave);font-size:13px;text-align:right}
.glossario details p{font-size:15px;margin:8px 0}.glossario .comp-ling{font-family:var(--ui);font-size:13px;color:var(--castanho);overflow:visible}
.downloads{list-style:none;padding:0;margin:20px 0 0;border-top:2px solid var(--tinta)}
.downloads li{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 20px;padding:14px 0;border-bottom:1px solid var(--linha)}
.downloads a{font-family:var(--display);font-weight:700;font-size:20px}
.downloads span{font-family:var(--ui);font-size:14px;color:var(--suave)}
#resumo .numero b{font-size:clamp(40px,4.8vw,62px)}
@media(max-width:640px){.campo{min-width:calc(50% - 9px)}.campo.largo{min-width:100%}.limpar{width:100%}
.catalogo{grid-template-columns:minmax(0,1fr)}.resumo-livro{grid-template-columns:1fr 1fr}.resumo-livro dd{font-size:19px}.glossario{grid-template-columns:1fr}}
"""

SECCOES = {
    "catalogo": ("Catálogo", "Os livros analisados, com os metadados principais e um resumo dos indicadores. Pesquise, "
                             "filtre e ordene; abra a análise detalhada de cada obra ou escolha livros para comparar."),
    "comparacao": ("Comparar livros", "Todos os indicadores da análise individual de cada livro, lado a lado e "
                                      "organizados por tema. Cada linha indica a unidade e se o indicador é comparável "
                                      "entre línguas; passe o rato pelo nome para ver a definição. Escolha os temas a "
                                      "mostrar ou fique só com os indicadores comparáveis."),
    "explorador": ("Explorar indicadores", "Escolha dois indicadores para ver como os livros se posicionam. Útil para "
                                           "perguntas como «as obras com frases mais longas têm vocabulário mais "
                                           "variado?», sempre dentro da mesma língua."),
    "metodo": ("Como ler os indicadores", "O que mede cada indicador, como se interpreta e quais são os seus limites. "
                                          "As definições são as mesmas dos relatórios e da documentação do projeto."),
    "dados": ("Dados e relatórios", "Os valores apresentados nesta página vêm destes ficheiros, gerados pelo "
                                    "livros-pln; nenhum valor é recalculado no navegador."),
}


MESES = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]


def _data(texto: str) -> str:
    """«2026-11-06 11:57 UTC» → «6 nov. 2026»."""
    try:
        a, m, d = texto[:10].split("-")
        return f"{int(d)} {MESES[int(m) - 1]} {a}"
    except (ValueError, IndexError):
        return "—"


def escrever(registos: list[dict], destino: Path, offline: bool = False):
    if not registos:
        return
    d = dados(registos)
    livros = d["livros"]
    anos = sorted(int(l["ano"][:4]) for l in livros if l["ano"] and l["ano"][:4].isdigit())
    autores = {l["autor"] for l in livros if l["autor"]}
    linguas = sorted({l["idioma"] for l in livros})
    atualizado = max((l["atualizado"] or "" for l in livros), default="")
    palavras = sum(l["valores"].get("palavras") or 0 for l in livros)
    periodo = f"{anos[0]}–{anos[-1]}" if len(anos) > 1 else (str(anos[0]) if anos else "—")
    numeros = [(str(len(livros)), "", "livros analisados"), (str(len(autores)), "", "autores"),
               (str(len(linguas)), "", "línguas: " + ", ".join(linguas).lower()),
               (_fmt(palavras, 0), "", "palavras analisadas"), (periodo, "", "período de publicação"),
               (_data(atualizado), "", "última atualização")]
    resumo = ('<p class="introducao">Esta página reúne os livros analisados pelo Livros-PLN. Cada obra tem uma análise '
              "detalhada (vocabulário, frases, gramática, legibilidade, sentimento, personagens e evolução ao longo do "
              "texto); aqui é possível encontrá-las, compará-las e perceber o que significam os indicadores. Os números "
              "descrevem o texto, não substituem a leitura.</p>")
    dados_json = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    extras = {
        "catalogo": catalogo_html(d),
        "comparacao": comparacao_html(d),
        "explorador": explorador_html(d, offline),
        "metodo": glossario_html(d),
        "dados": dados_html(interativo.FICHEIROS)
                 + f'<script type="application/json" id="dados-livros">{dados_json}</script><script>{JS}</script>',
    }
    rodape = dict(descricao=interativo.DESCRICAO, autoria=interativo.AUTORIA,
                  aviso="Indicadores dependentes da língua só se comparam entre obras na mesma língua.",
                  ligacoes=[("Relatório do Corpus", "README.md"), ("Dados em Excel", "indicadores.xlsx"),
                            ("Documentação dos Indicadores", f"{interativo.FICHEIROS}/docs/indicadores.md"),
                            ("Repositório no GitHub", interativo.REPOSITORIO)],
                  tecnico=[("Livros", str(len(livros))), ("Versão", max(l["versao"] or "" for l in livros)),
                           ("Atualizado em", atualizado or "—")])
    interativo.pagina("Livros Analisados", "", numeros, [], resumo, rodape, offline, destino,
                      antetitulo="Biblioteca Livros-PLN",
                      dados_rosto=[("Livros", str(len(livros))), ("Autores", str(len(autores))), ("Período", periodo)],
                      seccoes=SECCOES, extras=extras, css_extra=CSS)
