"""Deterministically build controlled synthetic dossiers from the 39 public seeds.

This generator deliberately DOES NOT read or reproduce private historical annotations.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

VARIANTS = ["base", "repeat_3", "repeat_5", "syndicated_linked_5", "syndicated_unknown_5", "independent_3"]
INDEPENDENCE = {"base":"NO", "repeat_3":"NO", "repeat_5":"NO", "syndicated_linked_5":"NO", "syndicated_unknown_5":"UNKNOWN", "independent_3":"YES"}
PAPERS = ["Alderwick Herald", "Briar Ledger", "Crescent Dispatch", "Vale Register", "Southern Sentinel"]


def archival_ref(seed):
    return 'RS-' + hashlib.sha256((seed['seed_id'] + '|epitrace-source').encode()).hexdigest()[:7].upper()


def unknown_clips(seed):
    """Different anonymous news briefs sharing a proposition, without traceable origins.

    No named shared publisher, reporter, dispatch code or common provenance is supplied.
    They are *not* proof of independence; we also do not assert that they are copies.
    """
    claim=seed['claim']
    sentences=[
       f"A brief unsigned report says that {claim}. This copy has no attribution field.",
       f"A news note describes a report concerning whether {claim}. Its source column is blank.",
       f"In a separate printed notice the claim is that {claim}. No reporter is credited.",
       f"The issue carries an unverified account according to which {claim}; no source is named.",
       f"A short city-column item mentions that {claim}. The archive provides no information about how this news reached the paper.",
    ]
    return '\n\n'.join(f"DOCUMENT {i} | {PAPERS[i-1]}\n{t}" for i,t in enumerate(sentences,1))


def linked_clips(seed):
    source=archival_ref(seed)
    excerpt=seed['excerpt']
    headers=[f"Archive credit: Regional Report Service, bulletin {source}",
             f"Desk credit: RRS / {source}",
             f"Attribution on the print: Regional Report Service - {source}",
             f"Catalogue credit: RRS bulletin {source}",
             f"Source line: wire bulletin {source} (RRS)"]
    return '\n\n'.join(f"DOCUMENT {i} | {PAPERS[i-1]}\n{excerpt}\n{headers[i-1]}"
                        for i in range(1,6))


def independent_clips(seed):
    claim=seed['claim']
    return ("DOCUMENT 1 | Press clipping\n" + seed['excerpt'] +
            "\n\nDOCUMENT 2 | Inspector Mira Vale's signed field notebook (kept by the district office)\n"
            f"Entry: I personally inspected the site and recorded that {claim}. This inspection took place before the paper's report was obtained."
            "\n\nDOCUMENT 3 | Caretaker Jonas Bell's work diary (separately maintained at the premises)\n"
            f"Entry: My own observation was that {claim}. The diary entry was made without access to the inspector's notebook or the newspaper clipping.")


def transform(seed,variant):
    e=seed['excerpt']
    if variant == 'base':return 'DOCUMENT 1 | Local newspaper excerpt\n' + e
    if variant in ('repeat_3','repeat_5'):
        copies=3 if variant=='repeat_3' else 5
        return '\n\n'.join(f'DOCUMENT {i} | Archived excerpt\n{e}' for i in range(1,copies+1))
    if variant=='syndicated_linked_5':return linked_clips(seed)
    if variant=='syndicated_unknown_5':return unknown_clips(seed)
    if variant=='independent_3':return independent_clips(seed)
    raise ValueError(variant)


def build(seeds):
    assert len(seeds)==39
    assert len({s['seed_id'] for s in seeds})==39
    out=[]
    for seed in seeds:
        assert seed['synthetic'] is True
        assert seed['content_origin'].startswith('original synthetic text')
        for variant in VARIANTS:
            out.append({'case_id':f"{seed['seed_id']}__{variant}",
                        'seed_id':seed['seed_id'],'variant':variant,
                        'date':seed['date'],'claim':seed['claim'],'input_text':transform(seed,variant),
                        'reference_epistemic_state':seed['reference_epistemic_state'],
                        'reference_closure':seed['reference_closure'],
                        'reference_independence':INDEPENDENCE[variant],
                        'invariance_expected':variant in ('base','repeat_3','repeat_5','syndicated_linked_5'),
                        'synthetic':True})
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',default='data/epitrace_seeds_public_v0.3.jsonl')
    parser.add_argument('--out',default='data/epitrace_benchmark_public_v0.3.jsonl')
    parser.add_argument('--metadata',default='data/epitrace_public_metadata_v0.3.csv')
    args=parser.parse_args()
    seeds=[json.loads(s) for s in Path(args.seeds).read_text(encoding='utf-8').splitlines() if s.strip()]
    rows=build(seeds)
    out=Path(args.out);out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows),encoding='utf-8')
    with Path(args.metadata).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['case_id','seed_id','variant','synthetic','license','original_source','reference_basis','source_count_reference'])
        w.writeheader()
        for row in rows:
            w.writerow({'case_id':row['case_id'],'seed_id':row['seed_id'],'variant':row['variant'],
                        'synthetic':'true','license':'CDLA-Permissive-2.0',
                        'original_source':'original fictional vignette, not real archive',
                        'reference_basis':'author-constructed conditions, not human gold',
                        'source_count_reference':'1' if row['reference_independence']=='NO' else ('at least 3' if row['reference_independence']=='YES' else 'unknown')})
    sha=hashlib.sha256(out.read_bytes()).hexdigest()
    print(json.dumps({'cases':len(rows),'seeds':len(seeds),'data_sha256':sha,'out':str(out)},indent=2))

if __name__=='__main__':main()
