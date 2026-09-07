"""Create original fictional CRE research packets; never reads model outputs."""
import copy
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'benchmarks/research-v1'
ASOF = '2026-08-31'
PROFILES = [
    ('alder', 'Multifamily', 'Charlotte', 80, 30_000_000),
    ('birch', 'Retail', 'Phoenix', 30_000, 12_000_000),
    ('cypress', 'Industrial', 'Columbus', 80_000, 10_000_000),
    ('dogwood', 'Multifamily', 'Tampa', 120, 35_000_000),
    ('elm', 'Retail', 'Raleigh', 45_000, 18_000_000),
    ('fir', 'Industrial', 'Dallas', 110_000, 16_000_000),
]
TASKS = ['sales_comps', 'rent_comps', 'sponsor_leads', 'refinance_leads']


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def build(task, v):
    stem, asset, market, size, price = PROFILES[v]
    rng = random.Random(f'research-2026-09-07-{task}-{v}')
    slug = task.replace('_', '-') + '-' + stem
    config = dict(case_id=slug, task=task, as_of=ASOF, market=market,
                  asset_type=asset, cutoff='2025-09-01', size_min=size * .65,
                  size_max=size * 1.45, max_distance_miles=8,
                  deal_min_usd=price * .5, deal_max_usd=price * 1.5,
                  refinance_window_start='2026-09-01', refinance_window_end='2027-08-31',
                  requested_count=5 if 'comps' in task else 10,
                  unit='unit' if asset == 'Multifamily' else 'sf',
                  contact_cutoff='2026-03-01')
    records = []
    updates = []
    ids = rng.sample(range(1000, 9999), 20)
    for j in range(20):
        rid = f'R{ids[j]}'
        eid = f'{stem.upper()}-{task[:3].upper()}-{rng.randrange(10000,99999)}'
        name = f'{stem.title()} {rng.choice(["Grove", "Park", "Crossing", "Square", "Point"])} {j+1}'
        factor = 0.8 + (j % 7) * .06
        r = dict(record_id=rid, entity_id=eid, name=name, asset_type=asset, market=market,
                 source_id=f'S-{rid}', published_at='2026-08-15',
                 event_date=f'2026-{2+j%6:02d}-{5+j%20:02d}', distance_miles=round(.8+j*.23,2))
        if task == 'sales_comps':
            amount = round(price * factor / 1000) * 1000
            amount_unit = ['USD', 'USD_thousands', 'USD_millions'][j % 3]
            r.update(property_size=round(size*factor), size_unit=config['unit'],
                     consideration=amount / {'USD':1,'USD_thousands':1000,'USD_millions':1e6}[amount_unit],
                     consideration_unit=amount_unit, status='closed', scope='single_asset',
                     interest='fee_simple', related_party=False, condition='stabilized',
                     evidence_kind='recorded_deed_and_closing_statement')
            changes = {
                7:dict(status='listing'), 8:dict(scope='portfolio_unallocated'),
                9:dict(related_party=True), 10:dict(interest='minority_equity_interest'),
                11:dict(condition='redevelopment'), 12:dict(asset_type='Office'),
                13:dict(event_date='2024-02-10'), 14:dict(distance_miles=18.6),
                15:dict(consideration=None), 16:dict(property_size=round(size*2.1)),
                17:dict(published_at='2026-09-03'), 18:dict(size_unit='acre'),
            }
        elif task == 'rent_comps':
            r.update(area_sf=round(1000*factor) if asset=='Multifamily' else round(size*.4*factor),
                     rent_quote=round(1.8+j*.07,3) if j%2 else round(21+j*.8,3),
                     rent_quote_unit='USD_per_sf_month' if j%2 else 'USD_per_sf_year',
                     expense_basis='gross' if j%3==0 else 'NNN',
                     annual_expenses_psf=6.25 if j%3==0 else None,
                     free_months=j%4, term_months=36+j%3*12, annual_increase_pct=2.5,
                     ti_allowance_psf=12+j%4*3, status='executed',
                     evidence_kind='executed_lease_abstract', size_unit='sf')
            changes = {
                7:dict(status='asking'),8:dict(free_months=None),
                9:dict(expense_basis='gross',annual_expenses_psf=None),
                10:dict(ti_allowance_psf=None),11:dict(status='unsigned_proposal'),
                12:dict(asset_type='Office'),13:dict(event_date='2024-02-10'),
                14:dict(distance_miles=18.6),15:dict(term_months=None),
                16:dict(rent_quote=None),17:dict(published_at='2026-09-03'),
                18:dict(rent_quote_unit='USD_per_sf_year',rent_quote=0),
            }
        elif task == 'sponsor_leads':
            r.update(firm_name=f'{name} Capital',firm_kind='owner_operator',
                     transaction_size_usd=round(price*factor),size_basis='single_asset_purchase',
                     activity='closed_acquisition', parent_entity_id=None, parent_link='not_applicable',
                     contact_name=f'{["Alex", "Morgan", "Jordan", "Taylor"][j%4]} {stem.title()}{j+1}',
                     contact_role='Head of Acquisitions' if j%2 else 'CFO',
                     contact_email=f'person{j+1}@{slug}.example', email_basis='published_business',
                     employment='current', contact_verified_at='2026-08-10',
                     evidence_kind='company_acquisition_release_and_team_page')
            changes = {
                7:dict(firm_kind='broker'),8:dict(firm_kind='property_manager'),
                9:dict(transaction_size_usd=price*7,size_basis='portfolio_total'),
                10:dict(activity='announced_bid'),11:dict(market='Seattle'),
                12:dict(asset_type='Office'),13:dict(event_date='2024-02-10'),
                14:dict(transaction_size_usd=price*.2),15:dict(employment='former'),
                16:dict(contact_role='Registered Agent'),17:dict(published_at='2026-09-03'),
                18:dict(contact_verified_at='2024-01-10'),
            }
        else:
            r.update(property_size=round(size*factor),owner_entity_id=f'O-{eid}',
                     owner_name=f'{name} Holdings',owner_relation='record_owner',
                     ownership_verified_at='2026-08-10',loan_id=f'L-{eid}',
                     loan_amount_usd=round(price*.6*factor),loan_amount_basis='original_principal',
                     outstanding_balance_usd=None, loan_status='active_confirmed',
                     maturity_date=f'2027-{1+j%7:02d}-15',maturity_basis='executed_note',
                     extension_status='none_executed',
                     contact_name=f'{["Casey", "Riley", "Avery", "Sam"][j%4]} {stem.title()}{j+1}',
                     contact_role='Director of Finance',contact_email=f'finance{j+1}@{slug}.example',
                     email_basis='published_business',employment='current',
                     contact_verified_at='2026-08-10',evidence_kind='note_owner_confirmation_and_team_page')
            changes = {
                7:dict(loan_status='released'),8:dict(owner_relation='property_manager'),
                9:dict(maturity_basis='inferred_from_origination'),
                10:dict(extension_status='option_unresolved',maturity_basis='unconfirmed'),
                11:dict(market='Seattle'),12:dict(asset_type='Office'),
                13:dict(maturity_date='2028-02-01'),14:dict(ownership_verified_at='2024-01-01'),
                15:dict(employment='former'),16:dict(contact_role='Registered Agent'),
                17:dict(published_at='2026-09-03'),18:dict(loan_status='status_unknown'),
            }
        r.update(changes.get(j,{}))
        records.append(r)
    # A duplicate is a second source, never an additional independent result.
    for key,value in records[0].items():
        if key not in ('record_id','source_id','published_at'): records[19][key]=copy.deepcopy(value)
    records[19]['evidence_kind']='second_source_same_underlying_record'
    # Explicit source amendments exercise precedence and as-of filtering.
    def amendment(j,changes,date='2026-08-20',kind='executed_amendment'):
        u=dict(source_id=f'U-{records[j]["record_id"]}-{len(updates)+1}',record_id=records[j]['record_id'],
               entity_id=records[j]['entity_id'],published_at=date,effective_date=date,
               document_kind=kind,changes=changes)
        updates.append(u)
    if task=='sales_comps':
        amendment(1,dict(consideration=price*.93,consideration_unit='USD'))
        amendment(2,dict(consideration=1,consideration_unit='USD'),date='2026-09-10')
        amendment(3,dict(consideration=price*.5),kind='unsigned_draft')
    elif task=='rent_comps':
        amendment(1,dict(free_months=4,ti_allowance_psf=18))
        amendment(2,dict(rent_quote=2),date='2026-09-10')
        amendment(3,dict(free_months=8),kind='unsigned_draft')
    elif task=='sponsor_leads':
        amendment(1,dict(contact_email=f'new.cfo@{slug}.example',contact_name=f'Drew {stem.title()}',contact_role='CFO'),kind='current_company_team_page')
        amendment(2,dict(employment='former'),date='2026-09-10',kind='current_company_team_page')
        amendment(3,dict(transaction_size_usd=price*4),kind='unsigned_draft')
        # An SPV already represented by its evidenced parent is not another sponsor.
        records[6].update(parent_entity_id=records[0]['entity_id'],parent_link='executed_ownership_schedule',firm_kind='property_SPV')
        records[4]['contact_email']=None
        records[4]['email_basis']='not_published'
    else:
        amendment(1,dict(maturity_date='2028-09-30',extension_status='executed'))
        amendment(2,dict(loan_status='released'),date='2026-09-10',kind='recorded_release')
        amendment(3,dict(maturity_date='2028-01-01'),kind='unsigned_draft')
        records[4]['contact_email']=None
        records[4]['email_basis']='not_published'
    # Sparse and zero-match cases: the brief stays feasible to answer by abstaining.
    if v==4:
        for j in (3,4,5,6): amendment(j,dict(asset_type='Office'))
    if v==5:
        for j in range(7): amendment(j,dict(market='Seattle'))
    rng.shuffle(records);rng.shuffle(updates)
    return config,records,updates


