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
    person, hero = p['person'], p['hero']
    base = p['site']['url']
    email = e(person['email'], quote=True)
    name = person['name'].split(' ', 1)
    first, last = e(name[0]), e(name[1] if len(name) > 1 else '')
    work = []
    for i, project in enumerate(p['projects'], 1):
        x = {k: e(str(v), quote=True) for k, v in project.items()}
        alt = f'Conceptual {project["name"]} study; not an application screenshot.'
        viewer = link(project['viewer'], 'Open viewer') if project.get('viewer') else ''
        work.append(f'''<article class="project" aria-labelledby="project-{x['id']}">
<div class="project-meta micro"><span>{i:02d} / {x['category']}</span><span>{x['status']}</span></div>
<div class="project-title-wrap"><h3 id="project-{x['id']}" data-kinetic><a href="{x['url']}">{x['name']}{arrow()}</a></h3></div>
<div class="project-body"><figure><a href="{x['url']}" aria-label="Explore {x['name']} source">{picture('study-'+project['id'], alt)}</a><figcaption class="micro">Concept study <span>Not an application screenshot</span></figcaption></figure><div class="project-copy"><p class="project-thesis">{x['title']}</p><p>{x['summary']}</p><p class="scope">{x['scope']}</p><div class="project-links">{link(project['url'], 'Source code')}{link(project['case_study'], 'Project notes')}{viewer}</div></div></div></article>''')
    steps = ''.join(f'<article><span class="micro">0{i} / {e(step["verb"])}</span><h3>{e(step["title"])}</h3><p>{e(step["text"])}</p><p class="question">{e(step["question"])}</p></article>' for i, step in enumerate(p['method']['steps'], 1))
    focus = ''.join('<div><h3 class="micro">'+e(group['title'])+'</h3><ul>'+''.join('<li>'+e(item)+'</li>' for item in group['items'])+'</ul></div>' for group in p['focus'])
    experience = ''.join(f'<li><span class="micro">{e(C.fmt_ym(x["start"]))} — {e(C.fmt_ym(x["end"])) if x["end"] else "Present"}</span><div><h4>{e(x["role"])}</h4><p>{e(x["company"])}</p><p class="scope">{e(x["description"])}</p></div></li>' for x in p['experience'])
    education = ''.join(f'<li><span class="micro">{e(x["period"])}</span><div><h4>{e(x["degree"])}</h4><p>{e(x["school"])}</p></div></li>' for x in p['education'])
    notes = ''.join(f'<a class="note" href="{e(note["url"], quote=True)}"><span class="micro">0{i}</span><h3>{e(note["title"])}</h3><span class="micro note-category">{e(note["category"])}</span>{arrow()}</a>' for i, note in enumerate(p['notes'], 1))
    explorations = ''.join(f'<a href="{e(x["url"], quote=True)}"><span>{e(x["name"])}</span><span class="micro">{e(x["label"])}</span>{arrow()}</a>' for x in p['explorations'])
    social = ''.join(link(x['href'], x['label'], 'pill') for x in p['links'])
    structured = json.dumps({'@context': 'https://schema.org', '@type': 'Person', 'name': person['name'], 'alternateName': person['alternate_names'], 'url': base, 'jobTitle': 'Software Engineer & Security Architect', 'sameAs': [x['href'] for x in p['links'] if x['id'] != 'website']}, ensure_ascii=False).replace('<', '\\u003c')
    biography = ''.join(f'<p>{e(x)}</p>' for x in p['about'])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['site']['title'])}</title><meta name="description" content="{e(p['site']['description'], quote=True)}">
