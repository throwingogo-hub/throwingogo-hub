#!/usr/bin/env python3
"""Validate the profile README, portfolio metadata, and share card."""

from html.parser import HTMLParser
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
PROJECT_URLS = {
    "https://github.com/throwingogo-hub/chatgpt-delagger",
    "https://github.com/throwingogo-hub/senel",
    "https://github.com/throwingogo-hub/DigitalPets",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: set[str] = set()
        self.meta: dict[str, str] = {}
        self.articles = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.add(values["href"] or "")
        if tag == "meta":
            key = values.get("name") or values.get("property")
            if key and values.get("content"):
                self.meta[key] = values["content"] or ""
        if tag == "article":
            self.articles += 1


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path}"
    return struct.unpack(">II", data[16:24])


def main() -> None:
    readme = (ROOT / "README.md").read_text()
    assert "detaches heavy" not in readme.lower()
    assert all(url in readme for url in PROJECT_URLS)

    parser = PageParser()
    parser.feed((ROOT / "index.html").read_text())
    assert parser.articles == 3
    assert PROJECT_URLS <= parser.links
    for key in ("description", "og:title", "og:description", "og:image", "twitter:card"):
        assert parser.meta.get(key), f"missing {key}"

    preview = ROOT / "assets/social-preview.png"
    assert png_size(preview) == (1280, 640)
    assert preview.stat().st_size < 1_000_000
    print("PASS: profile README, 3 project cards, sharing metadata, 1280x640 preview")


if __name__ == "__main__":
    main()
