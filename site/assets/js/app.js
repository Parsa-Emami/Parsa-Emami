/* Parsa Emami — profile site. No dependencies. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const root = document.documentElement;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isTyping = (t) => t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));

  /* ---------------- theme ---------------- */
  const dark = matchMedia("(prefers-color-scheme: dark)");
  const saved = () => { try { return localStorage.getItem("theme"); } catch (_) { return null; } };
  const applyTheme = (t) => {
    root.dataset.theme = t;
    const m = $('meta[name="theme-color"]');
    if (m) m.content = t === "dark" ? "#0a0a0a" : "#ffffff";
  };
  const toggleTheme = () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem("theme", next); } catch (_) { /* private mode */ }
  };
  dark.addEventListener("change", (e) => { if (!saved()) applyTheme(e.matches ? "dark" : "light"); });
  $$("[data-toggle-theme]").forEach((b) => b.addEventListener("click", toggleTheme));

  /* ---------------- flip sentences ---------------- */
  const flip = $("[data-flip]");
  if (flip && !reduce) {
    const items = $$(".flip-item", flip);
    let i = 0;
    if (items.length > 1) {
      setInterval(() => {
        if (document.hidden) return;
        const cur = items[i];
        i = (i + 1) % items.length;
        cur.classList.replace("on", "off") || cur.classList.add("off");
        items[i].classList.remove("off");
        items[i].classList.add("on");
      }, 2800);
    }
  }

  /* ---------------- show more / less ---------------- */
  $$("[data-more]").forEach((btn) => {
    const list = document.getElementById(btn.dataset.more);
    if (!list) return;
    const label = $(".lbl", btn);
    btn.addEventListener("click", () => {
      const open = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", String(open));
      $$("[data-extra]", list).forEach((el) => { el.hidden = !open; });
      if (label) label.textContent = open ? "Show less" : btn.dataset.label;
    });
  });

  /* ---------------- heatmap tooltip ---------------- */
  const tip = document.createElement("div");
  tip.className = "tip";
  tip.hidden = true;
  document.body.append(tip);
  const heat = $(".heat");
  const scroller = $(".heat-scroll");
  if (scroller) scroller.scrollLeft = scroller.scrollWidth; /* newest weeks visible on narrow screens */
  if (heat) {
    heat.addEventListener("pointermove", (e) => {
      const t = e.target.closest("[data-tip]");
      if (!t) { tip.hidden = true; return; }
      tip.textContent = t.dataset.tip;
      tip.style.left = e.clientX + "px";
      tip.style.top = e.clientY + "px";
      tip.hidden = false;
    });
    heat.addEventListener("pointerleave", () => { tip.hidden = true; });
  }

  /* ---------------- command palette ---------------- */
  const dlg = $("#palette");
  const dataEl = $("#palette-data");
  if (dlg && dataEl && typeof dlg.showModal === "function") {
    const items = JSON.parse(dataEl.textContent);
    const input = $("input", dlg);
    const list = $(".palette-list", dlg);
    let shown = [];
    let sel = 0;

    const run = (it) => {
      dlg.close();
      if (it.action === "theme") return toggleTheme();
      if (it.action === "copy") {
        if (navigator.clipboard) navigator.clipboard.writeText(location.href.split("#")[0]);
        return;
      }
      if (it.href && /^https?:/.test(it.href)) return window.open(it.href, "_blank", "noopener");
      if (it.href && it.href.startsWith("#")) {
        const target = document.getElementById(it.href.slice(1));
        if (target) {
          if (target.hidden) {
            const owner = target.closest("[data-list]");
            const btn = owner && $('[data-more="' + owner.id + '"]');
            if (btn) btn.click(); else target.hidden = false;
          }
          if (target.tagName === "DETAILS") target.open = true;
          target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
          history.replaceState(null, "", it.href);
        }
      }
    };

    const paint = () => {
      list.textContent = "";
      if (!shown.length) {
        const e = document.createElement("div");
        e.className = "palette-empty";
        e.textContent = "No results found.";
        list.append(e);
        input.removeAttribute("aria-activedescendant");
        return;
      }
      let group = "";
      shown.forEach((it, idx) => {
        if (it.group !== group) {
          group = it.group;
          const g = document.createElement("div");
          g.className = "palette-group";
          g.setAttribute("role", "presentation");
          g.textContent = group;
          list.append(g);
        }
        const row = document.createElement("div");
        row.className = "palette-item";
        row.id = "pal-" + idx;
        row.setAttribute("role", "option");
        row.setAttribute("aria-selected", String(idx === sel));
        const label = document.createElement("span");
        label.textContent = it.label;
        row.append(label);
        if (it.hint) {
          const h = document.createElement("span");
          h.className = "hint";
          h.textContent = it.hint;
          row.append(h);
        }
        row.addEventListener("pointermove", () => { if (sel !== idx) { sel = idx; mark(); } });
        row.addEventListener("click", () => run(it));
        list.append(row);
      });
      input.setAttribute("aria-activedescendant", "pal-" + sel);
    };
    const mark = () => {
      $$(".palette-item", list).forEach((el, idx) => el.setAttribute("aria-selected", String(idx === sel)));
      const cur = $("#pal-" + sel, list);
      if (cur) { cur.scrollIntoView({ block: "nearest" }); input.setAttribute("aria-activedescendant", cur.id); }
    };
    const filter = () => {
      const q = input.value.trim().toLowerCase();
      shown = items.filter((it) => !q || (it.label + " " + (it.keywords || "") + " " + it.group).toLowerCase().includes(q));
      sel = 0;
      paint();
    };
    const open = () => { input.value = ""; filter(); dlg.showModal(); input.focus(); };

    input.addEventListener("input", filter);
    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); if (shown.length) { sel = (sel + 1) % shown.length; mark(); } }
      else if (e.key === "ArrowUp") { e.preventDefault(); if (shown.length) { sel = (sel - 1 + shown.length) % shown.length; mark(); } }
      else if (e.key === "Enter") { e.preventDefault(); if (shown[sel]) run(shown[sel]); }
    });
    dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
    $$("[data-open-palette]").forEach((b) => b.addEventListener("click", open));
    document.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); dlg.open ? dlg.close() : open(); }
      else if (e.key === "/" && !isTyping(e.target) && !dlg.open) { e.preventDefault(); open(); }
    });
  } else {
    $$("[data-open-palette]").forEach((b) => { b.hidden = true; });
  }

  /* ---------------- "D" toggles the theme ---------------- */
  document.addEventListener("keydown", (e) => {
    if (e.key.toLowerCase() === "d" && !e.metaKey && !e.ctrlKey && !e.altKey && !isTyping(e.target) && !(dlg && dlg.open)) toggleTheme();
  });
})();
