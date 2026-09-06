"""Independent discounted-payment validation and exported workbook checks.

Does not import the case generator or its calculation functions. It calculates
DSCR capacity as the sum of discounted monthly payment budgets (rather than the
generator's closed-form debt constant), then reads actual delivered XLSX caches.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import openpyxl
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'benchmarks/workflow-v1'


def compare(field,actual,expected):
    if isinstance(expected,(int,float)) and not isinstance(expected,bool):
        tol=.0001 if field in {'contract_rate','sizing_rate','annual_debt_constant','sizing_dscr','sizing_debt_yield'} else max(1,abs(expected)*.0001)
        return isinstance(actual,(int,float)) and math.isfinite(actual) and abs(actual-expected)<=tol
    return actual==expected


def recalc(source,dest):
    dest.mkdir(parents=True,exist_ok=True)
    result=subprocess.run(['soffice','-env:UserInstallation='+ (ROOT/'work/workflow-v1/lo-verify').as_uri(),
        '--headless','--convert-to','xlsx','--outdir',str(dest),str(source)],capture_output=True,text=True,timeout=90)
    output=dest/source.name
    if result.returncode or not output.exists(): raise RuntimeError(result.stderr+result.stdout)
    return output


def verify(folder, use_lo=False):
    c=json.loads((folder/'authoring-data.json').read_text()); k=json.loads((folder/'answer-key.json').read_text())['fields']; checks=[]
    def add(name,actual,expected):
        checks.append({'check':name,'actual':actual,'expected':expected,'passed':compare(name,actual,expected)})
    history={label:sum(months) for label,months in c['t12_rows']}
    income=sum(history[label] for label in ['Gross potential base rent','Vacancy loss','Concessions','Bad debt','Other income / recoveries'])
    costs=sum(history[label] for label in ['Real estate taxes','Property insurance','Utilities','Repairs and maintenance','Payroll / contract labor','Administrative / legal','Management fee'])
    add('t12_egi',income,k['t12_egi']);add('t12_operating_expenses',costs,k['t12_operating_expenses'])
    add('t12_noi_before_reserves',income-costs,k['t12_noi_before_reserves'])
    proposed_income=c['uw_gross']-c['uw_gross']*c['uw_loss']+c['uw_other']
    proposed_costs=costs-history['Real estate taxes']+c['uw_tax']-history['Property insurance']+c['uw_insurance']-c['repair_remove']-history['Management fee']+max(history['Management fee'],proposed_income*c['mgmt'])
    net=proposed_income-proposed_costs
    reserves=c['reserve_rate']*(len(c['rows']) if c['reserve_basis']=='unit' else sum(row['area'] for row in c['rows']))
    add('uw_noi_before_reserves',net,k['uw_noi_before_reserves']);add('uw_ncf',net-reserves,k['uw_ncf'])
    annual_rate=max(c['fixed'] if c['fixed']>0 else max(c['index_floor'],c['index'])+c['spread'],c['sizing_floor'])
    discounted_budget=sum(((net-reserves)/c['dscr']/12)/((1+annual_rate/12)**month) for month in range(1,c['amort']*12+1))
    add('dscr_limit',discounted_budget,k['dscr_limit'])
    ltv=(net/c['cap'])*c['ltv'];dy=(net if c['dy_basis']=='NOI' else net-reserves)/c['dy']
    add('maximum_loan',min(discounted_budget,ltv,dy),k['maximum_loan'])
    add('source_count',len(list((folder/'sources').glob('*.pdf')))+len(list((folder/'sources').glob('*.xlsx'))),5)
    for source in (folder/'sources').glob('*.pdf'):
        pdf=PdfReader(source)
        expected_pages=2 if source.name in {'T12-Statement.pdf','Property-and-Plan.pdf'} or (source.name=='Lease-File.pdf' and c['amended_rent']) else 1
        add('page_count_'+source.name,len(pdf.pages),expected_pages)
        if source.name=='Lease-File.pdf' and c['scanned']:
            add('image_only_lease_text_length',sum(len(page.extract_text() or '') for page in pdf.pages),0)
        else:
            checks.append({'check':'extractable_text_'+source.name,'passed':all(len(page.extract_text() or '')>100 for page in pdf.pages)})
    workbook=folder/'reference-underwriting.xlsx'
    if use_lo:workbook=recalc(workbook,ROOT/'work/workflow-v1/verified'/c['id'])
    w=openpyxl.load_workbook(workbook,data_only=True);formulas=openpyxl.load_workbook(workbook,data_only=False)
    spec=json.loads((folder/'reference-workbook-spec.json').read_text())
    for field,loc in spec['output_map'].items():
        sheet,cell=loc.split('!');add(field,w[sheet][cell].value,k[field])
        checks.append({'check':'live_formula_'+field,'passed':formulas[sheet][cell].data_type=='f'})
    errors=[f'{sheet.title}!{cell.coordinate}: {cell.value}' for sheet in w for row in sheet for cell in row if cell.data_type=='e']
    checks.append({'check':'no_excel_errors','passed':not errors,'errors':errors})
    return {'case_id':c['id'],'engine':'LibreOfficeDev 26.8.0.0.alpha0' if use_lo else 'artifact-tool XLSX cached values','checks':checks,'passed':all(x['passed'] for x in checks)}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--libreoffice',action='store_true');a=parser.parse_args()
    results=[verify(folder,a.libreoffice) for group in ['cases','smoke'] for folder in sorted((BASE/group).iterdir()) if folder.is_dir()]
    report={'method':'Independent payment-by-payment discounted cash flow plus XLSX recalculation','independent_human_review':False,'results':results}
    (BASE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'cases':len(results),'checks':sum(len(r['checks']) for r in results),'all_passed':all(r['passed'] for r in results),'failures':[{'case':r['case_id'],'check':c} for r in results for c in r['checks'] if not c['passed']]},indent=2))
    if not all(r['passed'] for r in results):raise SystemExit(1)
