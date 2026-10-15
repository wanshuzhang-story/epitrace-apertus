"""Resume-safe Apertus runner: freezes data/prompt/model and verifies API model identity."""
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import requests
from prompt import ALLOWED_STATES, ALLOWED_CLOSURE, ALLOWED_INDEPENDENCE, get_system_prompt, build_user_prompt
from validate import load,validate

MODEL_DEFAULT='swiss-ai/Apertus-v1.5-8B'
BASE_DEFAULT='https://api.inference.cscs.ch/v1'
USER_AGENT='EpiTrace-Apertus/0.3.2' # Public AI API requires a User-Agent header.
MAX_TOKENS=350
TEMPERATURE=0

class ModelMismatchError(ValueError): pass


def prompt_hash():
    # The full prompt.py source, including the user template, is fingerprinted.
    return hashlib.sha256(Path(__file__).with_name('prompt.py').read_bytes()).hexdigest()


def run_fingerprint(model,protocol,dataset_sha,base=BASE_DEFAULT):
    spec={'model':model,'protocol':protocol,'dataset_sha256':dataset_sha,
          'prompt_sha256':prompt_hash(),'max_tokens':MAX_TOKENS,'temperature':TEMPERATURE,
          'interface':'openai-chat-completions-v1','api_base':base.rstrip('/')}
    return hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:14]


