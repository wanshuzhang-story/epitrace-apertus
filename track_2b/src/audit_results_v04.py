from pathlib import Path
import json,csv,hashlib,collections,statistics,math
from itertools import product
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SRC=Path(__file__).resolve().parents[2]
ROOT=SRC
DAT=SRC/'track_2b/data/epitrace_benchmark_public_v0.3.jsonl'
RES=SRC/'track_2b/results'
OUT=RES/'analysis'
OUT.mkdir(parents=True,exist_ok=True)
cs=[json.loads(x) for x in DAT.read_text(encoding='utf-8').splitlines() if x.strip()]
byid={x['case_id']:x for x in cs}
raw={}
for name in ['8B','70B']:
 p=list(RES.glob('apertus-v1.5-'+name.lower()+'__neutral__*.jsonl'))
 assert len(p)==1,p
 records=[json.loads(x) for x in p[0].read_text(encoding='utf-8').splitlines() if x.strip()]
 assert len(records)==234 and len(set(r['case_id'] for r in records))==234
 assert all(r['ok'] and r['served_model']=='swiss-ai/apertus-v1.5-'+name.lower() for r in records)
 raw[name]={r['case_id']:r for r in records}
sha=hashlib.sha256(DAT.read_bytes()).hexdigest()
assert sha=='eec19b80367947138a54b9b3e5188a6ccc70811bf722ca3a6eb275d53f574900'
base_cases=[c for c in cs if c['variant']=='base']
summary={n:json.loads((RES/'analysis'/f'model_{"a" if n=="8B" else "b"}_summary.json').read_text()) for n in ['8B','70B']}
cmp=json.loads((RES/'analysis/paired_comparison.json').read_text())

rows=[]
for name in ['8B','70B']:
 for c in cs:
  p=raw[name][c['case_id']]['prediction']
  base=raw[name][c['seed_id']+'__base']['prediction']
  issues=[];suggested=[]
  if c['variant']=='syndicated_unknown_5' and p['evidence_independence']!='UNKNOWN':
   issues.append('unresolved_source_lineage_as_'+p['evidence_independence'])
   suggested.append('Reference-defined UNKNOWN; inspect whether the model mistakes undocumented origins for shared origins.')
  if c['variant']=='base' and p['evidence_independence']!='NO':
   issues.append('baseline_single_excerpt_independence_'+p['evidence_independence'])
   suggested.append('Reference labels all base excerpts NO, but citations of official primary documents may deserve adjudication.')
  if c['variant'] in ('repeat_3','repeat_5','syndicated_linked_5') and p['evidence_independence']!='NO':
   issues.append('known_reuse_false_independence_'+p['evidence_independence'])
   suggested.append('Identical/explicitly credited copies must not constitute separate origins under benchmark definitions.')
  delta=round(p['claim_support_score']-base['claim_support_score'],5)
  if c['variant'] in ('repeat_3','repeat_5','syndicated_linked_5') and delta>.10000001:
   issues.append('dependent_copy_support_inflation')
   suggested.append('Support score rose by more than 0.10 despite no added evidence.')
  if not issues:continue
  level=('high' if any(s.startswith(('known_reuse','dependent_copy')) for s in issues) else ('medium' if c['variant']=='base' else 'systematic'))
  rows.append(dict(priority=level,model=name,case_id=c['case_id'],seed_id=c['seed_id'],variant=c['variant'],issues=';'.join(issues),
                   reference_independence=c['reference_independence'],predicted_independence=p['evidence_independence'],
                   reference_state=c['reference_epistemic_state'],predicted_state=p['epistemic_state'],
                   reference_closure=c['reference_closure'],predicted_closure=p['closure'],support_base=base['claim_support_score'],support_variant=p['claim_support_score'],support_delta=delta,
                   claim=c['claim'],input_excerpt=c['input_text'][:360].replace('\n',' '),rationale=p['rationale'],interpretation=' '.join(suggested)))
