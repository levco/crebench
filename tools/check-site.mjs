import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
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
const release=JSON.parse(fs.readFileSync(path.join(dist,'release.json')));
if(release.workflow){
  const results=JSON.parse(fs.readFileSync(path.join(dist,'workflow-results.json')));
  assert.equal(results.runs.length,30);
  assert.equal(new Set(results.runs.map(r=>[r.track,r.system,r.case_id].join('/'))).size,30);
  assert.equal(release.workflow.recorded_runs,results.runs.filter(r=>r.status==='completed').length);
  for(const r of results.runs){
    assert.equal(r.field_checks.length,39);
    assert(!r.field_checks.some(c=>c.field==='verified_renewal_insurance'));
    for(const group of ['extraction','financial']){
      const checks=r.field_checks.filter(c=>c.group===group);
      assert.equal(r.field_scores[group].passed,checks.filter(c=>c.passed).length);
      assert.equal(r.field_scores[group].total,group==='extraction'?17:22);
    }
    if(r.evidence_score){assert.equal(r.review.evidence.length,17);assert.equal(r.evidence_score.passed,r.review.evidence.filter(c=>c.passed).length);}
    if(r.status==='infrastructure_error')assert.equal(r.quality_status,'excluded_infrastructure');
    for(const f of r.artifacts){
      assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(dist,f.path))).digest('hex'),f.sha256);
      if(f.kind==='xlsx'&&r.workbook_audit)assert.equal(r.workbook_audit.source_workbook_sha256,f.sha256);
    }
  }
  const serialized=JSON.stringify(results);
  for(const privateMarker of ['X-Amz-Signature','kylegraves808@gmail.com','Authorization: Bearer','sk-ant-','vck_'])assert(!serialized.includes(privateMarker),`Private marker ${privateMarker}`);
  const plan=JSON.parse(fs.readFileSync('experiments/2026-09-06-workflow-v1/plan.json'));
  for(const [file,hash] of Object.entries(plan.sha256))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),hash,`Frozen input drift: ${file}`);
}else assert.deepEqual(release.model_results,[]);
for(const forbidden of ['private','heldout','.git','.env','outputs']) assert(!fs.existsSync(path.join(dist,forbidden)));
console.log(`Verified ${checked} local links/assets, ARIA targets, published score arithmetic, original artifact hashes, frozen protocol, and public-only output.`);
