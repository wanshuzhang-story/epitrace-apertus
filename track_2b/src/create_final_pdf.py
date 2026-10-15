from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, HRFlowable
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from xml.sax.saxutils import escape

TRACK=Path(__file__).resolve().parents[1]
ROOT=TRACK/'results/analysis'
A=json.loads((ROOT/'model_a_summary.json').read_text())
B=json.loads((ROOT/'model_b_summary.json').read_text())
C=json.loads((ROOT/'paired_comparison.json').read_text())
X=json.loads((ROOT/'EpiTrace_Independent_Audit_Stats.json').read_text())
OUT=TRACK/'EpiTrace_Report_v0.5.pdf'
NAVY=colors.HexColor('#172A3C');TEAL=colors.HexColor('#087E83'); GREY=colors.HexColor('#566579');BG=colors.HexColor('#EFF5F5'); BORDER=colors.HexColor('#D9E1E5');BLACK=colors.HexColor('#26384A');AMBER=colors.HexColor('#A05C12')
styles={
 'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=23,leading=28,spaceAfter=8,textColor=NAVY),
 'subtitle':ParagraphStyle('subtitle',fontName='Helvetica',fontSize=13,leading=16,spaceAfter=10,textColor=TEAL),
 'header':ParagraphStyle('header',fontName='Helvetica-Bold',fontSize=13,leading=16.5,spaceBefore=14,spaceAfter=8,keepWithNext=True,textColor=NAVY),
 'subheader':ParagraphStyle('subheader',fontName='Helvetica-Bold',fontSize=10.5,leading=13,spaceBefore=11,spaceAfter=6,keepWithNext=True,textColor=TEAL),
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10.0,leading=14.6,spaceAfter=8,textColor=BLACK),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8.9,leading=12.4,spaceAfter=6,textColor=BLACK),
 'tiny':ParagraphStyle('tiny',fontName='Helvetica',fontSize=8.0,leading=10.5,spaceAfter=3,textColor=BLACK),
 'headcell':ParagraphStyle('headcell',fontName='Helvetica-Bold',fontSize=8.5,leading=11,textColor=NAVY),
 'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=8.4,leading=11.2,textColor=BLACK),
 'metric':ParagraphStyle('metric',fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=TEAL,alignment=TA_CENTER),
 'metriclabel':ParagraphStyle('metriclabel',fontName='Helvetica',fontSize=7.3,leading=9,textColor=BLACK,alignment=TA_CENTER),
 'note':ParagraphStyle('note',fontName='Helvetica-Oblique',fontSize=8.4,leading=12.2,spaceAfter=7,textColor=GREY),
}

def P(s,style='body'):return Paragraph(s,styles[style])

def T(head,rows,widths,pad=6):
 data=[[P(str(s),'headcell') for s in head]]
 data+= [[P(str(s),'cell') for s in r] for r in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BG),('TEXTCOLOR',(0,0),(-1,0),NAVY),('LINEBELOW',(0,0),(-1,0),.8,TEAL),('LINEBELOW',(0,1),(-1,-1),.32,BORDER),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#FAFCFC')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 return t

def metric(key):
 x=C['differences_b_minus_a'][key];lo,hi=x['paired_seed_bootstrap_95ci'];return f'{100*A[key]:.1f}%',f'{100*B[key]:.1f}%',f'{100*x["difference"]:+.1f} pp [{100*lo:+.1f},{100*hi:+.1f}]'

def band_metrics(items):
 cells=[[P(v,'metric') for v,k in items],[P(k,'metriclabel') for v,k in items]]
 n=len(items);tab=Table(cells,colWidths=[505/n]*n)
 tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),BG),('TOPPADDING',(0,0),(-1,0),11),('BOTTOMPADDING',(0,1),(-1,1),11),('ALIGN',(0,0),(-1,-1),'CENTER'),('LINEBEFORE',(1,0),(-1,-1),.5,BORDER)]))
 return tab

