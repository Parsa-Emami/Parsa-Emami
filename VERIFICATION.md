# Kinetic Editorial portfolio verification

Verified locally on 2026-10-29 before committing.

- `python scripts/build.py` regenerates the README, 36 self-contained SVG cards and the static Pages site from tracked sources.
- `python -m unittest discover -s tests -v`: 21 passing tests, including escaped profile content, private-repository exclusion, local assets and anchors, canonical metadata and passive HTML alternatives.
- `node --test tests/*.test.cjs`: 9 passing tests, including OS theme changes, blocked storage, reduced-motion precedence, saved motion preferences, cross-tab changes and clipboard success/failure.
- `git diff --check`: passed.

Browser checks used the actual local preview in Chrome. Desktop and 320, 390 and 768 pixel iframe viewports were inspected. Each matched its document scroll width, with no horizontal page overflow. Both color palettes, local project artwork, navigation, the native experience disclosure, saved theme preference, motion pause and resume were checked. No site-origin warning or error appeared; unrelated browser-extension messages were excluded.

The HTTP preview correctly reports unavailable clipboard access and leaves the selectable email address and `mailto:` link available. Clipboard success is covered by the JavaScript tests; HTTPS behavior is checked after GitHub Pages publication.

HEAD requests returned HTTP 200 for the canonical website, Pages URL, résumé, both existing project case studies, MirageMesh source notes, the three writing links and the experiment destination. The architectural image is original decorative artwork. The three project illustrations are explicitly labeled concept studies.

The Pages mirror preserves the existing `noindex,follow` and canonical domain policy. GitHub README content uses passive Markdown/HTML and links to the interactive portfolio. No account permission, repository visibility, domain configuration, API token or paid GitSkins export is needed.
