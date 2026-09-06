import fs from 'node:fs/promises';
import path from 'node:path';
import {writeWorkbook} from './workflow-workbook.mjs';

const root=path.resolve('benchmarks/workflow-v1');
const folders=[];
for(const group of (process.argv.includes('--cases-only')?['cases']:['cases','smoke'])) for (const name of await fs.readdir(path.join(root,group))) folders.push(path.join(root,group,name));
const cell=(cell,value,role='body',number_format)=>({cell,value,role,...(number_format?{number_format}:{})});
const formula=(cell,formula,number_format='$#,##0;($#,##0);"-"')=>({cell,formula,number_format});
const dollars='$#,##0;($#,##0);"-"';

for(const folder of folders) {
  const c=JSON.parse(await fs.readFile(path.join(folder,'authoring-data.json'),'utf8'));
  const rr={name:'Rent Roll',cells:[cell('C2',`${c.name} | Rent roll`,'title'),
    {...cell('C3','As of August 31, 2026 | USD monthly | original fictional source','note'),wrap:false}],
    column_widths:{A:3,B:3,C:12,D:25,E:14,F:14,G:18,H:18,I:17},freeze_rows:6};
  const headings=['Unit / suite','Tenant','Area SF','Status','Monthly base rent','Market monthly rent','Lease expiry'];
  headings.forEach((h,i)=>rr.cells.push({...cell(`${String.fromCharCode(67+i)}6`,h,'header'),wrap:true,height:36}));
  c.rows.forEach((r,i)=>[r.unit,r.status==='Vacant'?'Vacant':r.tenant,r.area,r.status,r.rent,r.market_rent,r.expiry].forEach((v,j)=>rr.cells.push(cell(`${String.fromCharCode(67+j)}${7+i}`,v,'body',j===4||j===5?dollars:undefined))));
  rr.cells.push({...cell(`C${9+c.rows.length}`,'Blank contractual rent means no current rent for vacant premises. Market rent is not collected income.','note'),wrap:false});
  rr.cells.push({...cell(`C${11+c.rows.length}`,c.amended_rent?'Manager note: reconcile premises 101 to the attached executed amendment. This schedule has not been updated.':'Review executed lease evidence for premises 101; no option exercise notice is included.','note'),wrap:false});
  await writeWorkbook({sheets:[rr]},path.join(folder,'sources/Rent-Roll.xlsx'),folder.endsWith('adapter-smoke')?'C2:I12':false);

  // Reference workbook: source values on Inputs/Rent Roll/T12, live formulas on Analysis.
  const params=[
    ['Gross potential rent',c.uw_gross],['Revenue loss',c.uw_loss],['Other income',c.uw_other],['Annual taxes',c.uw_tax],
    ['Annual insurance allowance',c.uw_insurance],['Utilities',c.expenses[2]],['Repairs actual',c.expenses[3]],['Nonrecurring repairs',c.repair_remove],
    ['Payroll / contracts',c.expenses[4]],['Administrative / legal',c.expenses[5]],['Management actual',c.expenses[6]],['Management minimum',c.mgmt],
    ['Reserve rate',c.reserve_rate],['Reserve quantity',c.reserve_basis==='unit'?c.areas.length:c.areas.reduce((a,b)=>a+b,0)],
    ['Valuation cap rate',c.cap],['LTV limit',c.ltv],['Minimum DSCR',c.dscr],['Minimum debt yield',c.dy],
    ['Fixed contract rate (zero = floating)',c.fixed],['Current floating index',c.index],['Index floor',c.index_floor],['Spread',c.spread],
    ['Sizing rate floor',c.sizing_floor],['Amortization years',c.amort],['IO months',c.io],['Existing debt payoff',c.payoff],
    ['Loan origination fee',c.fee],['Fixed closing costs',c.closing],['EGI multiplier',1],['Sizing rate increment',0],['Cap rate increment',0],
    ['Debt yield uses NOI before reserves',c.dy_basis==='NOI'?1:0]];
  const inputs={name:'Inputs',cells:[cell('C2','Underwriting assumptions','title'),cell('C3','Source: Property-and-Plan.pdf and Lender-Terms.pdf. Blue values are editable.','note')],column_widths:{A:3,B:3,C:43,D:21,E:5,F:50}};
  const locations={};
  params.forEach(([label,value],i)=>{const row=i+7;locations[label]=`Inputs!D${row}`;inputs.cells.push(cell('C'+row,label),cell('D'+row,value,'input',/rate|loss|LTV|yield$|minimum$|fee|Spread|index|increment/i.test(label)&&!/quantity|years|months|before|DSCR/i.test(label)?'0.00%':'#,##0.00'));});
  inputs.cells.push(cell('F7',c.missing_insurance?'Insurance renewal missing: $36,000 is provisional, not verified.':'Annual insurance renewal is confirmed in source plan.','note'));
  const A=label=>locations[label];
  const analysis={name:'Analysis',cells:[cell('C2',c.name+' | Reference underwriting','title'),cell('C3','Author reference only | USD | Historical and scenario outputs remain separate','note'),cell('C6','Measure','header'),cell('D6','Amount / ratio','header'),cell('F6','Source / method','header')],column_widths:{A:3,B:3,C:41,D:23,E:4,F:57}};
  const lines=[
    ['Underwritten EGI',`=(${A('Gross potential rent')}*(1-${A('Revenue loss')})+${A('Other income')})*${A('EGI multiplier')}`],
    ['Management fee',`=MAX(${A('Management actual')},D7*${A('Management minimum')})`],
    ['Operating expenses',`=${A('Annual taxes')}+${A('Annual insurance allowance')}+${A('Utilities')}+${A('Repairs actual')}-${A('Nonrecurring repairs')}+${A('Payroll / contracts')}+${A('Administrative / legal')}+D8`],
    ['NOI before reserves','=D7-D9'],['Replacement reserves',`=${A('Reserve rate')}*${A('Reserve quantity')}`],['NCF after reserves','=D10-D11'],
    ['Valuation cap rate',`=${A('Valuation cap rate')}+${A('Cap rate increment')}`,'0.00%'],['Indicative value','=D10/D13'],
    ['Contract rate',`=IF(${A('Fixed contract rate (zero = floating)')}>0,${A('Fixed contract rate (zero = floating)')},MAX(${A('Current floating index')},${A('Index floor')})+${A('Spread')})`,'0.00%'],
    ['Sizing rate',`=MAX(D15,${A('Sizing rate floor')})+${A('Sizing rate increment')}`,'0.00%'],
    ['Annual debt constant',`=12*(D16/12)/(1-(1+D16/12)^(-${A('Amortization years')}*12))`,'0.0000%'],
    ['LTV capacity',`=D14*${A('LTV limit')}`],['DSCR capacity',`=D12/(${A('Minimum DSCR')}*D17)`],
    ['Debt yield capacity',`=IF(${A('Debt yield uses NOI before reserves')}=1,D10,D12)/${A('Minimum debt yield')}`],
    ['Maximum loan','=MIN(D18:D20)'],['Binding constraint','=IF(D21=D18,"LTV",IF(D21=D19,"DSCR","Debt yield"))','@'],
    ['Sizing debt service','=D21*D17'],['Sizing DSCR','=D12/D23','0.0000"x"'],
    ['Sizing debt yield',`=IF(${A('Debt yield uses NOI before reserves')}=1,D10,D12)/D21`,'0.00%'],
    ['Contractual first-year debt service',`=IF(${A('IO months')}>=12,D21*D15,D21*12*(D15/12)/(1-(1+D15/12)^(-${A('Amortization years')}*12)))`],
    ['Cash to borrower',`=D21-${A('Existing debt payoff')}-D21*${A('Loan origination fee')}-${A('Fixed closing costs')}`],
    ['Historical T12 EGI','=SUM(T12!P7:P11)'],['Historical operating expenses','=SUM(T12!P12:P18)'],
    ['Historical NOI before reserves','=D28-D29'],['Historical replacement reserves','=T12!P19'],['Historical NCF after reserves','=D30-D31']];
  lines.forEach(([label,f,fmt],i)=>{analysis.cells.push(cell('C'+(7+i),label),formula('D'+(7+i),f,fmt||dollars),cell('F'+(7+i),i<27?'Property plan / lender terms; see Inputs':'T12-Statement.pdf, both pages','note'));});
  const t12={name:'T12',cells:[cell('C2','Historical T12 | September 2025 - August 2026','title')],column_widths:{A:3,B:3,C:40,D:13,E:13,F:13,G:13,H:13,I:13,J:13,K:13,L:13,M:13,N:13,O:13,P:17},freeze_rows:6};
  ['Account','Sep-25','Oct-25','Nov-25','Dec-25','Jan-26','Feb-26','Mar-26','Apr-26','May-26','Jun-26','Jul-26','Aug-26','Annual'].forEach((v,j)=>t12.cells.push(cell(String.fromCharCode(67+j)+'6',v,'header')));
  c.t12_rows.forEach(([label,values],i)=>{t12.cells.push(cell('C'+(7+i),label));values.forEach((v,j)=>t12.cells.push(cell(String.fromCharCode(68+j)+(7+i),v,'body',dollars)));t12.cells.push(formula('P'+(7+i),`=SUM(D${7+i}:O${7+i})`));});
  const spec={sheets:[analysis,inputs,rr,t12],input_map:{cap_rate:locations['Valuation cap rate'],sizing_rate_increment:locations['Sizing rate increment'],egi_multiplier:locations['EGI multiplier']},output_map:{uw_egi:'Analysis!D7',uw_noi_before_reserves:'Analysis!D10',uw_ncf:'Analysis!D12',capitalization_value:'Analysis!D14',contract_rate:'Analysis!D15',sizing_rate:'Analysis!D16',annual_debt_constant:'Analysis!D17',ltv_limit:'Analysis!D18',dscr_limit:'Analysis!D19',debt_yield_limit:'Analysis!D20',maximum_loan:'Analysis!D21',binding_constraint:'Analysis!D22',first_year_debt_service:'Analysis!D26',cash_to_borrower:'Analysis!D27',t12_egi:'Analysis!D28',t12_operating_expenses:'Analysis!D29',t12_noi_before_reserves:'Analysis!D30',t12_reserves:'Analysis!D31',t12_ncf:'Analysis!D32'}};
  await fs.writeFile(path.join(folder,'reference-workbook-spec.json'),JSON.stringify(spec,null,2)+'\n');
  await writeWorkbook(spec,path.join(folder,'reference-underwriting.xlsx'),folder.endsWith('adapter-smoke')?'C2:F24':false);
  console.log(JSON.stringify({case:c.id,workbooks:2}));
}