def foot(canvas,doc):
 w,h=A4;canvas.saveState()
 canvas.setFillColor(NAVY);canvas.rect(0,h-7,w,7,fill=1,stroke=0)
 canvas.setStrokeColor(BORDER);canvas.setLineWidth(.6);canvas.line(45,34,w-45,34)
 canvas.setFillColor(GREY);canvas.setFont('Helvetica',7.1)
 canvas.drawString(45,22,'EpiTrace | Hack Apertus 2026 Track 2B | Actual Apertus results, 15 Oct 2026')
 canvas.drawRightString(w-45,22,f'Page {doc.page}')
 canvas.restoreState()

story=[]
# PAGE 1
story.extend([
 P('EpiTrace','title'),P('Epistemic Integrity Under Repetition','subtitle'),
 P('<b>Hack Apertus 2026 | Track 2B: Own Project</b> &nbsp;&nbsp; Models: Apertus v1.5 8B and 70B &nbsp;&nbsp; Data: original synthetic, non-historical','small'),
 band_metrics([('39','independent seed families'),('234','dossiers per model'),('468','verified model responses'),('105','diagnostic review flags')]),Spacer(1,12),
 P('1. Core problem and actual answer','header'),
 P('Does repeating a report make a language model confuse frequency of publication with independent corroboration? We evaluate the epistemic interpretation of report collections, not whether a fictional event actually occurred. The benchmark treats duplicated, syndicated, untraceable and independently authored accounts separately.'),
 P('<b>Main finding.</b> Both models recognized clearly duplicated evidence in almost all known-copy trials (232/234 correct NO decisions in aggregate). However, both labeled <b>all 78 unknown-lineage observations as NO</b> rather than UNKNOWN. Larger model size produced no baseline state-agreement gain (21/39 for each model). The weakness identified is not generalized gullibility under repetition; it is failure to represent <b>unresolved provenance</b> on this synthetic test.'),
 P('2. Working system and design','header'),
 P('The prototype constructs 234 evaluation dossiers from 39 original fictional newspaper-style seeds. Each dossier is sent through a JSON-only prompt to Apertus v1.5; responses are normalized, fingerprinted and scored. A case-level audit and seed-paired bootstrap compare both model sizes. The raw responses and reproducing scripts accompany this report.'),
 T(['Condition','N per model','Expected source relation','State invariance expected'],[
   ('Single fictional excerpt','39','NO (one recorded origin)','Baseline'),
   ('Identical report x3 / x5','78','NO (same evidence)','Yes'),
   ('Five linked clippings','39','NO (same credited dispatch)','Yes'),
   ('Five unsigned, unknown-origin briefs','39','UNKNOWN','Not required'),
   ('Press + 2 independent records','39','YES','Not required')],[185,68,137,115]),Spacer(1,7),
 P('The unknown-origin treatment alters how evidence is presented and therefore is evaluated on the independence label, not baseline-state invariance. Independent witnesses add new information and may legitimately change event state or closure.','note'),
 PageBreak()
])
# PAGE 2
story.extend([
 P('3. Evaluation protocol and integrity checks','header'),
 P('The model returns: <b>epistemic_state</b> (8 classes), <b>closure</b> (4 classes), <b>claim_support_score</b> (0-1 elicited event support), <b>evidence_independence</b> (YES / NO / UNKNOWN) and a brief rationale. The neutral system instruction provides definitions of these labels but no per-case reference labels. Conditions and case IDs are withheld.'),
 P('Each model received the same data and prompt with <b>temperature = 0</b> and <b>max_tokens = 350</b>. The Public AI API returned its exact served model name and vLLM fingerprint. Inference ran on 14 October 2026 at <b>https://api.publicai.co/v1</b>; it was not a CSCS-run or Swiss-residency test.'),
 P('The reference labels are construction labels, not human-adjudicated historical truth. 39 seeds span 8 labels: 7 RUMOURED; 5 each TENTATIVE, PROBABLE, CONFIRMED, CONTESTED, REJECTED and SETTLED; 2 NOT_APPLICABLE. The dataset SHA-256 is below; the prompts have a separate frozen hash.','small'),
 P(f'<b>Dataset:</b> <font face="Courier" size="7">{C["dataset_sha256"]}</font>','tiny'),
 P(f'<b>Prompt:</b> <font face="Courier" size="7">{C["prompt_sha256"]}</font>','tiny'),
 P('4. Diagnostics by reference label','header'),
 Image(str(ROOT/'EpiTrace_Figure2_StateAgreement.png'),width=480,height=220),
 P('The reference-state mismatches are structured rather than random: both models label all 5 PROBABLE seeds as TENTATIVE, all 5 SETTLED seeds as a less final state, and both NOT_APPLICABLE cases as factual assessments. Such disagreements may reflect rubric interpretation and require expert validation.','small'),
 P('Statistical method','subheader'),
 P('Because each seed produces six dependent variants, the independent resampling unit is <b>39 seed families</b>. We report a Wilson interval for baseline state agreement (both models: 38.6%-68.4%) and 5,000 seed-paired bootstrap draws for differences. These intervals describe uncertainty within the constructed families, not generalization to real-world news.'),
 P('Verification','subheader'),
 P('All 234 case IDs per model were unique and successful. Both served IDs match their requested Apertus variants. The `make smoke` suite passed 25 offline tests; `make report` independently reconstructed 105 flags and the paired comparisons. No additional inference was required for this audit.','small'),
 PageBreak()
])
# PAGE 3
head=['Pre-specified metric','Apertus 8B','Apertus 70B','70B minus 8B [95% CI]']
rows=[]
for label,key in [
 ('Baseline state agreement (39)','base_state_accuracy'),('Known-copy state invariant (117)','paired_state_invariance'),('Known-copy closure invariant (117)','paired_closure_invariance'),('Known-copy correctly NO (117)','duplicated_sources_correct_no_independence'),('Unknown-lineage correctly UNKNOWN (39)','unknown_lineage_correctly_unknown'),('Independent-origin correctly YES (39)','independent_positive_control_accuracy'),('Support inflation > 0.10 (117; lower better)','claim_support_inflation_gt_0.10_rate'),('All-criteria joint pass (39)','full_seed_joint_pass_rate')]:
 rows.append((label,*metric(key)))
