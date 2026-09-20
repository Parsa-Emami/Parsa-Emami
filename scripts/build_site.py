#!/usr/bin/env python3
"""Generate the static website in ./site from data/profile.json.

Design adapted from chanhdai.com (MIT). Output has no build step and no
runtime dependencies: open site/index.html, or serve the folder anywhere
(GitHub Pages, Netlify, S3 ...). All asset URLs are relative.
"""
from __future__ import annotations

import json
import shutil
from html import escape as e
from pathlib import Path

from lib import content as C
from lib import fonts, heat, icons, markdown

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AVATARS = ROOT / "assets" / "avatar"

_used_icons: set[str] = set()


# --------------------------------------------------------------------------- #
# tiny HTML helpers
# --------------------------------------------------------------------------- #
def ic(name: str, cls: str = "i") -> str:
    _used_icons.add(name)
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def sprite() -> str:
    symbols = []
    for name in sorted(_used_icons):
        if name == "github":
            symbols.append(f'<symbol id="i-github" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="{icons.GITHUB_PATH}"/></symbol>')
        else:
            symbols.append(
                f'<symbol id="i-{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round">{icons.stroke_icon(name)}</symbol>'
            )
    return '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(symbols) + "</svg>"


def link(href: str, label: str, cls: str = "u", icon: str | None = None) -> str:
    ext = href.startswith("http")
    attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
    return f'<a class="{cls}" href="{e(href, quote=True)}"{attrs}>{e(label)}{ic(icon) if icon else ""}</a>'


def pills(items: list[str], small: bool = False) -> str:
    cls = "pill sm" if small else "pill"
    return '<ul class="pills">' + "".join(f'<li class="{cls}">{e(i)}</li>' for i in items) + "</ul>"


def panel(pid: str, title: str, body: str, count: int | None = None, note: str = "", flush: bool = False) -> str:
    cnt = f' <span class="count">({count})</span>' if count is not None else ""
    note_html = f'<p class="panel-note">{e(note)}</p>' if note else ""
    cls = "panel-body flush" if flush else "panel-body"
    return (
        f'<section id="{pid}" class="panel line-b" aria-labelledby="{pid}-h">'
        f'<header class="panel-head"><h2 class="panel-title" id="{pid}-h"><a href="#{pid}">{e(title)}</a></h2>{cnt}</header>'
        f'{note_html}<div class="{cls}">{body}</div></section>'
    )


SEP = '<div class="sep hatch line-b" aria-hidden="true"></div>'


# --------------------------------------------------------------------------- #
# sections
# --------------------------------------------------------------------------- #
def cover(p: dict) -> str:
    per = p["person"]
    flips = "".join(
        f'<span class="flip-item{" on" if i == 0 else ""}" aria-hidden="true">{e(s)}</span>' for i, s in enumerate(per["flip"])
    )
    return f"""
<section class="cover" id="top" aria-label="Profile">
  <div class="cover-art hatch line-b"><span class="fig"><em>Fig. 1.</em> {e(per['name'])}, {e(per['coordinates'])}.</span></div>
  <div class="profile-row line-b">
    <div class="avatar">
      <img class="only-light" src="assets/img/avatar-light.webp" width="136" height="136" alt="Pencil-sketch portrait of {e(per['name'])}" fetchpriority="high">
      <img class="only-dark" src="assets/img/avatar-dark.webp" width="136" height="136" alt="Portrait of {e(per['name'])}" fetchpriority="high">
    </div>
    <div class="who">
      <h1 class="name">{e(per['name'])}</h1>
      <p class="role">{e(per['role'])}</p>
      <p class="flip" data-flip aria-label="{e(' / '.join(per['flip']))}">{flips}</p>
    </div>
  </div>
</section>"""


