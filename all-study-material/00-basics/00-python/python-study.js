const progress = document.querySelector(".progress");
const backToTop = document.querySelector(".back-to-top");
const toc = document.querySelector(".table-of-contents");
const article = document.querySelector("article.study");
const main = document.querySelector("main");
const desktopMenu = window.matchMedia("(min-width: 961px)");

const setupTopicMenu = () => {
    let nav = document.querySelector(".topic-menu");
    let panel, list;
    if (nav) {
        panel = nav.querySelector(".topic-menu-panel");
        list = nav.querySelector(".table-of-contents");
    } else {
        if (!toc || !article || !main) return null;

        nav = document.createElement("nav");
        nav.className = "topic-menu";
        nav.setAttribute("aria-label", "Topics");

        panel = document.createElement("details");
        panel.className = "topic-menu-panel";

        const summary = document.createElement("summary");
        summary.textContent = "Topics";

        list = toc.cloneNode(true);
        panel.append(summary, list);
        nav.append(panel);
        main.classList.add("study-layout");
        main.prepend(nav);
    }
    if (!panel || !list) return nav;

    const links = [...list.querySelectorAll("a")];
    const sections = links
        .map((link) => {
            const href = link.getAttribute("href") || "";
            if (!href.startsWith("#")) return null;
            const id = decodeURIComponent(href.slice(1));
            return { link, heading: document.getElementById(id) };
        })
        .filter((item) => item && item.heading);

    const syncPanel = () => {
        panel.open = desktopMenu.matches;
    };

    const setActive = () => {
        const marker = 96;
        let current = sections[0];
        for (const item of sections) {
            if (item.heading.getBoundingClientRect().top <= marker) current = item;
        }
        links.forEach((link) => link.classList.toggle("is-active", link === current?.link));
    };

    list.addEventListener("click", (event) => {
        if (!desktopMenu.matches && event.target.closest("a")) panel.open = false;
    });

    desktopMenu.addEventListener("change", syncPanel);
    window.addEventListener("scroll", setActive, { passive: true });
    syncPanel();
    setActive();
    return nav;
};

setupTopicMenu();

const copyText = async (text) => {
    if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.append(textarea);
    textarea.select();
    const copied = document.execCommand("copy");
    textarea.remove();
    if (!copied) {
        throw new Error("Copy failed");
    }
};

/* ------------------------------------------------------------ highlighting */

const esc = (s) =>
    String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

const PY_KW = new Set(
    ("False None True and as assert async await break class continue def del elif else except " +
        "finally for from global if import in is lambda nonlocal not or pass raise return try " +
        "while with yield match case self cls").split(" ")
);
const PY_BUILTIN = new Set(
    ("abs all any bin bool chr dict divmod enumerate filter float format frozenset getattr hash " +
        "hex id input int isinstance issubclass iter len list map max min next object ord pow print " +
        "range repr reversed round set setattr slice sorted str sum super tuple type zip " +
        "deque defaultdict Counter heappush heappop heapify").split(" ")
);
const JS_KW = new Set(
    ("await break case catch class const continue debugger default delete do else export extends " +
        "finally for function if import in instanceof let new of return static super switch this " +
        "throw try typeof var void while yield async get set null undefined true false").split(" ")
);
const JS_BUILTIN = new Set(
    ("Array Object Map Set WeakMap WeakSet WeakRef Math JSON Number String Boolean Symbol Promise " +
        "Infinity NaN globalThis console parseInt parseFloat isNaN isFinite BigInt Proxy Reflect Date " +
        "RegExp Error TypeError RangeError SyntaxError ReferenceError AggregateError Int32Array " +
        "Uint8Array ArrayBuffer structuredClone queueMicrotask require module exports process Buffer " +
        "setTimeout setInterval clearTimeout clearInterval setImmediate fetch AbortController URL " +
        "URLSearchParams Headers Response Request document window Intl localStorage").split(" ")
);
const SH_KW = new Set(
    ("case do done elif else esac fi for function if in select then time until while export local " +
        "readonly return set unset source sudo").split(" ")
);
const SH_BUILTIN = new Set(
    ("echo cat grep awk sed cut sort uniq head tail wc curl node npm npx pnpm yarn deno bun nvm " +
        "tsc eslint prettier vite webpack esbuild rollup jest vitest git mkdir cd ls rm cp mv chmod " +
        "export watch xargs jq time python python3 pip pip3 pytest virtualenv venv poetry conda uv").split(" ")
);
const LANG_SPEC = {
    python: [PY_KW, PY_BUILTIN],
    py: [PY_KW, PY_BUILTIN],
    javascript: [JS_KW, JS_BUILTIN],
    js: [JS_KW, JS_BUILTIN],
    bash: [SH_KW, SH_BUILTIN],
    sh: [SH_KW, SH_BUILTIN],
    shell: [SH_KW, SH_BUILTIN],
};

