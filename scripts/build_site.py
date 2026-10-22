from __future__ import annotations

import json
import shutil
from html import escape as e
from pathlib import Path

import make_og
from build_cards import study
from lib import content as C, fonts, markdown

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
TEMPLATES = ROOT / 'scripts' / 'templates'


def arrow():
    return '<svg class="arrow" width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'


def link(url, label, cls='text-link'):
    return f'<a class="{cls}" href="{e(url, quote=True)}">{e(label)}{arrow()}</a>'


def picture(name, alt):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/art/{name}-dark.svg">'
            f'<img src="assets/art/{name}-light.svg" data-themed="assets/art/{name}" alt="{e(alt, quote=True)}" width="830" height="290" loading="lazy"></picture>')


def theme_css(p):
    def block(selector, theme):
        scheme = 'dark' if theme == p['design']['themes']['dark'] else 'light'
        return selector+'{'+''.join(f'--{k}:{v};' for k, v in theme.items())+f'color-scheme:{scheme};'+'}'
    themes = p['design']['themes']
    return block(':root', themes['light']) + block(':root[data-theme="dark"]', themes['dark']) + '@media(prefers-color-scheme:dark){' + block(':root:not([data-theme="light"])', themes['dark']) + '}\n'


def render(p):
    per, hero, method = p['person'], p['hero'], p['method']
    base = p['site']['url']
    nav = f'<a href="#work">Work</a><a href="#about">About</a><a href="#notes">Notes</a><a href="{base}resume/">Résumé</a>'
    steps = ''.join(f'<article><span class="eyebrow accent">{i:02d} / {e(x["verb"].upper())}</span><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p><p class="question">{e(x["question"])}</p></article>' for i, x in enumerate(method['steps'], 1))
    work = []
    for i, x in enumerate(p['projects'], 1):
        alt = f'Conceptual {x["name"]} study; not an application screenshot.'
        work.append(f'<article class="work-feature"><div class="work-meta"><span>{i:02d} / {e(x["category"])}</span><span class="status">{e(x["status"])}</span></div><a class="work-art" href="{e(x["url"], quote=True)}" aria-label="Explore {e(x["name"])} source">{picture("study-"+x["id"], alt)}<span class="work-open">{arrow()}</span></a><div class="work-description"><h3>{e(x["name"])}<span>{e(x["title"])}</span></h3><div><p>{e(x["summary"])}</p><p class="scope">{e(x["scope"])}</p><div class="project-links">{link(x["url"], "Source")}{link(x["case_study"], "Project notes")}</div></div></div></article>')
    explorations = ''.join(f'<a href="{e(x["url"], quote=True)}"><span>{e(x["name"])}</span><small>{e(x["label"])}</small>{arrow()}</a>' for x in p['explorations'])
    focus = ''.join(f'<div><h3>{e(x["title"])}</h3><ul>'+''.join(f'<li>{e(t)}</li>' for t in x['items'])+'</ul></div>' for x in p['focus'])
    notes = ''.join(f'<a class="note" href="{e(x["url"], quote=True)}"><span class="eyebrow accent">{i:02d}</span><div><p class="eyebrow">{e(x["category"])}</p><h3>{e(x["title"])}</h3></div>{arrow()}</a>' for i, x in enumerate(p['notes'], 1))
    same_as = [x['href'] for x in p['links'] if x['id'] != 'website']
    structured = json.dumps({'@context':'https://schema.org', '@type':'Person', 'name':per['name'], 'alternateName':per['alternate_names'], 'url':base, 'jobTitle':'Software Engineer & Security Architect', 'sameAs':same_as}, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['site']['title'])}</title>
