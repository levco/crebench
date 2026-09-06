import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const dist = path.resolve('dist');
let checked = 0;
for(const name of fs.readdirSync(dist).filter(f=>f.endsWith('.html'))) {
  const html = fs.readFileSync(path.join(dist,name),'utf8');
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(ids).size,ids.length,`${name} duplicate IDs`);
  for(const [,url] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if(url.startsWith('http')) continue;
    if(url.startsWith('#')) {assert(ids.includes(url.slice(1)),`Missing anchor ${url}`);continue;}
    const parsed = new URL(url,'https://local.test');
    const target = path.join(dist,parsed.pathname==='/'?'index.html':parsed.pathname);
    assert(fs.existsSync(target),`${name}: missing ${url}`);
    if(parsed.hash) {
      const targetHtml=fs.readFileSync(target,'utf8');
      const targetIds=[...targetHtml.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
      assert(targetIds.includes(decodeURIComponent(parsed.hash.slice(1))),`${name}: missing fragment ${url}`);
    }
    checked++;
  }
  for(const [,id] of html.matchAll(/aria-(?:controls|labelledby)="([^"]+)"/g)) assert(ids.includes(id),`Missing ARIA target ${id}`);
}
assert.deepEqual(JSON.parse(fs.readFileSync(path.join(dist,'release.json'))).model_results,[]);
for(const forbidden of ['private','heldout','.git','.env','outputs']) assert(!fs.existsSync(path.join(dist,forbidden)));
console.log(`Verified ${checked} local links/assets, ARIA targets, no fabricated results, and public-only output.`);
