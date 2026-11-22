import zipfile
import os

zip_path = r'D:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\wade-bench-snapshots.zip'
dest_dir = r'D:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'

daft_1 = 'SNAP_REAL_DAFT.IE_001_LISTING/'
daft_2 = 'SNAP_REAL_DAFT.IE_002_DETAIL/'

with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        # Match paths inside the zip that belong to the two Daft snapshots
        if 'realestate/' + daft_1 in name or 'realestate/' + daft_2 in name:
            # Get the relative path after 'realestate/'
            rel_path = name.split('realestate/')[-1]
            if rel_path:
                target_path = os.path.join(dest_dir, rel_path)
                
                if name.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with z.open(name) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
                        
print("Restored original Daft.ie snapshots from ZIP!")
