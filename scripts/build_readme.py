from __future__ import annotations

from html import escape as e
import json
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
    if p.get('readme', {}).get('presentation') == 'seyi-editorial-reference':
        return render_reference(p)
    base = p['site']['url']
    out = [card('hero', p['person']['name']+' — '+p['person']['role']+'. '+p['person']['perspective']+' '+p['hero']['intro'], p['site']['pages_url'])]
    out.append(f'# {p["person"]["name"]}\n\n**{p["person"]["role"]} · Red team perspective**\n\n{p["hero"]["intro"]}\n\nBased in {p["person"]["location"]}. {p["hero"]["availability"]}\n')
    out.append(f'[Interactive portfolio]({p["site"]["pages_url"]}) · [Website]({base}) · [Selected work]({base}projects/) · [Notes]({base}writing/) · [Résumé]({base}resume/) · [LinkedIn](https://www.linkedin.com/in/parsaaemm/) · [Email](mailto:{p["person"]["email"]})\n')
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


def render_reference(p):
    data = json.loads((ROOT / p['readme']['snapshot']).read_text(encoding='utf-8'))
    directory = 'assets/seyi-editorial'

    def visual(name, alt, href):
        desktop = 'hero-desktop.jpg' if name == 'hero' else name+'.svg'
        return (f'<a href="{e(href, quote=True)}"><picture>'
                f'<source media="(max-width: 640px)" srcset="{directory}/{name}-mobile.svg">'
                f'<img src="{directory}/{desktop}" alt="{e(alt, quote=True)}" width="100%" align="top">'
                '</picture></a>')

    images = [visual('hero', data['name']+' — '+data['hero_role']+'. IN PUBLIC. '+data['intro']+' Open the interactive original.', data['source'])]
    for number, project in enumerate(data['projects'], 1):
        if number == 5:
            images.append(visual('repositories', f'Public repositories. {data["name"]} shares {data["totals"]["public_repositories"]} public repositories in the reference snapshot. Explore all projects.', data['repositories_url']))
        images.append(visual(f'project-{number}', f'{project["title"]} — {project["language"]}, {project["stars"]} stars in the reference snapshot. View project.', project['url']))
    images.append(visual('activity', f'GitHub activity snapshot captured from GitSkins on {data["captured_on"]}; cached counts, not live GitHub totals. Interests: '+data['interests']+'. '+data['intro'], data['repositories_url']))
    images.append(visual('contact', data['contact']+' LET’S TALK — LET’S COLLABORATE — SAY HELLO. '+data['handle'], data['github']))
    images.append(visual('footer', data['location']+'. GitHub, profile, repositories and projects. Design by Isaac Fayemi. Original portfolio by Oluwadare Oluwaseyi.', data['repositories_url']))
    out = ['<p align="center">'+''.join(images)+'</p>\n', '<details>\n<summary>Profile, project links & design credits</summary>\n', '# '+data['name']+'\n\n'+data['intro']+'\n']
    out.append(f'[Interactive original]({data["source"]}) · [GitHub profile]({data["github"]}) · [All repositories]({data["repositories_url"]}) · [Email](mailto:{p["person"]["email"]})\n')
    out.append('### Selected work\n\n'+'\n'.join(f'- [{item["name"]}]({item["url"]}) — {item["language"]}' for item in data['projects'])+'\n')
    out.append('### Interests\n\n'+data['interests']+'\n')
    out.append('### Let’s talk\n\n'+data['contact']+'\n')
    out.append(f'This README preserves the appearance and project order of the linked GitSkins reference captured on {data["captured_on"]}. Its displayed repository, star and follower counts reproduce that cached reference; they are not live GitHub totals. The appearance stays dark in both GitHub themes. Project images open their repositories; the hero opens the interactive original. GitHub README images do not run the original video, scrolling, hover, clock or clipboard scripts.\n')
    out.append(' · '.join(f'[{credit["label"]}]({credit["url"]})' for credit in data['credits'])+'\n\nOpen Sauce typography by Alfredo Marco Pradil / Creative Sauce, SIL Open Font License 1.1. See [source and asset notices](NOTICE.md) and [build instructions](SETUP.md).\n\n</details>\n')
    return '\n'.join(out)


def build():
    text = render(C.load_readme_profile(), C.load_contributions())
    (ROOT / 'README.md').write_text(text, encoding='utf-8')
    print('readme: wrote README.md')


if __name__ == '__main__':
    build()
