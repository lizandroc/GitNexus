// Bundles the renderer into a single self-contained HTML file that runs in
// any browser with no install — for users who don't want the Electron app.
// Usage: node build-standalone.js [outfile]
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, 'renderer');
const css = fs.readFileSync(path.join(dir, 'styles.css'), 'utf8');
const engine = fs.readFileSync(path.join(dir, 'engine.js'), 'utf8');
const app = fs.readFileSync(path.join(dir, 'app.js'), 'utf8');
let html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');

// The Electron CSP blocks inline scripts; the standalone file needs them.
html = html
  .replace(/^\s*<meta http-equiv="Content-Security-Policy".*\n/m, '')
  .replace('<link rel="stylesheet" href="styles.css" />', '<style>\n' + css + '\n</style>')
  .replace('<script src="engine.js"></script>', '<script>\n' + engine + '\n</script>')
  .replace('<script src="app.js"></script>', '<script>\n' + app + '\n</script>')
  // No macOS traffic lights in a browser tab.
  .replace('padding: 0 20px 0 90px; /* room for traffic lights */', 'padding: 0 20px;');

const out = process.argv[2] || path.join(__dirname, 'standalone', 'QuillCheck.html');
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, html);
console.log('wrote', out, (fs.statSync(out).size / 1024).toFixed(1) + ' KB');