def overview(p: dict) -> str:
    rows = []
    for row in p["overview"]:
        bits = []
        for part in row["parts"]:
            bits.append(link(part["href"], part["t"]) if part.get("href") else f"<span>{e(part['t'])}</span>")
        rows.append(f'<li><span class="ico">{ic(row["icon"])}</span><span>{" ".join(bits)}</span></li>')
    per = p["person"]
    if per.get("email"):
        rows.append(f'<li><span class="ico">{ic("mail")}</span>{link("mailto:" + per["email"], per["email"])}</li>')
    if per.get("phone"):
        rows.append(f'<li><span class="ico">{ic("phone")}</span>{link("tel:" + per["phone"].replace(" ", ""), per["phone"])}</li>')
    if per.get("pronouns"):
        rows.append(f'<li><span class="ico">{ic("user")}</span><span>{e(per["pronouns"])}</span></li>')
    return panel("overview", "Overview", f'<ul class="ov">{"".join(rows)}</ul>')


def socials(p: dict, base: str) -> str:
    cells = []
    for l in p["links"]:
        cells.append(
            f'<a class="social" href="{e(l["href"], quote=True)}" target="_blank" rel="noopener noreferrer">'
            f'<span class="ico">{ic(l["icon"])}</span><span><span class="lbl">{e(l["label"])}</span>'
            f'<span class="handle">{e(l["handle"])}</span></span>{ic("arrow-up-right", "i go")}</a>'
        )
    body = f'<div class="lined cols-3">{"".join(cells)}</div>'
    if p.get("cta"):
        body += f'<p class="cta line-t">{e(p["cta"])}</p>'
    return panel("social-links", "Social Links", body, flush=True)


def contributions(contrib: dict) -> str:
    days = contrib.get("days", [])
    cells, cols, labels = heat.build(days)
    if not cells:
        return panel("github-contributions", "GitHub Contributions", '<p class="caption">No activity data yet.</p>')
    cell, gap, top = 11, 3, 16
    pitch = cell + gap
    w, h = cols * pitch - gap, top + 7 * pitch - gap
    rects = "".join(
        f'<rect class="l{c.level}" x="{c.col * pitch}" y="{top + c.row * pitch}" width="{cell}" height="{cell}" data-tip="{e(heat.tip(c))}"/>'
        for c in cells
    )
    months = "".join(f'<text x="{col * pitch}" y="9">{m}</text>' for col, m in labels)
    svg = (
        f'<svg class="heat" viewBox="0 0 {w} {h}" role="img" aria-label="Contribution heatmap, {contrib["total_contributions"]} contributions in the last year">'
        f"{months}{rects}</svg>"
    )
    r = contrib["range"]
    legend = "".join(f'<i style="background:var(--heat{i})"></i>' for i in range(5))
    foot = (
        f'<div class="heat-foot"><p class="caption"><em>Fig. 2.</em> {contrib["total_contributions"]:,} contributions, '
        f'{C.fmt_day(r["start"])} – {C.fmt_day(r["end"])}. Source: <a class="u" href="https://github.com/{e(contrib["username"])}" '
        f'target="_blank" rel="noopener noreferrer">GitHub</a>.</p>'
        f'<span class="legend" aria-hidden="true">Less {legend} More</span></div>'
    )
    return panel("github-contributions", "GitHub Contributions", f'<div class="heat-scroll">{svg}</div>{foot}', flush=True)


def about(p: dict) -> str:
    return panel("about", "About", '<ul class="about">' + "".join(f"<li>{C.to_html(t)}</li>" for t in p["about"]) + "</ul>")


def principles(p: dict) -> str:
    cells = "".join(
        f'<div class="cell"><div class="n"><span>{i:02d}</span><span>{e(x["verb"])}</span></div><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></div>'
        for i, x in enumerate(p["principles"], 1)
    )
    return panel("principles", "Principles", f'<div class="lined cols-2">{cells}</div>', count=len(p["principles"]), flush=True)


def focus(p: dict) -> str:
    cells = "".join(
        f'<div class="cell"><span class="ico">{ic(x["icon"])}</span><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></div>'
        for x in p["focus"]
    )
    return panel("focus", "Focus", f'<div class="lined cols-2">{cells}</div>', count=len(p["focus"]), flush=True)


