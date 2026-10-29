from __future__ import annotations

import base64
import json
from pathlib import Path

from lib.seyi import ACCENT, BACKGROUND, BORDER, INK, LABEL, MUTED, Drawing, measure

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/seyi-editorial'


def snapshot():
    return json.loads((ROOT / 'data/seyi-reference.json').read_text(encoding='utf-8'))


def mobile_hero(p):
    d = Drawing(390)
    data = base64.b64encode((OUT / 'hero-background.jpg').read_bytes()).decode('ascii')
    d.defs.append('<linearGradient id="shade" x2="1" y2="0"><stop stop-color="#050605" stop-opacity=".9"/><stop offset="1" stop-color="#050605" stop-opacity=".45"/></linearGradient>')
    d.parts.append(f'<image x="16" y="78" width="358" height="558" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}"/>')
    d.rect(16, 78, 358, 558, 'url(#shade)')
    d.label(16, 24, 'PARSA', 8, INK)
    d.label(16, 35, 'EMAMI', 8, INK)
    d.label(129, 24, 'JAVASCRIPT DEVELOPER', 6, MUTED)
    d.label(129, 35, '@PARSA-EMAMI', 6, MUTED)
    d.pill(301, 17, 'CONTACT', 6, height=22)
    d.line(16, 59, 374)
    d.rect(16, 78, 358, 558, stroke=BORDER)
    d.rect(24, 86, 342, 542, stroke=BORDER)
    d.parts.append(f'<circle cx="34" cy="108" r="2" fill="{ACCENT}"/>')
    d.label(42, 110, 'PROFILE / @PARSA-EMAMI', 6, MUTED)
    d.label(353, 110, '01 / 04', 6, MUTED, 'end')
    d.label(32, 209, p['hero_role'], 7)
    d.text(30, 279, 'PARSA', 77, tracking=-5.4)
    d.text(30, 346, 'EMAMI', 77, tracking=-5.4)
    d.text(50, 399, 'IN PUBLIC.', 57, tracking=-4, outline=True)
    d.paragraph(32, 437, p['intro'], 300, 12, 18, weight=400)
    width = d.pill(32, 484, 'Explore selected work ↘', 8, ACCENT, BACKGROUND, height=28)
    d.pill(40+width, 484, 'GitHub profile ↗', 8, height=28)
    d.label(32, 607, 'BUILT FROM PUBLIC WORK', 5.5, MUTED)
    d.label(356, 607, '↓ SCROLL TO EXPLORE', 5.5, MUTED, 'end')
    return d.svg(674, 'Parsa Emami — In public.', p['intro']+' Open the original interactive portfolio.')


def project_card(p, number, mobile=False):
    d = Drawing(390 if mobile else 1348)
    item = p['projects'][number]
    x, right = (16, 374) if mobile else (42.59375, 1305.40625)
    leading = 18 if mobile else (58 if number in (0, 4) else 0)
    top = leading + (12 if mobile else 9)
    d.line(x, top, right)
    label_y = top + (21 if mobile else 23)
    label_size = 7 if mobile else 6.34174
    if number == 0:
        d.label(x, label_y, 'FEATURED', label_size, LABEL)
        d.label(x, label_y+10, 'PROJECTS (6)', label_size, LABEL)
    label_x = right if number == 0 else x
    anchor = 'end' if number == 0 else 'start'
    d.label(label_x, label_y, item['language'].upper()+' /', label_size, LABEL, anchor)
    d.label(label_x, label_y+10, f'{item["stars"]} STARS', label_size, LABEL, anchor)
    size = 40 if mobile else 60.5778
    tracking = -size*.07
    if mobile:
        while measure(item['title'], size, tracking=tracking) > right-x:
            size -= 1
            tracking = -size*.07
    d.text(x, top+(85 if mobile else 99), item['title'], size, tracking=tracking)
    d.label(x, top+(112 if mobile else 132), 'VIEW PROJECT ↗', 7 if mobile else 6.815)
    height = leading+(147 if mobile else 169.4375)
    if number in (3, 5):
        d.line(x, height-8, right)
    return d.svg(height, item['title'], f'{item["name"]} — {item["language"]}, {item["stars"]} stars in the GitSkins reference snapshot. View project on GitHub.')


def repository_intro(p, mobile=False):
    d = Drawing(390 if mobile else 1348)
    center = d.width/2
    top = 76 if mobile else 175
    d.label(center, top, 'PUBLIC REPOSITORIES', 8 if mobile else 6.62569, anchor='middle')
    text = f'{p["name"]} shares {p["totals"]["public_repositories"]} public repositories on GitHub.'
    y = d.paragraph(center, top+40, text, 335 if mobile else 492.1875, 28 if mobile else 32.1819, 34 if mobile else 37.0092, tracking=-1.44819, anchor='middle')
    d.label(center, y+10, 'EXPLORE ALL PROJECTS', 9 if mobile else 14.6712, anchor='middle')
    return d.svg(y+(86 if mobile else 150), 'Public repositories', text+' Explore all projects.')


