import os
import csv
from pathlib import Path

def main():
    root_dir = Path("data/raw_snapshots")
    output_csv = "snapshots_to_verify.csv"
    
    if not root_dir.exists():
        print(f"Error: {root_dir} does not exist.")
        return

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'snapshot_dir', 'mhtml_path', 'screenshot_path'])
        
        count = 0
        for domain_dir in root_dir.iterdir():
            if domain_dir.is_dir():
                for snapshot_dir in domain_dir.iterdir():
                    if snapshot_dir.is_dir():
                        mhtml_path = snapshot_dir / "page.mhtml"
                        screenshot_path = snapshot_dir / "screenshot.png"
                        
                        # Convert to absolute file URIs for Playwright
                        mhtml_uri = mhtml_path.absolute().as_uri()
                        screenshot_uri = screenshot_path.absolute().as_uri()
                        
                        writer.writerow([domain_dir.name, snapshot_dir.name, mhtml_uri, screenshot_uri])
                        count += 1
                
    print(f"Generated {output_csv} with {count} snapshots.")

if __name__ == "__main__":
    main()
