const fs = require('fs');
const path = require('path');

const baseDir = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';

// Domain configs
const domains = [
  { name: 'E-commerce / Products', folder: 'ecommerce', taskFile: 'ecommerce_all_tasks_20.jsonl' },
  { name: 'Jobs / Careers', folder: 'jobs', taskFile: 'jobs_all_tasks_20.jsonl' },
  { name: 'Academic / Events / Conferences', folder: 'academic', taskFile: 'academic_all_tasks_20.jsonl' },
  { name: 'Government / Tenders / Announcements', folder: 'government', taskFile: 'government_all_tasks.jsonl' },
  { name: 'Real Estate / Services / Listings', folder: 'realestate', taskFile: 'realestate_all_tasks_20.jsonl' },
];

const REQUIRED_FILES = ['page.html', 'screenshot.png', 'text.txt', 'metadata.json'];
const REQUIRED_METADATA_FIELDS = ['website_id', 'url', 'page_type', 'schema_id'];
const METADATA_ID_FIELDS = ['task_id', 'snapshot_id']; // at least one
const METADATA_DATE_FIELDS = ['captured_at', 'snapshot_date']; // at least one

function readJsonl(filepath) {
  if (!fs.existsSync(filepath)) return [];
  return fs.readFileSync(filepath, 'utf8')
    .split('\n')
    .filter(line => line.trim())
    .map(line => {
      try { return JSON.parse(line); } catch { return null; }
    })
    .filter(Boolean);
}

function getSnapshotFolders(domainFolder) {
  const dir = path.join(baseDir, 'data/raw_snapshots', domainFolder);
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
}

function checkFiles(domainFolder, snapshotFolder) {
  const dir = path.join(baseDir, 'data/raw_snapshots', domainFolder, snapshotFolder);
  const result = { existing: [], missing: [], hasAxTree: false };
  for (const f of REQUIRED_FILES) {
    if (fs.existsSync(path.join(dir, f))) {
      result.existing.push(f);
    } else {
      result.missing.push(f);
    }
  }
  result.hasAxTree = fs.existsSync(path.join(dir, 'ax_tree.json'));
  return result;
}

function checkMetadata(domainFolder, snapshotFolder) {
  const metaPath = path.join(baseDir, 'data/raw_snapshots', domainFolder, snapshotFolder, 'metadata.json');
  if (!fs.existsSync(metaPath)) return { exists: false, missingFields: ['entire file'], data: null };
  try {
    const data = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    const missingFields = [];
    
    // Check required fields
    for (const f of REQUIRED_METADATA_FIELDS) {
      if (!data[f]) missingFields.push(f);
    }
    // Check at least one ID field
    if (!METADATA_ID_FIELDS.some(f => data[f])) missingFields.push('task_id or snapshot_id');
    // Check at least one date field
    if (!METADATA_DATE_FIELDS.some(f => data[f])) missingFields.push('captured_at or snapshot_date');
    
    return { exists: true, missingFields, data };
  } catch {
    return { exists: false, missingFields: ['invalid JSON'], data: null };
  }
}

