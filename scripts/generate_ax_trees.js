const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const baseDir = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';
const domains = ['ecommerce', 'jobs', 'academic', 'government', 'realestate'];

async function generateAxTree() {
  const browser = await chromium.launch({ headless: true });
  // We keep JS disabled to prevent external tracking scripts from hanging file:// loads
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    javaScriptEnabled: false,
    bypassCSP: true
  });

  const results = [];
  let total = 0;
  let success = 0;
  let failed = 0;

  for (const domain of domains) {
    const domDir = path.join(baseDir, 'data/raw_snapshots', domain);
    if (!fs.existsSync(domDir)) continue;
    const folders = fs.readdirSync(domDir, { withFileTypes: true })
      .filter(d => d.isDirectory() && d.name !== '.gitkeep')
      .map(d => d.name);

    console.log(`\n=== Processing ${domain} (${folders.length} folders) ===`);

    for (const folder of folders) {
      total++;
      const snapshotDir = path.join(domDir, folder);
      const htmlPath = path.join(snapshotDir, 'page.html');
      const axTreePath = path.join(snapshotDir, 'ax_tree.json');

      if (!fs.existsSync(htmlPath)) {
        console.log(`  FAIL ${folder} (page.html missing)`);
        failed++;
        continue;
      }

      try {
        const page = await context.newPage();
        
        // Abort all network requests to avoid hanging on external resources
        await page.route('**/*', route => {
          if (route.request().url().startsWith('file://')) {
            route.continue();
          } else {
            route.abort();
          }
        });

        const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');
        
        // Short timeout, domcontentloaded is enough for snapshot-derived
        await page.goto(fileUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });

        // Use CDP to get full AX Tree since Playwright 1.60 removed page.accessibility
        const client = await context.newCDPSession(page);
        const axTree = await client.send('Accessibility.getFullAXTree');

        if (axTree && axTree.nodes) {
          fs.writeFileSync(axTreePath, JSON.stringify(axTree, null, 2), 'utf8');
          const size = fs.statSync(axTreePath).size;
          console.log(`  OK   ${folder} (${(size / 1024).toFixed(1)} KB)`);
          success++;
          results.push({ domain, folder, status: 'success' });
        } else {
          console.log(`  FAIL ${folder} (getFullAXTree returned empty)`);
          failed++;
        }

        await page.close();
      } catch (err) {
        console.log(`  FAIL ${folder} (${err.message.substring(0, 80).replace(/\n/g, ' ')})`);
        failed++;
      }
    }
  }

  await context.close();
  await browser.close();

  console.log(`\n========================================`);
  console.log(`SUMMARY`);
  console.log(`  Total: ${total} | Success: ${success} | Failed: ${failed}`);
  console.log(`========================================`);
}

generateAxTree().catch(console.error);
