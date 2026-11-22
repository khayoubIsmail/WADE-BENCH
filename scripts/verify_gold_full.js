const fs = require('fs');
const path = require('path');

const BASE = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';
const goldDir = path.join(BASE, 'data/gold/by_task');
const schemasDir = path.join(BASE, 'data/schemas');

const schemas = {};
fs.readdirSync(schemasDir).forEach(f => {
  if (f.endsWith('.json')) {
    const s = JSON.parse(fs.readFileSync(path.join(schemasDir, f), 'utf8'));
    schemas[s.schema_id] = s;
  }
});

let totalTasks = 0, totalRecords = 0, emptyTasks = 0;
let missingFields = 0, duplicateRecords = 0, suspiciousNames = 0;
const suspiciousWords = ['sale', 'sale price', 'regular price', 'cart', 'add to bag', 
  'skip', 'menu', 'home', 'search', 'sign in', 'log in', 'view all', 'read more',
  'results', 'image zoomed', 'more options', 'just in', 'best seller', 'new color',
  'free shipping', 'selling fast', 'star seller', 'ad by etsy', 'ad from etsy',
  'from:', 'comp. value:', 'feel:', 'support:', 'pressure relief:',
  'new products', 'cart (0)', 'waterproof', 'out of 5'];
const domainStats = {};

['ecommerce', 'jobs', 'academic', 'government', 'realestate'].forEach(domain => {
  domainStats[domain] = { tasks: 0, records: 0, missing: 0, duplicates: 0, suspicious: 0 };
  const dir = path.join(goldDir, domain);
  if (!fs.existsSync(dir)) return;

  fs.readdirSync(dir).forEach(f => {
    if (!f.endsWith('.json')) return;
    totalTasks++; domainStats[domain].tasks++;
    const gold = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
    const schema = schemas[gold.schema_id];
    if (!schema) return;

    if (gold.records.length === 0) emptyTasks++;
    totalRecords += gold.records.length;
    domainStats[domain].records += gold.records.length;

    // Check missing required fields
    gold.records.forEach((r, idx) => {
      schema.required_fields.forEach(field => {
        if (r[field] === null || r[field] === undefined) {
          missingFields++;
          domainStats[domain].missing++;
        }
      });
    });

    // Check duplicates
    const names = gold.records.map(r => {
      const nameField = r.product_name || r.job_title || r.event_name || r.tender_title || r.listing_title || '';
      return nameField.toLowerCase();
    });
    const nameSet = new Set();
    names.forEach(n => {
      if (nameSet.has(n)) { duplicateRecords++; domainStats[domain].duplicates++; }
      nameSet.add(n);
    });

    // Check suspicious names
    names.forEach((n, idx) => {
      if (suspiciousWords.some(sw => n === sw || n.startsWith(sw))) {
        suspiciousNames++;
        domainStats[domain].suspicious++;
        console.log(`  [SUS] ${f} rec#${idx}: "${n}"`);
      }
    });
  });
});

console.log('=== WADE-Bench Gold Comprehensive Verification ===');
console.log(`Total tasks: ${totalTasks}`);
console.log(`Total records: ${totalRecords}`);
console.log(`Empty tasks: ${emptyTasks}`);
console.log(`Missing required fields: ${missingFields}`);
console.log(`Duplicate records: ${duplicateRecords}`);
console.log(`Suspicious record names: ${suspiciousNames}`);
console.log('');
console.log('--- Per Domain ---');
for (const [d, s] of Object.entries(domainStats)) {
  console.log(`${d}: ${s.tasks} tasks, ${s.records} records, ${s.missing} missing, ${s.duplicates} dupes, ${s.suspicious} suspicious`);
}
