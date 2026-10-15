"""Strict, paired-seed scoring. Never divide by 0 and never count missing predictions as correct."""
import argparse,json,math
from collections import defaultdict,Counter
from pathlib import Path
from validate import load,validate

STRESS=['repeat_3','repeat_5','syndicated_linked_5']
UNKNOWN='syndicated_unknown_5'
POSITIVE='independent_3'

def rate(k,n):return round(k/n,5) if n else None

def wilson(k,n,z=1.959963984540054):
    if not n:return None
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [round(max(0,c-r),4),round(min(1,c+r),4)]

def macro_f1(pairs):
    labels=sorted(set(g for g,_ in pairs));out=[]
    for s in labels:
        tp=sum(g==s and p==s for g,p in pairs)
        fp=sum(g!=s and p==s for g,p in pairs)
        fn=sum(g==s and p!=s for g,p in pairs)
        out.append(2*tp/(2*tp+fp+fn) if (2*tp+fp+fn) else 0)
    return round(sum(out)/len(out),5) if out else None

def score(cases,predictions,allow_partial=False):
    byid={c['case_id']:c for c in cases}
    valid={};fail=[];unexpected=[]
    for r in predictions:
        cid=r.get('case_id')
        if cid not in byid:
            unexpected.append(cid);continue
        if r.get('ok') and isinstance(r.get('prediction'),dict):valid[cid]=r['prediction']
        else:fail.append(cid)
    count=len(valid)
    if not allow_partial and count!=len(cases):
        raise ValueError(f'Incomplete run: {count}/{len(cases)} succeeded. Pass --allow-partial for descriptive diagnostics only.')
    byseed=defaultdict(dict)
    for cid,p in valid.items():
        c=byid[cid];byseed[c['seed_id']][c['variant']]=(c,p)
    pairs=[];clo=[];inv=[];cinv=[];no=[];incr=[];unknown=[];yes=[];joint=[];byvariant=defaultdict(list)
    n_complete_seeds=0
    for sid,grp in byseed.items():
        for v,(c,p) in grp.items():
            byvariant[v].append(p['evidence_independence']==c['reference_independence'])
        if 'base' not in grp:continue
        bc,bp=grp['base']
        pairs.append((bc['reference_epistemic_state'],bp['epistemic_state']))
        clo.append(bc['reference_closure']==bp['closure'])
        stress_pass=[]
        for name in STRESS:
            if name not in grp:continue
            c,p=grp[name];si=p['epistemic_state']==bp['epistemic_state'];ci=p['closure']==bp['closure'];ni=p['evidence_independence']=='NO'
            inv.append(si);cinv.append(ci);no.append(ni)
            incr.append(p['claim_support_score']-bp['claim_support_score'])
            stress_pass.append(si and ci and ni and (p['claim_support_score']-bp['claim_support_score'])<=.10+1e-9)
        if UNKNOWN in grp:
            _,p=grp[UNKNOWN];unknown.append(p['evidence_independence']=='UNKNOWN')
        if POSITIVE in grp:
            _,p=grp[POSITIVE];yes.append(p['evidence_independence']=='YES')
        complete=len(grp)==6
        if complete:
            n_complete_seeds+=1
            joint.append(bc['reference_epistemic_state']==bp['epistemic_state'] and clo[-1] and
                        all(stress_pass) and len(stress_pass)==3 and bp['evidence_independence']=='NO' and unknown[-1] and yes[-1])
    correct=sum(g==p for g,p in pairs)
    positives=sum(yes);unknowns=sum(unknown);invok=sum(inv)
    score_note='Descriptive synthetic-test metrics; no external gold, no historical generalization or model accuracy claims.'
    return {'dataset_n_cases':len(cases),'n_successful_cases':count,'n_failed_or_missing_cases':len(cases)-count,
            'n_base_scored':len(pairs),'n_complete_6_variant_seeds':n_complete_seeds,'n_stress_pairs':len(inv),
            'base_state_accuracy':rate(correct,len(pairs)),
            'base_state_accuracy_wilson95':wilson(correct,len(pairs)),
            'base_state_macro_f1':macro_f1(pairs),'base_closure_accuracy':rate(sum(clo),len(clo)),
            'base_independence_correct_no':rate(sum(grp['base'][1]['evidence_independence']=='NO' for grp in byseed.values() if 'base' in grp),len(pairs)),
            'paired_state_invariance':rate(invok,len(inv)),
            'paired_closure_invariance':rate(sum(cinv),len(cinv)),
            'duplicated_sources_correct_no_independence':rate(sum(no),len(no)),
            'unknown_lineage_correctly_unknown':rate(unknowns,len(unknown)),
            'independent_positive_control_accuracy':rate(positives,len(yes)),
            'claim_support_inflation_gt_0.10_rate':rate(sum(x>.10+1e-9 for x in incr),len(incr)),
            'mean_claim_support_change_under_reuse':round(sum(incr)/len(incr),5) if incr else None,
            'full_seed_joint_pass_rate':rate(sum(joint),len(joint)),
            'source_independence_accuracy_by_variant':{v:rate(sum(vals),len(vals)) for v,vals in sorted(byvariant.items())},
            'scoring_note':score_note,'partial_run':count!=len(cases),'unexpected_prediction_case_ids':unexpected[:20]}

