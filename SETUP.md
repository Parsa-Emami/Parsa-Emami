# Profile source

[فارسی](SETUP.fa.md)

The README follows the [personalized GitSkins reference](https://www.gitskins.com/portfolio-templates/seyi-editorial/standalone/?username=Parsa-Emami): the architectural hero, Open Sauce typography, lime labels, six projects in the original order, public repositories, activity, interests and contact. The desktop hero captures the rendered reference. Other sections are self-contained SVGs with Open Sauce glyph paths; mobile versions use narrower layouts. Both GitHub themes keep the reference's dark appearance. The separate Pages mirror retains its own templates and palette.

`data/profile.json` supplies the public content and both color palettes. The builders produce `README.md`, responsive SVG cards and the static `site/` directory. Edit the source data or templates, then rebuild; generated output is replaced on the next build.

`data/readme.json` selects the reference presentation; `data/seyi-reference.json` stores its copy, project order, cached counts, capture date and credits. README and card builders use `load_readme_profile()`; the site builder uses `load_profile()`. The previous palette and additional-project settings remain available to the legacy card builder. Scheduled rebuilds preserve the reference presentation. Counts are deliberately frozen to the captured GitSkins source and are not live GitHub totals.

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

Use `--only cards`, `--only readme` or `--only site` for a targeted build. Cards also rebuild the reference vectors. Add `--fetch` to refresh the separate contribution snapshot; offline builds reuse `data/contributions.json`. `--only site` generates its own artwork and can run independently.

## Content

| Source | Purpose |
| --- | --- |
| `person`, `hero`, `perspective`, `method` | Identity, introduction and working approach |
| `projects`, `explorations` | Public work with explicit implementation status |
| `professional`, `experience`, `education` | Public professional chronology, without internal product details |
| `about`, `focus`, `notes`, `links` | Biography, skills, writing and contact routes |
| `design.themes` | Shared light and dark colors for the cards and site |
| `contributions` | Activity collection settings |
| `data/readme.json` | README presentation selection and legacy card settings |
| `data/seyi-reference.json` | Captured reference content, six projects, counts, date and credits |
| `scripts/build_seyi.py`, `scripts/lib/seyi.py` | Reference graphics and Open Sauce glyph outlines |
| `assets/seyi-editorial/hero-desktop.jpg`, `hero-background.jpg` | Captured hero and a still of the original video |
| `scripts/templates/` | Site CSS and JavaScript source |

Organizational product descriptions, interfaces and internal architecture are excluded from public output. Project status is editorial content: update it when the source repository changes.

Every project image opens its repository; the hero opens the interactive original. A collapsible text version supplies selectable identity, links, email, source date and credits. Mobile graphics are selected below 640px. GitHub cannot run the original video, scrolling, hover, live clock or clipboard scripts in README markup. Keep the captured hero image and JSON snapshot consistent when updating identity or reference content. Source images must be recaptured separately; builds do not contact GitSkins. See `NOTICE.md` for original design and asset attribution.

## Automation

`Update profile` refreshes contribution data, rebuilds, runs Python and theme tests, and commits generated changes including the reference vectors. It runs daily, on demand and after source changes on `main`. It requires `contents: write` and standard `GITHUB_TOKEN`; no new secret is needed. The contribution collector does not change reference counts.

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