def brief(c):
    task=c['task']; common=f'''# {c['case_id']}\n\nFictional CRE research evaluation. As of {ASOF}, work only from the supplied record extracts and source updates. These records are original fixtures, not real properties or contacts. Do not use external search, other deals, CRM records or contact enrichment; do not send messages or create CRM records. Routine analysis and requested file generation are authorized.\n\nScope: {c['asset_type']} in {c['market']}. Use evidence published and effective on or before the cutoff. Executed amendments, recorded releases and current company team-page updates override the base extract for the same entity. Unsigned drafts and later-dated evidence do not. Apply entity updates to duplicate records of that entity. Missing is unknown, not zero.\n\n'''
    if task=='sales_comps':
        goal=f'''Select up to five unique comparable closed sales from {c['cutoff']} through {ASOF}, within {c['max_distance_miles']} miles, with {c['size_min']:g}–{c['size_max']:g} {c['unit']} of property size. Only stabilized, single-asset, fee-simple, unrelated-party transactions with known positive consideration and the correct size unit qualify. A listing, unallocated portfolio price, minority interest, or redevelopment is not a qualifying sale. Normalize consideration to USD and price per {c['unit']}. Rank qualified results by distance ascending, then most recent closing date; exact ties are acceptable.\nRequired facts for each selected row: entity_id, event_date, consideration_usd, property_size, price_per_unit.\n'''
    elif task=='rent_comps':
        goal=f'''Select up to five unique executed leases from {c['cutoff']} through {ASOF} within {c['max_distance_miles']} miles. Asking/unsigned rents do not qualify. Positive rent and known term, free rent and TI are required; gross leases also require a known expense deduction. Compare effective net rent per sf per year using this client convention: convert the face quote to annual $/sf; increase face rent by the stated annual percentage at months 13, 25, etc.; charge no face rent in the first free_months; deduct annual_expenses_psf/12 in EVERY month for gross leases (NNN deduction is zero); subtract TI once; divide net total by term_months and multiply by 12. This is an undiscounted rent-only convention, not a market appraisal. Rank qualified results by distance ascending, then latest lease date.\nRequired facts: entity_id, event_date, annual_face_rent_psf, effective_net_rent_psf_year, term_months.\n'''
    elif task=='sponsor_leads':
        goal=f'''Select up to ten distinct operating sponsors with a closed single-asset acquisition in the specified market/asset class from {c['cutoff']} through {ASOF}, with transaction size ${c['deal_min_usd']:,.0f}–${c['deal_max_usd']:,.0f}. Exclude brokers, managers, announced bids and portfolio totals. Resolve property SPVs to evidenced operating parents and avoid duplicate sponsors. A current CFO, Head of Acquisitions or Director of Finance verified since {c['contact_cutoff']} is required. Registered agents and former employees do not qualify. A business email is optional; report null if it is not published, never guess one. Rank by qualifying transaction date descending, then transaction size descending.\nRequired facts: entity_id (operating parent), firm_name, transaction_size_usd, event_date, contact_name, contact_role, contact_email.\n'''
    else:
        goal=f'''Select up to ten distinct property/loan refinance opportunities with confirmed active debt and an executed, unextended-or-amended maturity between {c['refinance_window_start']} and {c['refinance_window_end']}. A record owner verified since {c['contact_cutoff']} and current CFO, Head of Acquisitions or Director of Finance verified since that date are required. Exclude released/unknown-status loans, unconfirmed/inferred maturities, unresolved extensions, stale owners, managers and registered agents. Respect executed extensions. Original principal is not outstanding balance. Email is optional; report null unless published. Rank by confirmed maturity ascending, then original principal descending.\nRequired facts: entity_id (property), owner_entity_id, maturity_date, original_principal_usd, outstanding_balance_usd, contact_name, contact_email.\n'''
    contract='''\nReturn your complete answer as a JSON object (a fenced JSON block is acceptable) with:\n- shortlist: ordered array of {record_id, facts: {required facts above}, source_ids: [base and controlling update IDs], rationale}.\n- candidate_decisions: one row for EVERY base record, {record_id, eligible: true/false, reason, source_ids}. Eligibility means satisfying the business rules before deduplication; note duplicates in reason. A valid SPV mapped to a qualifying evidenced parent is eligible but must not add a second sponsor slot.\n- summary: concise conclusion, including insufficient evidence or no qualifying results.\n- limitations: array of uncertainties.\nCitations must name the exact S-/U- source identifiers supplied in the packet. Do not claim an unsupported field or contact. Also produce a downloadable comp-grid XLSX for comps or prospect CSV for leads with citations and the same selected facts. Preserve explicit nulls and numeric units. Artifact creation is outside the direct API control and is assessed only for agent/native tracks.\n'''
    return common+goal+contract


if __name__=='__main__':
    for task in TASKS:
        for v in range(6):
            c,rs,us=build(task,v);p=BASE/'cases'/c['case_id']
            write(p/'case.json',c);write(p/'sources/records.json',rs);write(p/'sources/updates.json',us)
            b=brief(c);(p/'brief.md').write_text(b)
            packet=b+'\n## Base source extracts\n\n'+'\n'.join(json.dumps(r,ensure_ascii=False) for r in rs)+'\n\n## Source updates\n\n'+'\n'.join(json.dumps(u,ensure_ascii=False) for u in us)+'\n'
            (p/'packet.md').write_text(packet)
    print('Created 24 original fictional packets with 20 candidate records each.')
