from __future__ import annotations

from pathlib import Path

from lib import content as C, heat
from lib.brand import Drawing, measure

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'cards'


def hero(theme, p):
    d = Drawing(theme)
    for x, y, w, h in [(540, 85, 230, 240), (580, 65, 190, 200), (620, 40, 150, 165)]:
        d.rect(x, y, w, h, theme['card'], theme['border'])
    d.line(540, 325, 770, 325, theme['accent'])
    d.label(32, 34, p['hero']['eyebrow'])
    names = p['person']['name'].upper().split(' ', 1)
    for text, y in zip(names, [150, 258]):
        size = min(128, 470 / measure(text, 1, 500, tracking=-.065))
        d.text(27, y, text, size, 500, tracking=-size*.065)
    d.text(32, 324, 'IN PUBLIC.', 63, 400, theme['accent'], tracking=-3.5)
    d.text(32, 357, 'Software engineer. Security architect.', 16, color=theme['text'])
    d.line(32, 378, 798, 378)
    d.label(32, 401, p['person']['brand'])
    d.label(491, 401, 'BASED IN IRAN / OPEN WORLDWIDE')
    return d.svg(416, p['person']['name'], p['person']['role'] + '. ' + p['hero']['intro'])


def perspective(theme, p):
    d = Drawing(theme)
    d.label(32, 33, '01 / A POINT OF VIEW')
    d.text(32, 94, p['perspective']['title'], 48, 400, tracking=-2)
    d.serif(32, 150, p['perspective']['accent'], 52)
    d.para(32, 199, p['perspective']['text'], 752, 17, theme['text'], 27)
    return d.svg(267, 'A point of view', p['perspective']['text'] + ' ' + p['perspective']['detail'])


def method(theme, p):
    d = Drawing(theme)
    d.label(32, 33, '02 / HOW I THINK')
    d.text(32, 90, p['method']['title'], 40, tracking=-1.5)
    d.serif(370, 90, p['method']['accent'], 42)
    y = 133
    for i, step in enumerate(p['method']['steps'], 1):
        d.line(32, y, 798, y)
        d.label(32, y+30, f'{i:02d} / {step["verb"].upper()}', theme['accent'])
        d.text(220, y+33, step['title'], 23, 500, tracking=-.7)
        d.para(220, y+62, step['text'], 565, 16, theme['text'], 25)
        y += 114
    d.label(32, y+16, 'BEHAVIOR → BOUNDARY → EVIDENCE')
    return d.svg(y+42, 'Understand first. Then change.', ' '.join(x['title']+' '+x['text'] for x in p['method']['steps']))


def study(theme, project):
    d = Drawing(theme)
    d.rect(0, 0, 830, 290, theme['card'])
    d.label(32, 34, project['category'].upper())
    if project['id'] == 'attestara':
        for i, label in enumerate(['BYTES', 'POLICY', 'SIGNER']):
            x = 50+i*260
            d.rect(x, 81, 210, 118, theme['paper'], theme['border'], 5)
            d.label(x+16, 110, f'0{i+1} / ASSESSMENT')
            d.text(x+16, 154, label, 24, 500, tracking=-.5)
            d.circle(x+178, 169, 4, theme['accent'])
        d.line(155, 199, 155, 220)
        d.line(155, 220, 675, 220)
        d.line(415, 199, 415, 220)
        d.line(675, 199, 675, 220)
        d.label(273, 252, 'THREE SEPARATE QUESTIONS')
    elif project['id'] == 'miragemesh':
        stages = [('SENSOR', 55), ('SPOOL', 315), ('TRIAGE', 575)]
        for i, (label, x) in enumerate(stages, 1):
            d.rect(x, 91, 200, 108, theme['paper'], theme['border'], 5)
            d.label(x+16, 120, f'0{i} / LOCAL')
            d.text(x+16, 163, label, 23, 500, tracking=-.5)
            if i < 3:
                d.line(x+200, 145, x+260, 145, theme['accent'])
        d.label(55, 252, 'OFFLINE DURABILITY / EXPLICIT TRUST')
    else:
        d.rect(105, 75, 620, 143, theme['paper'], theme['border'], 6)
        d.label(125, 101, 'BOUNDARY / A MODELING DIRECTION')
        for x, label in [(145, 'CONTEXT'), (485, 'AUTHORITY')]:
            d.rect(x, 127, 200, 58, theme['card'], theme['border'], 4)
            d.text(x+20, 163, label, 20, 500)
        d.line(345, 155, 485, 155, theme['accent'])
        d.line(415, 115, 415, 197, theme['accent'])
        d.circle(415, 155, 6, theme['accent'])
        d.label(105, 252, 'STRUCTURE BEFORE ASSUMPTION')
    return d.svg(290, project['name']+' study', 'Conceptual illustration for '+project['name']+'; not an application screenshot.')


