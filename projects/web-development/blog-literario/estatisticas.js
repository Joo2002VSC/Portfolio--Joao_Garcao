/* =========================================================
   EM NÚMEROS — gráficos a partir de assets/dados/estatisticas.js
   (gerado pelas consultas SQL em analise-sql/sql/03_blog.sql)
========================================================= */
(function () {
    const D = window.ESTATISTICAS;
    if (!D) return;

    const NS = "http://www.w3.org/2000/svg";
    const fmt = (n, dec = 0) => Number(n).toLocaleString("pt-PT", { minimumFractionDigits: dec, maximumFractionDigits: dec });
    const MESES_LONGOS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
                          "setembro", "outubro", "novembro", "dezembro"];
    const reduzMov = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const $ = id => document.getElementById(id);
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

    /* ---------- textos ---------- */
    const R = D.resumo;
    const [a, m, d] = D.gerado_em.split("-").map(Number);
    const ritmo = R.lidos_ano_atual / D.mes;
    const diff = R.lidos_ano_atual - R.lidos_ano_anterior;
    const comNota = D.notas.reduce((s, n) => s + n.livros, 0);
    const textos = {
        data: `${d} de ${MESES_LONGOS[m - 1]} de ${a}`,
        livros: fmt(R.livros_lidos),
        paginas: fmt(R.paginas),
        autores: fmt(R.autores),
        nota: fmt(R.nota_media, 2),
        ano: D.ano,
        ano_livros: R.lidos_ano_atual,
        ano_paginas: fmt(R.paginas_ano_atual),
        ano_ritmo: fmt(ritmo, 1),
        vs_anterior: diff > 0 ? `+${diff} do que em ${D.ano - 1} inteiro`
                   : diff === 0 ? `tantos como em ${D.ano - 1}`
                   : `${-diff} abaixo de ${D.ano - 1}`,
        com_nota: comNota,
        pilha: fmt(D.pilha.livros),
        pilha_anos: fmt(D.pilha.anos, 1).replace(",0", ""),
        pilha_ritmo: fmt(D.pilha.ritmo_mes, 1)
    };
    document.querySelectorAll("[data-k]").forEach(el => {
        if (el.dataset.k in textos) el.textContent = textos[el.dataset.k];
    });

    /* ---------- tooltip partilhado ---------- */
    const tip = $("grTip");
    function mostrarTip(html, ev) {
        tip.innerHTML = html;
        tip.hidden = false;
        const r = tip.getBoundingClientRect();
        let x = ev.clientX + 14, y = ev.clientY + 14;
        if (x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - 14;
        if (y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - 14;
        tip.style.left = x + "px";
        tip.style.top = y + "px";
    }
    const esconderTip = () => { tip.hidden = true; };

    /* ---------- utilitários ---------- */
    function el(tag, attrs = {}, parent) {
        const n = document.createElementNS(NS, tag);
        for (const k in attrs) n.setAttribute(k, attrs[k]);
        if (parent) parent.appendChild(n);
        return n;
    }
    function niceMax(v) {
        const passos = [1, 2, 5, 10, 20, 25, 50, 100];
        for (const p of passos) { if (v / p <= 5) return Math.ceil(v / p) * p; }
        return Math.ceil(v / 100) * 100;
    }
    function tabela(id, cab, linhas) {
        $(id).innerHTML = `<table><thead><tr>${cab.map(c => `<th>${c}</th>`).join("")}</tr></thead><tbody>` +
            linhas.map(l => `<tr>${l.map(c => `<td>${c}</td>`).join("")}</tr>`).join("") + "</tbody></table>";
    }
    // coluna com topo arredondado (4px) e base reta
    function colPath(x, y, w, h, r = 4) {
        r = Math.min(r, w / 2, h);
        return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
    }

    /* ---------- gráfico de colunas (SVG) ---------- */
    function colunas(id, dados, { destaque, rotulo, tooltip }) {
        const W = 400, H = 210, M = { t: 22, r: 6, b: 26, l: 26 };
        const iw = W - M.l - M.r, ih = H - M.t - M.b;
        const max = niceMax(Math.max(...dados.map(x => x.v)));
        const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "gr-svg", role: "img" });
        // grelha
        for (let i = 0; i <= 4; i++) {
            const v = max / 4 * i, y = M.t + ih - ih * v / max;
            el("line", { x1: M.l, x2: W - M.r, y1: y, y2: y, class: i ? "gr-grid-l" : "gr-base" }, svg);
            el("text", { x: M.l - 6, y: y + 3.5, class: "gr-ax", "text-anchor": "end" }, svg).textContent = fmt(v);
        }
        const band = iw / dados.length, bw = Math.min(24, band * 0.62);
        dados.forEach((x, i) => {
            const h = ih * x.v / max, cx = M.l + band * i + band / 2, y = M.t + ih - h;
            const g = el("g", { class: "gr-col" }, svg);
            el("rect", { x: cx - band / 2, y: M.t, width: band, height: ih, class: "gr-hit" }, g);
            if (x.v > 0) {
                el("path", { d: colPath(cx - bw / 2, y, bw, h), class: "gr-bar " + (destaque(x) ? "is-hi" : "is-lo"),
                             style: `--d:${i * 40}ms` }, g);
            }
            el("text", { x: cx, y: H - 8, class: "gr-ax", "text-anchor": "middle" }, svg).textContent = x.k;
            if (rotulo(x)) el("text", { x: cx, y: y - 7, class: "gr-val", "text-anchor": "middle" }, g).textContent = x.v;
            g.addEventListener("mousemove", ev => mostrarTip(tooltip(x), ev));
            g.addEventListener("mouseleave", esconderTip);
        });
        $(id).appendChild(svg);
    }

    /* ---------- barras horizontais (HTML) ---------- */
    function barras(id, dados, { cor = "teal", rotulo = x => x.k, valor = x => x.v, extra, tooltip }) {
        const max = Math.max(...dados.map(x => x.v));
        $(id).innerHTML = dados.map((x, i) => `
            <div class="gr-row" data-i="${i}">
                <span class="gr-row-l">${rotulo(x)}</span>
                <span class="gr-row-track"><span class="gr-row-fill gr-row-fill--${cor}" style="--w:${(x.v / max * 100).toFixed(1)}%;--d:${i * 40}ms"></span></span>
                <span class="gr-row-v">${valor(x)}</span>
                ${extra ? `<span class="gr-row-x">${extra(x)}</span>` : ""}
            </div>`).join("");
        if (tooltip) $(id).querySelectorAll(".gr-row").forEach(r => {
            r.addEventListener("mousemove", ev => mostrarTip(tooltip(dados[r.dataset.i]), ev));
            r.addEventListener("mouseleave", esconderTip);
        });
    }

    const estrelasTxt = n => "★".repeat(Math.floor(n)) + (n % 1 ? "½" : "");

    /* =========================================================
       1. RITMO ACUMULADO — linhas (ano anterior vs atual)
    ========================================================= */
    (function () {
        const ant = D.acumulado.anterior, atu = D.acumulado.atual;
        const series = [
            { nome: String(D.ano - 1), v: ant, cls: "s-ant" },
            { nome: String(D.ano), v: atu, cls: "s-atu" }
        ];
        $("legendRitmo").innerHTML = series.map(s =>
            `<span class="gr-key"><i class="gr-key-line ${s.cls}"></i>${s.nome}</span>`).join("");

        const W = 560, H = 230, M = { t: 14, r: 70, b: 26, l: 28 };
        const iw = W - M.l - M.r, ih = H - M.t - M.b;
        const max = niceMax(Math.max(...ant, ...atu));
        const X = i => M.l + iw * i / 11, Y = v => M.t + ih - ih * v / max;
        const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "gr-svg", role: "img",
                                "aria-label": `Livros acumulados: ${series.map(s => s.nome + " " + s.v[s.v.length - 1]).join(", ")}` });
        for (let i = 0; i <= 4; i++) {
            const v = max / 4 * i;
            el("line", { x1: M.l, x2: W - M.r, y1: Y(v), y2: Y(v), class: i ? "gr-grid-l" : "gr-base" }, svg);
            el("text", { x: M.l - 6, y: Y(v) + 3.5, class: "gr-ax", "text-anchor": "end" }, svg).textContent = v;
        }
        D.meses.forEach((mm, i) => {
            el("text", { x: X(i), y: H - 8, class: "gr-ax", "text-anchor": "middle" }, svg).textContent = mm.mes;
        });
        const cross = el("line", { y1: M.t, y2: M.t + ih, class: "gr-cross", visibility: "hidden" }, svg);
        series.forEach(s => {
            const d = s.v.map((v, i) => `${i ? "L" : "M"}${X(i)},${Y(v)}`).join("");
            if (s.cls === "s-atu") {
                el("path", { d: d + `L${X(s.v.length - 1)},${Y(0)}L${X(0)},${Y(0)}Z`, class: "gr-area " + s.cls }, svg);
            }
            const p = el("path", { d, class: "gr-line " + s.cls }, svg);
            if (!reduzMov) {
                const len = p.getTotalLength ? p.getTotalLength() : 1000;
                p.style.strokeDasharray = len; p.style.strokeDashoffset = len;
                p.dataset.len = len;
            }
            const li = s.v.length - 1;
            el("circle", { cx: X(li), cy: Y(s.v[li]), r: 4.5, class: "gr-dot " + s.cls }, svg);
            el("text", { x: X(li) + 9, y: Y(s.v[li]) + 4, class: "gr-end" }, svg).textContent = `${s.nome} · ${s.v[li]}`;
        });
        const hit = el("rect", { x: M.l, y: M.t, width: iw, height: ih, class: "gr-hit" }, svg);
        hit.addEventListener("mousemove", ev => {
            const box = svg.getBoundingClientRect();
            const px = (ev.clientX - box.left) * W / box.width;
            const i = Math.max(0, Math.min(11, Math.round((px - M.l) / iw * 11)));
            cross.setAttribute("x1", X(i)); cross.setAttribute("x2", X(i));
            cross.setAttribute("visibility", "visible");
            mostrarTip(`<b>Até ${MESES_LONGOS[i]}</b>` + series.map(s =>
                `<span class="gr-tip-row"><i class="gr-key-line ${s.cls}"></i>${s.nome}<em>${s.v[i] ?? "—"}</em></span>`).join(""), ev);
        });
        hit.addEventListener("mouseleave", () => { cross.setAttribute("visibility", "hidden"); esconderTip(); });
        $("chartRitmo").appendChild(svg);

        tabela("tableRitmo", ["Mês", D.ano - 1, D.ano],
            D.meses.map((mm, i) => [mm.mes, ant[i], atu[i] ?? "—"]));
    })();

    /* =========================================================
       2. LIVROS POR ANO
    ========================================================= */
    colunas("chartAnos", D.por_ano.map(x => ({ k: String(x.ano), v: x.livros, p: x.paginas })), {
        destaque: x => x.k === String(D.ano),
        rotulo: () => true,
        tooltip: x => `<b>${x.k}</b><span class="gr-tip-row">${x.v} livros<em>${fmt(x.p)} pág.</em></span>`
    });
    tabela("tableAnos", ["Ano", "Livros", "Páginas"], D.por_ano.map(x => [x.ano, x.livros, fmt(x.paginas)]));

    /* =========================================================
       3. MÊS A MÊS (ano atual)
    ========================================================= */
    const meses = D.meses.map((x, i) => ({ k: x.mes, v: x.livros, t: x.titulos, i }));
    const maxMes = Math.max(...meses.map(x => x.v));
    colunas("chartMeses", meses, {
        destaque: x => x.v === maxMes,
        rotulo: x => x.v === maxMes,
        tooltip: x => `<b>${MESES_LONGOS[x.i]} · ${x.v} livro${x.v === 1 ? "" : "s"}</b>` +
            (x.t.length ? `<ul>${x.t.map(t => `<li>${esc(t)}</li>`).join("")}</ul>` : `<span class="gr-tip-row">${x.i + 1 > D.mes ? "ainda por vir" : "nenhum livro terminado"}</span>`)
    });
    tabela("tableMeses", ["Mês", "Livros", "Títulos"], meses.map(x => [x.k, x.v, x.t.map(esc).join(" · ")]));

    /* =========================================================
       4. NOTAS
    ========================================================= */
    const notas = [...D.notas].reverse().map(x => ({ k: x.estrelas, v: x.livros }));
    barras("chartNotas", notas, {
        cor: "orange",
        rotulo: x => `<span class="gr-stars">${estrelasTxt(x.k)}</span>`,
        valor: x => `${x.v}`,
        tooltip: x => `<b>${fmt(x.k, x.k % 1 ? 1 : 0)} estrelas</b><span class="gr-tip-row">${x.v} livros<em>${fmt(x.v / comNota * 100)}%</em></span>`
    });
    tabela("tableNotas", ["Estrelas", "Livros", "%"], notas.map(x => [fmt(x.k, 1), x.v, fmt(x.v / comNota * 100, 1)]));

    /* =========================================================
       5. AUTORES
    ========================================================= */
    const autores = D.autores.map(x => ({ k: x.autor, v: x.livros, n: x.nota_media }));
    barras("chartAutores", autores, {
        valor: x => x.v,
        extra: x => x.n ? `${fmt(x.n, 1)}<span class="gr-star" aria-hidden="true">★</span>` : "—"
    });
    tabela("tableAutores", ["Autor", "Livros", "Nota média"], autores.map(x => [esc(x.k), x.v, x.n ? fmt(x.n, 2) : "—"]));

    /* =========================================================
       6. ÉPOCAS
    ========================================================= */
    const epocas = D.epocas.map(x => ({ k: x.epoca, v: x.livros, n: x.nota_media }));
    barras("chartEpocas", epocas, {
        valor: x => x.v,
        extra: x => `${fmt(x.n, 1)}<span class="gr-star" aria-hidden="true">★</span>`
    });
    tabela("tableEpocas", ["Época", "Livros", "Nota média"], epocas.map(x => [x.k, x.v, fmt(x.n, 2)]));

    /* =========================================================
       7. EXTENSÃO vs NOTA — dot plot
    ========================================================= */
    (function () {
        const dados = D.extensao;
        const lo = Math.floor(Math.min(...dados.map(x => x.nota_media)) * 4) / 4 - 0.25;
        const hi = Math.ceil(Math.max(...dados.map(x => x.nota_media)) * 4) / 4 + 0.25;
        const best = Math.max(...dados.map(x => x.nota_media));
        const pos = v => ((v - lo) / (hi - lo) * 100).toFixed(1);
        $("chartExtensao").innerHTML = dados.map((x, i) => `
            <div class="gr-drow" data-i="${i}">
                <span class="gr-row-l">${x.paginas}<small>${x.livros} livros</small></span>
                <span class="gr-drow-track">
                    <i class="gr-ddot${x.nota_media === best ? " is-hi" : ""}" style="left:${pos(x.nota_media)}%"></i>
                </span>
                <span class="gr-row-v">${fmt(x.nota_media, 2)}</span>
            </div>`).join("") +
            `<div class="gr-dscale"><span></span><span class="gr-drow-axis"><i style="left:0">${fmt(lo, 2)}</i><i style="left:100%">${fmt(hi, 2)}</i></span><span></span></div>`;
        tabela("tableExtensao", ["Páginas", "Livros", "Nota média"], dados.map(x => [x.paginas, x.livros, fmt(x.nota_media, 2)]));
    })();

    /* =========================================================
       8. ESTANTE DE HONRA
    ========================================================= */
    $("shelf").innerHTML = D.favoritos.map((f, i) => `
        <article class="gr-book" style="--h:${[0, 1, 2, 3][i % 4]}">
            <span class="gr-book-t">${esc(f.title)}</span>
            <span class="gr-book-a">${esc(f.author)}</span>
            <span class="gr-book-b">
                ${f.nota === 5 ? '<span class="gr-badge gr-badge--star">★ 5</span>' : `<span class="gr-badge gr-badge--soft">${fmt(f.nota, 2)} ★</span>`}
                ${f.favorito ? '<span class="gr-badge gr-badge--fav" title="Estante de favoritos">♥</span>' : ""}
            </span>
        </article>`).join("");

    /* =========================================================
       9. A LER / CURIOSIDADES
    ========================================================= */
    $("aLer").innerHTML = D.a_ler.map(x =>
        `<li><span class="gr-book-t">${esc(x.title)}</span><span class="gr-book-a">${esc(x.author)}</span></li>`).join("");

    const longo = D.extremos.find(x => x.tipo === "mais longo"), curto = D.extremos.find(x => x.tipo === "mais curto");
    $("factos").innerHTML = [
        `O mais longo: <em>${esc(longo.title)}</em>, ${fmt(longo.paginas)} páginas.`,
        `O mais curto: <em>${esc(curto.title)}</em>, ${curto.paginas} páginas.`,
        `Um livro espera em média <strong>${fmt(D.espera.media_dias)} dias</strong> na estante até ser lido.`,
        `<strong>${fmt(D.espera.pct_primeiro_mes)}%</strong> são lidos no primeiro mês depois de entrarem na estante.`
    ].map(t => `<li>${t}</li>`).join("");

    /* =========================================================
       ANIMAÇÕES AO ENTRAR NO ECRÃ
    ========================================================= */
    const cards = document.querySelectorAll(".gr-card, .gr-hero");
    if (reduzMov || !("IntersectionObserver" in window)) {
        cards.forEach(c => c.classList.add("is-in"));
        document.querySelectorAll(".gr-line").forEach(p => { p.style.strokeDashoffset = 0; });
        return;
    }
    const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (!e.isIntersecting) return;
            e.target.classList.add("is-in");
            e.target.querySelectorAll(".gr-line").forEach(p => {
                p.style.transition = "stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)";
                p.style.strokeDashoffset = 0;
            });
            obs.unobserve(e.target);
        });
    }, { threshold: 0.15 });
    cards.forEach(c => obs.observe(c));
})();
