# Setup

> فارسی: [SETUP.fa.md](SETUP.fa.md)

This repository is your **GitHub profile README** (`Parsa-Emami/Parsa-Emami`) plus a matching
**website** in the same design (inspired by [chanhdai.com](https://chanhdai.com)).
Everything is generated from one file: [`data/profile.json`](data/profile.json).

```
data/profile.json ──► scripts/build.py ──► README.md          (what visitors see on github.com/Parsa-Emami)
                                       ├─► assets/cards/*.svg  (light + dark cards used by the README)
                                       └─► site/               (static website, deployable to GitHub Pages)
```

A GitHub README cannot run CSS or JavaScript, so the README is made of SVG cards that copy the
website's look, and the website is the fully interactive version (⌘K / Ctrl+K search, theme toggle,
"Show more", animated tagline).

## 1. Publish it (5 minutes)

1. The repository must be **public** and named exactly `Parsa-Emami` (same as your username).
2. Replace the repository contents with the contents of this folder and push to `main`:
   ```bash
   git clone https://github.com/Parsa-Emami/Parsa-Emami.git
   cd Parsa-Emami
   # delete the old files, copy the new ones in, then:
   git add -A && git commit -m "feat: chanhdai-style profile" && git push
   ```
3. **Settings → Actions → General → Workflow permissions →** choose **Read and write permissions** → Save.
4. **Actions → Update profile → Run workflow.** It refreshes the activity heatmap, rebuilds everything and commits the result.
   It then runs by itself every day and whenever you change `data/profile.json`.

### Optional: the website

**Settings → Pages → Build and deployment → Source: GitHub Actions.**
Then run **Actions → Deploy site**. It will be live at `https://parsa-emami.github.io/Parsa-Emami/`
(the README's "Interactive site" button points there; change `site.url` in `profile.json` if you use another address).

## 2. Edit your content

Open `data/profile.json`, change text, commit. The workflow rebuilds README and site.

| Key | What it controls |
| --- | --- |
| `person` | name, role, rotating tagline (`flip`), coordinates in "Fig. 1", location. Optional `email`, `phone`, `pronouns` are hidden while empty. |
| `overview`, `links`, `cta` | the icon list, social buttons and the closing line |
| `about`, `principles`, `focus` | text sections (`[label](url)` makes a link) |
| `stack`, `experience`, `education`, `projects`, `lab`, `research` | the structured sections |
| `awards`, `certifications` | empty by default. Add items like `{ "title": "...", "issuer": "...", "year": 2026, "url": "..." }` and the section appears. |
| `contributions` | which accounts feed the heatmap (see below) |

Dates use `YYYY-MM`; use `"end": null` for a current role. Durations ("1y 1m") are computed automatically.

## 3. Change the photo

```bash
pip install -r scripts/requirements-local.txt
python scripts/prep_avatar.py assets/source/source-photo.jpg --cx 1015 --cy 1215 --size 1500
python scripts/make_og.py        # optional: link-preview image (needs `playwright install chromium`)
python scripts/build.py
```
`--cx/--cy/--size` are the square crop (centre and side, in original photo pixels).
Light theme gets a pencil-sketch version, dark theme gets the graded photo.

## 4. Preview locally

```bash
pip install -r scripts/requirements.txt
python scripts/build.py
python -m http.server -d site 8000     # open http://localhost:8000
```
Run the tests with `python -m unittest discover -s tests -v`.

## 5. About the empty heatmap

GitHub's own calendar counts only commits whose e-mail is linked to your account. Your public
calendar currently shows **0 contributions** for `Parsa-Emami` (and 1 for `parsaemm`), while your repositories'
commits are authored by `parsaemm`. So `scripts/fetch_contributions.py` merges two sources per day (taking the larger
value, never adding): the calendars of the accounts in `contributions.accounts`, **plus** the commits in your public
repositories, whoever authored them. Set `"include_repo_commits": false` to show only GitHub's official calendar.

To make GitHub's own graph count your work as well: **Settings → Emails →** add the e-mail you use in `git config user.email`
to the account, or commit with your `@users.noreply.github.com` address.

## 6. Layout

| Path | Purpose |
| --- | --- |
| `README.md` | generated, do not edit by hand |
| `data/profile.json` | **all content** |
| `data/contributions.json` | generated activity data |
| `assets/cards/` | generated SVG cards (light + dark) |
| `assets/avatar/`, `assets/source/` | avatar variants and the original photo |
| `site/` | generated website (`assets/css`, `assets/js` are hand-written) |
| `scripts/` | build pipeline (`build.py` runs everything) |
| `tests/` | unit tests for the activity collector |
| `.github/workflows/` | `update-profile.yml` (daily rebuild), `pages.yml` (deploy site) |

## Troubleshooting

* **The workflow can't push** → step 3 above (workflow permissions).
* **Deploy site fails with "Pages not enabled"** → Settings → Pages → Source: GitHub Actions.
* **Cards look different from the preview** → they embed the Geist font; if a viewer blocks embedded fonts it falls back to system fonts (layout stays readable).
* **The README doesn't update** → GitHub caches images for a few minutes; hard-refresh.