story.extend([
 P('5. Verified Apertus results','header'),
 T(head,rows,[198,76,76,155],pad=5),Spacer(1,5),
 P('Paired intervals overlap zero for every model-size difference. The zero full-seed joint score is mechanically driven by the UNKNOWN failure and is not useful as a standalone ranking. The support-inflation threshold is an arbitrary diagnostic cut-off, not a calibrated probabilistic criterion.','note'),
 Image(str(ROOT/'EpiTrace_Figure1_Independence.png'),width=493,height=259),
 P('Figure. The benchmark expects NO for one-source and known-copy conditions, UNKNOWN for untraceable origin, and YES only when independent origins are documented. Prediction classes are shown, not ground-truth event outcomes.','small'),
 P('<b>Interpretation:</b> 8B correctly classified all 117 known-copy independence conditions; 70B missed two repetitions of the same published retraction. In contrast, both models produced NO on all 39 unknown-origin conditions. These are separable behaviors: competent recognition of visible duplication, paired with overconfident denial when lineage is untraceable.','small'),
 PageBreak()
])
# PAGE 4
story.extend([
 P('6. Error analysis: 105 flagged observations','header'),
 P('An automated flag is not automatically a validated model error. The flags are model-case observations; several share the same constructed seed or underlying issue.'),
 T(['Flag category','Count','Assessment'],[
   ('Unknown-origin classified NO','78','Central, systematic three-class rubric failure: 39 per model.'),
   ('Base excerpt classified YES / UNKNOWN','22','10 from 8B; 12 from 70B. Official documents and verification cues complicate adjudication.'),
   ('Known copies classified YES','2','70B, PUB029 x3 and x5: repeated corrections mistaken for independent evidence.'),
   ('Dependent-copy support increase >0.10','3','8B PUB037 x3/x5; 70B PUB018 x5. Both increases 0.75 to 0.95.')],[190,45,270]),Spacer(1,6),
 P('Key case 1 - PUB001__syndicated_unknown_5','subheader'),
 P('Five unsigned briefs appear in five newspapers, with blank source fields or uncredited reporters. Both models output NO; their rationales note that no independent confirmation is documented. That is insufficient to establish a <i>single shared origin</i>. The author-reference label is UNKNOWN. This exemplifies the danger of equating <i>not demonstrated independent</i> with <i>demonstrated dependent</i>.'),
 P('Key case 2 - PUB029__repeat_3 and __repeat_5','subheader'),
 P('The same newspaper retracts a false theft report; 70B outputs YES on both duplicated variants. Its explanation appears to treat multiple copies of a correction as reinforcement. The two copies introduce no new underlying source, so these are clear errors within EpiTrace\'s stated rule.'),
 P('Key case 3 - PUB021__base','subheader'),
 P('A single newspaper reports a signed bridge-closure order. Both models output YES although the author-defined single-excerpt reference is NO. A cited primary document may be viewed as evidentiary verification rather than an independent publication. This illustrates a <b>construct-validity and annotation issue</b> requiring independent human review before treating the flag as proven error.'),
 P('Key case 4 - PUB037 and PUB018','subheader'),
 P('Support scores rise from 0.75 to 0.95 on exact copied materials even though independence stays NO (8B at PUB037 x3/x5; 70B at PUB018 x5). The models can identify copies correctly while still inflating an elicited support score. This score is not a calibrated probability.'),
 P('Secondary result - classification semantics','subheader'),
 P('Both models systematically downgrade PROBABLE and SETTLED presentations; neither reliably recognizes the deliberately non-factual figurative or advertising cases. These reflect presentation-level state interpretation, not necessarily source-independence reasoning.','small'),
 PageBreak()
])
# PAGE 5
money=X['estimated_api_billing_usd_excluding_pilot']
story.extend([
 P('7. Resource use, operational value, and limitations','header'),
 T(['Measured / estimated item','Apertus 8B','Apertus 70B'],[
  ('Prompt tokens, logged',f"{A['runtime_usage']['prompt_tokens']:,}",f"{B['runtime_usage']['prompt_tokens']:,}"),
  ('Completion tokens, logged',f"{A['runtime_usage']['completion_tokens']:,}",f"{B['runtime_usage']['completion_tokens']:,}"),
  ('Median recorded latency, seconds',f"{A['runtime_usage']['median_latency_seconds']:.3f}",f"{B['runtime_usage']['median_latency_seconds']:.3f}"),
  ('Sum of recorded latency, seconds',f"{A['runtime_usage']['total_logged_latency_seconds']:.2f}",f"{B['runtime_usage']['total_logged_latency_seconds']:.2f}"),
  ('Token-tariff estimate, USD*',f"${money['8b']:.4f}",f"${money['70b']:.4f}")],[255,125,125]),Spacer(1,6),
 P(f'* Based on Public AI listed rates of $0.10/$0.20 (8B) and $0.82/$2.92 (70B) per million input/output tokens on 12 October 2026. Estimated model-call total: <b>${money["both"]:.4f}</b>; not a verified invoice. Excludes six pilot calls, taxes, provider rounding and any separate charges. Hardware and server load differ; latency is not evidence that 70B scales faster.','note'),
 P('Value and scope','subheader'),
 P('EpiTrace is a low-cost, reproducible diagnostic for document-analysis systems: a downstream workflow can avoid converting repeated publication into independent corroboration, and can preserve UNKNOWN when provenance is unavailable. It uses a <1 MB public synthetic benchmark, simple Python dependencies, a Docker client and an OpenAI-compatible API. Future production use requires human-reviewed source graphs and more varied templates.'),
 P('Interpretive and deployment limitations','subheader'),
 P('<b>Construct validity:</b> All 39 fictional seeds, the dependence relation and epistemic-state labels were authored for this test without blind annotators. The independent controls explicitly assert separate firsthand origin and are relatively easy. Even the neutral prompt explains YES/NO/UNKNOWN. The 39 unknown variants share the same textual template; neither 0/39 nor 39/39 can be projected to unseen corpora.'),
 P('<b>Calibration and repeatability:</b> The 0-1 score is an elicited rating, not a calibrated posterior. Each model was evaluated once at requested temperature zero; stochasticity and backend serving conditions were not sampled. Bootstrap confidence limits only reflect between-seed variation in this selected test set.'),
 P('<b>Sovereignty:</b> The Apertus model weights are open and Swiss-developed, but actual inference was served by Public AI. The report does not claim Swiss-hosted data, air-gapped inference or successful Swiss on-premise deployment. The submitted Docker entry point now replays the original results without remote API access; Docker was not available for independent local testing.'),
 P('8. Reproduction and release readiness','header'),
 P('Full logs, structured output and a case-level audit are included in the submission candidate. From the repository root, <b><font face="Courier">make smoke</font></b> checks the code and dataset; <b><font face="Courier">make replay</font></b> rescored the 468 provided responses offline; <b><font face="Courier">make run</font></b> replays saved model data in Docker without any API key; new live inference requires <b><font face="Courier">make run-live</font></b> and LLM_NAME, LLM_BASE_URL, LLM_API_KEY. No API key is included. Code: Apache-2.0; docs: CC BY 4.0; synthetic dataset: CDLA-Permissive-2.0.'),
 P('<b>Submission status as of 15 Oct 2026:</b> Empirical report prepared; public GitHub publication, judge-side Docker test and official submission remain participant actions. A preview demonstration video is provided with this package. Public release requires author approval.','note'),
 PageBreak()
])
# PAGE 6 REFS
story.extend([
 P('References / public documentation','header'),
 P('References are separated from the five-page technical report body.' ,'small'),Spacer(1,12),
 P('1. Hack Apertus (2026). <i>Online Hackathon: Tracks 1 and 2, 1-16 October 2026.</i> <link href="https://hackapertus.ch/online-hack" color="#087E83">https://hackapertus.ch/online-hack</link>.'),
 P('2. Hack Apertus (2026). <i>Hack Apertus project template</i> (Track 2B directory structure, Docker make run, environment variable convention). <link href="https://github.com/HackApertus/project-template" color="#087E83">https://github.com/HackApertus/project-template</link>.'),
 P('3. Hack Apertus (2026). <i>Terms and conditions</i> (public release and licensing). <link href="https://hackapertus.ch/terms-and-conditions" color="#087E83">https://hackapertus.ch/terms-and-conditions</link>.'),
 P('4. Public AI (2026). <i>Available models</i> (Apertus 1.5 8B/70B names and published input/output token tariffs; page modified 12 October 2026). <link href="https://platform.publicai.co/models" color="#087E83">https://platform.publicai.co/models</link>.'),
 P('5. Public AI (2026). <i>Developer portal</i> (OpenAI-compatible chat completions and key requirements). <link href="https://platform.publicai.co/docs" color="#087E83">https://platform.publicai.co/docs</link>.'),
 P('6. EpiTrace (2026). <i>Original synthetic benchmark</i>, `epitrace_benchmark_public_v0.3.jsonl` and deterministic builder, included in this repository; SHA-256 '+C['dataset_sha256']+'.'),
 P('7. EpiTrace (2026). <i>Actual model logs and derived analysis</i>, two complete 234-case JSONL response files, `paired_comparison.json`, `per_case_audit.csv`, `model_a_summary.json`, `model_b_summary.json`, plus independent review appendix, included in the release candidate.'),
 Spacer(1,16),HRFlowable(width='100%',color=BORDER,thickness=.6),Spacer(1,10),
 P('Data governance: No historical Livingstone quotations or private research-derived annotations are included in the release candidate. All experiment vignettes are deliberately fictitious. EpiTrace does not measure the factual truth of historical events.','note')
])

D=SimpleDocTemplate(str(OUT),pagesize=A4,topMargin=41,bottomMargin=45,leftMargin=45,rightMargin=45,title='EpiTrace - Actual-results technical report v0.5',author='EpiTrace',subject='Hack Apertus Track 2B real Apertus evaluation')
D.build(story,onFirstPage=foot,onLaterPages=foot)
print('PDF',OUT)