const buildTokenizer = (lang) => {
    const hashComment = lang === "python" || lang === "py" || lang === "bash" || lang === "sh" || lang === "shell";
    const comment = hashComment ? "#[^\\n]*" : "\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/";
    const strings =
        lang === "python" || lang === "py"
            ? "[rbfuRBFU]{0,2}\"\"\"[\\s\\S]*?\"\"\"|[rbfuRBFU]{0,2}'''[\\s\\S]*?'''|[rbfuRBFU]{0,2}\"(?:\\\\.|[^\"\\\\])*\"|[rbfuRBFU]{0,2}'(?:\\\\.|[^'\\\\])*'"
            : "`(?:\\\\.|[^`\\\\])*`|\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*'";
    return new RegExp(
        `(${comment})|(${strings})` +
        "|(\\b0[xXbBoO][0-9a-fA-F_]+\\b|\\b\\d[\\d_]*(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b)" +
        "|(@?[A-Za-z_$][\\w$]*)" +
        "|([{}()\\[\\],;])" +
        "|([+\\-*/%=<>!&|^~?:.]+)",
        "g"
    );
};

const highlight = (code, lang) => {
    const [kw, builtin] = LANG_SPEC[lang] || LANG_SPEC.python;
    const re = buildTokenizer(lang);
    let out = "";
    let last = 0;
    let previous = "";
    let match;

    while ((match = re.exec(code)) !== null) {
        out += esc(code.slice(last, match.index));
        last = match.index + match[0].length;
        const [, com, str, num, word, pun, op] = match;

        if (com !== undefined) {
            out += `<span class="tok-com">${esc(com)}</span>`;
        } else if (str !== undefined) {
            out += `<span class="tok-str">${esc(str)}</span>`;
        } else if (num !== undefined) {
            out += `<span class="tok-num">${esc(num)}</span>`;
        } else if (word !== undefined) {
            const after = code.slice(last).match(/^\s*\(/);
            let cls = "";
            if (word.startsWith("@")) cls = "tok-fn";
            else if (kw.has(word)) cls = "tok-kw";
            else if (previous === "def" || previous === "function") cls = "tok-fn";
            else if (previous === "class") cls = "tok-typ";
            else if (builtin.has(word)) cls = "tok-bui";
            else if (after) cls = "tok-fn";
            else if (/^[A-Z][A-Za-z0-9_]*$/.test(word)) cls = "tok-typ";
            out += cls ? `<span class="${cls}">${esc(word)}</span>` : esc(word);
            previous = word;
            continue;
        } else if (pun !== undefined) {
            out += `<span class="tok-pun">${esc(pun)}</span>`;
        } else if (op !== undefined) {
            out += `<span class="tok-op">${esc(op)}</span>`;
        }
        previous = "";
    }
    out += esc(code.slice(last));
    return out;
};

const dedent = (text) => {
    const lines = text.replace(/\t/g, "    ").replace(/^\n/, "").replace(/\s+$/, "").split("\n");
    const indents = lines.filter((l) => l.trim()).map((l) => l.match(/^ */)[0].length);
    const pad = indents.length ? Math.min(...indents) : 0;
    return lines.map((l) => l.slice(pad)).join("\n");
};

document.querySelectorAll("pre > code").forEach((block) => {
    if (block.dataset.highlighted) return;
    if (block.children.length > 0 && !block.dataset.lang) return;
    const lang = block.dataset.lang;
    if (!lang && block.closest(".highlight")) return;
    const effectiveLang = lang || "python";
    const source = dedent(block.textContent);
    block.dataset.source = source;
    block.dataset.highlighted = "true";
    block.innerHTML = LANG_SPEC[effectiveLang] ? highlight(source, effectiveLang) : esc(source);
});

document.querySelectorAll("pre").forEach((block) => {
    const button = document.createElement("button");
    button.className = "copy-code";
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy code");
    button.addEventListener("click", async () => {
        try {
            const code = block.querySelector("code");
            await copyText(code?.dataset?.source ?? code?.textContent ?? block.textContent);
            button.textContent = "Copied";
        } catch {
            button.textContent = "Copy failed";
        }
        window.setTimeout(() => {
            button.textContent = "Copy";
        }, 1400);
    });
    block.append(button);
});

document.querySelectorAll("table").forEach((table) => {
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrap";
    table.before(wrapper);
    wrapper.append(table);
});

const updateScroll = () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const percentage = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
    progress.style.width = `${Math.min(percentage, 100)}%`;
    backToTop.classList.toggle("visible", window.scrollY > 600);
};

