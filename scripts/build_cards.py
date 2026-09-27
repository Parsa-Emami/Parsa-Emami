#!/usr/bin/env python3
"""Render every README card as a light + dark SVG pair into assets/cards/.

Each card is a panel in the chanhdai.com style: hairline borders, a diagonal
hatch strip, Geist type, mono "Fig." captions. Text is wrapped with real font
metrics and the glyphs are embedded, so the images look the same everywhere.
"""
from __future__ import annotations

from pathlib import Path

from lib import content as C
from lib import fonts, heat
from lib.svgkit import HATCH_H, HEAD_H, PAD, THEMES, W, Doc, assemble, jpeg_data_uri

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "cards"
AVATARS = ROOT / "assets" / "avatar"

BODY_Y = HATCH_H + HEAD_H + 1      # first pixel below the header line
INNER = W - 2 * PAD


# --------------------------------------------------------------------------- #
# generic helpers
# --------------------------------------------------------------------------- #
def grid(d: Doc, y: float, cells, cols: int = 2) -> float:
    """Lined grid. ``cells`` are callables (sub_doc, width) -> height. Returns bottom y."""
    cw = W / cols
    i = 0
    while i < len(cells):
        row = cells[i:i + cols]
        subs = []
        for fn in row:
            s = d.sub()
            subs.append((s, fn(s, cw)))
        h = max(hh for _, hh in subs)
        for j, (s, _) in enumerate(subs):
            d.place(s, j * cw, y)
        if i + cols < len(cells):
            d.line(0, y + h, W, y + h)
        y += h
        i += cols
    for j in range(1, cols):
        d.vline(j * cw, BODY_Y, y)
    return y


def finish(d: Doc, bottom: float, title: str, desc: str, head=None, css: str = "") -> str:
    return assemble(d, bottom, title, desc, css=css, head=head)