<meta name="robots" content="noindex,follow"><meta name="color-scheme" content="light dark"><meta name="theme-color" content="#10110f">
<link rel="canonical" href="{e(base, quote=True)}"><link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="profile"><meta property="og:title" content="{e(p['site']['title'], quote=True)}"><meta property="og:description" content="{e(p['site']['description'], quote=True)}"><meta property="og:url" content="{e(p['site']['pages_url'], quote=True)}"><meta property="og:image" content="{e(p['site']['pages_url'], quote=True)}assets/img/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Parsa Emami — Software Engineer and Security Architect"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/img/architecture.png" as="image" fetchpriority="high">
<script src="assets/js/theme-init.js"></script><link rel="stylesheet" href="assets/css/site.css"><script src="assets/js/app.js" defer></script><script src="assets/js/editorial.js" defer></script>
<script type="application/ld+json">{structured}</script>
</head>
<body id="top">
<a class="skip-link" href="#main">Skip to content</a><div class="reading-progress" aria-hidden="true"></div>
<header class="site-header wrap"><a class="wordmark" href="#top" aria-label="Parsa Emami, home">{first}<br>{last}<span aria-hidden="true">.</span></a><p class="header-role micro">Software engineer<br>Security architect</p><nav class="header-nav micro" aria-label="Main"><a href="#work">Work</a><a href="#about">About</a><a href="#notes">Notes</a></nav><div class="header-actions"><button type="button" class="theme-toggle" hidden aria-label="Color theme: System. Switch to light mode."><span aria-hidden="true">◐</span><span data-theme-label>System</span></button>{link('#contact', 'Contact', 'pill header-contact')}</div></header>
<main id="main" tabindex="-1">
<section class="hero wrap" aria-labelledby="hero-name"><div class="hero-frame"><div class="hero-top micro"><span><i class="status-dot"></i>Profile / @{e(person['username'])}</span><span>01 / 05</span></div><div class="hero-content"><p class="micro hero-role">Engineering / Security / Curiosity</p><h1 id="hero-name"><span>{first}</span> <span>{last}</span></h1><p class="hero-outline" aria-label="In public">In public.</p><p class="hero-intro">{e(hero['intro'])}</p><div class="hero-links">{link('#work', 'Explore selected work', 'pill primary')}{link('https://github.com/'+person['username'], 'GitHub profile', 'pill')}</div></div><div class="hero-bottom micro"><span>Built with intent. Open to inspection.</span><a href="#work">Scroll to explore ↓</a></div></div></section>
<section id="work" class="work wrap section" aria-labelledby="work-title"><div class="section-label micro"><h2 id="work-title">Selected work <span>({len(p['projects']):02d})</span></h2><span>Personal projects / Inspectable source</span></div>{''.join(work)}<div class="explorations"><p class="micro">Elsewhere in the workshop</p>{explorations}</div><p class="professional-note">{e(p['professional']['text'])} <a href="{e(p['professional']['resume'], quote=True)}">View professional experience {arrow()}</a></p></section>
<section id="method" class="method wrap section" aria-labelledby="method-title"><div class="section-label micro"><span>02 / A way of thinking</span><span>Behavior → Boundary → Evidence</span></div><div class="statement"><p class="micro">A software engineer’s care.<br>A red teamer’s questions.</p><h2 id="method-title">Build with<br>intent.<br><span>Question</span><br>the obvious.</h2></div><div class="method-steps">{steps}</div><blockquote>“{e(p['method']['principle'])}”<cite class="micro">My working principle</cite></blockquote></section>
<section id="about" class="about wrap section" aria-labelledby="about-title"><div class="section-label micro"><span>03 / Behind the handle</span><span>{e(person['brand'])} / {e(person['location'])}</span></div><div class="about-grid"><figure class="portrait"><img src="assets/img/avatar-dark.webp" width="440" height="440" loading="lazy" alt="Portrait of Parsa Emami"><figcaption class="micro">Parsa Emami <span>Always a work in progress.</span></figcaption></figure><div class="about-copy"><h2 id="about-title">I build.<br>I question.<br><span>I keep learning.</span></h2>{biography}{link(p['professional']['resume'], 'Read my résumé')}</div></div><div class="focus-grid">{focus}</div><details class="experience"><summary><span>Experience & education</span><span class="expand-mark" aria-hidden="true">+</span></summary><div class="experience-content"><h3 class="micro">Professional experience</h3><ol>{experience}</ol><h3 class="micro">Education</h3><ol>{education}</ol></div></details></section>
<section id="notes" class="notes wrap section" aria-labelledby="notes-title"><div class="section-label micro"><span>04 / Field notes</span>{link(base+'writing/', 'All writing')}</div><h2 id="notes-title">The thinking,<br><span>in writing.</span></h2><div class="notes-list">{notes}</div><aside class="experiment"><div><p class="micro">An interactive side note</p><h3>{e(p['experiment']['title'])}</h3><p>{e(p['experiment']['text'])}</p><small>{e(p['experiment']['note'])}</small></div>{link(p['experiment']['url'], 'Try the experiment', 'pill')}</aside></section>
<section id="contact" class="contact section" aria-labelledby="contact-title"><div class="wrap"><div class="section-label micro"><span>05 / The next chapter</span><span><i class="status-dot"></i>Open to international roles</span></div><div class="contact-intro"><p>{e(hero['availability'])}</p><button class="motion-toggle micro" type="button" data-motion-toggle hidden aria-pressed="false">Pause motion</button></div><h2 id="contact-title" class="contact-title"><a href="mailto:{email}">Let’s talk.{arrow()}</a></h2></div><div class="marquee" aria-hidden="true"><div><span>Let’s build something considered. ↗</span><span>Let’s build something considered. ↗</span></div></div><div class="contact-email wrap"><div><a href="mailto:{email}">{e(person['email'])}</a><button type="button" class="copy-email micro" data-copy-email="{email}" hidden>Copy email {arrow()}</button><p class="copy-status micro" role="status" aria-live="polite" data-copy-status></p></div>{link(p['professional']['resume'], 'Your next engineer', 'pill')}</div></section>
</main>
<footer class="site-footer wrap"><div class="footer-top"><p class="micro">{e(person['location'])}<br><time data-local-time>Asia / Tehran</time></p><nav class="social-links" aria-label="Elsewhere">{social}</nav><a class="micro back-top" href="#top">Back to top ↑</a></div><div class="footer-bottom micro"><span>© {C.today().year} Parsa Emami</span><span>Software, security & the details between.</span><a href="https://www.gitskins.com/portfolio/templates/seyi-editorial">Inspired by Kinetic Editorial</a></div></footer>
</body></html>'''


def build():
    p = C.load_profile()
    for sub in ['css', 'js', 'art', 'img', 'fonts']:
        (SITE / 'assets' / sub).mkdir(parents=True, exist_ok=True)
    (SITE / 'index.html').write_text(render(p), encoding='utf-8')
    (SITE / 'index.md').write_text(markdown.render(p, C.load_contributions()), encoding='utf-8')
    (SITE / 'assets' / 'css' / 'site.css').write_text(theme_css(p) + (TEMPLATES / 'site.css').read_text(encoding='utf-8'), encoding='utf-8')
    for name in ['theme-init.js', 'app.js', 'editorial.js']:
        shutil.copyfile(TEMPLATES / name, SITE / 'assets' / 'js' / name)
    for project in p['projects']:
        for theme, tokens in p['design']['themes'].items():
            (SITE / 'assets' / 'art' / f'study-{project["id"]}-{theme}.svg').write_text(study(tokens, project), encoding='utf-8')
    shutil.copyfile(ROOT / 'assets' / 'avatar' / 'avatar-dark.webp', SITE / 'assets' / 'img' / 'avatar-dark.webp')
    shutil.copyfile(ROOT / 'assets' / 'editorial' / 'architecture.png', SITE / 'assets' / 'img' / 'architecture.png')
    fonts.write_site_fonts(SITE / 'assets' / 'fonts')
    make_og.build(p)
    (SITE / 'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#10110f"/><path d="M18 45V19h12c15 0 15 18 0 18H18m26-18v26H31" fill="none" stroke="#c5fa57" stroke-width="4"/></svg>\n', encoding='utf-8')
    (SITE / '404.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found — Parsa Emami</title><link rel="stylesheet" href="{p["site"]["pages_url"]}assets/css/site.css"></head><body class="error-page"><main class="wrap"><p class="micro">404 / A path less traveled</p><h1>Nothing<br>here. Yet.</h1><p><a class="pill primary" href="{p["site"]["pages_url"]}">Return to the portfolio →</a></p><a href="{p["site"]["url"]}">Visit parsaaemm.dev</a></main></body></html>\n', encoding='utf-8')
    (SITE / '.nojekyll').write_text('', encoding='utf-8')
    (SITE / 'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
    (SITE / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{p["site"]["url"]}</loc></url></urlset>\n', encoding='utf-8')
    (SITE / 'llms.txt').write_text(f'# {p["person"]["name"]}\n\n{p["site"]["description"]}\n\n- [Canonical website]({p["site"]["url"]})\n- [Text profile](index.md)\n- [Résumé]({p["professional"]["resume"]})\n', encoding='utf-8')
    print('site: wrote Kinetic Editorial portfolio')


if __name__ == '__main__':
    build()