function checkHtmlQuality(domainFolder, snapshotFolder) {
  const htmlPath = path.join(baseDir, 'data/raw_snapshots', domainFolder, snapshotFolder, 'page.html');
  if (!fs.existsSync(htmlPath)) return { exists: false, issue: 'page.html missing' };
  
  const stat = fs.statSync(htmlPath);
  const size = stat.size;
  const content = fs.readFileSync(htmlPath, 'utf8');
  
  const result = {
    exists: true,
    size,
    hasExternalCSS: /<link[^>]+rel\s*=\s*["']stylesheet["'][^>]*>/i.test(content),
    hasExternalJS: /<script[^>]+src\s*=\s*["'][^"']+["'][^>]*>/i.test(content),
    hasMeaningfulContent: content.length > 5000,
    looksBlocked: /access.denied|blocked|captcha|just.a.moment|cloudflare|checking.your.browser/i.test(content),
    looksEmpty: content.length < 2000,
    issue: null
  };
  
  if (result.looksEmpty) result.issue = `HTML too small (${size} bytes)`;
  else if (result.looksBlocked) result.issue = 'HTML appears blocked/CAPTCHA';
  else if (!result.hasMeaningfulContent) result.issue = `HTML possibly incomplete (${size} bytes)`;
  
  return result;
}

function matchTaskToSnapshot(task, snapshotFolders) {
  const taskId = task.task_id || '';
  const websiteId = task.website_id || '';
  const pageType = taskId.toLowerCase().includes('listing') ? 'listing' : 'detail';
  
  // Try exact task_id match
  if (snapshotFolders.includes(taskId)) return taskId;
  
  // Try common naming patterns
  for (const folder of snapshotFolders) {
    const fl = folder.toLowerCase();
    const wl = websiteId.toLowerCase();
    
    // Check if folder contains website_id and matching page type
    if (fl.includes(wl) && fl.includes(pageType)) return folder;
    
    // Check if folder starts with website_id base (e.g. ted_001 -> ted_001_listing)
    const websiteBase = wl.replace(/_\d+$/, ''); // e.g. ted_001 -> ted
    if (fl.includes(websiteBase) && fl.includes(pageType)) return folder;
  }
  
  return null;
}

// ========== MAIN AUDIT ==========
const report = {
  globalSummary: {
    domainsFound: 0,
    totalTasks: 0,
    listingTasks: 0,
    detailTasks: 0,
    completeSnapshots: 0,
    incompleteSnapshots: 0,
    missingDomains: [],
    missingRequiredFiles: 0,
    missingAxTreeBefore: 0,
    problematicHtml: 0,
    scopeInconsistencies: [],
  },
  domains: {},
  missingTasks: [],
  snapshotProblems: [],
  metadataProblems: [],
  htmlProblems: [],
  axTreeReport: [],
};

for (const domain of domains) {
  console.log(`\n=== Auditing: ${domain.name} ===`);
  
  // Load tasks
  const taskPath = path.join(baseDir, 'data/tasks', domain.taskFile);
  const tasks = readJsonl(taskPath);
  console.log(`  Tasks loaded: ${tasks.length}`);
  
  // Get snapshot folders
  const snapshotFolders = getSnapshotFolders(domain.folder);
  console.log(`  Snapshot folders found: ${snapshotFolders.length}`);
  
  const domainReport = {
    status: 'unknown',
    tasksFound: tasks.length,
    snapshotFoldersFound: snapshotFolders.length,
    completeSnapshots: 0,
    incompleteSnapshots: 0,
    missingRequiredFiles: [],
    missingAxTree: [],
    problematicHtml: [],
    scopeInconsistency: null,
    notes: [],
    taskMapping: [],
  };
  
  // Check scope
  if (tasks.length !== 20) {
    const msg = `${domain.name}: expected 20 tasks, found ${tasks.length}`;
    domainReport.scopeInconsistency = msg;
    report.globalSummary.scopeInconsistencies.push(msg);
    console.log(`  ⚠ SCOPE: ${msg}`);
  }
  
  // Count listing vs detail
  const listingTasks = tasks.filter(t => (t.task_id || '').toLowerCase().includes('listing'));
  const detailTasks = tasks.filter(t => (t.task_id || '').toLowerCase().includes('detail'));
  report.globalSummary.listingTasks += listingTasks.length;
  report.globalSummary.detailTasks += detailTasks.length;
  report.globalSummary.totalTasks += tasks.length;
  
  // Match tasks to snapshots
  for (const task of tasks) {
    const matched = matchTaskToSnapshot(task, snapshotFolders);
    domainReport.taskMapping.push({ task_id: task.task_id, website_id: task.website_id, matched_snapshot: matched });
    
    if (!matched) {
      report.missingTasks.push({
        domain: domain.name,
        task_id: task.task_id,
        expected_snapshot: `${task.website_id}_${task.task_id.toLowerCase().includes('listing') ? 'listing' : 'detail'}`,
        problem: 'No matching snapshot folder found',
        missing_files: 'all',
      });
      console.log(`  ✗ Task ${task.task_id} -> NO MATCH`);
    } else {
      console.log(`  ✓ Task ${task.task_id} -> ${matched}`);
    }
  }
  
  // Check each snapshot folder
  for (const folder of snapshotFolders) {
    if (folder === '.gitkeep') continue;
    
    const fileCheck = checkFiles(domain.folder, folder);
    const metaCheck = checkMetadata(domain.folder, folder);
    const htmlCheck = checkHtmlQuality(domain.folder, folder);
    
    // Required files check
    if (fileCheck.missing.length === 0) {
      domainReport.completeSnapshots++;
    } else {
      domainReport.incompleteSnapshots++;
      domainReport.missingRequiredFiles.push({ folder, missing: fileCheck.missing });
      report.snapshotProblems.push({
        domain: domain.name,
        snapshot_folder: folder,
        problem: `Missing required files: ${fileCheck.missing.join(', ')}`,
        missing_files: fileCheck.missing.join(', '),
      });
      report.globalSummary.missingRequiredFiles += fileCheck.missing.length;
    }
    
    // ax_tree check
    if (!fileCheck.hasAxTree) {
      domainReport.missingAxTree.push(folder);
      report.globalSummary.missingAxTreeBefore++;
      const url = metaCheck.data?.url || metaCheck.data?.initial_url || metaCheck.data?.final_url || 'UNKNOWN';
      report.axTreeReport.push({
        domain: domain.name,
        snapshot_folder: folder,
        status: 'missing',
        url: url,
        notes: '',
      });
    }
    
    // Metadata check
    if (metaCheck.missingFields.length > 0) {
      report.metadataProblems.push({
        domain: domain.name,
        snapshot_folder: folder,
        missing_metadata_fields: metaCheck.missingFields.join(', '),
      });
    }
    
    // HTML quality check
    if (htmlCheck.issue) {
      domainReport.problematicHtml.push({ folder, issue: htmlCheck.issue });
      report.htmlProblems.push({
        domain: domain.name,
        snapshot_folder: folder,
        issue: htmlCheck.issue,
        size: htmlCheck.size,
        hasExternalCSS: htmlCheck.hasExternalCSS,
        hasExternalJS: htmlCheck.hasExternalJS,
        recommendation: htmlCheck.looksBlocked ? 'Recapture with Playwright networkidle' :
                         htmlCheck.looksEmpty ? 'Recapture - HTML too small' : 'Review manually',
      });
      report.globalSummary.problematicHtml++;
    }
  }
  
  domainReport.status = (domainReport.incompleteSnapshots === 0 && !domainReport.scopeInconsistency) ? '✅ Complete' : '⚠ Issues Found';
  report.domains[domain.name] = domainReport;
  report.globalSummary.completeSnapshots += domainReport.completeSnapshots;
  report.globalSummary.incompleteSnapshots += domainReport.incompleteSnapshots;
}

report.globalSummary.domainsFound = domains.length;

// Write report as JSON for further processing
const reportPath = path.join(baseDir, 'scripts', 'audit_report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`\n\nAudit report saved to: ${reportPath}`);
console.log(`\n===== GLOBAL SUMMARY =====`);
console.log(`Domains: ${report.globalSummary.domainsFound}`);
console.log(`Total tasks: ${report.globalSummary.totalTasks}`);
console.log(`Listing tasks: ${report.globalSummary.listingTasks}`);
console.log(`Detail tasks: ${report.globalSummary.detailTasks}`);
console.log(`Complete snapshot folders: ${report.globalSummary.completeSnapshots}`);
console.log(`Incomplete snapshot folders: ${report.globalSummary.incompleteSnapshots}`);
console.log(`Missing required files (count): ${report.globalSummary.missingRequiredFiles}`);
console.log(`Missing ax_tree.json: ${report.globalSummary.missingAxTreeBefore}`);
console.log(`Problematic HTML: ${report.globalSummary.problematicHtml}`);
console.log(`Scope inconsistencies: ${report.globalSummary.scopeInconsistencies.length > 0 ? report.globalSummary.scopeInconsistencies.join('; ') : 'None'}`);
console.log(`Missing tasks (no snapshot): ${report.missingTasks.length}`);
