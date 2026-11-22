const fs = require('fs');
const path = require('path');

const BASE = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';
const schemasDir = path.join(BASE, 'data/schemas');
const goldDir = path.join(BASE, 'data/gold/by_task');

const schemas = {};
fs.readdirSync(schemasDir).forEach(f => {
  if (f.endsWith('.json')) {
    const s = JSON.parse(fs.readFileSync(path.join(schemasDir, f), 'utf8'));
    schemas[s.schema_id] = s;
  }
});

let missingCount = 0;
let emptyTasks = 0;
let totalTasks = 0;

['ecommerce', 'jobs', 'academic', 'government', 'realestate'].forEach(domain => {
  const dir = path.join(goldDir, domain);
  if (!fs.existsSync(dir)) return;
  fs.readdirSync(dir).forEach(f => {
    if (f.endsWith('.json')) {
      totalTasks++;
      const goldPath = path.join(dir, f);
      const gold = JSON.parse(fs.readFileSync(goldPath, 'utf8'));
      const schema = schemas[gold.schema_id];
      if (!schema) return;
      
      if (gold.records.length === 0) {
        console.log(`[EMPTY] ${f}`);
        emptyTasks++;
      }

      gold.records.forEach((record, idx) => {
        schema.required_fields.forEach(field => {
          if (record[field] === null || record[field] === undefined) {
             console.log(`[MISSING] ${f} - Record ${idx} - Field ${field}`);
             missingCount++;
          }
        });
      });
    }
  });
});

console.log(`\nVerification Complete.`);
console.log(`Total Tasks Checked: ${totalTasks}`);
console.log(`Empty Tasks: ${emptyTasks}`);
console.log(`Missing Required Fields: ${missingCount}`);