# --------------------------------------------------------------------------- #
# hero
# --------------------------------------------------------------------------- #
def hero(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    per = p["person"]
    cover_h = 132
    d.hatch(0, 0, W, cover_h)
    d.line(0, cover_h, W, cover_h)

    # Fig. 1 caption (bottom-right of the cover)
    cap_a, cap_b = "Fig. 1.", f" {per['name']}, {per['coordinates']}."
    cw = fonts.text_width(cap_a + cap_b, 11.5, 400, True) + 18
    bx, by = W - 14 - cw, cover_h - 12 - 22
    d.rect(bx + .5, by + .5, cw - 1, 21, fill=t["bg"], stroke=t["border"], rx=6)
    d.spans(bx + 9, by + 15, [(cap_a, t["fg"], 400), (cap_b, t["muted_fg"], 400)], size=11.5)

    # avatar straddling the cover line: outer ring + image
    cx, cy, r = PAD + 76, cover_h, 68
    uri = jpeg_data_uri(AVATARS / t["avatar"], 272)
    clip = d.uid("av")
    d.defs.append(f'<clipPath id="{clip}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    d.circle(cx, cy, r + 6, fill=t["bg"], stroke=t["border"])
    d.parts.append(
        f'<image x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" href="{uri}" xlink:href="{uri}" '
        f'clip-path="url(#{clip})" preserveAspectRatio="xMidYMid slice"/>'
    )
    d.circle(cx, cy, r, stroke=t["border"])

    # identity
    x = cx + r + 30
    d.text(x, cover_h + 44, per["name"], 32, 600, t["fg"])
    d.text(x, cover_h + 70, per["role"], 14.5, 400, t["muted_fg"])
    flips = per["flip"]
    fy = cover_h + 98
    for i, s in enumerate(flips):
        d.text(x, fy, s, 14, 400, t["muted_fg"], mono=True, cls=f"f f{i}")
    row_b = fy + 24
    d.line(0, row_b, W, row_b)

    # overview
    y = row_b + 24
    for row in p["overview"]:
        d.icon_box(PAD, y, row["icon"])
        d.text(PAD + 42, y + 19, C.parts_text(row["parts"]), 15, 400, t["fg"])
        y += 40
    bottom = y + 6

    n = len(flips)
    slot = 2.8
    total = n * slot
    pct = 100 / n
    css = (
        f"@keyframes flip{{0%{{opacity:0;transform:translateY(8px)}}2.5%{{opacity:1;transform:translateY(0)}}"
        f"{pct - 3:.2f}%{{opacity:1;transform:translateY(0)}}{pct - 0.5:.2f}%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}"
        f".f{{opacity:0;animation:flip {total:g}s infinite}}.f0{{opacity:1}}"
        + "".join(f".f{i}{{animation-delay:{i * slot:g}s}}" for i in range(n))
        + "@media (prefers-reduced-motion:reduce){.f{animation:none}}"
    )
    desc = f"{per['name']} — {per['role']}. " + " ".join(C.parts_text(r["parts"]) + "." for r in p["overview"])
    return assemble(d, bottom, f"{per['name']} — profile", desc, css=css)


# --------------------------------------------------------------------------- #
# social buttons (each one is a separate image so it can be a real link)
# --------------------------------------------------------------------------- #
def social_button(tn: str, icon: str, label: str, w: int = 196, h: int = 46) -> str:
    d = Doc(tn)
    t = d.t
    d.rect(.5, .5, w - 1, h - 1, fill=t["bg"], stroke=t["border"], rx=10)
    d.icon(icon, 16, h / 2 - 9, 18, t["fg"])
    d.text(44, h / 2 + 5, label, 14.5, 500, t["fg"])
    d.icon("arrow-up-right", w - 32, h / 2 - 8, 16, t["muted_fg"])
    return assemble(d, h, label, f"Open {label}", width=w, frame=False)


# --------------------------------------------------------------------------- #
# contributions
# --------------------------------------------------------------------------- #
def contributions(tn: str, p: dict, contrib: dict) -> str:
    d = Doc(tn)
    t = d.t
    days = contrib.get("days", [])
    cells, cols, labels = heat.build(days)
    gap = 3
    pitch = (INNER + gap) / max(cols, 1)
    cell = pitch - gap
    top = BODY_Y + 22
    for col, name in labels:
        d.text(PAD + col * pitch, top - 8, name, 10.5, 400, t["muted_fg"], mono=True)
    parts = []
    for c in cells:
        parts.append(
            f'<rect class="c" x="{PAD + c.col * pitch:.2f}" y="{top + c.row * pitch:.2f}" width="{cell:.2f}" height="{cell:.2f}" '
            f'rx="2.5" fill="{t["heat"][c.level]}" style="animation-delay:{c.col * 14}ms"/>'
        )
    d.parts.append("".join(parts))
    y = top + 7 * pitch + 20
    r = contrib.get("range", {})
    total = contrib.get("total_contributions", 0)
    cap = f" {total:,} contributions, {C.fmt_day(r['start'])} – {C.fmt_day(r['end'])}. Source: GitHub." if r.get("start") else " No activity data yet."
    d.spans(PAD, y, [("Fig. 2.", t["fg"], 400), (cap, t["muted_fg"], 400)], size=11.5)
    # legend
    lx = W - PAD
    d.text(lx, y, "More", 11, 400, t["muted_fg"], mono=True, anchor="end")
    lx -= fonts.text_width("More", 11, 400, True) + 8
    for i in range(4, -1, -1):
        d.rect(lx - 11, y - 10, 11, 11, fill=t["heat"][i], rx=2.5)
        lx -= 15
    d.text(lx - 3, y, "Less", 11, 400, t["muted_fg"], mono=True, anchor="end")
    bottom = y + 26
    css = "@keyframes pop{from{opacity:0}to{opacity:1}}.c{animation:pop .4s ease backwards}@media (prefers-reduced-motion:reduce){.c{animation:none}}"
    return finish(d, bottom, "GitHub contributions", f"Contribution heatmap: {total} contributions in the last year.", head=("GitHub Contributions", 0), css=css)


# --------------------------------------------------------------------------- #
# about / principles / focus
# --------------------------------------------------------------------------- #
def about(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y + 24
    for para in p["about"]:
        d.rect(PAD, y + 8, 5, 5, fill=t["ring"], rx=1)
        y = d.para(PAD + 20, y, para, 690, size=15, fill=t["fg"], lh=25) + 14
    bottom = y - 14 + 26
    return finish(d, bottom, "About", " ".join(C.plain(x) for x in p["about"]), head=("About", 0))


def principles(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t

    def make(i, x):
        def draw(s: Doc, w: float) -> float:
            s.text(PAD, 36, f"{i:02d}", 12, 500, t["muted_fg"], mono=True)
            s.text(PAD + 26, 36, x["verb"], 12, 500, t["muted_fg"], mono=True)
            s.text(PAD, 66, x["title"], 16, 600, t["fg"])
            b = s.para(PAD, 78, x["text"], w - 2 * PAD, size=13.5, fill=t["muted_fg"], lh=21)
            return b + 22
        return draw

    bottom = grid(d, BODY_Y, [make(i, x) for i, x in enumerate(p["principles"], 1)])
    return finish(d, bottom, "Principles", " ".join(f"{x['verb']}: {x['title']}" for x in p["principles"]), head=("Principles", len(p["principles"])))


def focus(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t

    def make(x):
        def draw(s: Doc, w: float) -> float:
            s.icon_box(PAD, 24, x["icon"])
            s.text(PAD, 80, x["title"], 15.5, 600, t["fg"])
            b = s.para(PAD, 90, x["text"], w - 2 * PAD, size=13.5, fill=t["muted_fg"], lh=21)
            return b + 22
        return draw

    bottom = grid(d, BODY_Y, [make(x) for x in p["focus"]])
    return finish(d, bottom, "Focus", " ".join(x["title"] + "." for x in p["focus"]), head=("Focus", len(p["focus"])))


# --------------------------------------------------------------------------- #
# stack
# --------------------------------------------------------------------------- #
def stack(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y
    left, right, rw = PAD, 262, W - 262 - PAD
    for i, g in enumerate(p["stack"], 1):
        if i > 1:
            d.line(0, y, W, y)
        top = y + 20
        d.text(left, top + 15, f"{i:02d}", 12, 400, t["muted_fg"], mono=True)
        name_lines = fonts.wrap_text(g["name"], 190, 14.5, 500)
        for k, ln in enumerate(name_lines):
            d.text(left + 28, top + 15 + k * 20, ln, 14.5, 500, t["fg"])
        bottom_chips = d.chips(right, top, [x["name"] for x in g["items"]], rw, size=12.5, h=26, gap=8, pad=10, rx=8, fg=t["fg"])
        y = max(bottom_chips, top + 15 + (len(name_lines) - 1) * 20 + 6) + 20
    return finish(d, y, "Stack", "; ".join(f"{g['name']}: " + ", ".join(x["name"] for x in g["items"]) for g in p["stack"]), head=("Stack", 0))


# --------------------------------------------------------------------------- #
# experience & education
# --------------------------------------------------------------------------- #
def experience(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y
    tx = 76                       # text column for positions
    for ci, ex in enumerate(p["experience"]):
        if ci:
            d.line(0, y, W, y)
        y += 22
        d.tile(PAD, y, 40, ex["monogram"])
        d.text(PAD + 56, y + 17, ex["company"], 17, 600, t["fg"])
        meta = [x for x in (ex.get("location"), ex.get("location_type")) if x]
        current = any(pos["end"] is None for pos in ex["positions"])
        if current:
            meta.append("Current")
        d.text(PAD + 56, y + 35, " · ".join(meta), 12, 400, t["muted_fg"], mono=True)
        y += 40 + 18
        first_dot = None
        last_dot = y
        for pos in ex["positions"]:
            first_dot = first_dot if first_dot is not None else y + 8
            last_dot = y + 8
            d.circle(PAD + 20, y + 8, 4, fill=t["bg"], stroke=t["ring"])
            d.text(tx, y + 13, pos["title"], 15, 500, t["fg"])
            bits = [pos["type"], C.fmt_period(pos["start"], pos["end"]), C.duration(pos["start"], pos["end"])]
            if pos.get("location_type"):
                bits.append(pos["location_type"])
            d.text(tx, y + 33, " · ".join(bits), 12, 400, t["muted_fg"], mono=True)
            b = d.para(tx, y + 46, pos["description"], W - tx - PAD, size=13.5, fill=t["muted_fg"], lh=21)
            b = d.chips(tx, b + 10, pos["skills"], W - tx - PAD, size=12, h=24, gap=6)
            y = b + 22
        if first_dot is not None:
            d.vline(PAD + 20, first_dot, y - 22 if len(ex["positions"]) > 1 else last_dot + 4, stroke=t["border"])
        y += 4
    return finish(d, y, "Experience", "; ".join(f"{e['company']}: " + ", ".join(x['title'] for x in e['positions']) for e in p["experience"]),
                  head=("Experience", len(p["experience"])))


def education(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y
    for i, ed in enumerate(p["education"]):
        if i:
            d.line(0, y, W, y)
        y += 20
        mono = "".join(w[0] for w in ed["school"].split() if w[0].isupper())[:4] or "EDU"
        d.tile(PAD, y, 40, mono)
        d.text(PAD + 56, y + 16, f"{ed['degree']}, {ed['field']}", 16, 600, t["fg"])
        d.text(PAD + 56, y + 36, ed["school"], 13.5, 400, t["muted_fg"])
        bits = [f"{ed['start']}—{ed['end']}"] + ([ed["status"]] if ed.get("status") else [])
        d.text(PAD + 56, y + 55, " · ".join(bits), 12, 400, t["muted_fg"], mono=True)
        y += 60 + 20
    return finish(d, y, "Education", "; ".join(f"{e['degree']}, {e['field']} — {e['school']}" for e in p["education"]),
                  head=("Education", len(p["education"])))


# --------------------------------------------------------------------------- #
# projects / lab / research
# --------------------------------------------------------------------------- #
def projects(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y
    for i, pr in enumerate(p["projects"]):
        if i:
            d.line(0, y, W, y)
        y += 20
        wname = d.text(PAD, y + 16, pr["name"], 16, 600, t["fg"])
        wtag = d.tag(PAD + wname + 10, y + 1, pr["kind"])
        d.text(PAD + wname + 10 + wtag + 12, y + 15, pr["category"], 13, 400, t["muted_fg"])
        b = d.para(PAD, y + 30, pr["summary"], INNER - 20, size=13.5, fill=t["muted_fg"], lh=21)
        b = d.chips(PAD, b + 10, pr["tags"], INNER, size=12, h=24, gap=6)
        y = b + 20
    return finish(d, y, "Projects", "; ".join(f"{x['name']} ({x['kind']}): {x['category']}" for x in p["projects"]),
                  head=("Projects", len(p["projects"])))


def lab(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y + 18
    y = d.para(PAD, y, p["lab"]["note"], 640, size=13.5, fill=t["muted_fg"], lh=21) + 18
    d.line(0, y, W, y)
    top = y

    def make(it):
        def draw(s: Doc, w: float) -> float:
            wn = s.text(PAD, 38, it["name"], 15.5, 600, t["fg"])
            s.tag(PAD + wn + 10, 23, "Spec")
            b = s.para(PAD, 50, it["summary"], w - 2 * PAD, size=13, fill=t["muted_fg"], lh=20)
            b = s.chips(PAD, b + 10, it["tags"], w - 2 * PAD, size=11.5, h=23, gap=6, pad=8)
            return b + 20
        return draw

    cells = [make(x) for x in p["lab"]["items"]]
    cw = W / 2
    i = 0
    while i < len(cells):
        subs = []
        for fn in cells[i:i + 2]:
            s = d.sub()
            subs.append((s, fn(s, cw)))
        h = max(hh for _, hh in subs)
        for j, (s, _) in enumerate(subs):
            d.place(s, j * cw, y)
        if i + 2 < len(cells):
            d.line(0, y + h, W, y + h)
        y += h
        i += 2
    d.vline(cw, top, y)
    return finish(d, y, "Lab", "; ".join(f"{x['name']}: {x['summary']}" for x in p["lab"]["items"]), head=("Lab", len(p["lab"]["items"])))


def research(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    y = BODY_Y + 22
    b = d.chips(PAD, y, p["research"], INNER, size=13, h=28, gap=8, pad=11, rx=8, fg=t["fg"])
    return finish(d, b + 24, "Research Signals", "; ".join(p["research"]), head=("Research Signals", len(p["research"])))


# --------------------------------------------------------------------------- #
# footer
# --------------------------------------------------------------------------- #
def footer(tn: str, p: dict) -> str:
    d = Doc(tn)
    t = d.t
    repo = p["site"]["repo"]
    rows = [
        ("Crafted by", "@" + p["person"]["username"]),
        ("Build", f"{C.build_id()} · {C.today().isoformat()}"),
        ("Source", f"github.com/{repo}"),
        ("Typeface", "Geist Sans & Mono"),
        ("Stack", "Python · SVG · GitHub Actions"),
        ("Inspired by", "chanhdai.com (MIT)"),
    ]
    y = 34
    for k, v in rows:
        d.text(PAD, y, k, 12, 400, t["muted_fg"], mono=True)
        d.text(PAD + 116, y, v, 12, 400, t["fg"], mono=True)
        y += 22
    y += 8
    d.text(PAD, y, p.get("cta", ""), 14, 400, t["fg"])
    return assemble(d, y + 26, "About this profile", "Build details and credits", frame=True)


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def build() -> list[str]:
    p = C.load_profile()
    contrib = C.load_contributions()
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for tn in THEMES:
        jobs = {
            "hero": hero(tn, p),
            "contributions": contributions(tn, p, contrib),
            "about": about(tn, p),
            "principles": principles(tn, p),
            "focus": focus(tn, p),
            "stack": stack(tn, p),
            "experience": experience(tn, p),
            "education": education(tn, p),
            "projects": projects(tn, p),
            "lab": lab(tn, p),
            "research": research(tn, p),
            "footer": footer(tn, p),
        }
        for l in p["links"]:
            jobs[f"social-{l['id']}"] = social_button(tn, l["icon"], l["label"])
        jobs["social-site"] = social_button(tn, "monitor", "Interactive site")
        for name, svg in jobs.items():
            path = OUT / f"{name}-{tn}.svg"
            path.write_text(svg, encoding="utf-8")
            written.append(str(path.relative_to(ROOT)))
    print(f"cards: wrote {len(written)} SVGs to {OUT.relative_to(ROOT)}/")
    return written


if __name__ == "__main__":
    build()