def project_card(theme, project, number):
    d = Drawing(theme)
    d.label(32, 34, f'{number:02d} / '+project['category'].upper())
    d.label(32, 62, project['status'].upper(), theme['accent'])
    d.text(32, 122, project['name'], 49, 500, tracking=-1.8)
    d.arrow(768, 89, 25)
    y = d.para(32, 165, project['title'], 740, 20, theme['ink'], 29)
    d.line(32, y+1, 798, y+1)
    y = d.para(32, y+31, project['summary'], 752, 16, theme['text'], 25)
    y = d.para(32, y+12, project['scope'], 752, 14, theme['subtle'], 22)
    return d.svg(y+23, project['name'], project['status']+'. '+project['summary']+' '+project['scope'])


def contact(theme, p):
    d = Drawing(theme)
    d.contours(950, 170)
    d.label(32, 33, 'THE NEXT CHAPTER')
    d.text(32, 100, 'Your next', 56, tracking=-2)
    d.serif(270, 100, 'engineer.', 62)
    d.text(32, 161, p['person']['email'], 27, tracking=-.6)
    d.arrow(762, 130, 25)
    d.line(32, 194, 798, 194)
    d.text(32, 224, p['hero']['availability'], 15, color=theme['text'])
    return d.svg(252, 'Let’s talk', p['hero']['availability']+' Email '+p['person']['email'])


def contributions(theme, contrib):
    d = Drawing(theme)
    d.label(32, 33, 'PUBLIC ACTIVITY / SNAPSHOT')
    cells, cols, months = heat.build(contrib.get('days', []))
    if not cells:
        d.text(32, 88, 'No activity snapshot available.', 18)
        return d.svg(120, 'Public activity', 'No activity snapshot available.')
    pitch = min(14, 766 / cols)
    top = 76
    shades = [theme['surface'], theme['border'], theme['subtle'], theme['text'], theme['accent']]
    for col, label in months:
        d.text(32+col*pitch, 61, label, 10, mono=True, color=theme['subtle'])
    for cell in cells:
        d.rect(32+cell.col*pitch, top+cell.row*pitch, pitch-3, pitch-3, shades[cell.level], radius=2)
    r = contrib.get('range', {})
    label = f'{r.get("start", "")} — {r.get("end", "")}'
    d.label(32, 204, label)
    d.text(32, 232, 'Calendar + public repository signals; not the official profile total.', 13, color=theme['subtle'])
    return d.svg(258, 'Public activity snapshot', label+'. Calendar and public repository commit signals; not the official GitHub profile total.')


def mobile_hero(theme, p):
    d = Drawing(theme, 420)
    d.rect(262, 60, 134, 240, theme['card'], theme['border'])
    d.rect(300, 45, 96, 190, theme['paper'], theme['border'])
    d.label(24, 31, 'ENGINEERING / SECURITY / CURIOSITY')
    d.text(20, 126, 'Parsa', 94, 600, tracking=-4)
    w = d.text(20, 211, 'Emami', 94, 600, tracking=-4)
    d.text(20+w, 211, '.', 94, 600, theme['accent'])
    d.line(24, 242, 396, 242, theme['ink'])
    d.text(24, 281, 'Software engineer.', 24, 500, tracking=-.7)
    d.text(24, 312, 'Security architect.', 24, 500, tracking=-.7)
    d.text(24, 342, p['person']['perspective'], 16, color=theme['subtle'])
    d.text(24, 407, 'IN PUBLIC.', 60, 400, theme['accent'], tracking=-3)
    d.text(24, 448, 'Build with intent. Question the obvious.', 16, color=theme['text'])
    d.line(24, 477, 396, 477)
    d.label(24, 509, 'BASED IN IRAN / OPEN WORLDWIDE')
    return d.svg(539, p['person']['name'], p['person']['role']+'. '+p['hero']['intro'])