def load_verified_model_records(pred_path, data_path, require_complete=True):
    """Prevent a stale checksum, mixed prompt/model or unverified backend spoiling scores.

    Multiple unsuccessful attempts can coexist with a later successful retry.
    A successful case is counted once, never as an independent data point.
    """
    from run_benchmark import prompt_hash,normalize,model_route
    cases=load(data_path); meta=validate(data_path)
    target_ids={c['case_id'] for c in cases}
    raw=load(pred_path)
    if not raw:raise ValueError(f'empty model output: {pred_path}')
    expected_prompt_sha=prompt_hash()
    signatures=set()
    successful={}
    for idx,r in enumerate(raw,1):
        cid=r.get('case_id')
        if cid not in target_ids:raise ValueError(f'unexpected case_id at record {idx}: {cid}')
        if r.get('dataset_sha256')!=meta['sha256']:
            raise ValueError(f'dataset hash mismatch at {cid}; score only against the original dataset')
        if r.get('prompt_sha256')!=expected_prompt_sha:
            raise ValueError(f'prompt source hash mismatch at {cid}; do not score edited prompts')
        signature=(r.get('model'),r.get('protocol'),r.get('run_id'),r.get('prompt_sha256'),r.get('dataset_sha256'))
        if not all(signature):raise ValueError(f'incomplete experiment fingerprint at {cid}')
        signatures.add(signature)
        if r.get('ok'):
            canonical,provider=model_route(r['model'],r.get('api_base') or 'https://api.inference.cscs.ch/v1')
            if r.get('served_model') not in (canonical,r['model']):
                raise ValueError(f'unverified or mismatched served model at {cid}')
            if provider and r.get('requested_provider')!=provider:
                raise ValueError(f'HF provider provenance missing or mismatched at {cid}')
            normalize(r.get('prediction'))
            successful[cid]=r
    if len(signatures)!=1:raise ValueError('prediction file mixes model, prompt, run, or dataset identities')
    if require_complete and set(successful)!=target_ids:
        raise ValueError(f'incomplete evaluation: {len(successful)}/{len(target_ids)} cases succeeded')
    return list(successful.values()),next(iter(signatures)),raw


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data',default='data/epitrace_benchmark_public_v0.3.jsonl')
    p.add_argument('--pred',required=True)
    p.add_argument('--out',default=None)
    p.add_argument('--allow-partial',action='store_true')
    a=p.parse_args()
    predictions,signature,raw=load_verified_model_records(a.pred,a.data,require_complete=not a.allow_partial)
    d=score(load(a.data),predictions,allow_partial=a.allow_partial)
    d['experiment']={'model':signature[0],'protocol':signature[1],'run_id':signature[2],
                     'prompt_sha256':signature[3],'dataset_sha256':signature[4]}
    d['n_total_log_records']=len(raw)
    out=Path(a.out or (str(Path(a.pred).with_suffix(''))+'_summary.json'))
    out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(d,indent=2));print('Saved',out)
if __name__=='__main__':main()
