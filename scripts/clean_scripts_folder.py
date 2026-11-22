import os
import shutil
import argparse
import datetime
import json
import re
import ast
from pathlib import Path

OFFICIAL_SCRIPTS = {
    'clean_scripts_folder.py',
    'create_safe_html.py',
    'audit_snapshots.js',
    'snapshot.py',
    'generate_ax_trees.js',
    'verify_gold.js',
    'verify_gold_full.js',
    'generate_report.js',
    'generate_screenshot_gallery.js',
    'build_splits.py',
    'run_baselines.py',
    'evaluate_outputs.py',
    'aggregate_results.py',
    'update_metadata.js',
    'update_tasks.js',
    'generate_snapshot_csv.py',
    'restore_from_zip.py'
}

def get_local_dependencies(script_path, scripts_dir):
    """Finds local .py or .js dependencies imported by a script."""
    deps = set()
    if not os.path.exists(script_path):
        return deps
        
    if script_path.endswith('.py'):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        potential_file = module_name + '.py'
                        if os.path.exists(os.path.join(scripts_dir, potential_file)):
                            deps.add(potential_file)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        potential_file = module_name + '.py'
                        if os.path.exists(os.path.join(scripts_dir, potential_file)):
                            deps.add(potential_file)
        except Exception:
            pass
    elif script_path.endswith('.js'):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # simple regex for require('./file') or require('./file.js')
            reqs = re.findall(r"require\(['\"](\.[^'\"]+)['\"]\)", content)
            for r in reqs:
                # normalize path
                if r.startswith('./'):
                    name = r[2:]
                    if not name.endswith('.js'):
                        name += '.js'
                    if os.path.exists(os.path.join(scripts_dir, name)):
                        deps.add(name)
        except Exception:
            pass
    return deps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Please specify --dry-run or --apply")
        return

    scripts_dir = Path('scripts')
    if not scripts_dir.exists():
        print("scripts directory not found.")
        return

    all_files = [f.name for f in scripts_dir.iterdir() if f.is_file() and (f.name.endswith('.py') or f.name.endswith('.js'))]

    # Find dependencies recursively
    kept_official = set(f for f in OFFICIAL_SCRIPTS if f in all_files)

    kept_dependencies = set()
    to_process = list(kept_official)
    processed = set()
    
    while to_process:
        current = to_process.pop()
        if current in processed:
            continue
        processed.add(current)
        current_path = os.path.join(scripts_dir, current)
        deps = get_local_dependencies(current_path, scripts_dir)
        for d in deps:
            if d not in kept_official and d not in kept_dependencies:
                kept_dependencies.add(d)
                to_process.append(d)

    archive_candidates = []
    
    for f in all_files:
        if f in kept_official or f in kept_dependencies:
            continue
        
        # User requested to archive everything else aggressively
        archive_candidates.append(f)

    report = {
        "total_scripts_found": len(all_files),
        "kept_official": sorted(list(kept_official)),
        "kept_dependencies": sorted(list(kept_dependencies)),
        "archived": sorted(archive_candidates) if args.apply else [],
        "archive_candidates": sorted(archive_candidates),
        "errors": []
    }

    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)
    
    if args.dry_run:
        report_path = reports_dir / 'scripts_cleanup_plan.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        print("DRY RUN: No files moved.")
        print(f"Total scripts: {report['total_scripts_found']}")
        print(f"Kept official: {len(report['kept_official'])}")
        print(f"Kept dependencies: {len(report['kept_dependencies'])}")
        print(f"Archive candidates (WILL MOVE): {len(report['archive_candidates'])}")
        print(f"Report written to {report_path}")
        print("\nTo apply these changes, run:")
        print("python scripts/clean_scripts_folder.py --apply")
        
    elif args.apply:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = Path('_archive') / 'scripts_old' / timestamp
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        moved = []
        for ac in archive_candidates:
            src = scripts_dir / ac
            dst = archive_dir / ac
            try:
                shutil.move(str(src), str(dst))
                moved.append(ac)
            except Exception as e:
                report["errors"].append(f"Failed to move {ac}: {e}")
                
        report["archived"] = moved
        report_path = reports_dir / 'scripts_cleanup_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        print(f"Moved {len(moved)} files to {archive_dir}")
        print(f"Report written to {report_path}")

if __name__ == '__main__':
    main()