def activity(p, mobile=False):
    d = Drawing(390 if mobile else 1348)
    totals = p['totals']
    values = [f'{totals["public_repositories"]} public repositories', f'{totals["stars"]} stars earned', f'{totals["followers"]} followers', f'{totals["following"]} following']
    values += [f'{x["name"]} ⏤ {x["stars"]} stars' for x in p['projects']]
    start = 76 if mobile else 180
    x = 16 if mobile else 42.59375
    d.label(x, start, 'GITHUB X', 8 if mobile else 6.62569)
    d.label(x, start+11, 'ACTIVITY', 8 if mobile else 6.62569)
    width = 173 if mobile else 329.921875
    gap = 12 if mobile else 11.828125
    row_height = 35 if mobile else 29.3125
    for i, text in enumerate(values):
        col, row = i%2, i//2
        left = x+col*(width+gap)
        y = start+29+row*row_height
        d.line(left, y, left+width)
        d.text(left, y+21, text, 8.5 if mobile else 7.38292, weight=400, color=MUTED)
    rx = 16 if mobile else 808.9375
    ry = start+270 if mobile else start
    d.label(rx, ry, 'INTERESTS', 8 if mobile else 6.62569)
    d.paragraph(rx, ry+30 if mobile else ry+29, p['interests'], 358 if mobile else 496, 14.6712, 22, tracking=-.293424, weight=400)
    d.label(rx, ry+88 if mobile else ry+69.61, 'ICEBREAKERS', 8 if mobile else 6.62569)
    d.paragraph(rx, ry+118 if mobile else ry+98.61, p['intro'], 358 if mobile else 496, 14.6712, 22, tracking=-.293424, weight=400)
    height = ry+190 if mobile else start+252
    d.line(x, height-1, 374 if mobile else 1305.40625)
    return d.svg(height, 'GitHub activity and interests', f'GitSkins reference captured {p["captured_on"]}; cached counts, not live GitHub totals. '+'. '.join(values)+'. Interests: '+p['interests'])


def contact(p, mobile=False):
    d = Drawing(390 if mobile else 1348)
    x, right = (16, 374) if mobile else (42.59375, 1305.40625)
    top = 104 if mobile else 193
    lines = ['Got a question, proposal or', 'project or want to work', 'together on something? Feel', 'free to reach out.']
    size = 24 if mobile else 25.5562
    for i, line in enumerate(lines):
        d.text(x, top+i*29.3897, line, size, tracking=-1.02225)
    y = top+132
    d.line(x, y, right)
    d.text(x+30 if not mobile else x, y+79 if not mobile else y+63, 'LET’S TALK — LET’S COLLABORATE — SAY HELLO — WANNA BE STARTING SOMETHING?', 66 if not mobile else 49, color=MUTED, tracking=-4.6 if not mobile else -3)
    d.line(x, y+113 if not mobile else y+96, right)
    d.text(x, y+166 if not mobile else y+143, p['handle'], 28 if not mobile else 26, tracking=-1.3)
    return d.svg(y+(250 if mobile else 240), 'Let’s talk', p['contact']+' '+p['handle']+'. Open GitHub profile.')


def footer(p, mobile=False):
    d = Drawing(390 if mobile else 1348)
    x = 16 if mobile else 42.59375
    d.line(x, 1, 374 if mobile else 1305.40625)
    left = x+8
    for text in ['GITHUB', 'PROFILE', 'REPOSITORIES', 'PROJECTS']:
        left += d.pill(left, 15, text, 8 if mobile else 15, padding=8, height=22 if mobile else 28)+8
    if mobile:
        d.label(x, 73, p['location'], 7, MUTED)
        d.text(x, 101, 'Design by Isaac Fayemi', 8, color=MUTED)
        d.text(x, 120, 'Original portfolio by Oluwadare Oluwaseyi ↗', 7.5, color=MUTED)
    else:
        d.text(503, 24, p['location'], 6.62569, color=MUTED)
        d.text(598, 24, 'Design by Isaac Fayemi', 6.62569, color=MUTED)
        d.text(574, 48, 'Original portfolio by Oluwadare Oluwaseyi ↗', 6.62569, color=MUTED)
    return d.svg(145 if mobile else 75, 'Profile links and design credits', p['location']+'. '+'. '.join(c['label'] for c in p['credits']))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    p = snapshot()
    jobs = {'hero-mobile': mobile_hero(p)}
    for mobile in [False, True]:
        suffix = '-mobile' if mobile else ''
        for number in range(len(p['projects'])):
            jobs[f'project-{number+1}{suffix}'] = project_card(p, number, mobile)
        for name, builder in [('repositories', repository_intro), ('activity', activity), ('contact', contact), ('footer', footer)]:
            jobs[name+suffix] = builder(p, mobile)
    for name, svg in jobs.items():
        (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
    print(f'seyi: wrote {len(jobs)} reference graphics')
    return [str((OUT / f'{name}.svg').relative_to(ROOT)) for name in jobs]


if __name__ == '__main__':
    build()
