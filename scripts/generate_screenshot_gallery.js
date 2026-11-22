/**
 * generate_screenshot_gallery.js
 * 
 * Generates an HTML gallery of all 100 snapshots to easily audit for popups or blocked pages.
 */
import fs from 'fs';
import path from 'path';

const baseDir = 'd:/PhD/myArticlesAndPapers/my-papers/5-WISE/wade-bench';
const domains = ['ecommerce', 'jobs', 'academic', 'realestate', 'government'];
const outputFile = path.join(baseDir, 'verification', 'screenshot_gallery.html');

let html = `
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>WADE-Bench Snapshot Gallery</title>
<style>
  body { font-family: system-ui, sans-serif; background: #f4f4f5; color: #111827; padding: 20px; }
  h1 { text-align: center; }
  .domain-section { margin-bottom: 50px; }
  .domain-title { background: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; position: sticky; top: 0; z-index: 100; }
  .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
  .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); display: flex; flex-direction: column; }
  .card h3 { font-size: 14px; margin: 0 0 10px 0; word-break: break-all; }
  .image-container { position: relative; width: 100%; height: 400px; overflow-y: auto; overflow-x: hidden; border: 1px solid #e5e7eb; border-radius: 4px; background: #f9fafb; }
  .image-container img { width: 100%; display: block; }
  .stats { font-size: 12px; color: #6b7280; margin-top: 10px; }
</style>
</head>
<body>
<h1>WADE-Bench: 100 Snapshots Gallery</h1>
<p style="text-align:center">Scroll through the images inside each card to verify that the captures are clean and free of obtrusive popups.</p>
`;

let totalCount = 0;

for (const domain of domains) {
  const snapDir = path.join(baseDir, 'data/raw_snapshots', domain);
  if (!fs.existsSync(snapDir)) continue;

  html += `<div class="domain-section">
    <h2 class="domain-title">${domain.toUpperCase()}</h2>
    <div class="gallery">`;

  const subdirs = fs.readdirSync(snapDir).filter(f => fs.statSync(path.join(snapDir, f)).isDirectory());
  
  for (const sd of subdirs) {
    const ssPath = path.join(snapDir, sd, 'screenshot.png');
    const relativeImgPath = `../data/raw_snapshots/${domain}/${sd}/screenshot.png`;
    
    let statsStr = 'N/A';
    if (fs.existsSync(ssPath)) {
      totalCount++;
      const stats = fs.statSync(ssPath);
      statsStr = `${(stats.size / 1024).toFixed(1)} KB`;
    }

    html += `
      <div class="card">
        <h3>${sd}</h3>
        <div class="image-container">
          <img loading="lazy" src="${relativeImgPath}" alt="${sd}" onerror="this.src=''; this.alt='Screenshot missing'">
        </div>
        <div class="stats">Size: ${statsStr}</div>
      </div>
    `;
  }

  html += `</div></div>`;
}

html += `
<div style="text-align: center; margin-top: 50px; font-weight: bold; font-size: 18px;">
  Total Snapshots Generated: ${totalCount}
</div>
</body>
</html>`;

fs.writeFileSync(outputFile, html, 'utf8');
console.log(`Gallery generated at: ${outputFile} containing ${totalCount} snapshots.`);
