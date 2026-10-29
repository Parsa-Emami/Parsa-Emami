# Profile source

[فارسی](SETUP.fa.md)

The GitHub README uses an independently implemented editorial design inspired by [Kinetic Editorial](https://www.gitskins.com/portfolio/templates/seyi-editorial): oversized typography, graphite and lime, responsive cards and three selected public projects. The static Pages mirror has its own templates and palette, based on [parsaaemm.dev](https://parsaaemm.dev/).

`data/profile.json` supplies the public content and both color palettes. The builders produce `README.md`, responsive SVG cards and the static `site/` directory. Edit the source data or templates, then rebuild; generated output is replaced on the next build.

`data/readme.json` configures the README palette, additional featured projects and selected explorations independently from the Pages site. README and card builders use `load_readme_profile()`; the site builder uses `load_profile()`. Shared project metadata takes precedence when a featured project already exists in `data/profile.json`. The scheduled rebuild preserves the published README design.

## Local workflow

```sh
python -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m unittest discover -s tests -v
node --test tests/theme.test.cjs
.venv/bin/python -m http.server --directory site 8000
```

Python 3.12 and Node 22 are used in CI. Linux needs FreeType with RAQM for Pillow font rendering (`libraqm0` on Ubuntu). Node is only needed for the theme interaction tests; the published site has no runtime dependencies.

Use `--only cards`, `--only readme` or `--only site` for a targeted build. Add `--fetch` to refresh activity first; offline builds reuse `data/contributions.json`. `--only site` generates its own artwork and can run independently.

## Content

| Source | Purpose |
| --- | --- |
| `person`, `hero`, `perspective`, `method` | Identity, introduction and working approach |
| `projects`, `explorations` | Public work with explicit implementation status |
| `professional`, `experience`, `education` | Public professional chronology, without internal product details |
| `about`, `focus`, `notes`, `links` | Biography, skills, writing and contact routes |
| `design.themes` | Shared light and dark colors for the cards and site |
| `contributions` | Activity collection settings |
| `data/readme.json` | README-specific palette, additional public projects and exploration selection |
| `scripts/templates/` | Site CSS and JavaScript source |

Organizational product descriptions, interfaces and internal architecture are excluded from public output. Project status is editorial content: update it when the source repository changes.

The README uses real Markdown links and text alongside accessible SVGs. Each visual has a light and dark version, with separate narrow layouts selected below 640px. Geist glyphs are stored as vector outlines in the cards, so the main type needs no remote font request. The serif accent uses the viewer’s Georgia or serif font.

## Automation

`Update profile` refreshes activity, rebuilds, runs Python and theme tests, and commits generated changes. It runs daily, on demand and after source changes on `main`. It requires `contents: write` and standard `GITHUB_TOKEN`; no new secret is needed.

`Deploy site` publishes `site/` through GitHub Pages. Pages must already use **GitHub Actions** as its source. The Pages mirror keeps `https://parsaaemm.dev/` canonical and sends `noindex,follow`. It does not replace the live canonical website.

The activity graphic combines configured public calendars with public repository commit signals per day. It is labeled as an activity snapshot rather than GitHub’s official contribution total. If all sources fail, the collector preserves the previous snapshot.

## File map

| Path | Ownership |
| --- | --- |
| `README.md`, `assets/cards/`, `site/` | Generated output |
| `data/profile.json` | Public content and design tokens |
| `data/contributions.json` | Cached activity snapshot |
| `scripts/build.py` | Build entry point |
| `scripts/build_cards.py`, `scripts/lib/brand.py` | Responsive vector graphics |
| `scripts/build_readme.py`, `scripts/lib/markdown.py` | GitHub and plain text presentation |
| `scripts/build_site.py`, `scripts/templates/` | Static Pages mirror |
| `scripts/make_og.py` | Deterministic 1200 × 630 sharing image |
| `tests/` | Source, output and theme checks |

Generated cards no longer in the build are removed from `assets/cards/`. Keep hand-authored assets outside that directory. Original portrait sources remain under `assets/`.