def stack(p: dict) -> str:
    rows = []
    for i, g in enumerate(p["stack"], 1):
        items = "".join(
            f'<li>{link(x["url"], x["name"], "pill", "arrow-up-right")}</li>' if x.get("url") else f'<li class="pill">{e(x["name"])}</li>'
            for x in g["items"]
        )
        rows.append(
            f'<div class="stack-row"><div class="stack-name"><span class="num">{i:02d}</span><h3>{e(g["name"])}</h3></div>'
            f'<ul class="pills">{items}</ul></div>'
        )
    return panel("stack", "Stack", "".join(rows), flush=True)


def experience(p: dict) -> str:
    out = []
    for ex in p["experience"]:
        current = any(x["end"] is None for x in ex["positions"])
        meta = [e(x) for x in (ex.get("location"), ex.get("location_type")) if x]
        meta_html = "".join(f'<span class="{"sep-dot" if i else ""}">{m}</span>' for i, m in enumerate(meta))
        if current:
            meta_html += f'<span class="{"sep-dot " if meta else ""}badge-now"><i class="dot"></i>Current</span>'
        name = link(ex["url"], ex["company"]) if ex.get("url") else e(ex["company"])
        positions = []
        for pos in ex["positions"]:
            bits = [pos["type"], C.fmt_period(pos["start"], pos["end"]), C.duration(pos["start"], pos["end"])]
            if pos.get("location_type"):
                bits.append(pos["location_type"])
            pm = "".join(f'<span class="{"sep-dot" if i else ""}">{e(b)}</span>' for i, b in enumerate(bits))
            positions.append(
                f'<div class="pos"><h4>{e(pos["title"])}</h4><div class="meta">{pm}</div>'
                f'<p>{e(pos["description"])}</p>{pills(pos["skills"], small=True)}</div>'
            )
        out.append(
            f'<article class="exp" id="experience-{e(ex["id"])}"><div class="exp-head"><span class="tile" aria-hidden="true">{e(ex["monogram"])}</span>'
            f'<div><h3 class="exp-name">{name}</h3><div class="meta">{meta_html}</div></div></div>'
            f'<div class="timeline">{"".join(positions)}</div></article>'
        )
    return panel("experience", "Experience", "".join(out), count=len(p["experience"]), flush=True)


def education(p: dict) -> str:
    rows = []
    for ed in p["education"]:
        mono = "".join(w[0] for w in ed["school"].split() if w[0].isupper())[:4] or "EDU"
        bits = [f'{ed["start"]}—{ed["end"]}'] + ([ed["status"]] if ed.get("status") else [])
        m = "".join(f'<span class="{"sep-dot" if i else ""}">{e(b)}</span>' for i, b in enumerate(bits))
        rows.append(
            f'<div class="edu"><span class="tile" aria-hidden="true">{e(mono)}</span><div><h3>{e(ed["degree"])}, {e(ed["field"])}</h3>'
            f'<p class="muted" style="color:var(--muted-fg);font-size:.875rem">{e(ed["school"])}</p><div class="meta">{m}</div></div></div>'
        )
    return panel("education", "Education", "".join(rows), count=len(p["education"]), flush=True)


LIMIT_PROJECTS = 4
LIMIT_LAB = 5


def more_button(list_id: str, hidden_count: int, label: str) -> str:
    if hidden_count <= 0:
        return ""
    return (
        f'<div class="more-row"><button class="more-btn" type="button" data-more="{list_id}" data-label="{e(label)}" aria-expanded="false" aria-controls="{list_id}">'
        f'<span class="lbl">{e(label)}</span>{ic("chevron-down")}</button></div>'
    )


def projects(p: dict) -> str:
    items = []
    for i, pr in enumerate(p["projects"]):
        extra = ' data-extra hidden' if i >= LIMIT_PROJECTS else ""
        opened = " open" if i == 0 else ""
        bullets = "".join(f"<li>{e(b)}</li>" for b in pr["bullets"])
        btn = f'<div class="link-row">{link(pr["url"], "View on GitHub", "btn", "arrow-up-right")}</div>' if pr.get("url") else ""
        items.append(
            f'<details class="proj" id="project-{e(pr["id"])}"{opened}{extra}><summary>'
            f'<span class="p-name">{e(pr["name"])}</span><span class="tag">{e(pr["kind"])}</span>'
            f'<span class="p-cat">{e(pr["category"])}</span>{ic("chevron-down", "i chev")}</summary>'
            f'<div class="proj-body"><p>{e(pr["summary"])}</p><ul class="bl">{bullets}</ul>{pills(pr["tags"], small=True)}{btn}</div></details>'
        )
    hidden = max(0, len(items) - LIMIT_PROJECTS)
    body = f'<div class="proj-list" id="projects-list" data-list>{"".join(items)}</div>' + more_button("projects-list", hidden, f"Show more ({hidden})")
    return panel("projects", "Projects", body, count=len(p["projects"]), flush=True)


