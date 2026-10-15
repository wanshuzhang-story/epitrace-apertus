"""Preflight validation; checks full 39 x 6 frozen benchmark and synthetic licensing."""
import argparse, json, hashlib
from pathlib import Path
from collections import Counter, defaultdict

VARIANTS = ["base", "repeat_3", "repeat_5", "syndicated_linked_5", "syndicated_unknown_5", "independent_3"]
EXPECTED = {"base":"NO", "repeat_3":"NO", "repeat_5":"NO", "syndicated_linked_5":"NO", "syndicated_unknown_5":"UNKNOWN", "independent_3":"YES"}

def load(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]

def validate(path, seed_path=None):
    path=Path(path);rows=load(path)
    assert len(rows)==234, f"expected 234 cases: {len(rows)}"
    assert len({x['case_id'] for x in rows})==234, 'case ID collision'
    assert len({x['seed_id'] for x in rows})==39, 'not 39 seeds'
    assert Counter(x['variant'] for x in rows)==Counter({v:39 for v in VARIANTS}), 'variant imbalance'
    assert all(x['synthetic'] is True for x in rows), 'public data includes non-synthetic text'
    assert all(x['input_text'].strip() and x['claim'].strip() for x in rows)
    byseed=defaultdict(dict)
    for x in rows:
        assert x['reference_independence']==EXPECTED[x['variant']], x['case_id']
        byseed[x['seed_id']][x['variant']]=x
    for sid,grp in byseed.items():
        assert set(grp)==set(VARIANTS),sid
        assert len({v['reference_epistemic_state'] for v in grp.values()})==1
        base=grp['base']['input_text'].split('\n',1)[1]
        assert grp['repeat_3']['input_text'].count(base)==3,sid
        assert grp['repeat_5']['input_text'].count(base)==5,sid
        assert base in grp['syndicated_linked_5']['input_text'],sid
        assert base not in grp['syndicated_unknown_5']['input_text'],sid
        assert 'FIRSTHAND ORIGIN' not in grp['independent_3']['input_text'],sid
        assert grp['independent_3']['input_text'].count('DOCUMENT ')==3,sid
        assert len({v['reference_closure'] for v in grp.values()})==1
    if seed_path:
        seeds=load(seed_path)
        assert len(seeds)==39 and len({s['seed_id'] for s in seeds})==39
        assert {s['seed_id'] for s in seeds}==set(byseed)
        assert all(s['synthetic'] and s['source_license']=='CDLA-Permissive-2.0' for s in seeds)
    return {'cases':len(rows),'seeds':len(byseed),'variants':len(VARIANTS),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/epitrace_benchmark_public_v0.3.jsonl');p.add_argument('--seeds',default='data/epitrace_seeds_public_v0.3.jsonl');a=p.parse_args()
    print(json.dumps(validate(a.data,a.seeds),indent=2))
