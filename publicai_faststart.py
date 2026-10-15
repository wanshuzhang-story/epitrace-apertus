"""EpiTrace Public AI fast path: no CSCS allocation, HF voucher, or Docker needed.

Requires requests from track_2b/requirements.txt for network operations.
This script never sends the token to ChatGPT or any unlisted endpoint.
The frozen benchmark and scoring logic are unchanged.
"""
import argparse
import getpass
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TRACK=ROOT/'track_2b'
SECRET=TRACK/'.env.publicai'
API_BASE='https://api.publicai.co/v1'
MODELS={'8b':'swiss-ai/apertus-v1.5-8b','70b':'swiss-ai/apertus-v1.5-70b'}
PILOT_PATHS={k: f'results/PUBLICAI_FASTSTART_PILOT_{k.upper()}.jsonl' for k in MODELS}
DATA=TRACK/'data/epitrace_benchmark_public_v0.3.jsonl'


def read_env_file():
    vals={}
    if SECRET.exists():
        for raw in SECRET.read_text(encoding='utf-8').splitlines():
            raw=raw.strip()
            if not raw or raw.startswith('#') or '=' not in raw: continue
            k,v=raw.split('=',1)
            vals[k.strip()]=v.strip().strip('"').strip("'")
    return vals


def auth_env():
    vals=read_env_file()
    key=os.getenv('PUBLICAI_API_KEY') or vals.get('LLM_API_KEY')
    if not key or key in {'YOUR_KEY_GOES_HERE','YOUR_KEY'}:
        raise SystemExit('Missing Public AI key. Run: python3 publicai_faststart.py setup')
    env=os.environ.copy()
    env.update({'LLM_API_KEY':key,'LLM_BASE_URL':API_BASE})
    env.pop('CSCS_INFERENCE_API_KEY',None)
    return env


def setup():
    if SECRET.exists():
        print(f'Private key file already exists: {SECRET.relative_to(ROOT)}. Not overwriting it.')
        print('To replace, edit it locally or remove it and run setup again.')
        return 0
    print('Obtain a Public AI API key at https://platform.publicai.co/docs (Login > Account > API Keys).')
    print('Its provider-issued starter credit is independent of the Hack Apertus HF promotion.')
    token=getpass.getpass('Paste your Public AI API key here (input hidden): ').strip()
    if len(token)<12 or token in {'YOUR_KEY_GOES_HERE','YOUR_KEY'}:
        print('No plausible key supplied. Nothing saved.',file=sys.stderr);return 2
    SECRET.write_text(f'LLM_BASE_URL={API_BASE}\nLLM_API_KEY={token}\nLLM_NAME={MODELS["8b"]}\n',encoding='utf-8')
    try: SECRET.chmod(0o600)
    except OSError: pass
    print(f'Saved local secret to {SECRET.relative_to(ROOT)} (excluded from git/ZIP).')
    return 0


def command(args,env):
    print('Executing:', ' '.join(str(x) for x in args),flush=True)
    return subprocess.call([sys.executable,*args],cwd=TRACK,env=env)


def preflight(env):
    try:
        import requests
    except ImportError:
        print('Missing dependency. Run: python3 -m pip install -r track_2b/requirements.txt',file=sys.stderr)
        return 2
    sys.path.insert(0,str(TRACK/'src'))
    from run_benchmark import check_model_access
    with requests.Session() as s:
        for model in MODELS.values():
            check_model_access(s,API_BASE,env['LLM_API_KEY'],model,30)
    print('Preflight PASSED: both named models advertised by this key. No generated tokens used.')
    return 0


def run_pilot(env):
    if preflight(env)!=0:return 2
    for label,model in MODELS.items():
        rc=command(['src/run_benchmark.py','--model',model,'--limit','3','--max-attempts','1',
                    '--out',PILOT_PATHS[label]],env)
        if rc:return rc
    print('PILOTS PASSED for both 8B and 70B. Each made three real completion requests.')
    print('Next: python3 publicai_faststart.py full')
    return 0


def pilot_complete():
    expected=[]
    with DATA.open(encoding='utf-8') as f:
        for line in f:
            if line.strip(): expected.append(json.loads(line)['case_id'])
            if len(expected)==3:break
    for label,model in MODELS.items():
        path=TRACK/PILOT_PATHS[label]
        if not path.exists():return False
        recs=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
        success={r.get('case_id') for r in recs if r.get('ok') and r.get('model')==model
                 and r.get('served_model')==model and r.get('api_base','').rstrip('/')==API_BASE}
        if not set(expected).issubset(success):return False
    return True


def run_full(env):
    if not pilot_complete():
        print('Both three-case Public AI pilots must pass before the full 468-request run.',file=sys.stderr)
        print('Run: python3 publicai_faststart.py pilot',file=sys.stderr)
        return 2
    print('Full run: 234 cases x 2 models. This may take considerable time and consumes provider credit.')
    for label,model in MODELS.items():
        print(f'Starting Apertus v1.5 {label.upper()} with automatic resume',flush=True)
        rc=command(['src/run_benchmark.py','--model',model,'--max-attempts','3'],env)
        if rc:
            print('Run incomplete. Correct the reported issue, then invoke full again to resume successes.',file=sys.stderr)
            return rc
    print('Both full runs finished. Next: python3 publicai_faststart.py report')
    return 0


def report():
    print('Running strict full-data checks and paired inference analysis.')
    return command(['src/report_results.py','--auto','--protocol','neutral'],os.environ.copy())


def status():
    print('Frozen dataset:',DATA)
    print('Dataset cases:',sum(bool(x.strip()) for x in DATA.read_text(encoding='utf-8').splitlines()))
    for label,model in MODELS.items():
        p=TRACK/PILOT_PATHS[label]
        if p.exists():
            recs=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
            print(f'Pilot {label}: {len({r.get("case_id") for r in recs if r.get("ok")})}/3 succeeded')
        else:print(f'Pilot {label}: not run')
        full=list((TRACK/'results').glob(f'apertus-v1.5-{label}__neutral__*.jsonl'))
        if full:
            for p in full:
                recs=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
                ok={r['case_id'] for r in recs if r.get('ok') and r.get('model')==model}
                print(f'Full {label} in {p.name}: {len(ok)}/234 successful')
        else:print(f'Full {label}: not run')
    return 0


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['setup','preflight','pilot','full','report','status'])
    args=ap.parse_args()
    if args.action=='setup':return setup()
    if args.action=='status':return status()
    if args.action=='report':return report()
    env=auth_env()
    if args.action=='preflight':return preflight(env)
    if args.action=='pilot':return run_pilot(env)
    if args.action=='full':return run_full(env)
    return 2

if __name__=='__main__':sys.exit(main())