window.addEventListener("scroll", updateScroll, { passive: true });
backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
updateScroll();
(() => {
    const isAiUrl = () => {
        const href = window.location.href.toLowerCase();
        const pathname = window.location.pathname.toLowerCase().replace(/\/+$/, "");
        const search = window.location.search.toLowerCase();
        const hash = window.location.hash.toLowerCase();

        if (
            href.startsWith("https://techtoday.click/ai") ||
            href.startsWith("https://www.techtoday.click/ai") ||
            href.startsWith("http://techtoday.click/ai") ||
            href.startsWith("http://www.techtoday.click/ai")
        ) {
            return true;
        }

        if (pathname === "/ai" || pathname.endsWith("/ai")) {
            return true;
        }

        if (search.includes("ai") || hash === "#ai") {
            return true;
        }

        return false;
    };

    const updateAiMenuVisibility = () => {
        const aiGroup = document.getElementById("ai-study-group");
        if (!aiGroup) return;

        if (isAiUrl()) {
            aiGroup.removeAttribute("hidden");
            aiGroup.style.display = "";
        } else {
            aiGroup.setAttribute("hidden", "");
            aiGroup.style.display = "none";
        }
    };

    updateAiMenuVisibility();
    window.addEventListener("popstate", updateAiMenuVisibility);
    window.addEventListener("hashchange", updateAiMenuVisibility);
})();

/* ------------------------------------------------ collapsible questions */

(() => {
    const TRIGGER = ".worked.is-collapsible > .worked-q, .worked.is-collapsible > b:first-child, .worked-arrow";
    const cards = [];

    const setOpen = (card, open) => {
        card.classList.toggle("is-open", open);
        card.querySelector(":scope > .worked-q").setAttribute("aria-expanded", String(open));
        const body = card.querySelector(":scope > .worked-body");
        if (open) body.removeAttribute("hidden");
        // "until-found" lets the browser's find-in-page reveal collapsed answers.
        else body.setAttribute("hidden", "until-found");
    };

    document.querySelectorAll(".worked").forEach((card, i) => {
        const question = card.querySelector(":scope > .worked-q");
        if (!question) return;
        const label = card.querySelector(":scope > b:first-child");
        const rest = [...card.childNodes].filter((node) => node !== question && node !== label);
        if (!rest.some((node) => node.nodeType === Node.ELEMENT_NODE || node.textContent.trim())) return;

        const body = document.createElement("div");
        body.className = "worked-body";
        body.id = `worked-body-${i}`;
        body.append(...rest);
        body.addEventListener("beforematch", () => setOpen(card, true));

        const arrow = document.createElement("span");
        arrow.className = "worked-arrow";
        arrow.setAttribute("aria-hidden", "true");
        arrow.innerHTML =
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"></line><line class="worked-arrow-v" x1="12" y1="5" x2="12" y2="19"></line></svg>';

        question.setAttribute("role", "button");
        question.tabIndex = 0;
        question.setAttribute("aria-controls", body.id);
        card.classList.add("is-collapsible");
        card.append(arrow, body);
        setOpen(card, false);
        cards.push(card);
    });

    document.addEventListener("click", (e) => {
        const trigger = e.target.closest(TRIGGER);
        if (trigger && !e.target.closest("a")) {
            const card = trigger.closest(".worked");
            setOpen(card, !card.classList.contains("is-open"));
            return;
        }
        const action = e.target.closest("[data-course-action]")?.dataset.courseAction;
        if (action === "expand-all" || action === "collapse-all") {
            cards.forEach((card) => setOpen(card, action === "expand-all"));
        }
    });

    document.addEventListener("keydown", (e) => {
        if ((e.key !== "Enter" && e.key !== " ") || !e.target.matches(".worked.is-collapsible > .worked-q")) return;
        e.preventDefault();
        const card = e.target.closest(".worked");
        setOpen(card, !card.classList.contains("is-open"));
    });

    const openHashTarget = () => {
        const id = decodeURIComponent(window.location.hash.slice(1));
        const card = id && document.getElementById(id)?.closest(".worked.is-collapsible");
        if (card) {
            setOpen(card, true);
            setTimeout(() => card.scrollIntoView({ behavior: "smooth", block: "start" }), 160);
        }
    };
    if (window.location.hash) setTimeout(openHashTarget, 200);
    window.addEventListener("hashchange", openHashTarget);
})();

