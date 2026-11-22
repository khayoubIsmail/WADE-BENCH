import fs from 'fs';
import path from 'path';

// Helper to write JSONL
function writeJsonl(filePath, data) {
  const content = data.map(item => JSON.stringify(item)).join('\n');
  fs.writeFileSync(filePath, content + '\n', 'utf8');
}

// Helper to read JSONL
function readJsonl(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  return content.split('\n').filter(line => line.trim()).map(line => JSON.parse(line));
}

// Helper to write CSV from JSON objects
function writeCsv(filePath, data) {
  if (data.length === 0) return;
  const headers = Object.keys(data[0]);
  const lines = [headers.join(',')];
  for (const item of data) {
    const row = headers.map(h => {
      let val = item[h];
      if (val === null || val === undefined) val = '';
      if (Array.isArray(val)) val = val.join(';');
      val = String(val).replace(/"/g, '""');
      if (val.includes(',') || val.includes('\n') || val.includes('"')) {
        val = `"${val}"`;
      }
      return val;
    });
    lines.push(row.join(','));
  }
  fs.writeFileSync(filePath, lines.join('\n') + '\n', 'utf8');
}

const baseDir = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';

// Update Tasks
const tasksFile = path.join(baseDir, 'data/tasks/ecommerce_all_tasks_20.jsonl');
let tasks = readJsonl(tasksFile);

// New Task Definitions
const newTasks = [
  {
    task_id: "WBV1_ECOM_02_NIKE_US_LISTING", domain: "E-commerce / Products", website_id: "nike_us", website_name: "Nike US", schema_id: "product_listing_v1",
    start_url: "https://www.nike.com/w/mens-shoes-nik1zy7ok", sample_detail_url: "https://www.nike.com/t/air-jordan-4-toro-mens-shoes-Aey77D4l/FQ8138-600",
    instruction: "Extract product listings from the Nike men's shoes category page. For each visible product, return product name, product type/subtitle, price, sale price if visible, number of colors available, product URL, and image URL.",
    requires_pagination: true, requires_detail_page: false, max_pages: 3, target_records: 30, difficulty: "medium", verified_status: "final_verified_replacement_for_hm", verification_basis: "manual_agent_mode_conversation_verification", snapshot_required: true,
    expected_fields: ["product_name", "product_subtitle", "price", "sale_price", "colors_available", "image_url", "product_url"]
  },
  {
    task_id: "WBV1_ECOM_02_NIKE_US_DETAIL", domain: "E-commerce / Products", website_id: "nike_us", website_name: "Nike US", schema_id: "product_detail_v1",
    start_url: "https://www.nike.com/w/mens-shoes-nik1zy7ok", sample_detail_url: "https://www.nike.com/t/air-jordan-4-toro-mens-shoes-Aey77D4l/FQ8138-600",
    instruction: "Open product detail pages from the Nike men's shoes listing page and extract product name, price, description, available sizes, available colors/variants, image URLs, and product URL.",
    requires_pagination: false, requires_detail_page: true, max_pages: 1, target_records: 10, difficulty: "medium", verified_status: "final_verified_replacement_for_hm", verification_basis: "manual_agent_mode_conversation_verification", snapshot_required: true,
    expected_fields: ["product_name", "price", "description", "available_sizes", "available_colors", "image_urls", "product_url"]
  },
  {
    task_id: "WBV1_ECOM_03_CASPER_US_LISTING", domain: "E-commerce / Products", website_id: "casper_us", website_name: "Casper US", schema_id: "product_listing_v1",
    start_url: "https://casper.com/collections/mattresses", sample_detail_url: "https://casper.com/products/casper-one-foam?variant=41670971261009",
    instruction: "Extract mattress product listings from the Casper mattresses category page. For each product, return product name, short description/tagline, price, review count, rating, product URL, and image URL.",
    requires_pagination: false, requires_detail_page: false, max_pages: 1, target_records: 15, difficulty: "easy", verified_status: "final_verified_replacement_for_sephora", verification_basis: "manual_agent_mode_conversation_verification", snapshot_required: true,
    expected_fields: ["product_name", "short_description", "price", "review_count", "rating", "image_url", "product_url"]
  },
  {
    task_id: "WBV1_ECOM_03_CASPER_US_DETAIL", domain: "E-commerce / Products", website_id: "casper_us", website_name: "Casper US", schema_id: "product_detail_v1",
    start_url: "https://casper.com/collections/mattresses", sample_detail_url: "https://casper.com/products/casper-one-foam?variant=41670971261009",
    instruction: "Open product detail pages from the Casper mattresses listing page and extract product name, price, description, available sizes, features/layers, image URLs, and product URL.",
    requires_pagination: false, requires_detail_page: true, max_pages: 1, target_records: 10, difficulty: "medium", verified_status: "final_verified_replacement_for_sephora", verification_basis: "manual_agent_mode_conversation_verification", snapshot_required: true,
    expected_fields: ["product_name", "price", "description", "available_sizes", "features", "image_urls", "product_url"]
  },
  {
    task_id: "WBV1_ECOM_04_WARBYPARKER_US_LISTING", domain: "E-commerce / Products", website_id: "warbyparker_us", website_name: "Warby Parker", schema_id: "product_listing_v1",
    start_url: "https://www.warbyparker.com/eyeglasses", sample_detail_url: "https://www.warbyparker.com/eyeglasses/wilkie/black-matte-eclipse?w=medium",
    instruction: "Extract eyeglasses product listings from the Warby Parker eyeglasses category page. For each product, return product name, price, number of colors/widths available, product URL, and image URL.",
    requires_pagination: true, requires_detail_page: false, max_pages: 3, target_records: 30, difficulty: "medium", verified_status: "final_verified_replacement_for_rei", verification_basis: "manual_agent_mode_conversation_verification", snapshot_required: true,
    expected_fields: ["product_name", "price", "available_options", "image_url", "product_url"]
  },
  {
    task_id: "WBV1_ECOM_04_WARBYPARKER_US_DETAIL", domain: "E-commerce / Products", website_id: "warbyparker_us", website_name: "Warby Parker", schema_id: "product_detail_v1",
    start_url: "https://www.warbyparker.com/eyeglasses", sample_detail_url: "https://www.warbyparker.com/eyeglasses/wilkie/black-matte-eclipse?w=medium",
    instruction: "Open product detail pages from the Warby Parker eyeglasses listing page and extract product name, price, frame width, frame measurements, color, description, image URLs, and product URL.",
    requires_pagination: false, requires_detail_page: true, max_pages: 1, target_records: 10, difficulty: "medium", verified_status: "final_verified_replacement_for_rei", verification_basis: "manual_agent_mode_conversation_verification", snapshot_required: true,
    expected_fields: ["product_name", "price", "frame_width", "frame_measurements", "color", "description", "image_urls", "product_url"]
  }
];

// Replace tasks 02, 03, 04
tasks = tasks.map(t => {
  if (t.website_id === 'hm_us' && t.schema_id === 'product_listing_v1') return newTasks[0];
  if (t.website_id === 'hm_us' && t.schema_id === 'product_detail_v1') return newTasks[1];
  if (t.website_id === 'sephora_de_redirect' && t.schema_id === 'product_listing_v1') return newTasks[2];
  if (t.website_id === 'sephora_de_redirect' && t.schema_id === 'product_detail_v1') return newTasks[3];
  if (t.website_id === 'rei_us' && t.schema_id === 'product_listing_v1') return newTasks[4];
  if (t.website_id === 'rei_us' && t.schema_id === 'product_detail_v1') return newTasks[5];
  return t;
});

// Write updated tasks
writeJsonl(path.join(baseDir, 'data/tasks/ecommerce_all_tasks_20.jsonl'), tasks);
writeCsv(path.join(baseDir, 'data/tasks/ecommerce_all_tasks_20.csv'), tasks);

// Write dev split (first 4 tasks = 2 websites: 01 and 02)
const devTasks = tasks.slice(0, 4);
writeJsonl(path.join(baseDir, 'data/tasks/ecommerce_dev_tasks_4.jsonl'), devTasks);

// Write test split (remaining 16 tasks = 8 websites: 03 to 10)
const testTasks = tasks.slice(4);
writeJsonl(path.join(baseDir, 'data/tasks/ecommerce_test_tasks_16.jsonl'), testTasks);

// Copy updated tasks to domain_files
const destTasks = path.join(baseDir, 'not-official-folder/wade_bench_v1_ecommerce_domain_files/data/tasks');
writeJsonl(path.join(destTasks, 'ecommerce_all_tasks_20.jsonl'), tasks);
writeCsv(path.join(destTasks, 'ecommerce_all_tasks_20.csv'), tasks);
writeJsonl(path.join(destTasks, 'ecommerce_dev_tasks_4.jsonl'), devTasks);
writeJsonl(path.join(destTasks, 'ecommerce_test_tasks_16.jsonl'), testTasks);


// --- Update ecommerce_websites_final_10.csv ---
const websitesFile = path.join(baseDir, 'data/metadata/ecommerce_websites_final_10.csv');
let websitesCsv = fs.readFileSync(websitesFile, 'utf8').split('\n');

const newWebsites = [
  '2,E-commerce / Products,nike_us,Nike US,https://www.nike.com,https://www.nike.com/,https://www.nike.com/w/mens-shoes-nik1zy7ok,https://www.nike.com/t/air-jordan-4-toro-mens-shoes-Aey77D4l/FQ8138-600,Men shoes,final_verified_replacement_for_hm,Replaces H&M US.,strong',
  '3,E-commerce / Products,casper_us,Casper US,https://casper.com,https://casper.com/,https://casper.com/collections/mattresses,https://casper.com/products/casper-one-foam?variant=41670971261009,Mattresses,final_verified_replacement_for_sephora,Replaces Sephora DE.,strong',
  '4,E-commerce / Products,warbyparker_us,Warby Parker,https://www.warbyparker.com,https://www.warbyparker.com/,https://www.warbyparker.com/eyeglasses,https://www.warbyparker.com/eyeglasses/wilkie/black-matte-eclipse?w=medium,Eyeglasses,final_verified_replacement_for_rei,Replaces REI US.,strong'
];

let outWebsites = websitesCsv.map(line => {
  if (line.startsWith('2,E-commerce / Products,hm_us')) return newWebsites[0];
  if (line.startsWith('3,E-commerce / Products,sephora_de')) return newWebsites[1];
  if (line.startsWith('4,E-commerce / Products,rei_us')) return newWebsites[2];
  return line;
});

const websitesContent = outWebsites.join('\n');
fs.writeFileSync(websitesFile, websitesContent, 'utf8');

// Copy to domain files
const destWebsites = path.join(baseDir, 'not-official-folder/wade_bench_v1_ecommerce_domain_files/data/metadata/ecommerce_websites_final_10.csv');
fs.writeFileSync(destWebsites, websitesContent, 'utf8');

console.log('Successfully updated WADE-Bench definitions to include the 3 replacement backup sites (Nike, Casper, Warby Parker) instead of H&M, Sephora, and REI.');
