# Parsa-Emami Animated GitHub Profile — Setup

This pack is already configured for the GitHub username `Parsa-Emami`.

## 1. Copy the pack into the profile repository

Clone:

```bash
git clone https://github.com/Parsa-Emami/Parsa-Emami.git
cd Parsa-Emami
```

Copy every file/folder from this pack into the cloned repository.

## 2. Generate your portrait locally

For best results, replace `source-photo.jpg` with a sharp 1:1 or portrait photo (at least 700 px wide).

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r scripts/requirements-local.txt

python scripts/prep_photo.py source-photo.jpg
python scripts/make_ascii_svg.py
python scripts/make_wordmark_svg.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r scripts/requirements-local.txt

python scripts/prep_photo.py source-photo.jpg
python scripts/make_ascii_svg.py
python scripts/make_wordmark_svg.py
```

## 3. Commit and push

```bash
git add .
git commit -m "feat: build animated GitHub profile"
git push origin main
```

## 4. Run the contribution workflow once

GitHub → `Parsa-Emami/Parsa-Emami` → **Actions** → **Refresh animated profile** → **Run workflow**.

The workflow fetches your public contribution calendar, generates `data/contributions.json`,
renders `contrib-heatmap.svg`, commits both files, and pushes them back to `main`.

## 5. Daily refresh

The workflow runs every day at `06:17 UTC` and regenerates the contribution art.

## Optional customizations

Edit `README.md` to change links/badges.

Edit `scripts/make_wordmark_svg.py` to change role/focus text.

Edit the palette constants in `scripts/make_ascii_svg.py`,
`scripts/make_wordmark_svg.py`, and `scripts/render_heatmap_svg.py`.

## Important

No Personal Access Token is required by this implementation. The workflow only needs
the repository-scoped `GITHUB_TOKEN` with `contents: write`, configured in the YAML.

If GitHub rejects the push, open:
Repository Settings → Actions → General → Workflow permissions,
and make sure the repository allows the workflow token to write repository contents.
