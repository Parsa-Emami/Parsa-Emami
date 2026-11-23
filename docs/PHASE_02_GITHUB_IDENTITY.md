# Phase 02 — GitHub Professional Identity acceptance

**Canonical identity:** Parsa Emami / پارسا امامی.
**Primary technical focus:** Software engineering, backend/full-stack systems,
application security and verifiable releases.
**Repository:** https://github.com/Parsa-Emami/Parsa-Emami

## Implemented in source and generated profile

- Curated six GitHub repositories: Attestara, KeyHelix, MirageMesh,
  BreachAtlas, Demian and RiskWeft; all have honest release status, a
  first-party GitHub source URL and a technical-evidence route.
- Professional positioning and English-speaking international availability
  are stored in data/readme.json. This affects the README only and does not
  silently alter the canonical website's public profile source.
- Correct official website, LinkedIn and GitHub links remain above the fold.
- The previously prominent 2026-10-29 GitSkins editorial project graphics
  are archived inside an accessible details element, retaining credit,
  locally stored artwork and explicitly historical figures. The actual
  hero still links to the official portfolio.
- The generator is authoritative: changes to README.md alone would be lost
  on the next scheduled rebuild. Tests verify source-to-output equality.
- All new verification code uses the Python standard library and unittest.
  Existing site/vector builds use locally installed FOSS Python/Node
  dependencies; no paid SEO API, external design SaaS or proprietary runtime
  is introduced by this phase.
- The static link auditor checks allowed URL schemes, local files,
  alt text and absence of active HTML. It is **not** an external HTTP uptime
  check; do not present it as one.

## Manual GitHub account acceptance (not changed by repository commits)

Complete and verify on https://github.com/settings/profile :

| Setting | Proposed public value | Owner action |
| --- | --- | --- |
| Name | Parsa Emami | Confirm name on GitHub profile |
| Bio | Software Engineer & Security Architect | Laravel, Backend & Application Security | Confirm profile bio |
| Website | https://parsaaemm.dev/ | Confirm website field |
| Location | Actual current location only | Do not misrepresent location for relocation |
| Hireable | As desired by account owner | Requires account control |
| Pinned repositories | Attestara, Keyhelix, Miragemesh, Breachatlas, Demian, Riskweft | Use Customize your pins on profile |

Manual pin UI: open GitHub profile → **Customize your pins** → select the
six named public repositories and save. GitHub enforces the six-item pin
limit. Pins are separate GitHub account data, **not** part of the README.
No GitHub connector action with the necessary pinned-repository or
profile-settings write permissions is available in this workflow; do not
claim that pins or account Name/Bio/Website have been changed via commit.

## Offline acceptance checklist

1. Regenerate: `python scripts/build.py --only readme`.
2. Verify stable output: `git diff --exit-code -- README.md`.
3. Run tests: `python -m unittest discover -s tests -v`.
4. Audit links/assets: `python tools/verify_profile_links.py`.
5. Run theme tests: `node --test tests/theme.test.cjs`.
6. Confirm that default branch CI passes at the exact final merge SHA.
7. Separately inspect manual account fields and six pinned repositories.

**Important exclusions:** This phase does not change private repository
visibility, assert SEO rankings, enable Google Search Console, publish
LinkedIn content, or certify Demian production/character-art acceptance.
Those are separate gates in the overall brand roadmap.

## Public engineering evidence used

- Attestara: https://github.com/Parsa-Emami/Attestara/blob/main/README.md
- KeyHelix: https://github.com/Parsa-Emami/Keyhelix/blob/main/README.md
- MirageMesh: https://github.com/Parsa-Emami/Miragemesh/blob/main/README.md
- BreachAtlas: https://github.com/Parsa-Emami/Breachatlas/blob/main/README.md
- Demian: https://github.com/Parsa-Emami/Demian/blob/main/README.fa.md
- RiskWeft: https://github.com/Parsa-Emami/Riskweft/blob/main/README.md

The PR CI now exercises the **full** source build, not just README generation. This prevents README-only projects from omitting vector card fields such as `title` and breaking the daily build after merge.
