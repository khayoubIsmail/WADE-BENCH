import fs from 'fs';
import path from 'path';

const baseDir = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';

const dirsToDelete = [
  'hm_us_listing_women_jeans', 'hm_us_detail_sample',
  'sephora_de_redirect_listing_skincare_face_care', 'sephora_de_redirect_detail_sample',
  'rei_us_listing_hiking_footwear', 'rei_us_detail_sample'
];

const newMetadata = [
  {
    snapshot_id: "nike_us_listing_mens_shoes",
    website_id: "nike_us",
    website_name: "Nike US",
    url: "https://www.nike.com/w/mens-shoes-nik1zy7ok",
    page_type: "listing",
    schema_id: "product_listing_v1",
    snapshot_date: "2026-05-27",
    capture_status: "captured",
    local_expected_files: ["page.html", "screenshot.png", "metadata.json", "text.txt"],
    status: "final_verified_replacement_for_hm"
  },
  {
    snapshot_id: "nike_us_detail_sample",
    website_id: "nike_us",
    website_name: "Nike US",
    url: "https://www.nike.com/t/air-jordan-4-toro-mens-shoes-Aey77D4l/FQ8138-600",
    page_type: "detail",
    schema_id: "product_detail_v1",
    snapshot_date: "2026-05-27",
    capture_status: "captured",
    local_expected_files: ["page.html", "screenshot.png", "metadata.json", "text.txt"],
    status: "final_verified_replacement_for_hm"
  },
  {
    snapshot_id: "casper_us_listing_mattresses",
    website_id: "casper_us",
    website_name: "Casper US",
    url: "https://casper.com/collections/mattresses",
    page_type: "listing",
    schema_id: "product_listing_v1",
    snapshot_date: "2026-05-27",
    capture_status: "captured",
    local_expected_files: ["page.html", "screenshot.png", "metadata.json", "text.txt"],
    status: "final_verified_replacement_for_sephora"
  },
  {
    snapshot_id: "casper_us_detail_sample",
    website_id: "casper_us",
    website_name: "Casper US",
    url: "https://casper.com/products/casper-one-foam?variant=41670971261009",
    page_type: "detail",
    schema_id: "product_detail_v1",
    snapshot_date: "2026-05-27",
    capture_status: "captured",
    local_expected_files: ["page.html", "screenshot.png", "metadata.json", "text.txt"],
    status: "final_verified_replacement_for_sephora"
  },
  {
    snapshot_id: "warbyparker_us_listing_eyeglasses",
    website_id: "warbyparker_us",
    website_name: "Warby Parker",
    url: "https://www.warbyparker.com/eyeglasses",
    page_type: "listing",
    schema_id: "product_listing_v1",
    snapshot_date: "2026-05-27",
    capture_status: "captured",
    local_expected_files: ["page.html", "screenshot.png", "metadata.json", "text.txt"],
    status: "final_verified_replacement_for_rei"
  },
  {
    snapshot_id: "warbyparker_us_detail_sample",
    website_id: "warbyparker_us",
    website_name: "Warby Parker",
    url: "https://www.warbyparker.com/eyeglasses/wilkie/black-matte-eclipse?w=medium",
    page_type: "detail",
    schema_id: "product_detail_v1",
    snapshot_date: "2026-05-27",
    capture_status: "captured",
    local_expected_files: ["page.html", "screenshot.png", "metadata.json", "text.txt"],
    status: "final_verified_replacement_for_rei"
  }
];

const paths = [
  'data/snapshots_manifest/per_site_metadata',
  'not-official-folder/wade_bench_v1_ecommerce_domain_files/data/snapshots_manifest/per_site_metadata'
];

paths.forEach(p => {
  const targetDir = path.join(baseDir, p);
  
  // Delete old folders
  dirsToDelete.forEach(d => {
    const dirPath = path.join(targetDir, d);
    if (fs.existsSync(dirPath)) {
      fs.rmSync(dirPath, { recursive: true, force: true });
    }
  });

  // Create new folders
  newMetadata.forEach(meta => {
    const dirPath = path.join(targetDir, meta.snapshot_id);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    fs.writeFileSync(path.join(dirPath, 'metadata.json'), JSON.stringify(meta, null, 2), 'utf8');
  });
});

console.log('Successfully updated per_site_metadata folders.');