<meta name="description" content="{e(p['site']['description'], quote=True)}">
<meta name="robots" content="noindex,follow"><meta name="color-scheme" content="light dark">
<link rel="canonical" href="{base}"><link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="profile"><meta property="og:title" content="{e(p['site']['title'], quote=True)}"><meta property="og:description" content="{e(p['site']['description'], quote=True)}"><meta property="og:url" content="{base}"><meta property="og:image" content="{p['site']['pages_url']}assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin>
<script src="assets/js/theme-init.js"></script><link rel="stylesheet" href="assets/css/site.css"><script src="assets/js/app.js" defer></script>
<script type="application/ld+json">{structured}</script>
</head>
<body id="top">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><a class="brand" href="#top" aria-label="Parsa Emami, home"><span class="monogram" aria-hidden="true">p<span>e</span></span>{e(per['brand'])}<b aria-hidden="true">.</b></a><nav aria-label="Main">{nav}</nav><button type="button" class="theme-toggle" hidden aria-label="Color theme: System. Switch to light mode."><span aria-hidden="true">◐</span><span data-theme-label>System</span></button>{link('#contact', 'Let’s talk', 'header-contact')}</header>
<main id="main" tabindex="-1">
<section class="hero wrap" aria-labelledby="hero-name"><div class="hero-top eyebrow"><span><i></i>{e(hero['eyebrow'])}</span><span>BASED IN IRAN <b>↗</b> OPEN WORLDWIDE</span></div><div class="hero-name-row"><h1 id="hero-name">Parsa Emami<span>.</span></h1><p class="eyebrow independent">INDEPENDENT<br>BY DESIGN.</p></div><div class="hero-rule eyebrow"><span>01 — A MIND AT WORK</span><span>SOFTWARE + SECURITY</span></div><div class="hero-grid"><div class="identity"><img src="assets/img/avatar-dark.webp" width="76" height="86" alt="Parsa Emami" fetchpriority="high"><p>Software engineer.<br>Security architect.</p><small>{e(per['perspective'])}</small>{link(base+'about/', 'The person behind the code')}</div><div class="hero-copy"><h2>{e(hero['title'])}<br><em>{e(hero['accent'])}</em></h2><p>{e(hero['intro'])}</p><div class="button-row">{link('#work', 'Explore selected work', 'button primary')}{link('#contact', 'Let’s talk')}</div></div><div class="hero-asides"><p class="eyebrow">ENGINEERING, WITH PERSPECTIVE.</p><p>Build with intent.<small>Software engineering</small></p><p>Make boundaries clear.<small>Security architecture</small></p><p>Look past the obvious.<small>Red team thinking</small></p></div></div><div class="hero-bottom"><div><a href="https://github.com/{per['username']}">GitHub</a><a href="https://www.linkedin.com/in/parsaaemm/">LinkedIn</a><a href="mailto:{per['email']}">Email</a></div><a class="eyebrow" href="#perspective">A LITTLE FURTHER DOWN ↓</a></div></section>
<section class="perspective wrap section" id="perspective" aria-labelledby="perspective-title"><div class="section-top"><p class="eyebrow"><span class="accent">01</span> A POINT OF VIEW</p><span class="eyebrow">SOFTWARE / SECURITY / CRAFT</span></div><h2 id="perspective-title">{e(p['perspective']['title'])}<br><em>{e(p['perspective']['accent'])}</em></h2><div class="perspective-copy"><p>{e(p['perspective']['text'])}</p><p>{e(p['perspective']['detail'])}</p></div></section>
<section class="method wrap section" id="method" aria-labelledby="method-title"><div class="section-top"><p class="eyebrow"><span class="accent">02</span> HOW I THINK</p><h2 id="method-title">{e(method['title'])}<br><em>{e(method['accent'])}</em></h2><p>A software engineer’s care.<br>A red teamer’s questions.</p></div><div class="method-layout"><div class="method-model" aria-label="Working model: input, rule, result, with explicit boundaries"><div class="eyebrow">THE WORKING MODEL <span class="accent">↳ 01—03</span></div><div class="model-stages"><span>INPUT</span><i>↓</i><span class="boundary">RULE</span><i>↓</i><span>RESULT</span></div><p class="eyebrow">BEHAVIOR → BOUNDARY → EVIDENCE</p></div><div class="method-steps">{steps}</div></div><blockquote>“Leaving it alone is better<br>than changing it <em>incorrectly.</em>”<span class="eyebrow">MY WORKING PRINCIPLE</span></blockquote></section>
<section class="selected-work wrap section" id="work" aria-labelledby="work-title"><div class="section-top"><p class="eyebrow"><span class="accent">03</span> WORK IN PUBLIC</p><p>Personal projects.<br>Inspectable code. Honest status.</p></div><div class="section-title"><h2 id="work-title">Open to<br><em>closer inspection.</em></h2>{link(base+'projects/', 'All work')}</div>{''.join(work)}<div class="explorations">{explorations}</div><div class="confidential"><p class="eyebrow">PROFESSIONAL EXPERIENCE</p><h3>Enterprise work. Kept confidential.</h3><p>{e(p['professional']['text'])}</p>{link(p['professional']['resume'], 'View experience')}</div></section>
<section class="experiment wrap section" id="experiment" aria-labelledby="experiment-title"><p class="eyebrow"><span class="accent">04</span> DON’T JUST READ IT</p><div class="experiment-grid"><h2 id="experiment-title">Try the<br><em>difference.</em></h2><div><h3>{e(p["experiment"]["title"])}</h3><p>{e(p["experiment"]["text"])}</p><small>{e(p["experiment"]["note"])}</small>{link(p["experiment"]["url"], "Open the browser experiment")}</div></div></section>
<section class="about wrap section" id="about" aria-labelledby="about-title"><p class="eyebrow"><span class="accent">05</span> THE PERSON BEHIND THE HANDLE</p><div class="about-grid"><figure><img src="assets/img/avatar-dark.webp" width="440" height="440" loading="lazy" alt="Portrait of Parsa Emami"><figcaption class="eyebrow">PARSA EMAMI / PARSAAEMM <span>IRN ↗</span></figcaption></figure><div><h2 id="about-title">I build.<br>I question.<br><em>I keep learning.</em></h2><p>{e(p['about'][1])}</p><p>{e(p['about'][2])}</p>{link(base+'about/', 'A little more about me')}</div></div><div class="focus-grid">{focus}</div></section>
<section class="notes wrap section" id="notes" aria-labelledby="notes-title"><div class="section-top"><p class="eyebrow"><span class="accent">06</span> FIELD NOTES</p>{link(base+'writing/', 'All notes')}</div><h2 id="notes-title">The thinking,<br><em>in writing.</em></h2><div class="notes-list">{notes}</div></section>
</main>
<section class="contact" id="contact" aria-labelledby="contact-title"><div class="wrap"><div class="section-top"><p class="eyebrow">THE NEXT CHAPTER</p><span>Open to international roles</span></div><h2 id="contact-title">Your next<br><em>engineer.</em></h2><a class="contact-email" href="mailto:{per['email']}">{e(per['email'])}{arrow()}</a><div class="section-top"><p>Software engineering · Security architecture<br>Open to relocation & selected collaborations</p>{link(base+'resume/', 'Read my résumé')}</div></div></section>
<footer class="wrap"><div><a class="brand" href="{base}">{e(per['brand'])}<b>.</b></a><p>Parsa Emami<br>Software, security & the details between.</p></div><nav aria-label="Elsewhere"><a href="https://github.com/{per['username']}">GitHub</a><a href="https://www.linkedin.com/in/parsaaemm/">LinkedIn</a><a href="{base}colophon/">Colophon</a><a href="#top">Back to top ↑</a></nav></footer>
</body></html>'''


def build():
    p = C.load_profile()
    for sub in ['css', 'js', 'art', 'img', 'fonts']:
        (SITE / 'assets' / sub).mkdir(parents=True, exist_ok=True)
    (SITE / 'index.html').write_text(render(p), encoding='utf-8')
    (SITE / 'index.md').write_text(markdown.render(p, C.load_contributions()), encoding='utf-8')
    css = theme_css(p) + (TEMPLATES / 'site.css').read_text(encoding='utf-8')
    (SITE / 'assets' / 'css' / 'site.css').write_text(css, encoding='utf-8')
    for name in ['theme-init.js', 'app.js']:
        shutil.copyfile(TEMPLATES / name, SITE / 'assets' / 'js' / name)
    for project in p['projects']:
        for theme, tokens in p['design']['themes'].items():
            name = f'study-{project["id"]}-{theme}.svg'
            (SITE / 'assets' / 'art' / name).write_text(study(tokens, project), encoding='utf-8')
    shutil.copyfile(ROOT / 'assets' / 'avatar' / 'avatar-dark.webp', SITE / 'assets' / 'img' / 'avatar-dark.webp')
    fonts.write_site_fonts(SITE / 'assets' / 'fonts')
    make_og.build(p)
    (SITE / 'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#262624"/><text x="9" y="44" font-family="Arial,sans-serif" font-size="40" letter-spacing="-6" fill="#faf9f5">pe</text><circle cx="51" cy="46" r="4" fill="#c94040"/></svg>\n', encoding='utf-8')
    (SITE / '404.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found — Parsa Emami</title><body><main><h1>Page not found.</h1><p><a href="{p["site"]["pages_url"]}">Return to the profile</a> · <a href="{p["site"]["url"]}">Visit parsaaemm.dev</a></p></main></body></html>\n', encoding='utf-8')
    (SITE / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
    (SITE / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{p["site"]["url"]}</loc></url></urlset>\n', encoding='utf-8')
    (SITE / 'llms.txt').write_text(f'# {p["person"]["name"]}\n\n{p["site"]["description"]}\n\n- [Canonical website]({p["site"]["url"]})\n- [Text profile](index.md)\n- [Résumé]({p["professional"]["resume"]})\n', encoding='utf-8')
    print('site: wrote static mirror')


if __name__ == '__main__':
    build()
