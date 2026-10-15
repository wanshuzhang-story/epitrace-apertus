"""Write reproducible comparison tables, example audit and SVG after REAL complete runs.

Never creates simulated or placeholder model results. Input model responses must have
valid run fingerprints, served model IDs and all 234 successful case IDs.
"""
import argparse
import csv
import html
import json
import statistics
from collections import defaultdict
from pathlib import Path
from compare_models import compare
from score import load_verified_model_records,score
from validate import load

SELECT_METRICS=[
 ('base_state_accuracy','Baseline state agreement (synthetic reference)'),
 ('paired_state_invariance','Known-copy state invariance'),
 ('paired_closure_invariance','Known-copy closure invariance'),
 ('duplicated_sources_correct_no_independence','Known-copy NO independence'),
 ('unknown_lineage_correctly_unknown','Unresolved-lineage UNKNOWN'),
 ('independent_positive_control_accuracy','Independent-witness YES'),
 ('claim_support_inflation_gt_0.10_rate','Support inflation rate (>0.10; lower is better)'),
 ('full_seed_joint_pass_rate','All-criteria joint pass per seed'),
]


def find_two_runs(directory,protocol):
    # Both CSCS canonical and Public AI lowercase aliases are supported.
    all_runs=sorted(directory.glob(f'*__{protocol}__*.jsonl'))
    a=[p for p in all_runs if p.name.split('__',1)[0].lower().split('_',1)[0]=='apertus-v1.5-8b']
    b=[p for p in all_runs if p.name.split('__',1)[0].lower().split('_',1)[0]=='apertus-v1.5-70b']
    if len(a)!=1 or len(b)!=1:
        raise ValueError(f'Expected precisely one run per model for protocol {protocol}: found 8B={len(a)}, 70B={len(b)}. Supply --pred-a and --pred-b explicitly if old runs remain.')
    return a[0],b[0]


def svg_chart(path,results):
    width=940;height=520;left=390;bar_area=465
    esc=html.escape
    colors=['#2B6CB0','#198A86']
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="940" height="520" fill="#ffffff"/>',
           '<text x="22" y="28" font-family="Arial,sans-serif" font-size="22" fill="#13253C" font-weight="bold">EpiTrace | Apertus comparison</text>',
           '<text x="22" y="50" font-family="Arial,sans-serif" font-size="12" fill="#566678">All proportions computed from 39 paired seeds; no historical gold labels.</text>']
    for index,(key,label) in enumerate(SELECT_METRICS):
        y=72+index*55
        parts.append(f'<text x="22" y="{y+16}" font-size="12" font-family="Arial,sans-serif" fill="#263548">{esc(label)}</text>')
        for j,k in enumerate(('a','b')):
            value=results[k][key]
            value=max(0.0,min(1.0,float(value or 0)))
            by=y+j*18
            parts.append(f'<rect x="{left}" y="{by}" width="{bar_area*value:.2f}" height="12" rx="2" fill="{colors[j]}"/>')
            parts.append(f'<text x="{left+bar_area+10}" y="{by+10}" font-size="11" font-family="Arial,sans-serif" fill="#263548">{value*100:.1f}%</text>')
    parts.append('<rect x="668" y="18" width="10" height="10" fill="#2B6CB0"/><text x="683" y="27" font-size="12" font-family="Arial">8B</text>')
    parts.append('<rect x="743" y="18" width="10" height="10" fill="#198A86"/><text x="758" y="27" font-size="12" font-family="Arial">70B</text>')
    parts.append('</svg>')
    path.write_text('\n'.join(parts),encoding='utf-8')


def evaluate_case(r,base):
    pred=r['prediction'];x={
       'state_correct':pred['epistemic_state']==base['reference_epistemic_state'],
       'closure_correct':pred['closure']==base['reference_closure'],
       'independence_correct':pred['evidence_independence']==base['reference_independence'],
    }
    return x


def summarize_runtime(records):
    durations=[r['latency_seconds'] for r in records if r.get('latency_seconds') is not None]
    return {'success_n':len(records),'median_latency_seconds':round(statistics.median(durations),3) if durations else None,
            'total_logged_latency_seconds':round(sum(durations),2) if durations else None,
            'prompt_tokens':sum(int((r.get('usage') or {}).get('prompt_tokens',0) or 0) for r in records),
            'completion_tokens':sum(int((r.get('usage') or {}).get('completion_tokens',0) or 0) for r in records)}


