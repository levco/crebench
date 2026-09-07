"""Resume only gateway 402 interruptions without changing the frozen model context.

The frozen runner is retained. Administrative waiting is excluded from its active
1800-second allowance; already consumed turns, tools, versions and costs remain.
"""
import argparse,base64,concurrent.futures,hashlib,json,math,time
from pathlib import Path
from .run_workflow import (ROOT,BASE,TOOLS,Budget,ToolContext,credential,digest,
                          model_call,now,parse_json,save)


def restore_request(path,run):
    request=json.loads(Path(path).read_text())
    for message in request['messages']:
        if isinstance(message.get('content'),list):
            for part in message['content']:
                if part.get('type')=='image_url':
                    url=part['image_url']['url']
                    if not url.startswith('artifact://input-views/'):
                        raise ValueError('Expected archived local image reference')
                    image=(Path(run)/url.removeprefix('artifact://')).resolve()
                    if not image.is_relative_to((Path(run)/'input-views').resolve()):raise ValueError('Invalid image path')
                    part['image_url']['url']='data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()
    return request


def interruption(run):
    result=json.loads((run/'result.json').read_text())
    if result['status']!='infrastructure_error' or result['attempts'][-1].get('http_status')!=402:
        raise ValueError('Only preserved pre-inference gateway credit interruptions can resume')
    candidates=sorted(run.glob('turn-*/attempt-*/result.json'))
    last=candidates[-1];failed=json.loads(last.read_text())
    if failed.get('http_status')!=402:raise ValueError('Latest archived request is not a 402')
    request=restore_request(last.with_name('request.json'),run)
    wire=json.dumps(request,allow_nan=False).encode()
    if hashlib.sha256(wire).hexdigest()!=json.loads(last.with_name('started.json').read_text())['wire_sha256']:
        raise ValueError('Restored wire differs from interrupted request')
    return result,request,int(last.parent.parent.name.split('-')[1]),last


