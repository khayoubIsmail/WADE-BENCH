import os
import re
import json
import argparse
from pathlib import Path

def scrub_redirect_scripts(html: str) -> tuple[str, int]:
    removed_count = 0
    def should_remove(script_content: str) -> bool:
        patterns = [
            r'location\.href\s*=',
            r'location\.replace\s*\(',
            r'window\.location\s*=',
            r'top\.location',
            r'document\.location\s*=',
        ]
        return any(re.search(p, script_content, flags=re.IGNORECASE) for p in patterns)

    def replace_script(match):
        nonlocal removed_count
        script = match.group(0)
        if should_remove(script):
            removed_count += 1
            return '<!-- script removed: redirect -->'
        return script

    scrubbed_html = re.sub(
        r'<script\b[^>]*>.*?</script>',
        replace_script,
        html,
        flags=re.DOTALL | re.IGNORECASE
    )
    return scrubbed_html, removed_count

def main():
    parser = argparse.ArgumentParser(description="Generate page.safe.html by stripping redirect scripts from page.html")
    parser.add_argument("--snapshots-root", required=True, help="Root directory containing the snapshots")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing page.safe.html files")
    args = parser.parse_args()

    snapshots_root = Path(args.snapshots_root)
    if not snapshots_root.exists() or not snapshots_root.is_dir():
        print(f"Error: {snapshots_root} does not exist or is not a directory.")
        return

    report = {
        "snapshots_root": str(snapshots_root).replace("\\", "/"),
        "total_page_html_found": 0,
        "page_safe_created": 0,
        "skipped_existing": 0,
        "files_with_redirect_scripts": 0,
        "total_redirect_scripts_removed": 0,
        "errors": [],
        "files": []
    }

    # Recursively find all page.html files
    for page_html_path in sorted(snapshots_root.rglob("page.html")):
        report["total_page_html_found"] += 1
        
        page_safe_html_path = page_html_path.with_name("page.safe.html")
        
        if page_safe_html_path.exists() and not args.overwrite:
            report["skipped_existing"] += 1
            report["files"].append({
                "page_html": str(page_html_path).replace("\\", "/"),
                "page_safe_html": str(page_safe_html_path).replace("\\", "/"),
                "redirect_scripts_removed": 0,
                "status": "skipped"
            })
            continue
            
        try:
            html_content = page_html_path.read_text(encoding="utf-8")
            scrubbed_html, removed_count = scrub_redirect_scripts(html_content)
            
            # Determine status before saving
            status = "overwritten" if page_safe_html_path.exists() else "created"
            
            page_safe_html_path.write_text(scrubbed_html, encoding="utf-8")
            
            report["page_safe_created"] += 1
            if removed_count > 0:
                report["files_with_redirect_scripts"] += 1
                report["total_redirect_scripts_removed"] += removed_count
                
            report["files"].append({
                "page_html": str(page_html_path).replace("\\", "/"),
                "page_safe_html": str(page_safe_html_path).replace("\\", "/"),
                "redirect_scripts_removed": removed_count,
                "status": status
            })
            
        except Exception as e:
            error_msg = f"Error processing {page_html_path}: {str(e)}"
            print(error_msg)
            report["errors"].append(error_msg)
            report["files"].append({
                "page_html": str(page_html_path).replace("\\", "/"),
                "page_safe_html": str(page_safe_html_path).replace("\\", "/"),
                "redirect_scripts_removed": 0,
                "status": "error"
            })

    # Save report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "page_safe_html_report.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Done. Processed {report['total_page_html_found']} files.")
    print(f"Created/Overwritten: {report['page_safe_created']}")
    print(f"Skipped: {report['skipped_existing']}")
    print(f"Total redirect scripts removed: {report['total_redirect_scripts_removed']} (across {report['files_with_redirect_scripts']} files)")
    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    main()
