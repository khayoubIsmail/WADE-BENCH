import re
from pathlib import Path

def clean_html(html: str) -> str:
    """
    Basic HTML cleaning utility.
    """
    if not html:
        return ""
    # Remove scripts and styles
    html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html, flags=re.IGNORECASE)
    # Remove HTML comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    return html

def read_html(path: str | Path) -> str:
    path = Path(path)
    return path.read_text(encoding="utf-8", errors="replace")


def lightly_clean_html(html: str) -> str:
    """
    Light cleaning only. Do not remove JSON-LD or embedded app data.
    """
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"\n\s*\n+", "\n", html)
    return html.strip()


def truncate_html(html: str, max_chars: int | None = 180000) -> str:
    """
    Temporary safety limit for long HTML.
    Better chunking can be added later.
    """
    if max_chars is None or len(html) <= max_chars:
        return html
    return html[:max_chars] + "\n<!-- HTML truncated due to context limit -->"