assert len(rows)==105,len(rows)
with (OUT/'EpiTrace_Flagged_Observations_105.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

variant_order=['base','repeat_3','repeat_5','syndicated_linked_5','syndicated_unknown_5','independent_3']
pervar=[]
for name in ('8B','70B'):
 for v in variant_order:
  pairs=[(c,raw[name][c['case_id']]['prediction']) for c in cs if c['variant']==v]
  co=collections.Counter(p['evidence_independence'] for c,p in pairs)
  pervar.append(dict(model=name,condition=v,n=len(pairs),reference_independence=pairs[0][0]['reference_independence'],
                     pred_yes=co['YES'],pred_no=co['NO'],pred_unknown=co['UNKNOWN'],independence_correct=sum(p['evidence_independence']==c['reference_independence'] for c,p in pairs),
                     state_reference_agreement=sum(p['epistemic_state']==c['reference_epistemic_state'] for c,p in pairs),
                     closure_reference_agreement=sum(p['closure']==c['reference_closure'] for c,p in pairs),
                     mean_claim_support=round(statistics.mean(p['claim_support_score'] for c,p in pairs),5)))
with (OUT/'EpiTrace_Condition_Results.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(pervar[0]));w.writeheader();w.writerows(pervar)

state_acc={}
for name in ('8B','70B'):
 for state in ['RUMOURED','TENTATIVE','PROBABLE','CONFIRMED','CONTESTED','REJECTED','SETTLED','NOT_APPLICABLE']:
  group=[c for c in base_cases if c['reference_epistemic_state']==state]
  state_acc[(name,state)]=sum(raw[name][c['case_id']]['prediction']['epistemic_state']==state for c in group)

seedrows=[]
for c in base_cases:
 sr={'seed_id':c['seed_id'],'claim':c['claim'],'reference_state':c['reference_epistemic_state'],'reference_closure':c['reference_closure']}
 for name in ('8B','70B'):
  base=raw[name][c['case_id']]['prediction']
  sr[name+'_base_state']=base['epistemic_state'];sr[name+'_base_correct']=int(base['epistemic_state']==c['reference_epistemic_state'])
  sr[name+'_base_independence']=base['evidence_independence'];sr[name+'_unknown_independence']=raw[name][c['seed_id']+'__syndicated_unknown_5']['prediction']['evidence_independence']
  sr[name+'_known_copies_no']=sum(raw[name][c['seed_id']+'__'+v]['prediction']['evidence_independence']=='NO' for v in ('repeat_3','repeat_5','syndicated_linked_5'))
  sr[name+'_state_invariant']=sum(raw[name][c['seed_id']+'__'+v]['prediction']['epistemic_state']==base['epistemic_state'] for v in ('repeat_3','repeat_5','syndicated_linked_5'))
  sr[name+'_copy_max_support_delta']=round(max(raw[name][c['seed_id']+'__'+v]['prediction']['claim_support_score']-base['claim_support_score'] for v in ('repeat_3','repeat_5','syndicated_linked_5')),3)
 seedrows.append(sr)
with (OUT/'EpiTrace_39_Seed_Paired_Review.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(seedrows[0]));w.writeheader();w.writerows(seedrows)

# Reviewer-facing figure 1: evidence-independence predictions by controlled condition
fig,ax=plt.subplots(figsize=(10.6,4.4))
colors={'NO':'#475569','UNKNOWN':'#f59e0b','YES':'#1d8790'}
labels={'base':'Base (1 excerpt)','repeat_3':'Identical x3','repeat_5':'Identical x5','syndicated_linked_5':'Linked syndication x5','syndicated_unknown_5':'Untraceable lineage x5','independent_3':'Independent accounts x3'}
order=[]
for v in variant_order:
 for name in ('8B','70B'):
  order.append((name,v))
for i,(name,v) in enumerate(order):
 row=next(z for z in pervar if z['model']==name and z['condition']==v)
 left=0
 for cat,field in [('NO','pred_no'),('UNKNOWN','pred_unknown'),('YES','pred_yes')]:
  count=row[field];width=count/39*100
  if width>0:
   ax.barh(i,width,left=left,color=colors[cat],height=.68,edgecolor='white',linewidth=.5)
   if width>=12:ax.text(left+width/2,i,f'{count}/39',color='white' if cat!='UNKNOWN' else '#222222',ha='center',va='center',fontsize=8.5,fontweight='bold')
   left+=width
ax.set_yticks(range(len(order)),[f'{labels[v]}   {name}' for name,v in order],fontsize=8.5)
ax.set_xlim(0,100);ax.invert_yaxis()
ax.set_xlabel('Predicted provenance class (% of 39 seeds)',fontsize=9.5)
ax.spines[['top','right','left']].set_visible(False)
ax.xaxis.grid(True,color='#e7ecef');ax.set_axisbelow(True)
handles=[plt.Rectangle((0,0),1,1,color=colors[k]) for k in ['NO','UNKNOWN','YES']]
ax.legend(handles,['NO','UNKNOWN','YES'],ncols=3,loc='upper right',bbox_to_anchor=(1,1.14),frameon=False)
fig.suptitle('Source-independence judgments: 8B versus 70B',x=.08,ha='left',fontsize=14,fontweight='bold',y=1.06)
fig.subplots_adjust(left=.265,right=.98,top=.88,bottom=.12)
fig.savefig(OUT/'EpiTrace_Figure1_Independence.png',dpi=200,bbox_inches='tight',facecolor='white')
plt.close(fig)

fig,ax=plt.subplots(figsize=(10.0,4.0))
states=['RUMOURED','TENTATIVE','PROBABLE','CONFIRMED','CONTESTED','REJECTED','SETTLED','NOT_APPLICABLE']
xx=list(range(len(states)));denoms=[sum(c['reference_epistemic_state']==s for c in base_cases) for s in states]
ax.bar([z-.19 for z in xx],[state_acc[('8B',s)]/d for s,d in zip(states,denoms)],width=.35,label='8B',color='#475569')
ax.bar([z+.19 for z in xx],[state_acc[('70B',s)]/d for s,d in zip(states,denoms)],width=.35,label='70B',color='#1d8790')
ax.set_xticks(xx,states,rotation=27,ha='right',fontsize=8.5)
ax.set_ylim(0,1.15);ax.set_ylabel('Agreement with synthetic reference',fontsize=9)
ax.legend(frameon=False,ncols=2);ax.spines[['top','right']].set_visible(False)
ax.yaxis.grid(True,color='#edf1f4');ax.set_axisbelow(True)
for i,d in enumerate(denoms):ax.text(i,1.06,f'n={d}',ha='center',fontsize=8,color='#475569')
fig.suptitle('Baseline state agreement varies by label',fontsize=14,fontweight='bold',x=.08,ha='left',y=1.02)
fig.tight_layout()
fig.savefig(OUT/'EpiTrace_Figure2_StateAgreement.png',dpi=200,bbox_inches='tight',facecolor='white')
plt.close(fig)

flags_counter=collections.Counter(x['issues'] for x in rows)
assert len(rows)==105
ci=cmp['differences_b_minus_a']
price8=.1*summary['8B']['runtime_usage']['prompt_tokens']/1e6+.2*summary['8B']['runtime_usage']['completion_tokens']/1e6
price70=.82*summary['70B']['runtime_usage']['prompt_tokens']/1e6+2.92*summary['70B']['runtime_usage']['completion_tokens']/1e6
extra={
 'date_utc':'2026-10-15',
 'raw_case_count':234,'paired_seed_count':39,'model_case_observations':468,
 'dataset_sha256':sha,'prompt_sha256':cmp['prompt_sha256'],
 'same_provider':cmp['api_base'],
 'flags_total':len(rows),'flag_categories':dict(flags_counter),
 'state_acc_by_label':{name:{s:[state_acc[(name,s)],denoms[states.index(s)]] for s in states} for name in ['8B','70B']},
 'base_accuracy_discordance':{ 'both_correct':0,'only_8b':0,'only_70b':0,'both_wrong':0 },
 'estimated_api_billing_usd_excluding_pilot':{'8b':round(price8,4),'70b':round(price70,4),'both':round(price8+price70,4),'assumed_2026_10_12_publicai_rates':True},
 'independent_source_positive':{name:sum(raw[name][c['seed_id']+'__independent_3']['prediction']['evidence_independence']=='YES' for c in base_cases) for name in ['8B','70B']},
}
for c in base_cases:
 a=raw['8B'][c['case_id']]['prediction']['epistemic_state']==c['reference_epistemic_state']
 b=raw['70B'][c['case_id']]['prediction']['epistemic_state']==c['reference_epistemic_state']
 extra['base_accuracy_discordance'][('both_correct' if a and b else 'only_8b' if a else 'only_70b' if b else 'both_wrong')]+=1
(OUT/'EpiTrace_Independent_Audit_Stats.json').write_text(json.dumps(extra,indent=2)+'\n',encoding='utf-8')

report=f'''# EpiTrace - independent post-evaluation audit

**Assessment date:** 15 October 2026. **Source:** full original logs uploaded as `EpiTrace_REAL_RESULTS.zip`. **Purpose:** separate measured results from design assumptions.

## Integrity and coverage

- Validated all 234 unique case IDs for each of two actual served models, plus consistent dataset/prompt SHA-256 values. Both runs completed on `https://api.publicai.co/v1` with `temperature=0`, 350-token generation cap and 39 paired seed families.
- Re-executed project `make smoke` (25 tests pass) and `make report` (same 105 flags) without a new API request.
- Frozen dataset SHA-256: `{sha}`. Prompt source SHA-256: `{cmp['prompt_sha256']}`.
- The model IDs are recorded by the API as `swiss-ai/apertus-v1.5-8b` and `swiss-ai/apertus-v1.5-70b` respectively; system fingerprint differs per model. The requested provider is Public AI, not CSCS. No Swiss residency was tested.

## Principal experimental results

| Measure | 8B | 70B | Comment |
|---|---:|---:|---|
| Baseline synthetic state agreement | 21/39 (53.8%) | 21/39 (53.8%) | Same aggregate, four different predictions; 19 both correct, 16 both incorrect, two unique to each. |
| Known-copy state invariance | 93/117 (79.5%) | 94/117 (80.3%) | Stable relative to each model's baseline, not correctness against author label. |
| Known-copy closure invariance | 108/117 (92.3%) | 107/117 (91.5%) | Same limitation. |
| Known-copy NO source independence | 117/117 (100%) | 115/117 (98.3%) | Two 70B errors occur in PUB029 x3 and x5 repeated retractions. |
| Unknown provenance labelled UNKNOWN | 0/39 | 0/39 | Both consistently returned NO. |
| Separate eyewitness sources labelled YES | 39/39 | 39/39 | Explicitly independent notebook/diary template, comparatively easy control. |
| Dependent-copy support inflation > 0.10 | 2/117 | 1/117 | 8B PUB037 x3/x5; 70B PUB018 x5. |
| Full-seed joint pass | 0/39 | 0/39 | Forced to zero by universal failure of unknown provenance; should not be used as a global ranking. |

Paired seed bootstrap for baseline state difference (70B minus 8B): **0.0 percentage points** with 95% interval **[-10.3,+10.3] pp**. No measured paired accuracy advantage of 70B is established; compare `paired_comparison.json` for all intervals.

## Decomposition of the 105 automated flags

The flagged entries are **model-case observations**, not distinct sources, seeds, or independently validated human errors.

- **78/105:** unknown-lineage case predicted NO by both models (39 per model). This is the dominant systematic failure under the benchmark's specified three-class definition.
- **22/105:** base excerpts predicting YES or UNKNOWN rather than author-reference NO (10 from 8B, 12 from 70B). Several cite official documents or corrections; these deserve independent adjudication because *independent origin* and *official verification* are being conflated by the model and perhaps ambiguity of annotation.
- **2/105:** 70B falsely returned YES on `PUB029__repeat_3` and `PUB029__repeat_5`, treating repeated retractions from a single newspaper as independent evidence.
- **3/105:** support increase >0.10 despite exact repetition: 8B `PUB037__repeat_3` and `PUB037__repeat_5` (0.75 to 0.95); 70B `PUB018__repeat_5` (0.75 to 0.95).

## Counterexamples and epistemic interpretation

**PUB001__syndicated_unknown_5 (both models):** Five unsigned publications share a claim without lineage. Both label NO, and their rationales explain lack of demonstrated independent corroboration rather than established common sourcing. This illustrates collapsing absence of demonstrated independence into evidence of dependence. Since the input deliberately withholds links, UNKNOWN is the construction label, not externally proven ground truth.

**PUB029__repeat_3 / repeat_5 (70B):** The same newspaper retracts its earlier claim in identical copies. The two YES predictions explicitly confuse correction/verification with independent evidentiary origins, a genuine protocol-defined error.

**PUB021__base (both models):** A single newspaper cites a signed bridge order. Both label YES, as if documentary verification implied independent corroboration. Under the author's stipulated single-source baseline this is marked wrong, but a human should check the conceptual boundary between publication and underlying official document before calling it a validated failure.

**PUB038__base / PUB039__base:** Neither model classified the clearly figurative comic/advertising input as NOT_APPLICABLE. This is a separate discourse-classification difficulty, not evidence repetition.

## Systematic state-reference mismatches

- `PROBABLE`: 0/5 baseline cases correct for **both** models; all five downgraded to TENTATIVE.
- `SETTLED`: 0/5 for **both**; usually downgraded to CONFIRMED (four seeds) or PROBABLE (one).
- `NOT_APPLICABLE`: 0/2 for **both**, despite overtly figurative text.
- `CONFIRMED`: 0/5 for 8B, 2/5 for 70B (mostly PROBABLE), indicating a systematic difference in how models read official confirmation.

The baseline reference labels are authored for synthetic material; some mismatches may reflect rubric interpretation. They should not be reported as newspaper-domain factual inaccuracies.

## Known limitations relevant to the contest jury

1. **Synthetic author labels, no blind human adjudication.** The data do not support claims of historical or real-world deployment accuracy.
2. **Templates make positive controls easy.** The independently maintained inspector/caretaker accounts openly establish their independence, and the common dispatch IDs visibly identify shared origin.
3. **Guide already explains source independence.** Even the 'neutral' prompt operationally defines YES, NO and UNKNOWN, so performance measures following the schema, not spontaneous uninstructed reasoning.
4. **Unknown cases are homogeneous.** All 39 unknown dossiers are created by one five-clipping template with substituted claims. The 0/39 result is systematic in this design, not evidence of universal model behavior.
5. **Elicited support is not calibrated probability.** Support-score inflation threshold 0.10 was chosen as a diagnostic threshold.
6. **No repeated sampling or controlled serving hardware.** Differences in median API latency cannot be interpreted as hardware-scaled throughput differences.
7. **Backend sovereignty is not demonstrated.** Apertus models have Swiss origin and are open, but these results were served through Public AI; do not assert Swiss data residency.

## Logged resource use and cost estimate

| Measure | 8B | 70B |
|---|---:|---:|
| Prompt tokens | {summary['8B']['runtime_usage']['prompt_tokens']:,} | {summary['70B']['runtime_usage']['prompt_tokens']:,} |
| Completion tokens | {summary['8B']['runtime_usage']['completion_tokens']:,} | {summary['70B']['runtime_usage']['completion_tokens']:,} |
| Median recorded latency | {summary['8B']['runtime_usage']['median_latency_seconds']:.3f} s | {summary['70B']['runtime_usage']['median_latency_seconds']:.3f} s |
| Total logged latency | {summary['8B']['runtime_usage']['total_logged_latency_seconds']:.2f} s | {summary['70B']['runtime_usage']['total_logged_latency_seconds']:.2f} s |
| Theoretical API charges* | ${price8:.3f} | ${price70:.3f} |

* At listed Public AI rates as of 12 October 2026: 8B $0.10/$0.20 and 70B $0.82/$2.92 per million input/output tokens. Approximate full benchmark call charges are **${price8+price70:.3f}** before pilots, credits, retries, tax, rounding or billing adjustments. These are NOT an invoice or verified account charges.

## Conclusion appropriate for release

> In 39 synthetic case families (234 dossiers per model), Apertus v1.5 8B and 70B almost always refused to treat explicitly shared-origin reports as independent, with no demonstrated scaling advantage on baseline state agreement. Both nevertheless returned NO rather than UNKNOWN for every case where source lineage was deliberately left unspecified. EpiTrace therefore identifies a reproducible uncertainty-representation failure within a controlled benchmark, not a general failure of Apertus to recognize copied articles.

**Files:** `EpiTrace_Flagged_Observations_105.csv`, `EpiTrace_39_Seed_Paired_Review.csv`, `EpiTrace_Condition_Results.csv`, two diagnostic plots, original verified raw predictions and the original analysis are included in the release candidate. No API credentials are part of this output.
'''
(OUT/'EpiTrace_Independent_Methodological_Audit.md').write_text(report,encoding='utf-8')
print('CREATED',OUT)
print('FLAGS',len(rows),'categories',dict(flags_counter))
print('COST theoretical',round(price8+price70,4))
print('OUTPUT',[(p.name,p.stat().st_size) for p in OUT.iterdir()])
