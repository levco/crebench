"""Deterministic reference interpretation for the frozen fictional research cases."""
import copy
import datetime as dt
import json
from pathlib import Path

ROLES = {'CFO', 'Head of Acquisitions', 'Director of Finance'}
AUTHORITATIVE = {'executed_amendment', 'recorded_release', 'current_company_team_page'}


def resolve(config, records, updates):
    resolved = {}
    for raw in records:
        row = copy.deepcopy(raw); evidence = [raw['source_id']]
        for u in sorted(updates, key=lambda u: (u['effective_date'], u['published_at'], u['source_id'])):
            if (u['entity_id'] == row['entity_id'] and u['document_kind'] in AUTHORITATIVE
                and u['effective_date'] <= config['as_of'] and u['published_at'] <= config['as_of']):
                row.update(u['changes']); evidence.append(u['source_id'])
        row['_evidence'] = evidence; resolved[row['record_id']] = row
    return resolved


def effective_rent(row):
    face = row['rent_quote'] * (12 if row['rent_quote_unit'] == 'USD_per_sf_month' else 1)
    expenses = row['annual_expenses_psf'] if row['expense_basis'] == 'gross' else 0
    net = -row['ti_allowance_psf']
    for month in range(row['term_months']):
        if month >= row['free_months']:
            net += face * (1 + row['annual_increase_pct']/100) ** (month//12) / 12
        net -= expenses/12
    return face, net/row['term_months']*12


def truth(config, records, updates):
    rows = resolve(config, records, updates); task = config['task']; result = {}
    parents = {r['entity_id']: r for r in rows.values() if r.get('firm_kind') == 'owner_operator'}
    for rid, r in rows.items():
        reasons = []
        def need(ok, message):
            if not ok: reasons.append(message)
        need(r['published_at'] <= config['as_of'], 'Source published after as-of date')
        need(r['market'] == config['market'], 'Wrong market')
        need(r['asset_type'] == config['asset_type'], 'Wrong asset type')
        facts = {}; entity = r['entity_id']; citations = list(r['_evidence'])
        if task != 'refinance_leads':
            need(config['cutoff'] <= r['event_date'] <= config['as_of'], 'Event outside lookback')
        if 'comps' in task:
            need(r['distance_miles'] <= config['max_distance_miles'], 'Outside radius')
        if task == 'sales_comps':
            for key, value in [('status','closed'), ('scope','single_asset'), ('interest','fee_simple'), ('condition','stabilized'), ('size_unit',config['unit'])]:
                need(r[key] == value, f'{key} is {r[key]}')
            need(not r['related_party'], 'Related-party transaction')
            need(config['size_min'] <= r['property_size'] <= config['size_max'], 'Outside size range')
            need(type(r['consideration']) in (int,float) and r['consideration'] > 0, 'No positive verified price')
            amount = (r['consideration'] * {'USD':1,'USD_thousands':1000,'USD_millions':1000000}[r['consideration_unit']]) if r['consideration'] is not None else None
            facts = dict(entity_id=entity,event_date=r['event_date'],consideration_usd=amount,
                         property_size=r['property_size'],price_per_unit=amount/r['property_size'] if amount is not None else None)
            order = (r['distance_miles'], -dt.date.fromisoformat(r['event_date']).toordinal())
        elif task == 'rent_comps':
            need(r['status']=='executed', 'Lease not executed')
            need(type(r['rent_quote']) in (int,float) and r['rent_quote']>0, 'No positive verified rent')
            for key in ['free_months','term_months','ti_allowance_psf']:
                need(r[key] is not None, f'Unknown {key}')
            need(r['expense_basis']=='NNN' or r['annual_expenses_psf'] is not None, 'Unknown gross expense deduction')
            face = net = None
            if all(r[k] is not None for k in ['rent_quote','free_months','term_months','ti_allowance_psf']) and (r['expense_basis']=='NNN' or r['annual_expenses_psf'] is not None):
                face, net = effective_rent(r)
            facts = dict(entity_id=entity,event_date=r['event_date'],annual_face_rent_psf=face,
                         effective_net_rent_psf_year=net,term_months=r['term_months'])
            order = (r['distance_miles'], -dt.date.fromisoformat(r['event_date']).toordinal())
        elif task == 'sponsor_leads':
            need(r['activity']=='closed_acquisition', 'Not a closed acquisition')
            need(r['size_basis']=='single_asset_purchase', 'Amount is not a single-asset purchase')
            need(config['deal_min_usd'] <= r['transaction_size_usd'] <= config['deal_max_usd'], 'Outside transaction size band')
            sponsor = r
            if r['firm_kind']=='property_SPV' and r.get('parent_link')=='executed_ownership_schedule' and r.get('parent_entity_id') in parents:
                sponsor=parents[r['parent_entity_id']];entity=sponsor['entity_id'];citations += sponsor['_evidence']
            else:need(r['firm_kind']=='owner_operator','Not an evidenced operating sponsor')
            need(sponsor['employment']=='current','Contact is not current')
            need(sponsor['contact_verified_at']>=config['contact_cutoff'],'Stale contact verification')
            need(sponsor['contact_role'] in ROLES,'Contact role does not qualify')
            facts = dict(entity_id=entity,firm_name=sponsor['firm_name'],transaction_size_usd=r['transaction_size_usd'],
                         event_date=r['event_date'],contact_name=sponsor['contact_name'],contact_role=sponsor['contact_role'],
                         contact_email=sponsor['contact_email'] if sponsor['email_basis']=='published_business' else None)
            order = (-dt.date.fromisoformat(r['event_date']).toordinal(), -r['transaction_size_usd'])
        else:
            need(r['owner_relation']=='record_owner','Not the record owner')
            need(r['ownership_verified_at']>=config['contact_cutoff'],'Stale ownership verification')
            need(r['loan_status']=='active_confirmed','Loan status not confirmed active')
            need(r['maturity_basis']=='executed_note','Maturity not confirmed by executed evidence')
            need(r['extension_status']!='option_unresolved','Unresolved extension')
            need(config['refinance_window_start'] <= r['maturity_date'] <= config['refinance_window_end'],'Maturity outside window')
            need(r['employment']=='current','Contact is not current')
            need(r['contact_verified_at']>=config['contact_cutoff'],'Stale contact verification')
            need(r['contact_role'] in ROLES,'Contact role does not qualify')
            facts = dict(entity_id=entity,owner_entity_id=r['owner_entity_id'],maturity_date=r['maturity_date'],
                         original_principal_usd=r['loan_amount_usd'],outstanding_balance_usd=r['outstanding_balance_usd'],
                         contact_name=r['contact_name'],contact_email=r['contact_email'] if r['email_basis']=='published_business' else None)
            order = (dt.date.fromisoformat(r['maturity_date']).toordinal(), -r['loan_amount_usd'])
        result[rid] = dict(eligible=not reasons, reasons=reasons, entity_id=entity, facts=facts,
                           required_sources=sorted(set(citations)),order=list(order))
    valid = sorted((rid for rid,r in result.items() if r['eligible']),key=lambda rid:(result[rid]['order'],rid))
    unique = [];seen=set()
    for rid in valid:
        eid=result[rid]['entity_id']
        if eid not in seen:unique.append(rid);seen.add(eid)
    return dict(case_id=config['case_id'],task=task,candidates=result,eligible_record_ids=valid,
                ordered_unique_ids=unique,requested_count=config['requested_count'],
                available_unique=len(unique),target_count=min(len(unique),config['requested_count']))


def from_case(case):
    case=Path(case)
    return truth(json.loads((case/'case.json').read_text()),json.loads((case/'sources/records.json').read_text()),json.loads((case/'sources/updates.json').read_text()))


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    for case in sorted((root/'benchmarks/research-v1/cases').iterdir()):
        key=from_case(case)
        (case/'answer-key.json').write_text(json.dumps(key,indent=2,allow_nan=False)+'\n')
        print(case.name,key['available_unique'])