def lab(p: dict) -> str:
    items = []
    for i, it in enumerate(p["lab"]["items"]):
        extra = " data-extra hidden" if i >= LIMIT_LAB else ""
        items.append(
            f'<a class="lab-item" id="lab-{C.slug(it["name"])}" href="{e(it["url"], quote=True)}" target="_blank" rel="noopener noreferrer"{extra}>'
            f'<span class="lab-top"><span class="p-name">{e(it["name"])}</span><span class="tag">Spec</span>{ic("arrow-up-right", "i go")}</span>'
            f'<p>{e(it["summary"])}</p>{pills(it["tags"], small=True)}</a>'
        )
    hidden = max(0, len(items) - LIMIT_LAB)
    body = f'<div id="lab-list" data-list>{"".join(items)}</div>' + more_button("lab-list", hidden, f"Show more ({hidden})")
    return panel("lab", "Lab", body, count=len(items), note=p["lab"]["note"], flush=True)


def research(p: dict) -> str:
    return panel("research", "Research Signals", pills(p["research"]), count=len(p["research"]))


def optional_lists(p: dict) -> str:
    out = []
    for key, title in (("awards", "Awards"), ("certifications", "Certifications")):
        items = p.get(key) or []
        if not items:
            continue
        rows = []
        for it in items:
            name = it.get("title") or it.get("name", "")
            head = link(it["url"], name) if it.get("url") else e(name)
            sub = " · ".join(x for x in (it.get("issuer"), str(it.get("year", "")) or None) if x)
            rows.append(f'<li class="edu"><div><h3>{head}</h3><div class="meta"><span>{e(sub)}</span></div></div></li>')
        out.append(SEP + panel(key, title, f'<ul>{"".join(rows)}</ul>', count=len(items), flush=True))
    return "".join(out)


def footer(p: dict, contrib: dict) -> str:
    repo = p["site"]["repo"]
    rows = [
        ("Crafted by", link(f'https://github.com/{p["person"]["username"]}', "@" + p["person"]["username"])),
        ("Build", f"{e(C.build_id())} · {C.today().isoformat()}"),
        ("Source", link(f"https://github.com/{repo}", f"github.com/{repo}")),
        ("Typeface", link("https://vercel.com/font", "Geist Sans & Mono")),
        ("Stack", "Static HTML · CSS · vanilla JS, generated by Python"),
        ("Inspired by", link("https://chanhdai.com", "chanhdai.com (MIT)")),
    ]
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    closing = f'<p class="closing">{e(p["cta"])}</p>' if p.get("cta") else ""
    return (
        f'<footer class="footer"><h2 class="sr-only">About this site</h2><dl class="details">{dl}</dl>{closing}'
        f'<p class="agents">For agents: <a class="u" href="llms.txt">llms.txt</a> · <a class="u" href="index.md">index.md</a></p></footer>'
    )


