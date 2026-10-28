/* =========================
   TRANSIÇÕES ENTRE PÁGINAS
========================= */

document.addEventListener("DOMContentLoaded", () => {

    // Fade in ao carregar a página
    document.body.classList.add("page-visible");

    // Interceta todos os links internos
    document.querySelectorAll("a[href]").forEach(link => {

        const href = link.getAttribute("href");

        if (
            !href ||
            href.startsWith("http") ||
            href.startsWith("#") ||
            href.startsWith("mailto")
        ) return;

        link.addEventListener("click", e => {
            e.preventDefault();

            localStorage.setItem("darkMode",  document.body.classList.contains("dark-mode"));
            localStorage.setItem("sepiaMode", document.body.classList.contains("sepia-mode"));

            document.body.classList.remove("page-visible");

            setTimeout(() => {
                window.location.href = href;
            }, 300);
        });
    });

    /* =========================
       MODO SÉPIA
    ========================= */

    const sepiaToggle = document.getElementById("sepiaToggle");

    if (localStorage.getItem("sepiaMode") === "true") {
        document.body.classList.add("sepia-mode");
    }

    if (sepiaToggle) {
        sepiaToggle.addEventListener("click", () => {
            const isSepia = document.body.classList.toggle("sepia-mode");
            localStorage.setItem("sepiaMode", isSepia);

            // Sépia e dark são mutuamente exclusivos
            if (isSepia) {
                document.body.classList.remove("dark-mode");
                localStorage.setItem("darkMode", false);
                const darkToggle = document.getElementById("darkToggle");
                if (darkToggle) darkToggle.innerHTML = "🌙";
            }
        });
    }

    /* =========================
       DARK MODE
    ========================= */

    const darkToggle = document.getElementById("darkToggle");

    if (localStorage.getItem("darkMode") === "true") {
        document.body.classList.add("dark-mode");
        if (darkToggle) darkToggle.innerHTML = "☀️";
    }

    if (darkToggle) {
        darkToggle.addEventListener("click", () => {
            const isDark = document.body.classList.toggle("dark-mode");
            darkToggle.innerHTML = isDark ? "☀️" : "🌙";
            localStorage.setItem("darkMode", isDark);

            // Dark e sépia são mutuamente exclusivos
            if (isDark) {
                document.body.classList.remove("sepia-mode");
                localStorage.setItem("sepiaMode", false);
            }
        });
    }

    /* =========================
       BOTÃO VOLTAR AO TOPO
    ========================= */

    const btn = document.createElement("button");
    btn.classList.add("back-to-top");
    btn.setAttribute("aria-label", "Voltar ao topo");
    btn.innerHTML = "↑";
    document.body.appendChild(btn);

    window.addEventListener("scroll", () => {
        btn.classList.toggle("visible", window.scrollY > 300);
    });

    btn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    /* =========================
       BARRA DE PROGRESSO DE SCROLL
    ========================= */

    const bar = document.createElement("div");
    bar.classList.add("progress-bar");
    document.body.appendChild(bar);

    window.addEventListener("scroll", () => {
        const scrollTop  = window.scrollY;
        const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
        const progress   = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        bar.style.width  = progress + "%";
    });

    /* =========================
       CITAÇÃO ROTATIVA
    ========================= */

    const quotes = [
        { text: "Um leitor vive mil vidas antes de morrer. Quem nunca lê vive apenas uma.", cite: "— George R.R. Martin" },
        { text: "Os livros são espelhos: só vemos neles o que já trazemos dentro de nós.", cite: "— Carlos Ruiz Zafón" },
        { text: "Não há navio que nos transporte tão longe como um livro.", cite: "— Emily Dickinson" },
        { text: "A leitura é para a mente o que o exercício é para o corpo.", cite: "— Joseph Addison" },
        { text: "Quantas histórias estão ainda por acontecer? Depende de quantos livros ainda tens para ler.", cite: "— Ítalo Calvino" },
        { text: "O homem que não lê não tem vantagem sobre o que não sabe ler.", cite: "— Mark Twain" }
    ];

    const quoteEl = document.getElementById("featuredQuote");
    const citeEl  = document.getElementById("featuredCite");

    if (quoteEl && citeEl) {
        const q = quotes[Math.floor(Math.random() * quotes.length)];
        quoteEl.textContent = q.text;
        citeEl.textContent  = q.cite;
        setTimeout(() => quoteEl.classList.add("visible"), 100);
    }

    /* =========================
       CONTADOR ANIMADO (0 → 39)
    ========================= */

    const countEl = document.getElementById("bookCount");

    if (countEl) {
        const target   = parseInt(countEl.getAttribute("data-target"), 10) || 0;
        const duration = 1400; // ms
        const start    = performance.now();

        function easeOut(t) {
            return 1 - Math.pow(1 - t, 3);
        }

        function updateCount(now) {
            const elapsed  = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const value    = Math.round(easeOut(progress) * target);
            countEl.textContent = value;

            if (progress < 1) {
                requestAnimationFrame(updateCount);
            } else {
                countEl.textContent = target;
            }
        }

        // Inicia quando o elemento entra no ecrã
        const counterObserver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    requestAnimationFrame(updateCount);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counterObserver.observe(countEl);
    }

    /* =========================
       BARRA DE PROGRESSO ANUAL
    ========================= */

    const fillEl = document.querySelector(".annual-progress-fill");

    if (fillEl) {
        const months = parseInt(fillEl.getAttribute("data-months"), 10) || 0;
        const total  = parseInt(fillEl.getAttribute("data-total"),  10) || 12;
        const pct    = Math.round((months / total) * 100);

        // Pequeno delay para a animação ser visível
        setTimeout(() => {
            fillEl.style.width = pct + "%";
        }, 300);
    }

    /* =========================
       ANIMAÇÃO DAS ESTRELAS
    ========================= */

    document.querySelectorAll(".star-animate").forEach(el => {
        const raw = el.textContent.trim();
        el.innerHTML = [...raw].map(
            (ch, i) => `<span class="star" style="transition-delay:${i * 80}ms">${ch}</span>`
        ).join("");

        const starObserver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    starObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });

        starObserver.observe(el);
    });

    /* =========================
       CARDS FADE + SLIDE AO SCROLL
    ========================= */

    const cards = document.querySelectorAll(".month");

    if (cards.length) {
        const cardObserver = new IntersectionObserver(entries => {
            entries.forEach((entry, i) => {
                if (entry.isIntersecting) {
                    // Pequeno delay escalonado por ordem de aparecimento
                    const delay = (entry.target.dataset.cardIndex || 0) * 60;
                    setTimeout(() => {
                        entry.target.classList.add("card-visible");
                    }, delay);
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        cards.forEach((card, i) => {
            card.dataset.cardIndex = i;
            cardObserver.observe(card);
        });
    }

    /* =========================
       FILTRO POR GÉNERO
    ========================= */

    const filterBtns = document.querySelectorAll(".filter-btn");
    const allCards   = document.querySelectorAll(".month");

    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            // Actualiza botão activo
            filterBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const filter = btn.getAttribute("data-filter");

            allCards.forEach(card => {
                if (filter === "all") {
                    card.classList.remove("hidden");
                } else {
                    const tag = card.querySelector(".genre-tag");
                    const genre = tag ? tag.getAttribute("data-genre") : "";
                    card.classList.toggle("hidden", genre !== filter);
                }
            });

            updateNoResults();
        });
    });

    /* =========================
       PESQUISA RÁPIDA
    ========================= */

    const searchInput = document.getElementById("bookSearch");

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.trim().toLowerCase();

            // Reset filtro de género ao pesquisar
            if (query) {
                filterBtns.forEach(b => b.classList.remove("active"));
                document.querySelector('.filter-btn[data-filter="all"]')?.classList.add("active");
            }

            allCards.forEach(card => {
                if (!query) {
                    card.classList.remove("hidden");
                    return;
                }

                const title  = card.querySelector("h3")?.textContent.toLowerCase()  || "";
                const author = card.querySelector(".month-author")?.textContent.toLowerCase() || "";
                const match  = title.includes(query) || author.includes(query);
                card.classList.toggle("hidden", !match);
            });

            updateNoResults();
        });
    }

    function updateNoResults() {
        // Remove aviso anterior
        const existing = document.querySelector(".no-results");
        if (existing) existing.remove();

        const visible = [...allCards].filter(c => !c.classList.contains("hidden"));
        if (visible.length === 0) {
            const msg = document.createElement("p");
            msg.classList.add("no-results");
            msg.textContent = "Nenhum livro encontrado.";
            document.querySelector(".months")?.appendChild(msg);
        }
    }

});
