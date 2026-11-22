from pathlib import Path
import json
from bs4 import BeautifulSoup

from wadebench.mcp.playwright_mcp_client import collect_playwright_mcp_evidence


def read_optional(path: str | Path | None, max_chars: int = 60000) -> str | None:
    if not path:
        return None

    path = Path(path)
    if not path.exists():
        return None

    text = path.read_text(encoding="utf-8", errors="replace")

    if len(text) > max_chars:
        return text[:max_chars] + "\n<!-- TRUNCATED -->"

    return text


def get_source_file(task: dict, keys: list[str]) -> str | None:
    source_files = task.get("source_files", {})

    for key in keys:
        if key in source_files and source_files[key]:
            return source_files[key]

    return None


def extract_html_signals(page_html_path: str | Path, max_items: int = 200) -> dict:
    html = read_optional(page_html_path, max_chars=150000)

    if not html:
        return {}

    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(" ", strip=True) if soup.title else None

    headings = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(" ", strip=True)
        if text:
            headings.append({
                "tag": tag.name,
                "text": text[:300],
            })
        if len(headings) >= max_items:
            break

    links = []
    for a in soup.find_all("a"):
        text = a.get_text(" ", strip=True)
        href = a.get("href")
        if text or href:
            links.append({
                "text": text[:300],
                "href": href,
            })
        if len(links) >= max_items:
            break

    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        alt = img.get("alt")
        if src or alt:
            images.append({
                "src": src,
                "alt": alt,
            })
        if len(images) >= max_items:
            break

    embedded_json = []
    for s in soup.find_all("script"):
        script_type = s.get("type", "")
        script_id = s.get("id", "")
        content = s.string or s.get_text() or ""

        if (
            "json" in script_type.lower()
            or "ld+json" in script_type.lower()
            or "__NEXT_DATA__" in script_id
        ):
            content = content.strip()
            if content:
                embedded_json.append({
                    "type": script_type,
                    "id": script_id,
                    "content": content[:20000],
                })

        if len(embedded_json) >= 20:
            break

    return {
        "title": title,
        "headings": headings,
        "links": links,
        "images": images,
        "embedded_json": embedded_json,
    }


def build_b4_mcp_evidence(task: dict) -> dict:
    task_id = task["task_id"]

    page_html = get_source_file(task, ["page_html", "html"])
    page_safe = get_source_file(task, ["page_safe_html", "safe_html", "page_safe"]) or page_html
    text_txt = get_source_file(task, ["text", "text_txt", "visible_text"])
    ax_tree = get_source_file(task, ["ax_tree", "ax_tree_json", "accessibility_tree"])
    metadata = get_source_file(task, ["metadata", "metadata_json"])
    screenshot = get_source_file(task, ["screenshot", "screenshot_png", "screenshot_path"])

    if not page_safe:
        raise FileNotFoundError(f"No page.safe.html/page.html found for {task_id}")

    mcp_evidence = collect_playwright_mcp_evidence(
        page_safe_path=page_safe,
        task_id=task_id,
    )

    html_signals = extract_html_signals(page_html) if page_html else {}

    evidence = {
        "task_id": task_id,
        "source_files": {
            "page_html": page_html,
            "page_safe_html": page_safe,
            "text_txt": text_txt,
            "ax_tree": ax_tree,
            "metadata": metadata,
            "screenshot": screenshot,
        },
        "mcp": {
            "file_url": mcp_evidence.get("file_url"),
            "available_tools": mcp_evidence.get("available_mcp_tools", []),
            "browser_snapshot": mcp_evidence.get("mcp_browser_snapshot", "")[:40000],
            "navigation_result": mcp_evidence.get("navigation_result", "")[:5000],
        },
        "visible_text": read_optional(text_txt, max_chars=20000),
        "ax_tree_excerpt": read_optional(ax_tree, max_chars=20000),
        "metadata_excerpt": read_optional(metadata, max_chars=10000),
        "html_signals": html_signals,
        "tool_trace": mcp_evidence.get("tool_trace", []),
    }

    return evidence


def save_b4_evidence_and_trace(evidence: dict, task_id: str, split: str = "dev") -> tuple[str, str]:
    evidence_dir = Path("data/processed_evidence/b4_playwright_mcp_agent") / task_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = evidence_dir / "evidence.json"
    evidence_path.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logs_dir = Path("logs/b4_playwright_mcp_agent") / split
    logs_dir.mkdir(parents=True, exist_ok=True)

    trace_path = logs_dir / f"{task_id}_tool_trace.json"
    trace_path.write_text(
        json.dumps(evidence.get("tool_trace", []), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return str(evidence_path), str(trace_path)
