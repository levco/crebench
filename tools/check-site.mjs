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
if(release.research){
  const results=JSON.parse(fs.readFileSync(path.join(dist,'research-results.json')));
  assert.equal(results.runs.length,120);
  assert.equal(new Set(results.runs.map(r=>[r.track,r.system,r.case_id].join('/'))).size,120);
  assert.equal(release.research.recorded_runs,results.runs.filter(r=>r.status==='completed').length);
  const plan=JSON.parse(fs.readFileSync('experiments/2026-09-07-research-v1/plan.json'));
  for(const [file,hash] of Object.entries(plan.sha256))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),hash,`Research frozen input drift: ${file}`);
  for(const r of results.runs){
    if(r.grade){
      const g=r.grade;
      assert.equal(g.candidate_accuracy.total,20);
      assert.equal(g.candidate_accuracy.passed,g.decision_checks.filter(c=>c.passed).length);
      assert.equal(g.verified_count,g.selected_checks.filter(c=>c.verified).length);
      assert.equal(g.eligible_count,g.selected_checks.filter(c=>c.eligible).length);
      assert.equal(g.verified_yield,g.target_count?g.verified_count/g.target_count:null);
    }
    if(r.trace_audit){
      assert.equal(r.packet_sha256,plan.sha256[`benchmarks/research-v1/cases/${r.case_id}/packet.md`]);
      assert(Math.abs(r.estimated_inference_cost_usd-r.trace_audit.generation_costs_usd.reduce((a,n)=>a+n,0))<1e-8);
    }
    for(const f of r.artifacts??[]){
      const p=path.join(dist,'research-artifacts',r.track,r.system.replace('/','--'),r.case_id,path.basename(f.path));
      assert.equal(crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),f.sha256);
    }
  }
  for(const s of results.summary){
    const runs=results.runs.filter(r=>r.track===s.track&&r.system===s.system);
    assert.equal(s.planned,24);
    assert.equal(s.verified,runs.reduce((n,r)=>n+(r.grade?.verified_count??0),0));
    assert.equal(s.target,runs.reduce((n,r)=>n+r.expected_target,0));
    assert.equal(s.screening.total,480);
    assert.equal(s.screening.unanswered,runs.filter(r=>!r.grade).length*20);
    assert.equal(s.screening.passed,runs.reduce((n,r)=>n+(r.grade?.candidate_accuracy.passed??0),0));
    assert.equal(s.material_errors,runs.reduce((n,r)=>n+(r.grade?.material_errors.length??0),0));
  }
  for(const marker of ['X-Amz-Signature','kylegraves808@gmail.com','Authorization: Bearer','sk-ant-','vck_'])assert(!JSON.stringify(results).includes(marker),`Private research marker: ${marker}`);
}
if(release.expansion){
  const expansionHtml=fs.readFileSync(path.join(dist,'expansion.html'),'utf8');
  assert(!/<script(?![^>]*\bsrc=)[^>]*>/i.test(expansionHtml),'Expansion scripts must obey the production CSP');
  const bytes=fs.readFileSync(path.join(dist,'expansion-results.json'));
  const data=JSON.parse(bytes);
  assert.equal(release.expansion.recorded_workflow_stages,data.rows.length);
  assert.equal(release.expansion.completed_workflow_stages,data.rows.filter(r=>r.status==='completed').length);
  assert.equal(release.expansion.target_workflow_stages,720);
  assert.equal(release.expansion.matched_stage_pairs,data.matched_keys.length);
  const manifest=JSON.parse(fs.readFileSync(path.join(dist,'expansion-figures/source-manifest.json')));
  assert.equal(manifest.sha256,crypto.createHash('sha256').update(bytes).digest('hex'));
  assert.deepEqual(manifest.matched_keys,data.matched_keys);
  for(const [name,hash] of Object.entries(manifest.figures))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(dist,'expansion-figures',name))).digest('hex'),hash);
}
console.log(`Verified ${checked} local links/assets, ARIA targets, published score arithmetic, original artifact hashes, frozen protocol, and public-only output.`);
