#!/usr/bin/env python3
"""Offline safety checks for public README identity, links and image assets.

Python standard library only. Does not crawl external sites or use paid APIs.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)')


class ProfileLinkError(ValueError):
    pass


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag.lower(), dict(attrs)))


def validate_link(value: str, root: Path = ROOT) -> None:
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise ProfileLinkError("Missing or invalid URL")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ProfileLinkError("Control character inside URL")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ProfileLinkError("Malformed URL") from exc
    if parsed.scheme == "mailto":
        address = parsed.path
        if not address or "@" not in address or parsed.netloc:
            raise ProfileLinkError("Invalid mailto link")
        return
    if parsed.scheme == "https":
        if not parsed.hostname or parsed.username or parsed.password or not parsed.netloc:
            raise ProfileLinkError("Untrusted HTTPS URL form")
        if any(ch.isspace() for ch in value):
            raise ProfileLinkError("Whitespace inside HTTPS URL")
        return
    if parsed.scheme or parsed.netloc or value.startswith(("/", "\\")):
        raise ProfileLinkError("Disallowed URL scheme or absolute path")
    if not parsed.path:
        if parsed.fragment:
            return  # Local heading fragment; GitHub renders it.
        raise ProfileLinkError("Empty relative path")
    local = unquote(parsed.path)
    candidate = (root / local).resolve()
    if not candidate.is_relative_to(root.resolve()) or not candidate.is_file():
        raise ProfileLinkError("Missing or escaping local asset: " + parsed.path)


def audit(text: str, root: Path = ROOT) -> dict:
    links = [match.group(1) for match in MARKDOWN_LINK.finditer(text)]
    images = 0
    for tag, attrs in Elements(text).tags:
        if tag in {"script", "iframe", "object", "embed", "form"}:
            raise ProfileLinkError("Executable or unsupported HTML tag: " + tag)
        if any(key.startswith("on") or key == "style" for key in attrs):
            raise ProfileLinkError("Inline active content not allowed")
        if tag == "img":
            images += 1
            if not attrs.get("alt"):
                raise ProfileLinkError("Image alt description is required")
        for attr in ("href", "src", "srcset"):
            if attr in attrs:
                links.append(attrs[attr])
    for link in links:
        validate_link(link, root)
    return {"checked_links": len(links), "image_count": images}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=ROOT / "README.md")
    args = parser.parse_args(argv)
    try:
        path = args.readme.resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ProfileLinkError("Refusing to audit outside repository")
        stats = audit(path.read_text(encoding="utf-8"))
        print(f"Verified {stats['checked_links']} safe link/asset references and {stats['image_count']} accessible images.")
        print("Offline validation only: live HTTP reachability and account settings are separate acceptance tasks.")
        return 0
    except (ProfileLinkError, OSError, UnicodeError) as exc:
        print(f"Profile link audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