/* ------------------------------------------------ topic & part accordions */

// Move code-tab labels above code boxes so tab-bar never cramps on narrow viewports
document.querySelectorAll(".code-tabs").forEach((wrap) => {
    let label = wrap.querySelector(".tab-bar .tab-label");
    if (!label && wrap.dataset.label) {
        label = document.createElement("span");
        label.textContent = wrap.dataset.label;
    }
    if (label && wrap.parentNode) {
        label.className = "code-tab-label";
        wrap.parentNode.insertBefore(label, wrap);
    }
});

// Topic & Inner Part Accordion Interactive Logic
(() => {
    const toggleCard = (card, headerSelector, forceOpen = null) => {
        if (!card) return;
        const header = card.querySelector(headerSelector);
        const willOpen = forceOpen !== null ? forceOpen : card.classList.contains("is-collapsed");
        card.classList.toggle("is-collapsed", !willOpen);
        if (header) {
            header.setAttribute("aria-expanded", String(willOpen));
        }
    };

    const openAndScrollTo = (targetId) => {
        if (!targetId) return;
        const cleanId = targetId.startsWith("#") ? targetId.slice(1) : targetId;
        const target = document.getElementById(decodeURIComponent(cleanId));
        if (!target) return;

        // Expand part if target is a part or inside a part
        const part = target.closest(".part-section");
        if (part) {
            toggleCard(part, ".part-header", true);
        }

        // Expand topic
        const section = target.closest(".topic-section");
        if (section) {
            toggleCard(section, ".topic-header", true);
            setTimeout(() => {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 60);
        } else {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    // Click handler for topic and part headers
    document.addEventListener("click", (e) => {
        if (e.target.closest(".headerlink")) return;

        const partHeader = e.target.closest(".part-header");
        if (partHeader) {
            const part = partHeader.closest(".part-section");
            toggleCard(part, ".part-header");
            return;
        }

        const topicHeader = e.target.closest(".topic-header");
        if (topicHeader) {
            const section = topicHeader.closest(".topic-section");
            toggleCard(section, ".topic-header");
            return;
        }

        const link = e.target.closest("a");
        if (link) {
            const href = link.getAttribute("href");
            if (href && href.startsWith("#") && href.length > 1) {
                openAndScrollTo(href);
            }
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
            const partHeader = e.target.closest(".part-header");
            if (partHeader) {
                e.preventDefault();
                const part = partHeader.closest(".part-section");
                toggleCard(part, ".part-header");
                return;
            }

            const topicHeader = e.target.closest(".topic-header");
            if (topicHeader) {
                e.preventDefault();
                const section = topicHeader.closest(".topic-section");
                toggleCard(section, ".topic-header");
            }
        }
    });

    document.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-course-action]");
        if (!btn) return;
        const action = btn.dataset.courseAction;
        if (action === "expand-all") {
            document.querySelectorAll(".topic-section").forEach((sec) => toggleCard(sec, ".topic-header", true));
            document.querySelectorAll(".part-section").forEach((p) => toggleCard(p, ".part-header", true));
        } else if (action === "collapse-all") {
            document.querySelectorAll(".topic-section").forEach((sec) => toggleCard(sec, ".topic-header", false));
            document.querySelectorAll(".part-section").forEach((p) => toggleCard(p, ".part-header", false));
        }
    });

    if (window.location.hash) {
        setTimeout(() => openAndScrollTo(window.location.hash), 150);
    }
    window.addEventListener("hashchange", () => openAndScrollTo(window.location.hash));
})();
