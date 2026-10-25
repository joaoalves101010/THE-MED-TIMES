// Dependency-free deployment gate: validate the COMMITTED artifact, never regenerate it.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { root, dist, hashes } from './dist-utils.mjs';
const read = name => fs.readFileSync(path.join(dist, name), 'utf8');
const cfg = JSON.parse(fs.readFileSync(path.join(root, 'edition.json')));
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'public-dist-sha256.json')));
assert.equal(manifest.project, 'the-med-times');
assert.equal(manifest.editionId, cfg.editionId);
assert.equal(manifest.localDate, cfg.localDate);
const actual = hashes();
assert.deepEqual(actual, manifest.files, 'Committed dist differs from the approved public artifact hashes');
const current = read('index.html');
const rows = JSON.parse(current.match(/id="edition-data" type="application\/json">(.*?)<\/script>/s)[1]);
const sourceRows = JSON.parse(fs.readFileSync(path.join(root, 'src/editions', cfg.editionId, 'articles.json')));
const expected = sourceRows.map(a => Object.fromEntries(['id','url','section','category','title','deck','paragraphs'].map(k => [k, a[k]])));
assert.deepEqual(rows, expected, 'Published article text differs from editorial source');
assert.equal(rows.length, 96);
assert.equal(new Set(rows.map(a => a.id)).size, 96);
const sections = ['pesquisa','clinica','saude-publica','formacao','inovacao','instituicoes'];
for (const section of sections) {
  const articles = rows.filter(a => a.section === section);
  assert.equal(articles.length, 16);
  const ids = [...read(`editorias/${section}/index.html`).matchAll(/data-article-id="([^"]+)"/g)].map(m => m[1]);
  assert.deepEqual(ids.sort(), articles.map(a => a.id).sort());
}
assert.equal([...current.matchAll(/data-article-id="([^"]+)"/g)].length, 9);
for (const history of cfg.history) assert.ok(actual[`edicoes/${history.editionId}/index.html`]);
assert.ok(read('styles-reading.css').includes('--paper:#FFFFFF'));
for (const name of ['styles.css', 'app.js']) {
  const shipped = name.replace('.', '-reading.');
  assert.equal(read(shipped), fs.readFileSync(path.join(root, 'src', name), 'utf8'));
}
let refs = 0, pages = 0;
const escapeHtml = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#x27;');
for (const article of sourceRows) {
  const body = read(article.url + 'index.html');
  for (const paragraph of article.paragraphs) assert.ok(body.includes(escapeHtml(paragraph)), `Changed body: ${article.id}`);
}
for (const name of Object.keys(actual)) {
  assert.ok(!/(?:^|\/)(?:RELEASE_MANIFEST\.json|release-evidence\.json|release-provenance|maintenance-provenance)(?:\/|$)/.test(name));
  if (!/\.(?:html|css|js|json|svg|txt)$/.test(name)) continue;
  const text = read(name);
  assert.ok(!/(?:appgprj_|appgversion_|appgdeploy_|sediment:\/\/|file:\/\/|\/workspace\/|\/home\/agent\/|https?:\/\/[^\s"'<>]*(?:chatgpt\.com\/|oaiusercontent\.com|blob\.core\.windows\.net))/.test(text), `Private metadata: ${name}`);
  let urls = [];
  if (name.endsWith('.html')) {
    pages++;
    assert.ok(text.includes('<html lang="pt-BR">'));
    urls = [...text.matchAll(/\b(?:href|src|srcset|action)="([^"]+)"/g)].map(m => m[1]);
  } else if (name.endsWith('.css')) urls = [...text.matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)].map(m => m[1]);
  for (const href of urls) {
    const url = new URL(href, `https://static.invalid/${name}`);
    if (url.origin !== 'https://static.invalid') continue;
    if (!url.pathname) continue;
    let target = path.join(dist, decodeURIComponent(url.pathname));
    assert.ok(target === dist || target.startsWith(dist + path.sep));
    if (fs.existsSync(target) && fs.statSync(target).isDirectory()) target = path.join(target, 'index.html');
    assert.ok(fs.existsSync(target), `Missing local reference in ${name}: ${href}`);
    refs++;
  }
}
console.log(`Public dist verified: ${Object.keys(actual).length} files, ${pages} HTML pages, ${refs} local references; 96 articles / 6 × 16 / 9 cover teasers.`);
