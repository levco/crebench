"""Versioned structured-output pilot with presentation-tolerant financial scoring."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import threading
import time
import urllib.error
import urllib.request
from .grade import read_json, sha256, verify_case
from .normalize import score_text
from .run_pilot import ENDPOINT, NoRedirect, credential, now, packet, write

MODELS = ['openai/gpt-5', 'anthropic/claude-opus-5']
FILES = ['crebench/run_v2.py','crebench/normalize.py','crebench/grade.py','crebench/run_pilot.py']


def schema(case):
    contract = read_json(Path(case)/'output-contract.json')
    fields = {}
    for name, spec in contract['fields'].items():
        fields[name] = {'type':'object','properties':{
            'value':{'type':[spec['type'],'null']},
            'evidence':{'type':'array','items':{'type':'string'}}},
            'required':['value','evidence'],'additionalProperties':False}
    return {'type':'object','properties':{
        'fields':{'type':'object','properties':fields,'required':list(fields),'additionalProperties':False},
        'discrepancies':{'type':'array','items':{'type':'string'}}},
        'required':['fields','discrepancies'],'additionalProperties':False}


def prepare(case, directory, catalog_path):
    content = packet(case)
    output_schema = schema(case)
    selected = [next(m for m in read_json(catalog_path)['data'] if m['id']==name) for name in MODELS]
    request_base = {'messages':[{'role':'user','content':content}], 'max_tokens':16384,'stream':False,
                    'response_format':{'type':'json_schema','json_schema':{
                        'name':'cre_financial_answer','strict':True,'schema':output_schema}}}
    ceiling = len(json.dumps(request_base).encode()) + 1024
    reserve = 3 * 2 * sum(2*(ceiling*float(m['pricing']['input'])+16384*float(m['pricing']['output'])) for m in selected)
    if reserve > 10:
        raise ValueError('Conservative reservation exceeds $10 experiment limit')
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=False)
    write(directory/'catalog.json',{'retrieved_at':now(),'source':'https://ai-gateway.vercel.sh/v1/models','data':selected})
    plan={'created_at':now(),'experiment':directory.name,'protocol':'v2-structured-presentation-tolerant',
          'models':MODELS,'repetitions':3,'unique_cases':1,'case_id':'harbor-court-001',
          'case_manifest_sha256':sha256(Path(case)/'manifest.json'),
          'source_sha256':{f:sha256(f) for f in FILES},'endpoint':ENDPOINT,
          'cost_reservation_usd':reserve,'max_cost_reservation_usd':10,
          'max_tokens':16384,'timeout_seconds':300,'concurrency':2,'transport_retries':1,
          'retry_statuses':[429,500,502,503,504], 'semantic_retries':0,'model_fallbacks':[],
          'provider_routing':'gateway default; returned model and usage retained',
          'reasoning':'provider_default','temperature':'provider_default','tools':[],
          'leaderboard_eligible':False,'request_sha256':{},
          'scoring':{'financial_checks':30,'reference_checks':27,'format':'diagnostic only',
                     'normalization':'Deterministic presentation changes only; no answer-key-driven repairs',
                     'unreadable':'needs_review; never invented values'},
          'limitations':['One public synthetic case and public answer key','No independent CRE review',
                        'Text input, not PDF ingestion or a product workflow','Canonical references supplied',
                        'Repeated calls are not independent cases','Provider defaults are not equal compute',
                        'No underwriting workbook or OM assessment','Cost reservation is not a billing cap']}
    for repetition in range(1,4):
        for index,model in enumerate(MODELS,1):
            run=directory/f'r{repetition}-{index}';run.mkdir()
            write(run/'request.json',{'model':model,**request_base})
            plan['request_sha256'][run.name]=sha256(run/'request.json')
    write(directory/'plan.json',plan)
    return plan


def execute(case,directory,env_file):
    directory=Path(directory);plan=read_json(directory/'plan.json');verify_case(case)
    if sha256(Path(case)/'manifest.json') != plan['case_manifest_sha256']:
        raise ValueError('Case changed')
    for path,digest in plan['source_sha256'].items():
        if sha256(path)!=digest: raise ValueError('Frozen code changed: '+path)
    for name,digest in plan['request_sha256'].items():
        if sha256(directory/name/'request.json')!=digest: raise ValueError('Request changed: '+name)
    token=credential(env_file);stop=threading.Event()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()

    def run_one(name):
        run=directory/name
        if stop.is_set() or (run/'started.json').exists(): return
        request=read_json(run/'request.json')
        write(run/'started.json',{'at':now(),'source_commit':commit,'request_sha256':sha256(run/'request.json')})
        total_start=time.monotonic()
        final={'model_evaluation':True,'leaderboard_eligible':False,'requested_model':request['model'],
               'status':'infrastructure_error','score':None,'attempts':[]}
        for attempt in range(1,plan['transport_retries']+2):
            attempt_dir=run/f'attempt-{attempt}';attempt_dir.mkdir()
            write(attempt_dir/'started.json',{'at':now()})
            info={'attempt':attempt}; retry=False; start=time.monotonic()
            try:
                req=urllib.request.Request(ENDPOINT,data=json.dumps(request).encode(),headers={
                    'Content-Type':'application/json','Authorization':'Bearer '+token})
                with urllib.request.build_opener(NoRedirect()).open(req,timeout=plan['timeout_seconds']) as response:
                    raw=response.read().decode().replace(token,'[REDACTED]');info['http_status']=response.status
                (attempt_dir/'response.json').write_text(raw)
                response=read_json(attempt_dir/'response.json')
                choices=response.get('choices',[]);choice=choices[0] if choices else {}
                answer=choice.get('message',{}).get('content')
                info.update(returned_model=response.get('model'),usage=response.get('usage'),finish_reason=choice.get('finish_reason'))
                final.update(returned_model=response.get('model'),usage=response.get('usage'),finish_reason=choice.get('finish_reason'))
                if isinstance(answer,str) and answer.strip():
                    (attempt_dir/'answer.txt').write_text(answer)
                    final['answer_path']=f'attempt-{attempt}/answer.txt'
                    try:
                        final['score']=score_text(case,answer);final['status']='scored'
                    except ValueError as exc:
                        final['status']='needs_review';final['parse_error']=str(exc)
                else: final['status']='no_answer'
                if choice.get('finish_reason')=='length':final['status']='output_limit'
            except urllib.error.HTTPError as exc:
                info.update(http_status=exc.code,error=exc.read().decode(errors='replace').replace(token,'[REDACTED]'))
                retry=exc.code in plan['retry_statuses']
                if exc.code in (401,402,403):stop.set()
            except (urllib.error.URLError,TimeoutError) as exc:
                info['error']=str(exc).replace(token,'[REDACTED]');retry=True
            except ValueError as exc:
                info['error']=str(exc).replace(token,'[REDACTED]')
            info.update(elapsed_seconds=round(time.monotonic()-start,3),completed_at=now())
            info['sha256']={p.name:sha256(p) for p in attempt_dir.iterdir() if p.is_file()}
            write(attempt_dir/'result.json',info);final['attempts'].append(info)
            if not retry or attempt>plan['transport_retries'] or stop.is_set(): break
            time.sleep(2)
        final.update(elapsed_seconds=round(time.monotonic()-total_start,3),completed_at=now())
        final['sha256']={str(p.relative_to(run)):sha256(p) for p in run.rglob('*') if p.is_file()}
        write(run/'result.json',final)
        print(json.dumps({'run':name,'model':request['model'],'status':final['status'],
                          'financial':final['score']['groups']['financial'] if final['score'] else None,
                          'seconds':final['elapsed_seconds']}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=plan['concurrency']) as pool:
        list(pool.map(run_one,plan['request_sha256']))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','execute']);p.add_argument('directory')
    p.add_argument('--case',default='cases/public/harbor-court-001');p.add_argument('--catalog',default='work/gateway-models-v2.json')
    p.add_argument('--env-file');a=p.parse_args()
    if a.action=='prepare':
        plan=prepare(a.case,a.directory,a.catalog);print(json.dumps({'models':plan['models'],'calls':6,'reserved_usd':plan['cost_reservation_usd']}))
    else:execute(a.case,a.directory,a.env_file)