def mobile_perspective(theme, p):
    d = Drawing(theme, 420)
    d.label(24, 31, '01 / A POINT OF VIEW')
    d.text(24, 91, p['perspective']['title'], 36, tracking=-1.4)
    d.serif(24, 139, p['perspective']['accent'], 41)
    y = d.para(24, 187, p['perspective']['text'], 366, 17, theme['text'], 27)
    return d.svg(y+22, 'A point of view', p['perspective']['text'])


def mobile_method(theme, p):
    d = Drawing(theme, 420)
    d.label(24, 31, '02 / HOW I THINK')
    d.text(24, 87, p['method']['title'], 36, tracking=-1.3)
    d.serif(24, 130, p['method']['accent'], 40)
    y = 165
    for i, step in enumerate(p['method']['steps'], 1):
        d.line(24, y, 396, y)
        d.label(24, y+29, f'{i:02d} / {step["verb"].upper()}', theme['accent'])
        d.text(24, y+69, step['title'], 25, 500, tracking=-.5)
        bottom = d.para(24, y+104, step['text'], 366, 17, theme['text'], 27)
        y = bottom+24
    return d.svg(y, 'Understand first. Then change.', ' '.join(x['title']+' '+x['text'] for x in p['method']['steps']))


def mobile_project(theme, project, number):
    d = Drawing(theme, 420)
    d.label(24, 31, f'{number:02d} / '+project['category'].upper())
    d.label(24, 60, project['status'].upper(), theme['accent'])
    d.text(24, 124, project['name'], 44, 500, tracking=-1.5)
    d.arrow(371, 94, 19)
    y = d.para(24, 168, project['title'], 366, 21, theme['ink'], 30)
    d.line(24, y+4, 396, y+4)
    y = d.para(24, y+37, project['summary'], 366, 17, theme['text'], 27)
    y = d.para(24, y+14, project['scope'], 366, 15, theme['subtle'], 24)
    return d.svg(y+23, project['name'], project['status']+'. '+project['summary']+' '+project['scope'])


def mobile_contact(theme, p):
    d = Drawing(theme, 420)
    d.contours(650, 120)
    d.label(24, 31, 'THE NEXT CHAPTER')
    d.text(24, 98, 'Your next', 47, tracking=-1.7)
    d.serif(24, 158, 'engineer.', 62)
    d.text(24, 216, p['person']['email'], 25, tracking=-.5)
    d.line(24, 247, 396, 247)
    y = d.para(24, 282, p['hero']['availability'], 366, 17, theme['text'], 27)
    return d.svg(y+20, 'Let’s talk', p['hero']['availability']+' Email '+p['person']['email'])


def build():
    p = C.load_readme_profile()
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for tn, theme in p['design']['themes'].items():
        jobs = {'hero': hero(theme, p), 'perspective': perspective(theme, p), 'principles': method(theme, p), 'footer': contact(theme, p), 'contributions': contributions(theme, C.load_contributions()), 'hero-mobile': mobile_hero(theme, p), 'perspective-mobile': mobile_perspective(theme, p), 'principles-mobile': mobile_method(theme, p), 'footer-mobile': mobile_contact(theme, p)}
        for i, project in enumerate(p['projects'], 1):
            jobs['project-'+project['id']] = project_card(theme, project, i)
            jobs['project-'+project['id']+'-mobile'] = mobile_project(theme, project, i)
            jobs['study-'+project['id']] = study(theme, project)
        for name, svg in jobs.items():
            path = OUT / f'{name}-{tn}.svg'
            path.write_text(svg, encoding='utf-8')
            written.append(str(path.relative_to(ROOT)))
    print(f'cards: wrote {len(written)} SVGs')
    expected = {ROOT / name for name in written}
    for path in OUT.glob('*.svg'):
        if path not in expected:
            path.unlink()
    return written


if __name__ == '__main__':
    build()