def extract_json(text):
    text=str(text or '').strip()
    if text.startswith('```'):
        text=re.sub(r'^```(?:json)?\s*','',text,flags=re.I)
        text=re.sub(r'\s*```$','',text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a=text.find('{'); b=text.rfind('}')
        if a<0 or b<=a:raise ValueError('no JSON object in model response')
        return json.loads(text[a:b+1])


def normalize(x):
    if not isinstance(x,dict):raise ValueError('model response not JSON object')
    state=str(x['epistemic_state']).upper().strip()
    closure=str(x['closure']).upper().strip()
    indep=str(x['evidence_independence']).upper().strip()
    score=x['claim_support_score']
    if isinstance(score,bool):raise ValueError('invalid boolean claim_support_score')
    score=float(score)
    if not math.isfinite(score) or not 0<=score<=1:
        raise ValueError('claim_support_score must be finite and between 0 and 1')
    if state not in ALLOWED_STATES or closure not in ALLOWED_CLOSURE or indep not in ALLOWED_INDEPENDENCE:
        raise ValueError(f'invalid categorical outputs: {state}, {closure}, {indep}')
    if state=='NOT_APPLICABLE' and closure!='NOT_APPLICABLE':
        raise ValueError('N/A state requires N/A closure')
    return {'epistemic_state':state,'closure':closure,'claim_support_score':score,
            'evidence_independence':indep,'rationale':str(x.get('rationale','')).strip()[:400]}


def model_route(model, base):
    """Separate Hugging Face provider pinning from the canonical model ID.

    An HF model is addressed as org/Model:provider. In a chat completion
    response, the model field commonly reports org/Model WITHOUT the suffix.
    We verify the exact canonical model while retaining the requested provider
    for provenance and paired comparison. This is not proof of physical location.
    """
    hf=base.rstrip('/').lower()=='https://router.huggingface.co/v1'
    if not hf:
        if ':' in model:raise ValueError('Provider routing suffixes are only supported for Hugging Face router')
        return model,None
    if ':' not in model:raise ValueError('For a reproducible HF run, pin a backend provider using :publicai or another documented suffix')
    canonical,provider=model.rsplit(':',1)
    if not canonical or not provider or not re.fullmatch('[a-z][a-z0-9-]*',provider):
        raise ValueError('Invalid Hugging Face model:provider selection')
    return canonical,provider


def check_model_access(session,base,key,model,timeout):
    """Preflight exact model identity and provider when router advertises it."""
    canonical,provider=model_route(model,base)
    r=session.get(base.rstrip('/')+'/models',headers={'Authorization':f'Bearer {key}','User-Agent':USER_AGENT},timeout=timeout)
    r.raise_for_status()
    items=[x for x in r.json().get('data',[]) if isinstance(x,dict)]
    matches=[x for x in items if x.get('id')==canonical]
    if not matches:
        available=sorted(x.get('id') for x in items if isinstance(x.get('id'),str))
        raise ModelMismatchError(f'Preflight: {canonical} is absent from /models. The HF Model Hub listing is not the same as deployed inference. Sample: {available[:12]}')
    if provider:
        metadata=matches[0].get('providers') or []
        if metadata:
            candidates=[p for p in metadata if p.get('provider')==provider]
            if not candidates or all(str(p.get('status','live')).lower() not in ('live','active','available') for p in candidates):
                raise ModelMismatchError(f'Preflight: {canonical} is listed, but provider {provider!r} is not live in /models; do not silently switch infrastructure')
        else:
            print('NOTICE: /models lists the model but not provider metadata; provider remains pinned in the requested model suffix',flush=True)
    print(f'Preflight /models: {canonical} present; pinned backend={provider or "direct API"}',flush=True)


def call_model(session,base,key,model,case,protocol,timeout):
    canonical,provider=model_route(model,base)
    payload={'model':model,'messages':[{'role':'system','content':get_system_prompt(protocol)},
              {'role':'user','content':build_user_prompt(case)}],
              'temperature':TEMPERATURE,'max_tokens':MAX_TOKENS}
    response=session.post(base.rstrip('/')+'/chat/completions',
                          headers={'Authorization':f'Bearer {key}','Content-Type':'application/json','User-Agent':USER_AGENT},
                          json=payload,timeout=timeout)
    response.raise_for_status()
    body=response.json()
    served=body.get('model')
    if not isinstance(served,str) or not served:
        raise ModelMismatchError('API response does not identify served model; refusing unverified model data')
    if served not in (model,canonical):
        raise ModelMismatchError(f'API served {served!r}, but requested canonical model {canonical!r}; refusing mislabeled results')
    message=body['choices'][0]['message'];content=message.get('content') or ''
    if isinstance(content,list):content=''.join(x.get('text','') for x in content if isinstance(x,dict))
    if not content:raise ValueError('empty model content')
    return str(content),body.get('usage') or {},response.status_code,served,body.get('system_fingerprint')


def run(args):
    stats=validate(args.data)
    model=args.model or os.getenv('LLM_NAME',MODEL_DEFAULT)
    base=os.getenv('LLM_BASE_URL',BASE_DEFAULT)
    canonical_model,requested_provider=model_route(model,base)
    cases=load(args.data)
    if args.limit is not None:
        if args.limit<1:raise ValueError('--limit must be positive')
        cases=cases[:args.limit]
    sha=stats['sha256'];prompt_sha=prompt_hash()
    run_id=run_fingerprint(model,args.protocol,sha,base)
    slug=re.sub('[^A-Za-z0-9_.-]+','_',model.rsplit('/',1)[-1])
    outpath=Path(args.out or f'results/{slug}__{args.protocol}__{run_id}.jsonl')
    if getattr(args,'dry_run',False):
        print(json.dumps({'dry_run':True,'no_inference_calls':True,'model':model,
              'protocol':args.protocol,'case_count':len(cases),'dataset_sha256':sha,
              'prompt_sha256':prompt_sha,'api_base':base,'run_id':run_id,'canonical_model':canonical_model,'requested_provider':requested_provider,'proposed_output':str(outpath),
              'first_user_prompt':build_user_prompt(cases[0])},indent=2))
        return 0
    key=os.getenv('LLM_API_KEY') or os.getenv('CSCS_INFERENCE_API_KEY')
    if not key or key.strip() in ('YOUR_KEY_GOES_HERE','YOUR_KEY'):
        print('No real API key provided. Set LLM_API_KEY or CSCS_INFERENCE_API_KEY locally (never commit it).',file=sys.stderr)
        return 2
    successful=set()
    if outpath.exists():
        for rec in load(outpath):
            if rec.get('run_id')!=run_id or rec.get('dataset_sha256')!=sha or rec.get('prompt_sha256')!=prompt_sha or rec.get('model')!=model or rec.get('protocol')!=args.protocol:
                raise ValueError(f'Refusing to resume mixed/old experiment file: {outpath}')
            if rec.get('ok') and isinstance(rec.get('prediction'),dict):successful.add(rec['case_id'])
    failures=0
    with requests.Session() as session:
        if not getattr(args,'skip_model_preflight',False):
            check_model_access(session,base,key,model,args.timeout)
        outpath.parent.mkdir(parents=True,exist_ok=True)
        with outpath.open('a',encoding='utf-8') as out:
            for i,case in enumerate(cases,1):
                if case['case_id'] in successful:continue
                record={'case_id':case['case_id'],'seed_id':case['seed_id'],'variant':case['variant'],
                        'model':model,'protocol':args.protocol,'run_id':run_id,
                        'dataset_sha256':sha,'prompt_sha256':prompt_sha,'api_base':base,
                        'canonical_model':canonical_model,'requested_provider':requested_provider,
                        'temperature':TEMPERATURE,'max_tokens':MAX_TOKENS,
                        'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
                start=time.monotonic()
                for attempt in range(1,args.max_attempts+1):
                    try:
                        raw,usage,status,served,fingerprint=call_model(session,base,key,model,case,args.protocol,args.timeout)
                        record.update({'ok':True,'prediction':normalize(extract_json(raw)),
                                      'raw':raw,'usage':usage,'http_status':status,'attempts':attempt,
                                      'served_model':served,'system_fingerprint':fingerprint})
                        break
                    except ModelMismatchError:
                        raise
                    except (requests.exceptions.RequestException,ValueError,KeyError,TypeError,IndexError) as exc:
                        record.update({'ok':False,'error':f'{type(exc).__name__}: {str(exc)[:220]}','attempts':attempt})
                        if attempt<args.max_attempts:time.sleep(min(2**attempt,8))
                record['latency_seconds']=round(time.monotonic()-start,3)
                if not record.get('ok'):failures+=1
                out.write(json.dumps(record,ensure_ascii=False)+'\n');out.flush()
                print(f'[{i}/{len(cases)}] {case["case_id"]} ok={record["ok"]} latency={record["latency_seconds"]}s',flush=True)
                if args.sleep:time.sleep(args.sleep)
    print(f'Wrote outputs to {outpath}. Failures this invocation: {failures}. Previous successes: {len(successful)}')
    return int(failures>0)


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--data',default='data/epitrace_benchmark_public_v0.3.jsonl')
    p.add_argument('--model',default=None)
    p.add_argument('--protocol',choices=['neutral','provenance_aware'],default='neutral')
    p.add_argument('--out',default=None)
    p.add_argument('--limit',type=int,default=None)
    p.add_argument('--sleep',type=float,default=0.0)
    p.add_argument('--timeout',type=int,default=120)
    p.add_argument('--max-attempts',type=int,default=3)
    p.add_argument('--dry-run',action='store_true',help='Show frozen configuration and first prompt; never call API')
    p.add_argument('--skip-model-preflight',action='store_true',help='Only for compatible private endpoints that do not implement GET /models')
    return p.parse_args()

if __name__=='__main__':sys.exit(run(parse_args()))
