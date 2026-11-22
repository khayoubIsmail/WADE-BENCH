"""
snapshot.py  —  WADE-Bench page capture tool
Combines Playwright (primary) + SingleFile (archive).

Outputs per URL:
  page.html        – rendered DOM after JS + lazy-scroll  [PRIMARY]
  screenshot.png   – full-page screenshot
  text.txt         – visible text (innerText)
  ax_tree.json     – full accessibility tree
  metadata.json    – capture provenance
  singlefile.html  – self-contained archive (assets inlined) [ARCHIVE ONLY]

Usage:
  python3 snapshot.py <url> [output_dir]
"""

import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Fix Windows console emoji encoding
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ── CLI args ──────────────────────────────────────────────────────────────────
url     = sys.argv[1] if len(sys.argv) > 1 else None
out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "snapshot_output")

if not url:
    sys.exit("Usage: python3 snapshot.py <url> [output_dir]")

out_dir.mkdir(parents=True, exist_ok=True)

VIEWPORT = {"width": 1440, "height": 900}

# ── 1. Playwright pass ────────────────────────────────────────────────────────
print("🚀 Launching browser…")
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    context = browser.new_context(
        viewport=VIEWPORT,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        },
    )
    page = context.new_page()
    # Patch common bot-detection signals
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        window.chrome = {runtime: {}};
        
        // Continuous popup killer for delayed ads/modals
        setInterval(() => {
            const btns = document.querySelectorAll("button[aria-label*='Close'], button[aria-label*='close'], .close-button, .modal-close, .klaviyo-close-form");
            for (let btn of btns) {
                if (btn.offsetParent !== null) { // Simple visibility check
                    btn.click();
                }
            }
        }, 1000);
    """)

    print(f"🌐 Navigating to {url}…")
    # Use domcontentloaded — many SPAs/CDNs keep background XHR alive forever,
    # causing networkidle to never fire (Warby Parker / Akamai pattern).
    response = page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    status = response.status if response else None

    # Wait for main content to render (product title or body — whichever comes first)
    try:
        page.wait_for_selector("main, [data-testid], h1, .product", timeout=15_000)
    except Exception:
        pass  # Continue even if selector not found; page may still be usable

    page.wait_for_timeout(5000)  # Extra settle time for JS frameworks & delayed popups (Klaviyo)

    # Attempt to dismiss common popups/banners that might block scrolling
    dismiss_texts = [
        "Stay on U.S. Site", "Accept Cookies", "Accept All", "Accept", 
        "Close", "Got it", "I Agree", "Dismiss", "No Thanks"
    ]
    for text in dismiss_texts:
        try:
            for btn in page.get_by_text(text).all():
                if btn.is_visible():
                    btn.click(force=True)
                    print(f"🛑 Dismissed popup by text: '{text}'")
                    page.wait_for_timeout(500)
        except Exception:
            pass

    # Attempt to click generic close icons
    try:
        close_btns = page.locator("button[aria-label*='Close'], button[aria-label*='close'], .close-button, .modal-close, .klaviyo-close-form")
        for i in range(close_btns.count()):
            btn = close_btns.nth(i)
            if btn.is_visible():
                btn.click(force=True)
                print("🛑 Dismissed popup by generic close button")
                page.wait_for_timeout(500)
    except Exception:
        pass

    # Attempt to click "Load more" or "View all" buttons to expand product lists
    load_more_texts = ["View all", "Load more", "Show more", "Load more products"]
    for text in load_more_texts:
        try:
            for btn in page.get_by_text(text).all():
                if btn.is_visible():
                    btn.click(force=True)
                    print(f"🔄 Clicked pagination button: '{text}'")
                    page.wait_for_timeout(2000)
        except Exception:
            pass

    # Scroll to trigger lazy-loaded images or infinite scrolls, then return to top
    page.evaluate("""async () => {
        await new Promise(resolve => {
            let total = 0;
            const dist = 400;
            let lastHeight = document.body.scrollHeight;
            let unchangedCount = 0;
            
            const timer = setInterval(() => {
                window.scrollBy(0, dist);
                total += dist;
                
                if (total >= document.body.scrollHeight) {
                    if (document.body.scrollHeight > lastHeight) {
                        // Height expanded (new content loaded)
                        lastHeight = document.body.scrollHeight;
                        unchangedCount = 0;
                    } else {
                        // Reached bottom, wait to see if it loads more
                        unchangedCount++;
                        if (unchangedCount >= 15) { // Wait ~1.5s at the bottom
                            clearInterval(timer);
                            window.scrollTo(0, 0);
                            resolve();
                        }
                    }
                }
            }, 100);
        });
    }""")
    page.wait_for_timeout(1000)

    final_url = page.url
    title     = page.title()

    # page.html  ───────────────────────────────────────────────────────────────
    print("💾 Saving page.html…")
    (out_dir / "page.html").write_text(page.content(), encoding="utf-8")

    # screenshot.png  ──────────────────────────────────────────────────────────
    print("📸 Taking screenshot…")
    page.screenshot(path=str(out_dir / "screenshot.png"), full_page=True)

    # text.txt  ────────────────────────────────────────────────────────────────
    print("📝 Extracting visible text…")
    text = page.evaluate("() => document.body.innerText")
    (out_dir / "text.txt").write_text(text, encoding="utf-8")

    # ax_tree.json  ────────────────────────────────────────────────────────────
    print("♿ Extracting accessibility tree…")
    ax = page.accessibility.snapshot(interesting_only=False)
    (out_dir / "ax_tree.json").write_text(
        json.dumps(ax, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    browser.close()

print("✅ Playwright artifacts saved.")

# ── 2. SingleFile pass ────────────────────────────────────────────────────────
# Windows-compatible binary lookup (covers .cmd wrapper on Windows)
sf_bin = shutil.which("single-file") or shutil.which("single-file.cmd")

# Resolve browser for SingleFile.
# Playwright's chrome.exe is instrumented and crashes inside single-file-cli's
# Node subprocess (exit 0xC0000009). Use a plain system browser instead,
# trying candidates in order of preference.
def _find_system_browser() -> "str | None":
    import platform
    candidates = []
    if platform.system() == "Windows":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            # Chromium from winget / scoop
            shutil.which("chromium") or "",
            shutil.which("chrome") or "",
        ]
    elif platform.system() == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:  # Linux
        candidates = [
            shutil.which("google-chrome") or "",
            shutil.which("chromium-browser") or "",
            shutil.which("chromium") or "",
            shutil.which("microsoft-edge") or "",
        ]

    from pathlib import Path as _P
    for c in candidates:
        if c and _P(c).exists():
            return c

    # Last resort: fall back to Playwright's own binary
    try:
        result = subprocess.run(
            [sys.executable, "-c",
             "from playwright.sync_api import sync_playwright\n"
             "with sync_playwright() as p: print(p.chromium.executable_path)"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None

chromium_path = _find_system_browser()

sf_captured = False
if sf_bin and chromium_path:
    print(f"📦 Running SingleFile…")
    print(f"   chromium : {chromium_path}")
    print(f"   binary   : {sf_bin}")
    sf_out = str(out_dir / "singlefile.html")
    try:
        result = subprocess.run(
            [
                sf_bin,
                "--browser-executable-path", chromium_path,
                "--browser-headless",                        # explicit headless mode
                "--filename-conflict-action", "overwrite",
                "--browser-args", json.dumps(["--no-sandbox", "--disable-gpu"]),
                url, sf_out,
            ],
            timeout=120, check=True,
            capture_output=True, text=True,
        )
        sf_captured = True
        print("✅ singlefile.html saved.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  SingleFile failed (exit {e.returncode})")
        if e.stderr:
            print(f"   stderr: {e.stderr[:500]}")
elif not sf_bin:
    print("⚠️  single-file not found — install: npm install -g single-file-cli")

# ── 3. metadata.json  ────────────────────────────────────────────────────────
def sha256(path: Path) -> "str | None":
    import hashlib
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

ARTIFACT_FILES = ["page.html", "screenshot.png", "text.txt", "ax_tree.json", "singlefile.html"]

metadata = {
    "url":                url,
    "final_url":          final_url,
    "title":              title,
    "http_status":        status,
    "viewport":           f"{VIEWPORT['width']}x{VIEWPORT['height']}",
    "capture_tool":       "Playwright + SingleFile",
    "captured_at":        datetime.datetime.utcnow().isoformat() + "Z",
    "page_html_primary":  True,
    "singlefile_archive": sf_captured,
    "sha256":             {f: sha256(out_dir / f) for f in ARTIFACT_FILES},
}
(out_dir / "metadata.json").write_text(
    json.dumps(metadata, indent=2), encoding="utf-8"
)

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n📂 Output:")
for f in sorted(out_dir.iterdir()):
    print(f"   {f.name:<22} {f.stat().st_size / 1024:>8.1f} KB")