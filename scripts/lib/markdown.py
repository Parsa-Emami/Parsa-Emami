"""Plain-text Markdown rendition of the whole profile.

Used for the collapsible "plain-text version" at the bottom of the README
(screen readers, search, copy/paste), and for site/index.md + site/llms.txt.
"""
from __future__ import annotations

from . import content as C


def render(p: dict, contrib: dict, base: str) -> str:
    person = p["person"]
    L: list[str] = []
    a = L.append
    a(f"# {person['name']}")
    a("")
    a(f"**{person['role']}** · {person['location']}")
    a("")
    a(f"> {p['person']['flip'][0]}")
    a("")
    a("## Overview")
    a("")
    for row in p["overview"]:
        bits = []
        for part in row["parts"]:
            bits.append(f"[{part['t']}]({C.resolve(part['href'], base)})" if part.get("href") else part["t"])
        a("- " + " ".join(bits))
    a("")
    a("## Links")
    a("")
    for l in p["links"]:
        a(f"- [{l['label']}]({l['href']}) — {l['handle']}")
    a(f"- [Interactive site]({base})")
    a("")
    a(p.get("cta", ""))
    a("")
    a("## About")
    a("")
    for t in p["about"]:
        a("- " + C.to_md(t, base))
    a("")
    a("## Principles")
    a("")
    for i, x in enumerate(p["principles"], 1):
        a(f"{i}. **{x['verb']} — {x['title']}** {x['text']}")
    a("")
    a("## Focus")
    a("")
    for x in p["focus"]:
        a(f"- **{x['title']}** — {x['text']}")
    a("")
    a("## Stack")
    a("")
    for i, g in enumerate(p["stack"], 1):
        names = ", ".join(x["name"] for x in g["items"])
        a(f"{i:02d}. **{g['name']}** — {names}")
    a("")
    a("## Experience")
    a("")
    for e in p["experience"]:
        loc = ", ".join(x for x in (e.get("location"), e.get("location_type")) if x)
        a(f"### {e['company']}" + (f" ({loc})" if loc else ""))
        a("")
        for pos in e["positions"]:
            per = C.fmt_period(pos["start"], pos["end"])
            a(f"- **{pos['title']}** · {pos['type']} · {per} · {C.duration(pos['start'], pos['end'])}")
            a(f"  {pos['description']}")
            a(f"  Skills: {', '.join(pos['skills'])}")
        a("")
    a("## Education")
    a("")
    for e in p["education"]:
        st = f" ({e['status']})" if e.get("status") else ""
        a(f"- **{e['degree']}, {e['field']}** — {e['school']} · {e['start']}—{e['end']}{st}")
    a("")
    a(f"## Projects ({len(p['projects'])})")
    a("")
    for pr in p["projects"]:
        title = f"[{pr['name']}]({pr['url']})" if pr.get("url") else pr["name"]
        a(f"### {title} · {pr['kind']}")
        a("")
        a(f"*{pr['category']}.* {pr['summary']}")
        a("")
        for b in pr["bullets"]:
            a(f"- {b}")
        a("")
        a(f"Tech: {', '.join(pr['tags'])}")
        a("")
    lab = p["lab"]
    a(f"## Lab ({len(lab['items'])})")
    a("")
    a(lab["note"])
    a("")
    for it in lab["items"]:
        a(f"- [{it['name']}]({it['url']}) — {it['summary']} ({', '.join(it['tags'])})")
    a("")
    a("## Research signals")
    a("")
    for r in p["research"]:
        a(f"- {r}")
    a("")
    for key, title in (("awards", "Awards"), ("certifications", "Certifications")):
        items = p.get(key) or []
        if items:
            a(f"## {title}")
            a("")
            for it in items:
                a(f"- {it.get('title') or it.get('name')} — {it.get('issuer', '')} {it.get('year', '')}".rstrip())
            a("")
    r = contrib.get("range", {})
    if r.get("start"):
        a("## GitHub activity")
        a("")
        a(f"{contrib['total_contributions']} contributions, {C.fmt_day(r['start'])} – {C.fmt_day(r['end'])}. Source: GitHub.")
        a("")
    return "\n".join(L).rstrip() + "\n"
