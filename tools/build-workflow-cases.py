"""Author original, deterministic CRE packets. Never reads private references.

Python authors PDFs and JSON; the companion artifact-tool JS authors XLSX.
Gold is deliberately outside each sources directory. Scored systems receive only
sources and brief, never this generator, the authoring data, or answer keys.
"""
import argparse
import calendar
import hashlib
import json
from pathlib import Path
import subprocess
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'benchmarks/workflow-v1'
YEAR = 2026
ASOF = '2026-08-31'


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def money(n):
    if n is None: return 'Not provided'
    return f'(${abs(n):,.0f})' if n < 0 else f'${n:,.0f}'


def pct(n): return f'{n:.2%}'


FONT_PAIRS=[('/System/Library/Fonts/Supplemental/Arial.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf'),
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
regular,bold=next(pair for pair in FONT_PAIRS if all(Path(f).exists() for f in pair))
pdfmetrics.registerFont(TTFont('BenchBody',regular));pdfmetrics.registerFont(TTFont('BenchBold',bold))
S = getSampleStyleSheet()
for style in S.byName.values(): style.fontName='BenchBold' if 'Heading' in style.name or style.name=='Title' else 'BenchBody'
S.add(ParagraphStyle(name='Body', fontName='BenchBody', fontSize=10, leading=15, spaceAfter=10))
S.add(ParagraphStyle(name='Note', fontName='BenchBody', fontSize=8, leading=11, textColor=colors.HexColor('#555B58'), spaceAfter=8))
S.add(ParagraphStyle(name='Cell', fontName='BenchBody', fontSize=8.3, leading=11))


def p(text, style='Body'): return Paragraph(escape(str(text)).replace('\n', '<br/>'), S[style])


def table(rows, widths, header=True):
    cells = [[p(v, 'Cell') for v in row] for row in rows]
    t = Table(cells, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
    commands = [('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),
                ('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#75887D'))]
    if header: commands += [('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7EEE9'))]
    t.setStyle(TableStyle(commands))
    return t


def pdf(path, title, pages):
    def footer(c, doc):
        c.setFont('BenchBody', 8); c.setFillColor(colors.HexColor('#536057'))
        c.drawString(42, 26, 'CRE Bench | Original fictional evaluation material | No real transaction')
        c.drawRightString(570, 26, f'{path.name} | {doc.page}')
    story=[]
    for i, blocks in enumerate(pages):
        if i: story.append(PageBreak())
        story += [p(title if i == 0 else title + ' / continued', 'Title'), Spacer(1, 12)] + blocks
    SimpleDocTemplate(str(path), pagesize=(612,792), rightMargin=42,leftMargin=42,
                      topMargin=36,bottomMargin=44,title=title,author='CRE Bench by Lev').build(story,onFirstPage=footer,onLaterPages=footer)


CASES = [
 dict(id='juniper-flats',name='Juniper Flats',asset='Multifamily',city='Raleigh, NC',address='2400 Juniper Bench Lane, Raleigh, NC 27610',
      scenario='Stabilized refinance; physical versus area occupancy; historical versus current rent',
      areas=[750]*20+[1050]*16,vacant=[8,24,35],rents=[1675]*20+[2175]*16,
      gross=840000,vacancy=-42000,concessions=-12000,bad_debt=-4500,other=39600,
      expenses=[108000,31200,28800,46200,42000,21600,30000],reserves=10800,capex=62000,
      uw_gross=864000,uw_loss=.06,uw_other=42000,uw_tax=112000,uw_insurance=33600,repair_remove=6000,
      mgmt=.03,reserve_basis='unit',reserve_rate=300,cap=.0575,ltv=.65,dscr=1.25,dy=.085,dy_basis='NCF',
      fixed=.059,spread=0,index=0,index_floor=0,sizing_floor=.0625,amort=30,io=24,term=84,
      payoff=3300000,fee=.0075,closing=45000,lease_rent=1675,amended_rent=None,lease_expiry='2027-07-31',
      lease_deposit=1675,missing_insurance=False,scanned=False),
 dict(id='cedar-landing',name='Cedar Landing',asset='Multifamily',city='San Antonio, TX',address='4800 Cedar Bench Drive, San Antonio, TX 78223',
      scenario='Lease-up; forecast not historical; IO debt service versus amortizing sizing',
      areas=[700]*24+[1100]*24,vacant=list(range(33,48)),rents=[1575]*24+[2025]*24,
      gross=1036800,vacancy=-302400,concessions=-64800,bad_debt=-8400,other=30000,
      expenses=[132000,40800,33600,54000,55200,27600,28000],reserves=14400,capex=184000,
      uw_gross=1056000,uw_loss=.07,uw_other=43200,uw_tax=138000,uw_insurance=45600,repair_remove=12000,
      mgmt=.035,reserve_basis='unit',reserve_rate=325,cap=.0575,ltv=.60,dscr=1.30,dy=.09,dy_basis='NCF',
      fixed=.0625,spread=0,index=0,index_floor=0,sizing_floor=.065,amort=30,io=36,term=60,
      payoff=4500000,fee=.01,closing=65000,lease_rent=1575,amended_rent=None,lease_expiry='2027-06-30',
      lease_deposit=1200,missing_insurance=False,scanned=False),
 dict(id='market-row',name='Market Row',asset='Retail',city='Columbus, OH',address='1800 Market Bench Avenue, Columbus, OH 43207',
      scenario='Executed amendment overrides a stale rent roll; unsigned broker draft is not authoritative',
      areas=[1800,2200,2500,3200,4000,5000,1500,2800],vacant=[7],rents=[7000,5500,6000,7200,9000,10500,3400,5200],
      gross=645600,vacancy=-46800,concessions=-14400,bad_debt=-3600,other=142800,
      expenses=[86400,25200,19200,28800,18000,14400,24000],reserves=9200,capex=98000,
      uw_gross=657600,uw_loss=.06,uw_other=150000,uw_tax=90000,uw_insurance=27600,repair_remove=4800,
      mgmt=.04,reserve_basis='sf',reserve_rate=.20,cap=.065,ltv=.65,dscr=1.25,dy=.09,dy_basis='NOI',
      fixed=.0625,spread=0,index=0,index_floor=0,sizing_floor=.065,amort=25,io=0,term=60,
      payoff=3400000,fee=.01,closing=48000,lease_rent=7000,amended_rent=7500,lease_expiry='2031-08-31',
      lease_deposit=15000,missing_insurance=False,scanned=False),
 dict(id='stonebridge-logistics',name='Stonebridge Logistics',asset='Industrial',city='Indianapolis, IN',address='8500 Stonebridge Bench Way, Indianapolis, IN 46241',
      scenario='Floating-rate index floor and separate underwriting floor; image-only lease evidence',
      areas=[18000,22000,30000,15000],vacant=[3],rents=[15000,18700,27000,12500],
      gross=852000,vacancy=-150000,concessions=-36000,bad_debt=-6000,other=186000,
      expenses=[126000,30000,12000,24000,18000,18000,25200],reserves=17000,capex=220000,
      uw_gross=900000,uw_loss=.08,uw_other=195000,uw_tax=132000,uw_insurance=33600,repair_remove=6000,
      mgmt=.03,reserve_basis='sf',reserve_rate=.20,cap=.0675,ltv=.60,dscr=1.30,dy=.10,dy_basis='NCF',
      fixed=0,spread=.0275,index=.0325,index_floor=.04,sizing_floor=.0725,amort=25,io=12,term=36,
      payoff=4200000,fee=.0125,closing=70000,lease_rent=15000,amended_rent=None,lease_expiry='2030-08-31',
      lease_deposit=30000,missing_insurance=False,scanned=True),
 dict(id='hawthorn-center',name='Hawthorn Center',asset='Retail',city='Greenville, SC',address='3200 Hawthorn Bench Road, Greenville, SC 29607',
      scenario='Lender management minimum; NOI-based debt yield versus NCF-based coverage; swap breakage',
      areas=[1400,1800,2200,2500,3000,3300,3800,4200,5000,1600],vacant=[9],
      rents=[3000,4000,4900,5600,6500,7400,8600,9200,10800,3400],
      gross=759600,vacancy=-40800,concessions=-22800,bad_debt=-6000,other=176400,
      expenses=[114000,32400,21600,36000,24000,18000,18000],reserves=11520,capex=74000,
      uw_gross=780000,uw_loss=.05,uw_other=180000,uw_tax=120000,uw_insurance=34800,repair_remove=0,
      mgmt=.04,reserve_basis='sf',reserve_rate=.15,cap=.0625,ltv=.625,dscr=1.25,dy=.09,dy_basis='NOI',
      fixed=.0635,spread=0,index=0,index_floor=0,sizing_floor=.0635,amort=25,io=0,term=60,
      payoff=4200000,fee=.008,closing=52000,lease_rent=3000,amended_rent=None,lease_expiry='2029-08-31',
      lease_deposit=6000,missing_insurance=False,scanned=False),
 dict(id='meadow-commerce',name='Meadow Commerce',asset='Industrial',city='Richmond, VA',address='6100 Meadow Bench Parkway, Richmond, VA 23234',
      scenario='Missing insurance renewal and conditional lease option; provisional sizing must stay qualified',
      areas=[16000,24000,32000],vacant=[],rents=[12800,20400,28800],
      gross=744000,vacancy=0,concessions=-18000,bad_debt=-2400,other=158400,
      expenses=[102000,26400,9600,19200,12000,16800,26400],reserves=14400,capex=112000,
      uw_gross=756000,uw_loss=.03,uw_other=162000,uw_tax=108000,uw_insurance=36000,repair_remove=0,
      mgmt=.03,reserve_basis='sf',reserve_rate=.20,cap=.065,ltv=.60,dscr=1.30,dy=.095,dy_basis='NCF',
      fixed=.061,spread=0,index=0,index_floor=0,sizing_floor=.065,amort=30,io=12,term=60,
      payoff=3600000,fee=.01,closing=55000,lease_rent=12800,amended_rent=None,lease_expiry='2028-08-31',
      lease_deposit=25600,missing_insurance=True,scanned=False),
]


def allocations(amount, seed=0):
    # Non-uniform integer monthly statements with exact annual reconciliation.
    weights=[94,96,98,99,101,103,104,106,103,101,98,97]
    weights=weights[seed%12:]+weights[:seed%12]
    first=[round(amount*w/sum(weights)) for w in weights[:-1]]
    return first+[amount-sum(first)]


EXPENSES=['Real estate taxes','Property insurance','Utilities','Repairs and maintenance','Payroll / contract labor','Administrative / legal','Management fee']


def derive(c):
    n=len(c['areas']); occupied=[i for i in range(n) if i not in c['vacant']]
    c['rows']=[{'unit':f'{101+i:03}', 'tenant':f'Household {101+i}' if c['asset']=='Multifamily' else f'Tenant {chr(65+i)} LLC',
        'area':a,'status':'Vacant' if i in c['vacant'] else 'Occupied',
        'rent':None if i in c['vacant'] else c['rents'][i], 'market_rent':c['rents'][i],
        'expiry':None if i in c['vacant'] else c['lease_expiry'] if i==0 else
                 (f'{2026+(8+i%12)//12}-{(8+i%12)%12+1:02d}-{calendar.monthrange(2026+(8+i%12)//12,(8+i%12)%12+1)[1]}'
                  if c['asset']=='Multifamily' else f'{2027+i%5}-08-31')} for i,a in enumerate(c['areas'])]
    c['t12_rows']=[(label,allocations(amount,i)) for i,(label,amount) in enumerate(zip(
        ['Gross potential base rent','Vacancy loss','Concessions','Bad debt','Other income / recoveries']+EXPENSES+
        ['Replacement reserves (below NOI)','Capital improvements (below cash flow)','Loan principal and interest (below cash flow)','Depreciation (noncash)'],
        [c['gross'],c['vacancy'],c['concessions'],c['bad_debt'],c['other']]+c['expenses']+[c['reserves'],c['capex'],294000,180000]))]
    return c


def key(c):
    occ=[r for r in c['rows'] if r['status']=='Occupied']
    egih=c['gross']+c['vacancy']+c['concessions']+c['bad_debt']+c['other']
    egif=c['uw_gross']*(1-c['uw_loss'])+c['uw_other']
    mgmt=max(c['expenses'][-1],egif*c['mgmt'])
    opex=c['uw_tax']+c['uw_insurance']+sum(c['expenses'][2:-1])-c['repair_remove']+mgmt
    noi=egif-opex
    reserve=(len(c['areas']) if c['reserve_basis']=='unit' else sum(c['areas']))*c['reserve_rate']
    ncf=noi-reserve
    rate=c['fixed'] or max(c['index'],c['index_floor'])+c['spread']
    sr=max(rate,c['sizing_floor']); r=sr/12; months=c['amort']*12
    constant=12*r/(1-(1+r)**(-months))
    value=noi/c['cap']; ltv=value*c['ltv']; dscr=ncf/(c['dscr']*constant)
    dy=(noi if c['dy_basis']=='NOI' else ncf)/c['dy']
    constraints={'LTV':ltv,'DSCR':dscr,'Debt yield':dy}; binding=min(constraints,key=constraints.get); loan=constraints[binding]
    stressed_egi=egif*.95
    stressed_noi=stressed_egi-(opex-mgmt+max(c['expenses'][-1],stressed_egi*c['mgmt']))
    rr=(sr+.01)/12; sc=12*rr/(1-(1+rr)**(-months))
    stress_loan=min(stressed_noi/c['cap']*c['ltv'],(stressed_noi-reserve)/(c['dscr']*sc),
        (stressed_noi if c['dy_basis']=='NOI' else stressed_noi-reserve)/c['dy'])
    f={
      'space_count':len(c['areas']),'occupied_count':len(occ),'total_area_sf':sum(c['areas']),
      'occupied_area_sf':sum(r['area'] for r in occ),'occupancy_count_pct':len(occ)/len(c['areas'])*100,
      'occupancy_area_pct':sum(r['area'] for r in occ)/sum(c['areas'])*100,
      'rent_roll_monthly_base':sum(r['rent'] for r in occ),
      'effective_monthly_base':sum(r['rent'] for r in occ)+(c['amended_rent']-c['lease_rent'] if c['amended_rent'] else 0),
      't12_egi':egih,'t12_operating_expenses':sum(c['expenses']),
      't12_noi_before_reserves':egih-sum(c['expenses']), 't12_reserves':c['reserves'],
      't12_ncf':egih-sum(c['expenses'])-c['reserves'],
      'uw_egi':egif,'uw_management_fee':mgmt,'uw_operating_expenses':opex,'uw_noi_before_reserves':noi,
      'uw_reserves':reserve,'uw_ncf':ncf,'capitalization_value':value,
      'contract_rate':rate,'sizing_rate':sr,'annual_debt_constant':constant,
      'ltv_limit':ltv,'dscr_limit':dscr,'debt_yield_limit':dy,'maximum_loan':loan,'binding_constraint':binding,
      'sizing_annual_debt_service':loan*constant,'sizing_dscr':ncf/(loan*constant),
      'sizing_debt_yield':(noi if c['dy_basis']=='NOI' else ncf)/loan,
      'first_year_debt_service':loan*rate if c['io']>=12 else loan*(12*(rate/12)/(1-(1+rate/12)**(-months))),
      'cash_to_borrower':loan-c['payoff']-loan*c['fee']-c['closing'],
      'stress_uw_noi':stressed_noi,'stress_maximum_loan':stress_loan,
      'subject_lease_monthly_rent':c['amended_rent'] or c['lease_rent'], 'subject_lease_expiry':c['lease_expiry'],
      'subject_lease_deposit':c['lease_deposit'],'verified_renewal_insurance':None if c['missing_insurance'] else c['uw_insurance'],
      'renewal_option_exercised':'Not evidenced', 'prepayment_friction':'Potential swap termination cost' if c['id']=='hawthorn-center' else 'As stated in term sheet',
    }
    extraction=list(f)[:13]+['subject_lease_monthly_rent','subject_lease_expiry','subject_lease_deposit','verified_renewal_insurance','renewal_option_exercised']
    refs={k:'Rent-Roll.xlsx / Rent Roll rows 7 onward' if k in extraction[:8] else 'T12-Statement.pdf / annual column, page 2' for k in extraction}
    refs.update({k:'Lease-File.pdf / clauses 2-5, including executed amendment where present' for k in ['subject_lease_monthly_rent','subject_lease_expiry','subject_lease_deposit','renewal_option_exercised']})
    refs['effective_monthly_base']='Rent-Roll.xlsx and Lease-File.pdf / executed amendment where present'
    refs['verified_renewal_insurance']='Property-and-Plan.pdf / underwriting plan, page 2'
    return {'case_id':c['id'],'fields':f,'extraction_fields':extraction,
            'financial_fields':[k for k in f if k not in extraction and k!='prepayment_friction'],
            'evidence_reference_notes':refs,'critical_fields':['maximum_loan','binding_constraint','uw_noi_before_reserves','uw_ncf','occupancy_count_pct','occupancy_area_pct','subject_lease_monthly_rent','verified_renewal_insurance'],
            'required_qualifications':[
             'Original fictional scenario; no external market or sponsor claims supported',
             'Historical T12 is distinct from current roll and the supplied underwriting plan',
             'Loan is indicative sizing, not a lender commitment',
             'Renewal option exercise is not evidenced']+
             (['Insurance renewal is missing; $36,000 is a provisional scenario allowance, not a verified quote'] if c['missing_insurance'] else [])+
             (['Executed amendment controls over rent roll and unsigned draft'] if c['amended_rent'] else [])+
             (['Prepayment without bank penalty may still incur swap termination cost'] if c['id']=='hawthorn-center' else [])}


FIELD_DESCRIPTIONS={
 'space_count':'unit/suite count','occupied_count':'occupied unit/suite count','total_area_sf':'total rentable square feet',
 'occupied_area_sf':'occupied rentable square feet','occupancy_count_pct':'physical occupancy by count, percent 0-100',
 'occupancy_area_pct':'occupancy by area, percent 0-100','rent_roll_monthly_base':'monthly base rent as printed on the rent roll',
 'effective_monthly_base':'monthly contractual base rent after applying authoritative lease amendments',
 't12_egi':'historical effective gross income','t12_operating_expenses':'historical operating expense excluding reserves/capex/debt/depreciation',
 't12_noi_before_reserves':'historical NOI before replacement reserves','t12_reserves':'historical replacement reserves','t12_ncf':'historical NCF after reserves',
 'uw_egi':'underwritten EGI','uw_management_fee':'lender-normalized management fee','uw_operating_expenses':'underwritten operating expense before reserves',
 'uw_noi_before_reserves':'underwritten NOI before reserves','uw_reserves':'underwritten replacement reserves','uw_ncf':'underwritten NCF after reserves',
 'capitalization_value':'indicative value from underwritten NOI before reserves and specified cap rate',
 'contract_rate':'current contractual annual rate, decimal','sizing_rate':'annual underwriting rate, decimal',
 'annual_debt_constant':'annual debt service per dollar of principal using sizing rate and monthly amortization',
 'ltv_limit':'maximum principal under LTV','dscr_limit':'maximum principal under DSCR','debt_yield_limit':'maximum principal under lender debt yield convention',
 'maximum_loan':'minimum of the three constraints','binding_constraint':'LTV, DSCR, or Debt yield',
 'sizing_annual_debt_service':'annual amortizing debt service at maximum loan and sizing rate','sizing_dscr':'NCF divided by sizing annual debt service',
 'sizing_debt_yield':'lender-defined cash-flow numerator divided by maximum loan',
 'first_year_debt_service':'first-year contractual debt service, observing IO if applicable',
 'cash_to_borrower':'loan less existing payoff, loan-based origination fee and fixed closing costs; negative means cash in',
 'stress_uw_noi':'NOI with EGI 5% lower, management recalculated; other expense unchanged',
 'stress_maximum_loan':'sizing with EGI 5% lower AND sizing rate 100 bps higher, cap rate unchanged',
 'subject_lease_monthly_rent':'current authoritative monthly rent for unit/suite 101',
 'subject_lease_expiry':'authoritative current expiry for unit/suite 101, ISO date',
 'subject_lease_deposit':'security deposit for unit/suite 101',
 'verified_renewal_insurance':'verified annual renewal insurance premium; unknown/null if absent, not the scenario allowance',
 'renewal_option_exercised':'whether delivered materials evidence exercise of the renewal option',
 'prepayment_friction':'describe actual prepayment friction, including swap termination if stated'}


def build_case(c, dest):
    c=derive(c); sources=dest/'sources'; sources.mkdir(parents=True,exist_ok=True)
    save(dest/'authoring-data.json',c); save(dest/'answer-key.json',key(c))
    expense_rows=[['Category','T12 actual','Underwriting treatment']]
    for i,(label,actual) in enumerate(zip(EXPENSES,c['expenses'])):
        change=money(c['uw_tax']) if i==0 else money(c['uw_insurance'])+(' provisional allowance; renewal quote missing' if c['missing_insurance'] else ' annual renewal quote supplied in this plan') if i==1 else \
               f'Remove {money(c["repair_remove"])} of one-time casualty cleanup; otherwise T12' if i==3 else \
               f'Greater of T12 actual or {pct(c["mgmt"])} of underwritten EGI' if i==6 else 'Use T12 actual'
        expense_rows.append([label,money(actual),change])
    pdf(sources/'Property-and-Plan.pdf',c['name']+' | Property and underwriting plan',[
      [p('Prepared September 1, 2026 | Refinance request | All dollars USD','Note'),
       table([['Item','Provided information'],['Property',c['name']],['Asset / market',c['asset']+' / '+c['city']],
              ['Scenario address',c['address']+' (fictional; do not geocode or source external property data)'],
              ['Sponsor',c['name']+' Owner LLC, a fictional single-property owner'],['As-of',ASOF],
              ['Existing debt payoff',money(c['payoff'])],['Fixed closing costs',money(c['closing'])]], [145,383]),
       Spacer(1,14),p('Transaction context','Heading2'),
       p('The owner seeks a cash-out refinance if proceeds permit, and can evaluate a cash-in refinance if required. The supplied operating plan is an underwriting scenario, not a lender-approved forecast. No appraisal, environmental report, sponsor track record, market comparables or completed credit approval is supplied.'),
       p('Occupancy is measured from the dated rent roll. Vacant space has market rent for context but no current contractual base rent. Historical income covers September 2025 through August 2026 and should not be forced to equal a point-in-time annualized rent roll.'),
       p('The historical accounting package may describe cash flow after reserves as "property NOI". Preserve the reported line and separately identify NOI before replacement reserves and NCF after replacement reserves. Debt, capital improvements and depreciation are not operating expenses.')],
      [p('Underwriting plan | annual amounts | September 2026 forward','Heading2'),
       table([['Assumption','Instruction'],['Gross potential base rent',money(c['uw_gross'])+' annual; supplied scenario, not inferred from the T12'],
              ['Combined revenue loss',pct(c['uw_loss'])+' of underwritten gross potential base rent; includes vacancy, concessions and bad debt'],
              ['Other income / recoveries',money(c['uw_other'])+' annual; add after revenue loss'],
              ['Management fee',f'Greater of T12 actual and {pct(c["mgmt"])} of underwritten EGI'],
              ['Replacement reserves',f'${c["reserve_rate"]:,.2f} per '+('unit' if c['reserve_basis']=='unit' else 'rentable SF')+' per year; deduct after NOI'],
              ['Insurance evidence','No renewal quote or binder delivered. Use $36,000 solely for provisional calculations; verified premium remains unknown.' if c['missing_insurance'] else f'Fictional insurer renewal confirmation dated August 25, 2026: annual premium {money(c["uw_insurance"])}; use in underwriting.']], [150,378]),
       Spacer(1,12),table(expense_rows,[146,90,292]),
       p('Sensitivity instruction: reduce total underwritten EGI by 5%, recompute the management minimum and hold all other operating expense and reserve assumptions constant. For the combined downside, also increase the sizing rate by 100 basis points. Cap rate stays constant in the combined downside. A separate cap-rate sensitivity uses +50 basis points.','Note')]])
    # Monthly statement split by half-year to keep native PDF tables legible.
    t12pages=[]
    for half in range(2):
        months=['Sep-25','Oct-25','Nov-25','Dec-25','Jan-26','Feb-26','Mar-26','Apr-26','May-26','Jun-26','Jul-26','Aug-26'][half*6:half*6+6]
        header=['Account']+months+(['Annual'] if half else [])
        rows=[header]
        for label,vals in c['t12_rows']:
            rows.append([label]+[f'({abs(n):,})' if n<0 else f'{n:,}' for n in vals[half*6:half*6+6]]+([f'{sum(vals):,}'] if half else []))
        widths=[150]+([54]*7 if half else [63]*6)
        t12pages.append([p('September 2025 - August 2026 | Actual cash accounting | USD','Note'),table(rows,widths),
            p('Parentheses indicate negative revenue. Expense rows are positive charges. Other income includes reimbursements. Replacement reserves, capital improvements, loan principal/interest and depreciation are shown for reconciliation and are below operating income. No subtotal should be treated as another expense.','Note')])
    pdf(sources/'T12-Statement.pdf',c['name']+' | Trailing twelve-month statement',t12pages)
    leasepages=[[p('Fictional executed lease extract | Premises 101 | Signed August 15, 2025','Note'),
        p('1. Parties and premises','Heading2'),p(f'{c["name"]} Owner LLC leases premises 101, comprising {c["areas"][0]:,} rentable square feet, to '+c['rows'][0]['tenant']+'.'),
        p('2. Term','Heading2'),p(f'Commencement September 1, 2025. The initial term expires {c["lease_expiry"]}. Any extension requires timely written exercise and satisfaction of the conditions below.'),
        p('3. Base rent and other charges','Heading2'),p(f'Base rent is {money(c["lease_rent"])} per month as of August 31, 2026. Base rent is separate from reimbursements, taxes and other additional rent. No base-rent increase applies before September 1, 2027.'),
        p('4. Security deposit','Heading2'),p(f'The security deposit is {money(c["lease_deposit"])} and is not prepaid rent or recurring income.'),
        p('5. Renewal option','Heading2'),p('Tenant has one conditional renewal option, subject to no uncured default and written notice at least 180 days before expiration. No exercise notice, landlord acknowledgment or amendment exercising this option is included in the packet. Do not extend the current expiry based on the existence of the option alone.'),
        p('6. Authority','Heading2'),p('A written amendment signed by both parties controls any conflicting prior rent schedule. Unsigned proposals do not modify this executed agreement. Financial schedules may require reconciliation to executed legal documents.')]]
    if c['amended_rent']:
        leasepages.append([p('Executed first amendment | Signed by both parties July 20, 2026','Heading2'),
          p('Effective August 1, 2026, base rent under Section 3 changes to $7,500 per month. The existing expiration date and $15,000 deposit remain unchanged. All other provisions remain in force.'),
          p('Attachment: broker proposal | UNSIGNED | August 27, 2026','Heading2'),
          p('For discussion only: possible rent of $8,000 per month and extension through August 31, 2033. Neither party has signed or accepted this draft. It is not a binding amendment.'),
          p('Manager note: the August 31 rent roll still shows the pre-amendment amount. The executed first amendment is authoritative for current contractual rent.','Note')])
    pdf(sources/'Lease-File.pdf',c['name']+' | Lease file',leasepages)
    if c['scanned']:
        scratch=ROOT/'work/workflow-v1/scans';scratch.mkdir(parents=True,exist_ok=True)
        subprocess.run(['pdftoppm','-scale-to','1800','-png',str(sources/'Lease-File.pdf'),str(scratch/c['id'])],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        from reportlab.pdfgen import canvas
        canv=canvas.Canvas(str(sources/'Lease-File.pdf'),pagesize=(612,792),invariant=1)
        for png in sorted(scratch.glob(c['id']+'-*.png')):
            canv.drawImage(str(png),0,0,width=612,height=792);canv.showPage()
        canv.save()
    rate_text=(pct(c['fixed'])+' fixed annual contractual rate' if c['fixed'] else
        f'Index {pct(c["index"])} with an index floor of {pct(c["index_floor"])}; add {pct(c["spread"])} spread AFTER applying the index floor')
    prepay='No bank prepayment penalty. A separately documented interest-rate swap may have a termination payment or receipt; "no penalty" does not mean cost-free exit.' if c['id']=='hawthorn-center' else '1% of outstanding principal if prepaid in years 1-2; no stated bank penalty thereafter. No swap is assumed in this fictional scenario.'
    pdf(sources/'Lender-Terms.pdf',c['name']+' | Indicative lender terms',[
      [p('Fictional term sheet | September 1, 2026 | Nonbinding discussion terms','Note'),
       table([['Term','Requirement'],['Purpose','First-mortgage refinance'],['Loan ceiling','Lowest of the LTV, DSCR and debt-yield constraints below; no separate dollar cap'],
              ['LTV',pct(c['ltv'])+' of indicative value'],['Valuation',f'Underwritten NOI BEFORE reserves divided by {pct(c["cap"])} cap rate; no appraisal is implied'],
              ['DSCR',f'Minimum {c["dscr"]:.2f}x using NCF AFTER reserves divided by annual amortizing debt service at sizing rate'],
              ['Debt yield',f'Minimum {pct(c["dy"])}; numerator is underwritten {c["dy_basis"]} '+('BEFORE reserves' if c['dy_basis']=='NOI' else 'AFTER reserves')],
              ['Contract rate',rate_text],['Sizing rate',f'Greater of current contractual rate and {pct(c["sizing_floor"])} underwriting floor'],
              ['Amortization',f'{c["amort"]} years, monthly payments; calculate annual debt service as 12 monthly payments'],
              ['Interest-only period',f'{c["io"]} months; underwriting DSCR still uses amortizing debt service'],
              ['Maturity',f'{c["term"]} months'],['Origination fee',pct(c['fee'])+' of actual initial principal'],['Prepayment',prepay]], [126,402]),
       p('Sizing uses unrounded intermediate values. Round displayed currency for readers only. No fee capitalization, interest reserve, cash sweep, earn-out or additional holdback is assumed. Existing debt payoff and fixed closing costs are in the property plan.','Note')]])
    fields='\n'.join(f'- `{k}`: {v}.' for k,v in FIELD_DESCRIPTIONS.items())
    brief=f'''# {c['name']}: prepare a refinance analysis

You are the CRE analyst preparing a financing package for internal review. Analyze the attached files as of August 31, 2026. All property, borrower, tenant, address and lender details are fictional. Use only this packet; do not research, geocode, invent comps or contact anyone.

Deliver four work products in this fresh workflow:

1. An extraction and financial analysis with source locations, showing historical T12, current contractual rent/occupancy and the supplied underwriting scenario separately. Reconcile authoritative documents and disclose unresolved evidence. Report the fields below in an easily readable table or structured appendix, using these field IDs where practical. JSON formatting is optional. Correct unambiguous financial content matters, not a particular serialization.
2. Loan sizing under each of the three constraints, the binding maximum, actual first-year versus sizing debt service, net cash to/from the borrower, and the specified downside. Follow this lender's definitions exactly. Unknown facts must remain unknown; explicitly permitted provisional assumptions can support conditional calculations.
3. A downloadable XLSX underwriting workbook with editable assumptions, live formulas, historical/underwritten separation, loan sizing, sources/uses and sensitivity outputs. A reviewer must be able to change cap rate, sizing rate and EGI and obtain correct recalculated results. Include a clear location map for these inputs and the loan/NOI/value outputs. Do not deliver only code or a table in place of the workbook.
4. A concise, polished financing memorandum, delivered as a PDF or native memo with PDF export. Include the financing decision, accurate key figures and period labels, tenant/lease discussion, assumptions, limitations, risks and source references. No invented market, sponsor or lender claims. This is an internal-review financing memorandum, not a legal opinion or credit commitment.

If the product requires an outline or generation confirmation, prepare it and request the confirmation. No content changes or corrected answers will be supplied. If a file is missing/unreadable, identify it and continue only where the available evidence permits. Report what you actually delivered and anything blocked.

## Requested analysis fields

Dollar amounts are USD; rates and ratios are decimal unless the ID specifies percent 0-100. Use ISO dates. Cite document/page or worksheet/row and show calculation inputs for derived values.

{fields}

Keep all rates and assumptions from the packet. Current rate, sizing rate, historic NOI, underwriting NOI and NCF are distinct. The first year of contractual debt service uses the contractual rate and stated IO period. The combined downside is EGI -5% AND sizing rate +100 bps; management is recalculated and the valuation cap rate is unchanged. The workbook should also support cap rate +50 bps separately.
'''
    (dest/'brief.md').write_text(brief)
    return c


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smoke-only',action='store_true');parser.add_argument('--cases-only',action='store_true');args=parser.parse_args()
    if not args.smoke_only:
        for case in CASES: build_case(case.copy(),BASE/'cases'/case['id'])
    if args.cases_only:
        print('Created the six scored packets; smoke files untouched.');return
    smoke=CASES[0].copy()
    smoke.update(id='adapter-smoke',name='Adapter House',areas=[600,900],vacant=[1],rents=[1200,1600],
                 address='2 Adapter Bench Lane, Raleigh, NC 27610',gross=33600,vacancy=-12000,concessions=0,bad_debt=0,other=1200,
                 expenses=[2400,1200,600,900,0,300,600],reserves=600,capex=2000,uw_gross=36000,uw_loss=.1,uw_other=1200,
                 uw_tax=2600,uw_insurance=1400,repair_remove=0,payoff=100000,closing=5000,lease_rent=1200,lease_deposit=1200)
    build_case(smoke,BASE/'smoke/adapter-smoke')
    print('Created original PDF packets and separate authoring data/keys. XLSX authoring is the next step.')


if __name__=='__main__': main()
