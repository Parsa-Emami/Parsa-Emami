#!/usr/bin/env python3
"""One command to rebuild everything generated from data/profile.json.

    python scripts/build.py            # README + SVG cards + website
    python scripts/build.py --fetch    # refresh data/contributions.json first (needs internet)
    python scripts/build.py --only readme|cards|site
"""
from __future__ import annotations

import argparse
import sys
import warnings

import build_cards
import build_readme
import build_site
import fetch_contributions

warnings.filterwarnings("ignore")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true", help="refresh contribution data before building")
    ap.add_argument("--only", choices=["readme", "cards", "site"], help="build just one target")
    args = ap.parse_args()

    if args.fetch:
        fetch_contributions.main()
    if args.only in (None, "cards"):
        build_cards.build()
    if args.only in (None, "readme"):
        build_readme.build()
    if args.only in (None, "site"):
        build_site.build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