def palette_items(p: dict) -> list[dict]:
    items = [{"group": "Sections", "label": t, "href": "#" + a, "keywords": k} for t, a, k in (
        ("Overview", "overview", "about me"), ("Social Links", "social-links", "contact"),
        ("GitHub Contributions", "github-contributions", "activity heatmap"), ("About", "about", "bio"),
        ("Principles", "principles", "philosophy"), ("Focus", "focus", "skills"), ("Stack", "stack", "tech skills"),
        ("Experience", "experience", "work jobs career"), ("Education", "education", "university degree"),
        ("Projects", "projects", "work"), ("Lab", "lab", "specs architecture"), ("Research Signals", "research", "topics"),
    )]
    items += [{"group": "Projects", "label": x["name"], "hint": x["kind"], "href": "#project-" + x["id"], "keywords": x["category"] + " " + " ".join(x["tags"])} for x in p["projects"]]
    items += [{"group": "Lab", "label": x["name"], "hint": "GitHub", "href": x["url"], "keywords": x["summary"]} for x in p["lab"]["items"]]
    items += [{"group": "Links", "label": l["label"], "hint": l["handle"], "href": l["href"]} for l in p["links"]]
    items += [
        {"group": "Actions", "label": "Toggle theme", "hint": "D", "action": "theme", "keywords": "dark light mode"},
        {"group": "Actions", "label": "Copy page link", "action": "copy", "keywords": "url share"},
    ]
    return items


def palette_dialog(p: dict) -> str:
    data = json.dumps(palette_items(p), ensure_ascii=False).replace("</", "<\\/")
    return f"""
<dialog id="palette" class="palette" aria-label="Command palette">
  <div class="palette-input">{ic("search", "i i-lg")}<input type="text" placeholder="Search…" aria-label="Search" role="combobox" aria-expanded="true" aria-controls="palette-list" autocomplete="off" spellcheck="false"></div>
  <div class="palette-list" id="palette-list" role="listbox"></div>
  <div class="palette-foot"><span>↑↓ navigate</span><span>↵ open</span><span>esc close</span></div>
</dialog>
<script type="application/json" id="palette-data">{data}</script>"""


# --------------------------------------------------------------------------- #
# page shell
# --------------------------------------------------------------------------- #
THEME_INIT = (
    "(function(){try{var t=localStorage.getItem('theme');if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';"
    "document.documentElement.dataset.theme=t;var m=document.querySelector('meta[name=theme-color]');"
    "if(m)m.content=t==='dark'?'#0a0a0a':'#ffffff'}catch(e){}})()"
)


def json_ld(p: dict, base: str) -> str:
    per = p["person"]
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": per["name"],
        "jobTitle": "Software Engineer",
        "description": p["site"]["description"],
        "url": base,
        "image": base + "assets/img/avatar-dark.webp",
        "sameAs": [l["href"] for l in p["links"]],
        "address": {"@type": "PostalAddress", "addressLocality": "Babol", "addressRegion": "Mazandaran", "addressCountry": "IR"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Mazandaran University of Science and Technology"},
    }
    return json.dumps(data, ensure_ascii=False)


def head(p: dict, base: str, title: str, canonical: str, extra: str = "") -> str:
    s = p["site"]
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(s['description'], quote=True)}">
<link rel="canonical" href="{e(canonical, quote=True)}">
<meta name="theme-color" content="#ffffff">
<script>{THEME_INIT}</script>
<meta property="og:type" content="profile">
<meta property="og:site_name" content="{e(p['person']['name'])}">
<meta property="og:title" content="{e(title, quote=True)}">
<meta property="og:description" content="{e(s['description'], quote=True)}">
<meta property="og:url" content="{e(canonical, quote=True)}">
<meta property="og:image" content="{e(base)}assets/img/og.png">
<meta property="og:locale" content="{e(s['locale'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title, quote=True)}">
<meta name="twitter:description" content="{e(s['description'], quote=True)}">
<meta name="twitter:image" content="{e(base)}assets/img/og.png">
<link rel="icon" href="{extra}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{extra}assets/css/site.css">"""


def header(p: dict) -> str:
    gh = next(l for l in p["links"] if l["id"] == "github")
    nav = "".join(f'<a href="#{a}">{t}</a>' for t, a in (("About", "about"), ("Stack", "stack"), ("Experience", "experience"), ("Projects", "projects"), ("Lab", "lab")))
    initials = "".join(w[0] for w in p["person"]["name"].split()).upper()
    return f"""