def resume_one(run,token,budget,pricing,node):
    old,request,start_turn,failed=interruption(run);case=BASE/'cases'/old['case_id'];record=run/'billing-resumption'
    record.mkdir(exist_ok=False);(record/'input-views').mkdir()
    save(record/'original-result.json',old)
    save(record/'resumption.json',{'at':now(),'reason':'Gateway account credit exhaustion, HTTP 402; no model response for interrupted request','interrupted_request':str(failed.with_name('request.json').relative_to(run)), 'restored_wire_sha256':json.loads(failed.with_name('started.json').read_text())['wire_sha256'], 'wire_identity_verified':True,'resume_model_turn':start_turn,'prior_active_seconds':old['elapsed_seconds'],'same_models_prompts_tools_limits':True,'operator_answer_hints':0,'administrative_wait_excluded_from_active_limit':True})
    ctx=ToolContext(case,run,node);ctx.versions=old['artifact_versions'].copy()
    if old.get('latest_workbook'):
        ctx.latest_workbook=run/old['latest_workbook'];ctx.latest_spec=ctx.latest_workbook.with_suffix('.json')
    messages=request['messages'];attempts=list(old['attempts']);tool_calls=old['tool_calls'];returned=list(old['returned_models'])
    start=time.monotonic();status='turn_limit'
    try:
        for turn in range(start_turn,2 if old['track']=='direct' else 33):
            if old['elapsed_seconds']+time.monotonic()-start>1800:status='time_limit';break
            request={**request,'messages':messages}
            response,info=model_call(request,record,turn,token,budget,pricing);attempts.extend(info)
            if response is None:status='infrastructure_error';break
            returned.append(response.get('model'));choice=(response.get('choices') or [{}])[0];message=choice.get('message') or {};content=message.get('content') or ''
            turn_dir=run/f'turn-{turn:02d}';turn_dir.mkdir(exist_ok=True)
            if content:(turn_dir/'answer.txt').write_text(content)
            if old['track']=='direct':
                try:save(run/'analysis.json',parse_json(content));status='completed'
                except (ValueError,TypeError):status='needs_transcription';(run/'answer.txt').write_text(content)
                if choice.get('finish_reason')=='length':status='output_limit'
                break
            calls=message.get('tool_calls') or []
            messages.append({'role':'assistant','content':message.get('content'),**({'tool_calls':calls} if calls else {})})
            if not calls:
                if turn<32 and not (run/'completion-reminder.json').exists():
                    reminder='Complete the requested deliverables with the available tools and call submit_analysis. If anything is blocked, record it explicitly. Do not claim a file exists unless a tool created it.'
                    save(run/'completion-reminder.json',{'turn':turn,'message':reminder});messages.append({'role':'user','content':reminder});continue
                status='incomplete';break
            for i,call in enumerate(calls,1):
                tool_calls+=1
                if tool_calls>96:raise ValueError('Tool-call limit')
                name=call.get('function',{}).get('name');rawargs=call.get('function',{}).get('arguments','{}');before=time.monotonic()
                tool_record={'name':name,'call_id':call.get('id'),'arguments_raw':rawargs}
                try:
                    args=parse_json(rawargs);output=ctx.call(name,args);tool_record.update(arguments=args,result=output,status='ok')
                except Exception as exc:
                    output={'error':str(exc)};tool_record.update(result=output,status='error')
                tool_record['elapsed_seconds']=round(time.monotonic()-before,3);target=turn_dir/f'tool-{i:02d}.json'
                if target.exists():raise ValueError('Refuse overwrite of previous tool execution')
                save(target,tool_record);messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(output,allow_nan=False,default=str)})
            if ctx.images:
                parts=[{'type':'text','text':'Requested source-page images, in tool-request order. Read the page labels and source filenames in the preceding tool results.'}]
                for image in ctx.images:parts.append({'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()}})
                messages.append({'role':'user','content':parts});ctx.images=[]
            print(json.dumps({'case':case.name,'model':old['requested_model'],'track':old['track'],'turn':turn,'tool_calls':tool_calls,'submitted':ctx.done,'resumed':True}),flush=True)
            if ctx.done:status='completed';break
    except Exception as exc:
        status='runner_error';save(record/'error.json',{'message':str(exc).replace(token,'[REDACTED]')})
    costs=[a.get('usage',{}).get('cost') for a in attempts if isinstance(a.get('usage'),dict)]
    known=[v for v in costs if isinstance(v,(int,float)) and math.isfinite(v) and v>=0]
    complete_cost=len(known)==len(attempts) and bool(attempts)
    result={**old,'status':status,'completed_at':now(),'returned_models':sorted(set(x for x in returned if x)),
      'elapsed_seconds':round(old['elapsed_seconds']+time.monotonic()-start,3),'latency_basis':'Original plus resumed active execution; administrative credit-pause wait excluded and recorded',
      'model_calls_including_retries':len(attempts),'tool_calls':tool_calls,'artifact_versions':ctx.versions,
      'gateway_reported_cost_usd':sum(known) if complete_cost else None,'known_partial_cost_usd':sum(known),'cost_complete':complete_cost,
      'attempts':attempts,'billing_resumption':'billing-resumption/resumption.json','original_result':'billing-resumption/original-result.json',
      'latest_workbook':str(ctx.latest_workbook.relative_to(run)) if ctx.latest_workbook else None,
      'latest_memo':f'artifacts/memorandum-v{ctx.versions["memo"]}.pdf' if ctx.versions['memo'] and (run/'artifacts'/f'memorandum-v{ctx.versions["memo"]}.pdf').exists() else None}
    save(run/'result.json',result);print(json.dumps({k:result[k] for k in ['case_id','requested_model','track','status','known_partial_cost_usd','elapsed_seconds']}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('experiment');p.add_argument('--node',default='node');p.add_argument('--env-file',default='.env.local');p.add_argument('--verify-only',action='store_true');a=p.parse_args();exp=Path(a.experiment).resolve();plan=json.loads((exp/'plan.json').read_text())
    for path,sha in plan['sha256'].items():
        if digest(ROOT/path)!=sha:raise ValueError('Frozen file changed: '+path)
    jobs=[]
    for result_path in exp.glob('*/*/*/result.json'):
        r=json.loads(result_path.read_text());run=result_path.parent
        if r['status']=='infrastructure_error' and r.get('attempts',[{}])[-1].get('http_status')==402:
            old,request,turn,failed=interruption(run);pricing=next(m for m in plan['catalog'] if m['id']==old['requested_model'])['pricing'];jobs.append((run,pricing))
    if a.verify_only:print(json.dumps({'eligible_interruptions':len(jobs),'frozen_hashes_verified':len(plan['sha256']),'all_interrupted_wire_hashes_identical':True}));return
    budget=Budget(plan['cost_reservation_limit_usd'],exp);token=credential(a.env_file)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda job:resume_one(job[0],token,budget,job[1],a.node),jobs))
    save(exp/f'billing-resumption-{int(time.time())}.json',{'at':now(),'resumed_runs':len(jobs),'observed_inference_usd':budget.actual,'conservative_reserved_usd':budget.reserved})

if __name__=='__main__':main()
