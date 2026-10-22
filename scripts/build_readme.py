from __future__ import annotations

from html import escape as e
from pathlib import Path

from lib import content as C, markdown

ROOT = Path(__file__).resolve().parents[1]


def picture(name, alt, directory='assets/cards'):
    mobile = '' if name == 'contributions' else (
        f'  <source media="(max-width: 640px) and (prefers-color-scheme: dark)" srcset="{directory}/{name}-mobile-dark.svg">\n'
        f'  <source media="(max-width: 640px)" srcset="{directory}/{name}-mobile-light.svg">\n')
    return (f'<picture>\n'
            f'{mobile}'
            f'  <source media="(prefers-color-scheme: dark)" srcset="{directory}/{name}-dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="{directory}/{name}-light.svg">\n'
            f'  <img src="{directory}/{name}-light.svg" alt="{e(alt, quote=True)}" width="830">\n'
            f'</picture>')


def card(name, alt, href):
    return f'<a href="{e(href, quote=True)}">\n{picture(name, alt)}\n</a>\n'


def render(p, contrib):
    base = p['site']['url']
    out = [card('hero', p['person']['name']+' — '+p['person']['role']+'. '+p['person']['perspective']+' '+p['hero']['intro'], base)]
    out.append(f'# {p["person"]["name"]}\n\n**{p["person"]["role"]} · Red team perspective**\n\n{p["hero"]["intro"]}\n\nBased in {p["person"]["location"]}. {p["hero"]["availability"]}\n')
    out.append(f'[Website]({base}) · [Selected work]({base}projects/) · [Notes]({base}writing/) · [Résumé]({base}resume/) · [LinkedIn](https://www.linkedin.com/in/parsaaemm/) · [Email](mailto:{p["person"]["email"]})\n')
    out.append('## 01 / A point of view\n')
    out.append(card('perspective', p['perspective']['title']+' '+p['perspective']['accent']+' '+p['perspective']['text'], base+'#perspective'))
    out.append(p['perspective']['detail']+'\n')
    out.append('## 02 / How I think\n')
    out.append(card('principles', 'Understand first. Then change. Observe: trace the behavior. Question: find the boundary. Refine: protect the meaning.', base+'#method'))
    out.append('> '+p['method']['principle']+'\n')
    out.append('## 03 / Work in public\n\nPersonal projects. Inspectable code. Honest status.\n')
    for project in p['projects']:
        out.append(card('project-'+project['id'], project['name']+' — '+project['status']+'. '+project['summary']+' '+project['scope'], project['url']))
        links = f'**[{project["name"]} — source]({project["url"]})** · [Project notes]({project["case_study"]})'
        if project.get('viewer'):
            links += f' · [Passport viewer]({project["viewer"]})'
        out.append(links+'\n')
    out.append('Other explorations: '+' · '.join(f'[{x["name"]}]({x["url"]})' for x in p['explorations'])+'.\n')
    out.append(p['professional']['text']+f' [Professional experience]({p["professional"]["resume"]}).\n')
    out.append('## 04 / A small experiment\n\n'+f'**[{p["experiment"]["title"]}]({p["experiment"]["url"]})**\n\n'+p['experiment']['text']+'\n\n'+p['experiment']['note']+'\n')
    out.append('## 05 / The person behind the handle\n\n'+'\n\n'.join(p['about'][1:])+'\n')
    rows = max(len(group['items']) for group in p['focus'])
    out.append('| '+' | '.join(group['title'] for group in p['focus'])+' |\n| '+' | '.join('---' for _ in p['focus'])+' |\n'+'\n'.join('| '+' | '.join(group['items'][i] if i < len(group['items']) else '' for group in p['focus'])+' |' for i in range(rows))+'\n')
    out.append('## 06 / Field notes\n\n'+'\n'.join(f'- [{x["title"]}]({x["url"]}) — {x["category"]}' for x in p['notes'])+'\n')
    out.append(card('footer', 'Your next engineer. '+p['hero']['availability']+' Email '+p['person']['email'], 'mailto:'+p['person']['email']))
    out.append(f'[Let’s talk](mailto:{p["person"]["email"]}) · [Read my résumé]({base}resume/) · [Explore the portfolio]({base})\n')
    out.append('<details>\n<summary>Activity snapshot</summary>\n\n'+picture('contributions', 'Public activity snapshot based on calendars and public repository commits; not the official GitHub profile total.')+'\n\n'+markdown.activity(contrib)+'\n\n</details>\n')
    return '\n'.join(out)


def build():
    text = render(C.load_profile(), C.load_contributions())
    (ROOT / 'README.md').write_text(text, encoding='utf-8')
    print('readme: wrote README.md')


if __name__ == '__main__':
    build()
