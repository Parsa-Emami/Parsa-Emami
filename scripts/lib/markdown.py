from __future__ import annotations


def activity(contrib):
    r = contrib.get('range', {})
    if not contrib.get('days'):
        return 'No activity snapshot available.'
    return f'Period: {r.get("start", "")} — {r.get("end", "")}. Calendar and public repository commit signals are merged per day. This is an activity snapshot, not the official GitHub profile contribution total.'


def render(p, contrib, base=''):
    out = [f'# {p["person"]["name"]}', p['person']['role'], p['hero']['intro'], p['hero']['availability'], '## A point of view', p['perspective']['title']+' '+p['perspective']['accent'], p['perspective']['text'], p['perspective']['detail'], '## How I think']
    out.extend(f'### {x["verb"]}: {x["title"]}\n\n{x["text"]}\n\n{x["question"]}' for x in p['method']['steps'])
    out.extend(['> '+p['method']['principle'], '## Work in public'])
    for x in p['projects']:
        out.append(f'### [{x["name"]}]({x["url"]})\n\n{x["status"]}\n\n{x["summary"]}\n\n{x["scope"]}\n\n[Project notes]({x["case_study"]})')
    out.extend(f'[{x["name"]}]({x["url"]}) — {x["label"]}' for x in p['explorations'])
    out.extend([p['professional']['text'], '## A small experiment', f'[{p["experiment"]["title"]}]({p["experiment"]["url"]})', p['experiment']['text'], p['experiment']['note'], '## About', *p['about'], '## Areas of focus'])
    out.extend(f'- **{x["title"]}** — '+', '.join(x['items']) for x in p['focus'])
    out.append('## Experience')
    out.extend(f'- **{x["role"]} · {x["company"]}** ({x["start"]} — {x["end"] or "present"}). {x["description"]}' for x in p['experience'])
    out.append('## Education')
    out.extend(f'- **{x["degree"]}** · {x["school"]} · {x["period"]}' for x in p['education'])
    out.append('## Field notes')
    out.extend(f'- [{x["title"]}]({x["url"]}) — {x["category"]}' for x in p['notes'])
    out.append(f'## Contact\n\n[{p["person"]["email"]}](mailto:{p["person"]["email"]})\n\n[Website]({p["site"]["url"]}) · [Résumé]({p["professional"]["resume"]})')
    return '\n\n'.join(out)+'\n'