<header class="site-header">
  <div class="container header-in">
    <a class="logo" href="#top" aria-label="{e(p['person']['name'])} — home">{e(initials)}</a>
    <nav class="nav" aria-label="Sections">{nav}</nav>
    <button class="search-btn" type="button" data-open-palette aria-label="Search (Ctrl or Command + K)">{ic("search")}<span class="txt">Search…</span><span class="kbd" aria-hidden="true">{ic("command")}K</span></button>
    <a class="icon-btn" href="{e(gh['href'], quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="GitHub">{ic("github", "i i-lg")}</a>
    <button class="icon-btn" type="button" data-toggle-theme aria-label="Toggle theme"><span class="only-light">{ic("moon", "i i-lg")}</span><span class="only-dark">{ic("sun", "i i-lg")}</span></button>
  </div>
</header>"""


def index_html(p: dict, contrib: dict, base: str) -> str:
    _used_icons.clear()
    body_sections = [
        cover(p), SEP, overview(p), SEP, socials(p, base), SEP, contributions(contrib), SEP, about(p), SEP,
        principles(p), SEP, focus(p), SEP, stack(p), SEP, experience(p), SEP, education(p), SEP, projects(p), SEP, lab(p), SEP, research(p),
    ]
    main = "".join(body_sections) + optional_lists(p) + SEP + footer(p, contrib)
    hdr = header(p)
    pal = palette_dialog(p)
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
{head(p, base, p['site']['title'], base)}
<script type="application/ld+json">{json_ld(p, base)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{sprite_placeholder}
{hdr}
<main id="main" class="container">{main}</main>
{pal}
<script src="assets/js/app.js" defer></script>
</body>
</html>
""".replace(sprite_placeholder, sprite())


sprite_placeholder = "<!--SPRITE-->"


def not_found(p: dict, base: str) -> str:
    _used_icons.clear()
    back = f'<a class="btn" href="{e(base)}">Back to home {ic("arrow-up-right")}</a>'
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
{head(p, base, "Page not found – " + p['person']['name'], base, extra=base)}
<meta name="robots" content="noindex">
</head>
<body>
{sprite()}
<main class="container nf"><h1 class="mono">404</h1><p>This page doesn't exist. Nothing to find here, but the real system is one click away.</p>
{back}</main>
<script src="{e(base)}assets/js/app.js" defer></script>
</body>
</html>
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><style>rect{fill:#0a0a0a}text{fill:#fafafa}@media (prefers-color-scheme:dark){rect{fill:#fafafa}text{fill:#0a0a0a}}</style><rect width="32" height="32" rx="8"/><text x="16" y="21" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="14" font-weight="700">PE</text></svg>
"""


def build() -> None:
    p = C.load_profile()
    contrib = C.load_contributions()
    base = p["site"]["url"]
    if not base.endswith("/"):
        base += "/"

    (SITE / "assets" / "img").mkdir(parents=True, exist_ok=True)
    for name in ("avatar-light.webp", "avatar-dark.webp"):
        src = AVATARS / name
        if src.exists():
            shutil.copyfile(src, SITE / "assets" / "img" / name)
    fonts.write_site_fonts(SITE / "assets" / "fonts")

    html = index_html(p, contrib, base)
    # the sprite must be produced after the sections registered their icons
    (SITE / "index.html").write_text(html, encoding="utf-8")
    (SITE / "404.html").write_text(not_found(p, base), encoding="utf-8")
    (SITE / "favicon.svg").write_text(FAVICON, encoding="utf-8")

    md = markdown.render(p, contrib, base)
    (SITE / "index.md").write_text(md, encoding="utf-8")
    (SITE / "llms.txt").write_text(
        f"# {p['person']['name']}\n\n> {p['site']['description']}\n\n"
        f"- [Full profile (Markdown)]({base}index.md)\n- [Website]({base})\n"
        f"- [GitHub](https://github.com/{p['person']['username']})\n- [Portfolio]({p['site']['portfolio']})\n",
        encoding="utf-8",
    )
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n", encoding="utf-8")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{base}</loc><lastmod>{C.today().isoformat()}</lastmod></url></urlset>\n",
        encoding="utf-8",
    )
    print(f"site: wrote {SITE.relative_to(ROOT)}/index.html ({len(html) // 1024} KB), 404.html, llms.txt, index.md, sitemap.xml")


if __name__ == "__main__":
    build()
