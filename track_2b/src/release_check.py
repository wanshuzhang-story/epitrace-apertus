"""Fail-closed check of public tree before uploading to GitHub or Hugging Face.

This is a screening aid, NOT legal clearance or a substitute for human data review.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'track_2b/data/epitrace_benchmark_public_v0.3.jsonl'
META=ROOT/'track_2b/data/epitrace_public_metadata_v0.3.csv'


def check():
    man=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    sha=hashlib.sha256(DATA.read_bytes()).hexdigest()
    assert sha==man['benchmark_sha256'],'MANIFEST benchmark checksum mismatch; data freeze invalidated'
    assert DATA.stat().st_size<100*1024*1024,'data limit 100MB exceeded'
    with META.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==234 and len({x['case_id'] for x in rows})==234,'metadata incomplete'
    assert all(r['synthetic']=='true' and r['license']=='CDLA-Permissive-2.0' for r in rows),'licensing metadata mismatch'
    for name in ('README.md','LICENSE','LICENSE-DATA.md','LICENSE-DOCS.md','MANIFEST.json','Makefile',
                 'track_2b/Makefile','track_2b/Dockerfile','track_2b/technical_report.md','track_2b/src/run_benchmark.py'):
        assert (ROOT/name).is_file(),f'missing required project file {name}'
    private_env_files=[p for p in (ROOT/'track_2b').glob('.env*') if p.is_file() and not p.name.endswith('.example')]
    assert not private_env_files,f'private environment files found in public tree: {private_env_files}'
    textfiles=list(ROOT.glob('**/*.py'))+list(ROOT.glob('**/*.md'))+list(ROOT.glob('**/*.json'))+list(ROOT.glob('**/*.jsonl'))
    for p in textfiles:
        if '/results/' in str(p):continue
        text=p.read_text(encoding='utf-8')
        assert not re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----',text),f'private key detected: {p}'
        assert not re.search(r'(?i)(?:api_key|token)\s*=\s*(?:sk-[A-Za-z0-9_-]{16,}|[A-Za-z0-9_-]{48,})',text),f'potential secret: {p}'
    assert not list(ROOT.rglob('livingstone_*.*')),'private historical file name in public tree'
    return {'pass':True,'dataset_sha256':sha,'metadata_rows':len(rows),'data_bytes':DATA.stat().st_size,
            'screened_text_files':len(textfiles),'disclaimer':'Local screening only; human release and license review required.'}

if __name__=='__main__':print(json.dumps(check(),indent=2))
