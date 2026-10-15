"""Offline inspector for one synthetic benchmark seed (no model calls)."""
import argparse
from validate import load

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',default='PUB001')
    p.add_argument('--data',default='data/epitrace_benchmark_public_v0.3.jsonl')
    a=p.parse_args()
    samples=[x for x in load(a.data) if x['seed_id']==a.seed]
    if not samples:raise SystemExit(f'Unknown seed: {a.seed}')
    for item in samples:
        print('\n'+'='*75)
        print('CONTROL',item['variant'],'| Target:',item['claim'],'| lineage gold:',item['reference_independence'])
        print('-'*75)
        print(item['input_text'][:1200])
        if len(item['input_text'])>1200:print(f'... [{len(item["input_text"])-1200} more characters]')
