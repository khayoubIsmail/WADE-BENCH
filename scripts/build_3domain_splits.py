import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

def load_json(path: Path) -> Dict[str, Any]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    records = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except Exception:
        pass
    return records

def find_task_file(domain: str) -> Path:
    tasks_dir = Path("data/tasks")
    for p in tasks_dir.glob(f"{domain}_all_tasks*.jsonl"):
        return p
    return None

def find_gold_file(domain: str, task_id: str) -> Path:
    possible_paths = [
        Path(f"data/gold/by_task/{domain}/{task_id}.json"),
        Path(f"data/gold/verified/{domain}/{task_id}.json"),
        Path(f"data/gold/{domain}/{task_id}.json")
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return None

def is_gold_valid(gold_data: Dict[str, Any]) -> bool:
    if not gold_data:
        return False
    # check verified flags
    if gold_data.get("verified") is True:
        return True
    
    ann_meta = gold_data.get("annotation_metadata", {})
    if isinstance(ann_meta, dict):
        if ann_meta.get("verified") is True:
            return True
        if ann_meta.get("verification_status") in ("human_verified", "verified", "final_verified"):
            return True
            
    ann = gold_data.get("annotation", {})
    if isinstance(ann, dict):
        if ann.get("verified") is True:
            return True

    # fallback
    records = gold_data.get("records", [])
    if isinstance(records, list) and len(records) > 0:
        return True
        
    return False

def get_website_id(data: Dict[str, Any], snapshot_name: str) -> str:
    val = "unknown"
    # Prefer explicit
    for key in ["website_id", "site_id", "source_site"]:
        if key in data and data[key]:
            val = data[key]
            break
    
    # Infer from snapshot name
    if val == "unknown" and snapshot_name:
        val = snapshot_name

    if val != "unknown":
        suffixes = [
            "_001_listing", "_002_detail", "_detail_sample", 
            "_listing_men_shoes", "_listing_women_dresses", "_listing_mattresses",
            "_listing_hiking_backpacks", "_listing_home_and_living", "_listing_skincare",
            "_listing_sofas_and_armchairs", "_listing_mobile_phones", "_listing_mens_shoes",
            "_listing_eyeglasses", "_001", "_002", "_listing", "_detail"
        ]
        for s in suffixes:
            if val.endswith(s):
                val = val[:-len(s)]
        # additional aggressive trimming
        val = val.split("_listing")[0]
        val = val.split("_detail")[0]
        
    return val

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-sites-per-domain", type=int, default=2)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    domains = ["ecommerce", "academic", "government"]
    tasks_gathered = []
    
    report = {
        "scope": "WADE-Bench v1 3-domain",
        "domains": domains,
        "excluded_domains": ["jobs", "real_estate", "realestate"],
        "expected_total_tasks": 60,
        "actual_total_tasks": 0,
        "dev_tasks": 0,
        "test_tasks": 0,
        "by_domain": {d: {"websites": 0, "tasks": 0, "dev_websites": args.dev_sites_per_domain, "test_websites": 0} for d in domains},
        "warnings": {
            "missing_screenshots": [],
            "missing_ax_trees": [],
            "missing_page_safe_html": [],
            "missing_gold": [],
            "invalid_gold": []
        },
        "leakage_check": {
            "passed": True,
            "overlapping_websites": []
        }
    }
    
    # Group tasks by domain -> website_id -> list of tasks
    grouped_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]] = {d: {} for d in domains}
    
    for domain in domains:
        task_file = find_task_file(domain)
        if not task_file:
            print(f"Task file not found for {domain}")
            continue
            
        tasks = load_jsonl(task_file)
        
        for task in tasks:
            task_id = task.get("task_id")
            if not task_id:
                continue
                
            gold_file = find_gold_file(domain, task_id)
            if not gold_file:
                report["warnings"]["missing_gold"].append(task_id)
                continue
                
            gold_data = load_json(gold_file)
            if not gold_data or not is_gold_valid(gold_data):
                report["warnings"]["invalid_gold"].append(task_id)
                continue
                
            # Determine snapshot path
            snapshot_path_str = gold_data.get("snapshot_path") or task.get("snapshot_path")
            if not snapshot_path_str:
                snapshot_id = gold_data.get("snapshot_id") or task.get("snapshot_id")
                if snapshot_id:
                    snapshot_path_str = f"data/raw_snapshots/{domain}/{snapshot_id}"
                else:
                    # try to find it via task_id or website_id matching
                    snapshot_path_str = "unknown"
            
            if snapshot_path_str and snapshot_path_str != "unknown":
                if not snapshot_path_str.startswith("data/"):
                    # e.g. raw_snapshots/ecommerce/ikea_us_detail_sample
                    snapshot_path_str = f"data/{snapshot_path_str}"
                    
            snapshot_dir = Path(snapshot_path_str)
            
            # Fallback if snapshot_dir doesn't exist (e.g. sell2wales_002_detail -> sell2wales_detail)
            if not snapshot_dir.exists() and snapshot_path_str != "unknown":
                site_hint = gold_data.get("website_id", "").replace("_001", "").replace("_002", "")
                if not site_hint:
                    site_hint = task.get("website_id", "").replace("_001", "").replace("_002", "")
                tt = "listing" if "LISTING" in task_id else "detail"
                possible_dirs = list(Path(f"data/raw_snapshots/{domain}").glob("*"))
                for pd in possible_dirs:
                    if pd.is_dir() and site_hint in pd.name and tt in pd.name:
                        snapshot_dir = pd
                        break
                        
            snapshot_name = snapshot_dir.name if snapshot_dir.exists() else ""
            
            website_id = get_website_id(gold_data, snapshot_name)
            if website_id == "unknown":
                website_id = get_website_id(task, snapshot_name)
                
            task_type = "listing" if "LISTING" in task_id else "detail"
            
            # Check files
            req_files = ["page.html", "page.safe.html", "text.txt", "metadata.json"]
            missing_critical = False
            for rf in req_files:
                if not (snapshot_dir / rf).exists():
                    if rf == "page.safe.html":
                        report["warnings"]["missing_page_safe_html"].append(task_id)
                    missing_critical = True
                    break
                    
            if missing_critical and args.strict:
                raise Exception(f"Strict mode: Missing critical file in {snapshot_dir} for task {task_id}")
                
            if not (snapshot_dir / "screenshot.png").exists():
                report["warnings"]["missing_screenshots"].append(task_id)
                
            if not (snapshot_dir / "ax_tree.json").exists():
                report["warnings"]["missing_ax_trees"].append(task_id)
                
            split_record = {
                "task_id": task_id,
                "domain": domain,
                "task_type": task_type,
                "website_id": website_id,
                "schema_id": gold_data.get("schema_id", task.get("schema_id", "unknown")),
                "task_path": str(task_file).replace("\\", "/"),
                "snapshot_path": str(snapshot_dir).replace("\\", "/"),
                "gold_path": str(gold_file).replace("\\", "/"),
                "source_files": {
                    "page_html": str(snapshot_dir / "page.html").replace("\\", "/"),
                    "page_safe_html": str(snapshot_dir / "page.safe.html").replace("\\", "/"),
                    "screenshot": str(snapshot_dir / "screenshot.png").replace("\\", "/"),
                    "text": str(snapshot_dir / "text.txt").replace("\\", "/"),
                    "ax_tree": str(snapshot_dir / "ax_tree.json").replace("\\", "/"),
                    "metadata": str(snapshot_dir / "metadata.json").replace("\\", "/")
                },
                "num_gold_records": len(gold_data.get("records", []))
            }
            
            if website_id not in grouped_tasks[domain]:
                grouped_tasks[domain][website_id] = []
            grouped_tasks[domain][website_id].append(split_record)
            
    # Now build splits
    all_split = []
    dev_split = []
    test_split = []
    
    dev_websites_global = set()
    test_websites_global = set()
    
    for domain in domains:
        websites = sorted(list(grouped_tasks[domain].keys()))
        dev_sites = websites[:args.dev_sites_per_domain]
        test_sites = websites[args.dev_sites_per_domain:]
        
        report["by_domain"][domain]["websites"] = len(websites)
        report["by_domain"][domain]["test_websites"] = len(test_sites)
        
        for site in websites:
            site_tasks = grouped_tasks[domain][site]
            report["by_domain"][domain]["tasks"] += len(site_tasks)
            report["actual_total_tasks"] += len(site_tasks)
            
            for t in site_tasks:
                all_split.append(t)
                if site in dev_sites:
                    dev_split.append(t)
                    dev_websites_global.add(f"{domain}_{site}")
                else:
                    test_split.append(t)
                    test_websites_global.add(f"{domain}_{site}")

    report["dev_tasks"] = len(dev_split)
    report["test_tasks"] = len(test_split)

    # Leakage check
    overlap = dev_websites_global.intersection(test_websites_global)
    if overlap:
        report["leakage_check"]["passed"] = False
        report["leakage_check"]["overlapping_websites"] = list(overlap)
        if args.strict:
            raise Exception(f"Strict mode: Website leakage detected: {overlap}")
            
    if args.strict and report["actual_total_tasks"] != report["expected_total_tasks"]:
        raise Exception(f"Strict mode: Expected {report['expected_total_tasks']} tasks but got {report['actual_total_tasks']}")

    # Write files
    Path("data/splits").mkdir(exist_ok=True, parents=True)
    
    with open("data/splits/wadebench_v1_3domain_all.jsonl", "w", encoding="utf-8") as f:
        for r in all_split:
            f.write(json.dumps(r) + "\n")
            
    with open("data/splits/wadebench_v1_3domain_dev.jsonl", "w", encoding="utf-8") as f:
        for r in dev_split:
            f.write(json.dumps(r) + "\n")
            
    with open("data/splits/wadebench_v1_3domain_test.jsonl", "w", encoding="utf-8") as f:
        for r in test_split:
            f.write(json.dumps(r) + "\n")

    Path("reports").mkdir(exist_ok=True)
    with open("reports/wadebench_v1_3domain_split_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Generated WADE-Bench v1 splits:")
    print(f"Total tasks: {report['actual_total_tasks']}")
    print(f"Dev tasks: {report['dev_tasks']}")
    print(f"Test tasks: {report['test_tasks']}")
    print(f"Leakage passed: {report['leakage_check']['passed']}")
    print("Files written to data/splits/ and reports/")

if __name__ == "__main__":
    main()
