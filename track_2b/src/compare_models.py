"""Compare two complete model runs, using 39 paired seed units for uncertainty."""
import argparse, json, random, statistics
from collections import defaultdict
from pathlib import Path
from validate import load, validate
from score import score,load_verified_model_records

METRICS=['base_state_accuracy','paired_state_invariance','paired_closure_invariance',
         'duplicated_sources_correct_no_independence','unknown_lineage_correctly_unknown',
         'independent_positive_control_accuracy','claim_support_inflation_gt_0.10_rate',
         'full_seed_joint_pass_rate']

def verified_predictions(path, cases, data_path):
    rows,signature,_=load_verified_model_records(path,data_path,require_complete=True)
    ids={c['case_id'] for c in cases}
    if {r['case_id'] for r in rows}!=ids:raise ValueError(f'incomplete run: {path}')
    return rows,signature

def compare(data_path,pred_a,pred_b,bootstrap=10000):
    meta=validate(data_path); cases=load(data_path)
    aa,sa=verified_predictions(pred_a,cases,data_path);bb,sb=verified_predictions(pred_b,cases,data_path)
    aa_bases={r.get('api_base') for r in aa if r.get('api_base')}
    bb_bases={r.get('api_base') for r in bb if r.get('api_base')}
    if len(aa_bases)>1 or len(bb_bases)>1 or (aa_bases and bb_bases and aa_bases!=bb_bases):
        raise ValueError('Paired model comparison must use the same serving provider')
    providers_a={r.get('requested_provider') for r in aa}
    providers_b={r.get('requested_provider') for r in bb}
    if len(providers_a)!=1 or len(providers_b)!=1 or providers_a!=providers_b:
        raise ValueError('Paired model comparison must pin the same HF backend provider; same router URL is insufficient')
    if sa[4]!=meta['sha256'] or sb[4]!=meta['sha256']:
        raise ValueError('Dataset SHA mismatch between predictions and scoring dataset')
    if sa[1]!=sb[1] or sa[3]!=sb[3]:raise ValueError('Use the same prompt protocol and source fingerprint for comparison')
    if sa[0]==sb[0]:raise ValueError('Model identifiers are identical: no between-model comparison')
    by_seed_cases=defaultdict(list)
    for c in cases:by_seed_cases[c['seed_id']].append(c)
    by_seed_a=defaultdict(list);by_seed_b=defaultdict(list)
    sid={c['case_id']:c['seed_id'] for c in cases}
    for p in aa:by_seed_a[sid[p['case_id']]].append(p)
    for p in bb:by_seed_b[sid[p['case_id']]].append(p)
    seeds=sorted(by_seed_cases)
    per_seed={}
    for seed in seeds:
        a=score(by_seed_cases[seed],by_seed_a[seed]);b=score(by_seed_cases[seed],by_seed_b[seed]);per_seed[seed]=(a,b)
    rng=random.Random(2026)
    result={'model_a':sa[0],'model_b':sb[0],'protocol':sa[1],'dataset_sha256':meta['sha256'],'paired_seed_n':len(seeds),'prompt_sha256':sa[3],'bootstrap_resamples':bootstrap,'backend_provider':next(iter(providers_a)),'api_base':next(iter(aa_bases)) if aa_bases else None,'differences_b_minus_a':{}}
    for metric in METRICS:
        diffs=[per_seed[seed][1][metric]-per_seed[seed][0][metric] for seed in seeds]
        draws=[]
        for _ in range(bootstrap):
            draw=[diffs[rng.randrange(len(diffs))] for _ in diffs]
            draws.append(statistics.mean(draw))
        draws.sort()
        result['differences_b_minus_a'][metric]={'difference':round(statistics.mean(diffs),5),
             'paired_seed_bootstrap_95ci':[round(draws[int(.025*(bootstrap-1))],5),round(draws[int(.975*(bootstrap-1))],5)]}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',default='data/epitrace_benchmark_public_v0.3.jsonl')
    p.add_argument('--pred-a',required=True)
    p.add_argument('--pred-b',required=True)
    p.add_argument('--bootstrap',type=int,default=5000)
    p.add_argument('--out',default='results/paired_model_comparison.json')
    x=p.parse_args()
    z=compare(x.data,x.pred_a,x.pred_b,x.bootstrap)
    Path(x.out).parent.mkdir(parents=True,exist_ok=True)
    Path(x.out).write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(z,indent=2))
