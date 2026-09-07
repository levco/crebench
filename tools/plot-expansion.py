"""Standalone figures use only the complete common case/stage intersection."""
import hashlib,json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/2026-09-07-cre-work-v2';D=json.loads((OUT/'results.json').read_text());FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
models=[c['model'] for c in D['conditions'] if any(r['model']==c['model'] for r in D['matched_rows'])]
labels={'lev/native':'Lev Agent','openai/gpt-5':'GPT-5\nAPI agent','anthropic/claude-opus-5':'Opus 5\nAPI agent','anthropic/claude-opus-4.7':'Opus 4.7\nAPI agent','claude/consumer-opus-5-high':'Claude Chat\nOpus 5 High'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#c9d3d8','text.color':'#162a31','axes.labelcolor':'#162a31','xtick.color':'#344e57','ytick.color':'#344e57','savefig.facecolor':'#f7faf9','figure.facecolor':'#f7faf9','axes.facecolor':'#f7faf9'})
def export(fig,name):
 for ext in ('png','svg','pdf'):fig.savefig(FIG/(name+'.'+ext),dpi=200,bbox_inches='tight')
 plt.close(fig)
if not models:sys.exit('No complete matched comparisons yet')
n=len(D['matched_keys']);case_count=len({k[0] for k in D['matched_keys']});subtitle=f'{case_count} synthetic deal packets · {n} matched stages · 1 trial per stage · diagnostic, not an overall ranking'
fig,axs=plt.subplots(1,3,figsize=(15,5.4));fig.suptitle('Where each system gets the facts right',x=.065,ha='left',fontsize=23,fontweight='bold',y=1.02)
for ax,group,title in zip(axs,['ingestion','financial','judgment'],['Document ingestion','Financial calculations','Risk recognition']):
 values=[];totals=[]
 for m in models:
  rows=[r for r in D['matched_rows'] if r['model']==m];passed=sum(r['scores'][group]['passed'] for r in rows);total=sum(r['scores'][group]['total'] for r in rows);values.append(passed/total*100);totals.append((passed,total))
 y=np.arange(len(models));ax.barh(y,values,color=['#06785f' if m=='lev/native' else '#7a91a0' for m in models],height=.62);ax.set_yticks(y,[labels[m].replace('\n',' ') for m in models] if group=='ingestion' else []);ax.invert_yaxis();ax.set_xlim(0,116);ax.set_xticks([0,50,100],['0%','50%','100%']);ax.set_title(title,loc='left',fontweight='bold',pad=18);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
 for i,(value,(passed,total)) in enumerate(zip(values,totals)):ax.text(value+1.5,i,f'{passed}/{total}',va='center',fontsize=10)
fig.text(.065,-.06,subtitle+'\nThree ambiguous ratio/capacity fields excluded for all systems; original grades and erratum remain public.',fontsize=10,color='#52666f');fig.tight_layout(w_pad=2);export(fig,'matched-facts')
fig,axs=plt.subplots(1,2,figsize=(12.7,5));fig.suptitle('A correct answer must survive a change in assumptions',x=.06,ha='left',fontsize=20,fontweight='bold',y=1.03)
for idx,m in enumerate(models):
 rows=[r for r in D['matched_rows'] if r['model']==m];checks=[p for r in rows for p in ((r.get('audit') or {}).get('workbook',{}).get('perturbations',[]))];passed=sum(p['passed'] for p in checks);total=3*len(rows)
 axs[0].barh(idx,passed,color='#06785f' if m=='lev/native' else '#7a91a0',height=.6);axs[0].text(passed+.08,idx,f'{passed}/{total}',va='center')
 costs=[r['cost_usd'] for r in rows];known=sum(r['cost_usd'] if r['cost_usd'] is not None else (r['known_partial_cost_usd'] or 0) for r in rows)
 if all(v is not None for v in costs):axs[1].barh(idx,known,color='#06785f' if m=='lev/native' else '#7a91a0',height=.6);axs[1].text(known+.05,idx,f'${known:.2f}'+(' estimated' if m=='lev/native' else ''),va='center',fontsize=10)
 elif m.startswith('claude/'):axs[1].text(.05,idx,'Unmeasured',va='center',fontsize=10)
 else:axs[1].barh(idx,known,color='#7a91a0',height=.6,hatch='///',alpha=.65);axs[1].text(known+.05,idx,f'≥ ${known:.2f}',va='center',fontsize=10)
for ax in axs:ax.set_ylim(len(models)-.5,-.5);ax.set_yticks(range(len(models)),[labels[m].replace('\n',' ') for m in models] if ax==axs[0] else []);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
axs[0].set_xlim(0,3*n+1);axs[0].set_title('Workbook sensitivity scenarios passed',loc='left',fontweight='bold');axs[0].set_xlabel('Cap rate +50 bps · rent −5% · sizing rate +100 bps')
axs[1].set_xlim(right=max(axs[1].get_xlim()[1]*1.35,6));axs[1].set_title('Inference cost for these same stages',loc='left',fontweight='bold');axs[1].set_xlabel('API reported / Lev trace estimate / consumer unmeasured')
fig.text(.06,-.08,subtitle+'\nEach scenario checks six workbook outputs. Original files stay unchanged; checks use copies.\nExcludes subscriptions, indexing, search-service fees and human review. Not customer pricing or professional acceptance.',fontsize=10,color='#52666f');fig.tight_layout(w_pad=3);export(fig,'matched-delivery-cost')
fig,axs=plt.subplots(3,1,figsize=(6.4,11.5));fig.suptitle('Where each system gets\nthe facts right',x=.05,ha='left',fontsize=22,fontweight='bold',y=1.01)
for ax,group,title in zip(axs,['ingestion','financial','judgment'],['Document ingestion','Financial calculations','Risk recognition']):
 for i,m in enumerate(models):
  rs=[r for r in D['matched_rows'] if r['model']==m];p=sum(r['scores'][group]['passed'] for r in rs);t=sum(r['scores'][group]['total'] for r in rs)
  ax.barh(i,p/t*100,color='#06785f' if m=='lev/native' else '#7a91a0',height=.6);ax.text(p/t*100+2,i,f'{p}/{t}',va='center',fontsize=10)
 ax.set_yticks(range(len(models)),[labels[m].replace('\n',' ') for m in models]);ax.invert_yaxis();ax.set_xlim(0,125);ax.set_xticks([0,50,100],['0%','50%','100%']);ax.set_title(title,loc='left',fontweight='bold',pad=16);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
fig.text(.05,-.08,f'{case_count} synthetic packets · {n} matched stages · one trial\nDiagnostic comparison; independent CRE review pending.\nThree ambiguous fields excluded for every system.',fontsize=10);fig.tight_layout(h_pad=3);export(fig,'matched-facts-mobile')
fig,axs=plt.subplots(2,1,figsize=(6.4,8.8));fig.suptitle('Workbook behavior\nand inference cost',x=.05,ha='left',fontsize=22,fontweight='bold',y=1.01)
maxcost=0
for i,m in enumerate(models):
 rs=[r for r in D['matched_rows'] if r['model']==m];p=sum(c['passed'] for r in rs for c in (r.get('audit') or {}).get('workbook',{}).get('perturbations',[]))
 axs[0].barh(i,p,color='#06785f' if m=='lev/native' else '#7a91a0',height=.6);axs[0].text(p+.15,i,f'{p}/{3*len(rs)}',va='center',fontsize=10)
 cost=sum(r['cost_usd'] if r['cost_usd'] is not None else r['known_partial_cost_usd'] or 0 for r in rs);maxcost=max(maxcost,cost)
 axs[1].barh(i,cost,color='#06785f' if m=='lev/native' else '#7a91a0',height=.6);axs[1].text(cost+.1,i,('≥ ' if any(r['cost_usd'] is None for r in rs) else '')+f'${cost:.2f}',va='center',fontsize=10)
for ax,title in zip(axs,['Correct sensitivity scenarios','Inference cost for these stages']):
 ax.set_yticks(range(len(models)),[labels[m].replace('\n',' ') for m in models]);ax.invert_yaxis();ax.set_title(title,loc='left',fontweight='bold',pad=16);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
axs[0].set_xlim(0,3*n*1.25);axs[1].set_xlim(0,maxcost*1.4)
fig.text(.05,-.10,f'{case_count} synthetic packets · {n} matched stages · one trial\nLev: trace estimate. APIs: reported inference usage.\nExcludes search, subscriptions and human review.\nEach sensitivity checks six outputs in workbook copies.',fontsize=10);fig.tight_layout(h_pad=3);export(fig,'matched-delivery-cost-mobile')
(FIG/'source-manifest.json').write_text(json.dumps({'source':'../results.json','sha256':hashlib.sha256((OUT/'results.json').read_bytes()).hexdigest(),'models':models,'matched_keys':D['matched_keys'],'selection':'Complete common case/stage/trial intersection across native Lev and all three API conditions.','figures':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FIG.iterdir()) if p.suffix in ['.png','.svg','.pdf']}},indent=2)+'\n')
print(FIG)
