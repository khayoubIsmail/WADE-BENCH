import json
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib

def sha256(path: Path) -> "str | None":
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

out_dir = Path(r"data/raw_snapshots/jobs/github_careers_listing")
sf_path = out_dir / "singlefile.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(sf_path.as_uri())
    
    # Generate ax_tree.json
    ax = page.accessibility.snapshot(interesting_only=False)
    (out_dir / "ax_tree.json").write_text(json.dumps(ax, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Generate text.txt
    text = page.evaluate("() => document.body.innerText")
    (out_dir / "text.txt").write_text(text, encoding="utf-8")
    browser.close()

# Generate metadata.json
ARTIFACT_FILES = ["page.html", "screenshot.png", "text.txt", "ax_tree.json", "singlefile.html"]
metadata = {
    "url": "https://www.github.careers/careers-home/jobs",
    "final_url": "https://www.github.careers/careers-home/jobs",
    "title": "GitHub Careers",
    "http_status": 200,
    "viewport": "1440x900",
    "capture_tool": "Playwright MCP + Local CSS Extract",
    "captured_at": datetime.datetime.utcnow().isoformat() + "Z",
    "page_html_primary": True,
    "singlefile_archive": True,
    "sha256": {f: sha256(out_dir / f) for f in ARTIFACT_FILES},
}

(out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
print("Saved ax_tree.json, text.txt, metadata.json")