def generate(data_path,pred_a,pred_b,out_dir,bootstrap=5000):
    cases=load(data_path)
    a,sa,_=load_verified_model_records(pred_a,data_path)
    b,sb,_=load_verified_model_records(pred_b,data_path)
    if sa[1]!=sb[1] or sa[3]!=sb[3] or sa[4]!=sb[4]:
        raise ValueError('Different prompts or dataset fingerprints; cannot do paired analysis')
    bases_a={r.get('api_base') for r in a if r.get('api_base')}
    bases_b={r.get('api_base') for r in b if r.get('api_base')}
    if len(bases_a)>1 or len(bases_b)>1 or (bases_a and bases_b and bases_a!=bases_b):
        raise ValueError('Mixed API providers: use the same endpoint for a paired model comparison')
    if not (sa[0].lower().split(':',1)[0]=='swiss-ai/apertus-v1.5-8b' and sb[0].lower().split(':',1)[0]=='swiss-ai/apertus-v1.5-70b'):
        raise ValueError('Model A must be Apertus v1.5 8B and model B v1.5 70B; do not reverse them')
    runs={'a':a,'b':b};summaries={k:score(cases,rows) for k,rows in runs.items()}
    comparison=compare(data_path,pred_a,pred_b,bootstrap=bootstrap)
    for k in ('a','b'):summaries[k]['runtime_usage']=summarize_runtime(runs[k])
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/'paired_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n',encoding='utf-8')
    for k in ('a','b'):
        (out_dir/f'model_{k}_summary.json').write_text(json.dumps(summaries[k],indent=2)+'\n',encoding='utf-8')

    cases_by_id={c['case_id']:c for c in cases}
    pred_by_run={k:{r['case_id']:r for r in records} for k,records in runs.items()}
    fieldnames=['case_id','seed_id','variant','reference_state','reference_closure','reference_independence',
                'model','state','closure','independence','claim_support','state_correct','closure_correct',
                'independence_correct','support_delta_from_base','rationale','latency_seconds']
    failures=[]
    with (out_dir/'per_case_audit.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader()
        for model_k in ('a','b'):
            name=sa[0] if model_k=='a' else sb[0]
            for case in cases:
                r=pred_by_run[model_k][case['case_id']]
                p=r['prediction'];sid=case['seed_id']
                base_id=sid+'__base'
                base_score=pred_by_run[model_k][base_id]['prediction']['claim_support_score']
                diff=round(p['claim_support_score']-base_score,5)
                e=evaluate_case(r,case)
                w.writerow({'case_id':case['case_id'],'seed_id':sid,'variant':case['variant'],
                            'reference_state':case['reference_epistemic_state'],'reference_closure':case['reference_closure'],
                            'reference_independence':case['reference_independence'],'model':name,
                            'state':p['epistemic_state'],'closure':p['closure'],
                            'independence':p['evidence_independence'],'claim_support':p['claim_support_score'],
                            **e,'support_delta_from_base':diff,'rationale':p['rationale'],
                            'latency_seconds':r.get('latency_seconds')})
                if (case['variant'] in ('repeat_3','repeat_5','syndicated_linked_5') and diff>.10+1e-9) or not e['independence_correct']:
                    failures.append((case,model_k,p,diff,e))
    report=[f'# EpiTrace complete-run analysis ({sa[1]})',
            '',f'Frozen dataset SHA-256: `{sa[4]}`',f'Prompt source SHA-256: `{sa[3]}`',
            f'API base: `{next(iter(bases_a)) if bases_a else "not recorded in fixture"}`','',
            f'Model A: `{sa[0]}`. Model B: `{sb[0]}`. All 234 cases succeeded for each model.',
            '','| Metric | Apertus 8B | Apertus 70B | 70B - 8B [paired bootstrap 95%] |',
            '|---|---:|---:|---:|']
    for metric,label in SELECT_METRICS:
        s=comparison['differences_b_minus_a'][metric];lo,hi=s['paired_seed_bootstrap_95ci']
        report.append(f'| {label} | {summaries["a"][metric]:.3f} | {summaries["b"][metric]:.3f} | {s["difference"]:+.3f} [{lo:+.3f},{hi:+.3f}] |')
    report.extend(['','## Runtime and tokens (recorded, not estimated)','',
                   '| Statistic | 8B | 70B |','|---|---:|---:|'])
    for name in ('median_latency_seconds','total_logged_latency_seconds','prompt_tokens','completion_tokens'):
        ra=summarize_runtime(a);rb=summarize_runtime(b)
        report.append(f'| {name} | {ra[name]} | {rb[name]} |')
    report.extend(['','## Priority examples for manual adjudication','',
                   'The examples below are DIAGNOSTIC flags; they are not automatically validated human errors.',''])
    for case,k,p,delta,check in failures[:12]:
        report.extend([f'### {case["case_id"]} — {"8B" if k=="a" else "70B"}',
                       f'- Reference independence: `{case["reference_independence"]}`; predicted: `{p["evidence_independence"]}`',
                       f'- Claim support change from baseline: {delta:+.3f}',
                       f'- Model rationale: {p["rationale"]}',
                       f'- Excerpt: {case["input_text"][:200]} ...',''])
    report.extend(['## Interpretive safeguards','',
                   '- Authors constructed the synthetic references; no independent annotator adjudicated them.',
                   '- The support score is elicited, not a calibrated probability.',
                   '- Independent-control cases add evidence; their state may legitimately change.',
                   '- Bootstrap resamples 39 seeds, not 234 dependent rows.',
                   '- Do not call these results historical accuracy or proof of reliability in real OSINT.'])
    (out_dir/'RESULTS_SUMMARY.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    svg_chart(out_dir/'model_comparison.svg',summaries)
    return {'analysis_dir':str(out_dir),'model_a':sa[0],'model_b':sb[0],
            'n_flagged_for_manual_review':len(failures),'dataset_sha256':sa[4]}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',default='data/epitrace_benchmark_public_v0.3.jsonl')
    p.add_argument('--pred-a',default=None)
    p.add_argument('--pred-b',default=None)
    p.add_argument('--auto',action='store_true')
    p.add_argument('--protocol',choices=['neutral','provenance_aware'],default='neutral')
    p.add_argument('--results-dir',default='results')
    p.add_argument('--out-dir',default='results/analysis')
    p.add_argument('--bootstrap',type=int,default=5000)
    a=p.parse_args()
    if a.auto:
        pred_a,pred_b=find_two_runs(Path(a.results_dir),a.protocol)
    else:
        if not a.pred_a or not a.pred_b:p.error('Set --auto or supply both --pred-a and --pred-b')
        pred_a,pred_b=a.pred_a,a.pred_b
    print(json.dumps(generate(a.data,pred_a,pred_b,a.out_dir,a.bootstrap),indent=2))
