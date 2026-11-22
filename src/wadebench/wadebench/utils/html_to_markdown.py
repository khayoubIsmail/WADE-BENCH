from pathlib import Path
from bs4 import BeautifulSoup
import re


NOISE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "svg",
    "iframe",
    "canvas",
    "template",
]


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


def html_to_markdown(html: str, base_url: str | None = None, max_chars: int | None = 40000) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Remove noisy tags
    for selector in NOISE_SELECTORS:
        for tag in soup.find_all(selector):
            tag.decompose()

    lines = []

    # Page title
    if soup.title and soup.title.get_text(strip=True):
        lines.append(f"# {clean_text(soup.title.get_text())}")
        lines.append("")

    # Extract useful visible elements
    useful_tags = [
        "h1", "h2", "h3", "h4",
        "p", "li",
        "a",
        "img",
        "td", "th",
        "span", "div"
    ]

    seen = set()

    for tag in soup.find_all(useful_tags):
        text = clean_text(tag.get_text(" ", strip=True))

        if not text and tag.name != "img":
            continue

        # Avoid excessive duplicate lines
        key = (tag.name, text[:200])
        if key in seen:
            continue
        seen.add(key)

        if tag.name in ["h1", "h2", "h3", "h4"]:
            level = int(tag.name[1])
            lines.append("#" * level + " " + text)

        elif tag.name == "a":
            href = tag.get("href")
            if href:
                lines.append(f"- Link text: {text}")
                lines.append(f"  URL: {href}")
            elif text:
                lines.append(f"- {text}")

        elif tag.name == "img":
            alt = clean_text(tag.get("alt", ""))
            src = tag.get("src") or tag.get("data-src") or tag.get("data-original")
            if alt or src:
                lines.append("- Image:")
                if alt:
                    lines.append(f"  Alt: {alt}")
                if src:
                    lines.append(f"  URL: {src}")

        elif tag.name in ["td", "th"]:
            if text:
                lines.append(f"| {text} |")

        elif text:
            lines.append(f"- {text}")

        if max_chars is not None and len("\n".join(lines)) > max_chars:
            lines.append("")
            lines.append("<!-- MARKDOWN TRUNCATED DUE TO CONTEXT LIMIT -->")
            break

    markdown = "\n".join(lines)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def html_file_to_markdown(path: str | Path, max_chars: int | None = 40000) -> str:
    html = Path(path).read_text(encoding="utf-8", errors="replace")
    return html_to_markdown(html, max_chars=max_chars)
