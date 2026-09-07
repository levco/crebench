"""Transcribe visible response-table values with exact table/row attribution."""
import json,re,sys
from pathlib import Path
case=sys.argv[1];run=Path('experiments/2026-09-06-workflow-v1/lev_native/lev--native')/case
brief=(Path('benchmarks/workflow-v1/cases')/case/'brief.md').read_text();ids=set(re.findall(r'^- `([^`]+)`:',brief,re.M));tables=json.loads((run/'response-tables.json').read_text());fields=[]
for ti,table in enumerate(tables):
 if not table:continue
 for ri,row in enumerate(table[1:],1):
  label=row[0].strip('`') if row else ''
  match=re.match(r'^([a-z_]+)(?:\s+\(|$)',label);field=match.group(1) if match else label
  if len(row)<2 or field not in ids:continue
  vi=2 if len(table[0])>2 and table[0][2].lower() in {'max loan','max principal'} else 1
  evidence=row[2:] if vi==1 else []
  fields.append({'id':field,'value':row[vi],'evidence':evidence,'calculation':row[1] if vi==2 else '',
    'transcription_excerpt':row,'transcription_location':{'table':ti,'row':ri,'value_column':vi}})
# Missing IDs remain missing until a reviewer explicitly maps other visible text.
(run/'analysis.transcribed.json').write_text(json.dumps({'fields':fields,'qualifications':[],'blocked':[],
 'transcription_method':'Exact displayed table values; table/row/column and complete row retained. No financial corrections.'},indent=2)+'\n')
print(json.dumps({'case':case,'transcribed':len(fields),'missing_ids':sorted(ids-set(f['id'] for f in fields))}))
