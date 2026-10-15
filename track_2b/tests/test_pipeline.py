"""Offline validation using explicitly synthetic MOCK predictions, never model results."""
import sys,unittest,os,tempfile,threading,argparse,json
from http.server import BaseHTTPRequestHandler,HTTPServer
from unittest.mock import patch
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from validate import validate,load
from prompt import build_user_prompt,get_system_prompt
from run_benchmark import normalize,extract_json,run,call_model,prompt_hash,run_fingerprint,ModelMismatchError,check_model_access,USER_AGENT,model_route
from score import score,load_verified_model_records

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/epitrace_benchmark_public_v0.3.jsonl'
SEEDS=ROOT/'data/epitrace_seeds_public_v0.3.jsonl'
CASES=load(DATA)

def make_predictions(kind='perfect'):
    out=[]
    for x in CASES:
        pred={'epistemic_state':x['reference_epistemic_state'],'closure':x['reference_closure'],
            'claim_support_score':0.55,'evidence_independence':x['reference_independence'],'rationale':'Synthetic fixture, not Apertus.'}
        if kind=='always_no':pred['evidence_independence']='NO'
        if kind=='constant_state':
            pred['epistemic_state']='CONFIRMED';pred['closure']='YES'
        if kind=='inflate' and x['variant']=='repeat_5':pred['claim_support_score']=0.9
        out.append({'case_id':x['case_id'],'model':'MOCK-NOT-APERTUS','ok':True,'prediction':pred})
    return out

class TestEpiTrace(unittest.TestCase):
    def test_dataset(self):
        z=validate(DATA,SEEDS)
        self.assertEqual(z['cases'],234)
        self.assertEqual(z['seeds'],39)

    def test_prompt_hides_variant_and_gold(self):
        case=next(x for x in CASES if x['variant']=='repeat_3')
        p=build_user_prompt(case)
        self.assertNotIn('repeat_3',p)
        self.assertNotIn('reference_epistemic_state',p)
        self.assertNotIn(case['case_id'],p)
        self.assertNotIn('SAME REPORT REPEATED',p)
        self.assertNotEqual(get_system_prompt('neutral'),get_system_prompt('provenance_aware'))

    def test_clean_perfect_mock(self):
        z=score(CASES,make_predictions())
        for metric in ['base_state_accuracy','base_closure_accuracy','paired_state_invariance',
             'paired_closure_invariance','duplicated_sources_correct_no_independence',
             'unknown_lineage_correctly_unknown','independent_positive_control_accuracy',
             'full_seed_joint_pass_rate']:
            self.assertEqual(z[metric],1.0,metric)
        self.assertEqual(z['claim_support_inflation_gt_0.10_rate'],0.0)
        self.assertEqual(z['n_complete_6_variant_seeds'],39)

    def test_trivial_no_strategy_fails(self):
        z=score(CASES,make_predictions('always_no'))
        self.assertEqual(z['independent_positive_control_accuracy'],0.0)
        self.assertEqual(z['unknown_lineage_correctly_unknown'],0.0)
        self.assertEqual(z['full_seed_joint_pass_rate'],0.0)

    def test_consistently_wrong_state_does_not_win(self):
        z=score(CASES,make_predictions('constant_state'))
        self.assertEqual(z['paired_state_invariance'],1.0)
        self.assertLess(z['base_state_accuracy'],0.25)
        self.assertLess(z['full_seed_joint_pass_rate'],0.25)

    def test_inflation_rate_is_paired_only(self):
        z=score(CASES,make_predictions('inflate'))
        self.assertAlmostEqual(z['claim_support_inflation_gt_0.10_rate'],1/3,places=4)
        self.assertEqual(z['full_seed_joint_pass_rate'],0.0)

    def test_parser_rejects_missing_or_invalid_values(self):
        obj={'epistemic_state':'RUMOURED','closure':'NO','evidence_independence':'UNKNOWN','claim_support_score':.4}
        self.assertEqual(normalize(extract_json('```json\n'+__import__('json').dumps(obj)+'\n```'))['evidence_independence'],'UNKNOWN')
        with self.assertRaises(KeyError):normalize({'epistemic_state':'RUMOURED'})
        with self.assertRaises(ValueError):normalize(dict(obj,claim_support_score=2))
        with self.assertRaises(ValueError):normalize(dict(obj,epistemic_state='NOT_APPLICABLE',closure='YES'))

    def test_mock_http_end_to_end_is_not_a_model_experiment(self):
        # Exercise the complete runner against localhost only; no actual Apertus service.
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.server.last_request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                body={'choices':[{'message':{'content':json.dumps({'epistemic_state':'RUMOURED',
                    'closure':'NO','claim_support_score':0.2,'evidence_independence':'NO',
                    'rationale':'HTTP transport test, not a model.'})}}], 'usage':{'total_tokens':12},'model':'mock-HTTP-NOT-APERTUS'}
                b=json.dumps(body).encode()
                self.send_response(200);self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
            def log_message(self,*args):pass
        server=HTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with tempfile.TemporaryDirectory() as td:
                target=Path(td)/'fixture.jsonl'
                args=argparse.Namespace(data=str(DATA),model='mock-HTTP-NOT-APERTUS',protocol='neutral',
                    out=str(target),limit=1,sleep=0,timeout=5,max_attempts=1,dry_run=False,skip_model_preflight=True)
                with patch.dict(os.environ,{'LLM_API_KEY':'MOCK_KEY','LLM_BASE_URL':f'http://127.0.0.1:{server.server_port}/v1'}):
                    self.assertEqual(run(args),0)
                self.assertEqual(len(load(target)),1)
                self.assertEqual(load(target)[0]['model'],'mock-HTTP-NOT-APERTUS')
                self.assertEqual(server.last_request['model'],'mock-HTTP-NOT-APERTUS')
                self.assertNotIn('repeat_3',server.last_request['messages'][1]['content'])
        finally:
            server.shutdown();worker.join(2);server.server_close()

    def test_refuses_partial_silent_scoring(self):
        with self.assertRaises(ValueError):score(CASES,make_predictions()[:6])
        z=score(CASES,make_predictions()[:6],allow_partial=True)
        self.assertTrue(z['partial_run'])
        self.assertEqual(z['n_successful_cases'],6)

    def test_unknown_provenance_does_not_quote_single_publisher(self):
        for seed in sorted({x['seed_id'] for x in CASES}):
            orig=next(x for x in CASES if x['seed_id']==seed and x['variant']=='base')['input_text'].split('\n',1)[1]
            unknown=next(x for x in CASES if x['seed_id']==seed and x['variant']=='syndicated_unknown_5')['input_text']
            self.assertNotIn(orig,unknown)
            self.assertEqual(unknown.count('DOCUMENT '),5)

    def test_refuses_mismatched_served_model(self):
        case=CASES[0]
        reply={'model':'different-backend','choices':[{'message':{'content':'{"epistemic_state":"RUMOURED"}'}}]}
        response=Mock(status_code=200);response.json.return_value=reply
        session=Mock();session.post.return_value=response
        with self.assertRaises(ModelMismatchError):
            call_model(session,'https://example.invalid/v1','test-key','swiss-ai/Apertus-v1.5-8B',case,'neutral',1)

    def test_dry_run_never_requires_credentials(self):
        with tempfile.TemporaryDirectory() as td:
            args=argparse.Namespace(data=str(DATA),model='swiss-ai/Apertus-v1.5-8B',protocol='neutral',
                out=str(Path(td)/'nonexistent.jsonl'),limit=1,sleep=0,timeout=2,max_attempts=1,
                dry_run=True,skip_model_preflight=False)
            with patch.dict(os.environ,{'LLM_API_KEY':'','CSCS_INFERENCE_API_KEY':''}):
                self.assertEqual(run(args),0)
            self.assertFalse(Path(args.out).exists())

    def make_full_fingerprint_fixture(self,td,model='swiss-ai/Apertus-v1.5-8B'):
        z=validate(DATA,SEEDS)
        tag=run_fingerprint(model,'neutral',z['sha256'])
        rows=[]
        for p in make_predictions():
            p.update({'model':model,'served_model':model,'protocol':'neutral',
                      'run_id':tag,'dataset_sha256':z['sha256'],'prompt_sha256':prompt_hash()})
            rows.append(p)
        dest=Path(td)/'predictions.jsonl'
        dest.write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf-8')
        return dest,rows

    def test_strict_score_checks_dataset_and_prompt_hash(self):
        with tempfile.TemporaryDirectory() as td:
            dest,rows=self.make_full_fingerprint_fixture(td)
            ok,_,_=load_verified_model_records(dest,DATA)
            self.assertEqual(len(ok),234)
            rows[0]['dataset_sha256']='BAD-STALE-DATA'
            dest.write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'dataset hash mismatch'):
                load_verified_model_records(dest,DATA)
            rows[0]['dataset_sha256']=validate(DATA)['sha256']
            rows[0]['prompt_sha256']='BAD-STALE-PROMPT'
            dest.write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'prompt source hash mismatch'):
                load_verified_model_records(dest,DATA)

    def test_report_generator_is_not_creating_fake_data(self):
        from report_results import generate
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            # All fixtures exist in temp only; never packaged as model responses.
            a0,rows_a=self.make_full_fingerprint_fixture(td,'swiss-ai/Apertus-v1.5-8B')
            file_a=base/'mock_a.jsonl';file_a.write_bytes(a0.read_bytes())
            b0,rows_b=self.make_full_fingerprint_fixture(td,'swiss-ai/Apertus-v1.5-70B')
            file_b=base/'mock_b.jsonl';file_b.write_bytes(b0.read_bytes())
            out=base/'computed'
            stats=generate(DATA,file_a,file_b,out,bootstrap=60)
            self.assertEqual(stats['n_flagged_for_manual_review'],0)
            self.assertTrue((out/'RESULTS_SUMMARY.md').exists())
            self.assertEqual(len((out/'per_case_audit.csv').read_text().splitlines()),469)
            self.assertIn('<svg', (out/'model_comparison.svg').read_text())


    def test_publicai_model_aliases_are_distinct_provider_fingerprints(self):
        sha=validate(DATA,SEEDS)['sha256']
        c=run_fingerprint('swiss-ai/Apertus-v1.5-8B','neutral',sha,'https://api.inference.cscs.ch/v1')
        p=run_fingerprint('swiss-ai/apertus-v1.5-8b','neutral',sha,'https://api.publicai.co/v1')
        self.assertNotEqual(c,p)
        self.assertEqual(validate(DATA,SEEDS)['cases'],234)

    def test_publicai_user_agent_is_present_in_model_preflight_and_completions(self):
        model='swiss-ai/apertus-v1.5-8b'
        session=Mock()
        model_response=Mock(status_code=200)
        model_response.json.return_value={'data':[{'id':model}]}
        session.get.return_value=model_response
        check_model_access(session,'https://api.publicai.co/v1','fixture-key',model,5)
        self.assertEqual(session.get.call_args.kwargs['headers']['User-Agent'],USER_AGENT)
        message=json.dumps({'epistemic_state':'RUMOURED','closure':'NO',
                 'claim_support_score':0.2,'evidence_independence':'NO','rationale':'test'})
        response=Mock(status_code=200)
        response.json.return_value={'model':model,'choices':[{'message':{'content':message}}]}
        session.post.return_value=response
        raw,usage,status,served,fingerprint=call_model(session,'https://api.publicai.co/v1','fixture-key',model,CASES[0],'neutral',5)
        self.assertEqual(served,model)
        self.assertEqual(session.post.call_args.kwargs['headers']['User-Agent'],USER_AGENT)
        self.assertIn('epistemic_state',raw)

    def test_publicai_report_autodiscovery(self):
        from report_results import find_two_runs
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'apertus-v1.5-8b__neutral__ABC.jsonl'
            b=Path(td)/'apertus-v1.5-70b__neutral__DEF.jsonl'
            a.write_text('{}\n');b.write_text('{}\n')
            self.assertEqual(find_two_runs(Path(td),'neutral'),(a,b))

    def test_reject_cross_provider_comparison(self):
        from compare_models import compare
        with tempfile.TemporaryDirectory() as td:
            a,rows_a=self.make_full_fingerprint_fixture(td,'swiss-ai/Apertus-v1.5-8B')
            b,rows_b=self.make_full_fingerprint_fixture(td,'swiss-ai/Apertus-v1.5-70B')
            pa=Path(td)/'a.jsonl';pb=Path(td)/'b.jsonl'
            for row in rows_a:row['api_base']='https://api.inference.cscs.ch/v1'
            for row in rows_b:row['api_base']='https://api.publicai.co/v1'
            pa.write_text(''.join(json.dumps(x)+'\n' for x in rows_a))
            pb.write_text(''.join(json.dumps(x)+'\n' for x in rows_b))
            with self.assertRaisesRegex(ValueError,'same serving provider'):
                compare(DATA,pa,pb,bootstrap=20)


    def test_publicai_report_generator_accepts_lowercase_model_ids(self):
        from report_results import generate
        with tempfile.TemporaryDirectory() as td:
            pa,rows_a=self.make_full_fingerprint_fixture(td,'swiss-ai/apertus-v1.5-8b')
            pb,rows_b=self.make_full_fingerprint_fixture(td,'swiss-ai/apertus-v1.5-70b')
            a=Path(td)/'a.jsonl';b=Path(td)/'b.jsonl'
            a.write_text(''.join(json.dumps(x)+'\n' for x in rows_a))
            b.write_text(''.join(json.dumps(x)+'\n' for x in rows_b))
            z=generate(DATA,a,b,Path(td)/'report',bootstrap=20)
            self.assertEqual(z['model_a'],'swiss-ai/apertus-v1.5-8b')
            self.assertEqual(z['model_b'],'swiss-ai/apertus-v1.5-70b')

    def test_hf_router_requires_pinned_provider_and_canonical_model(self):
        self.assertEqual(model_route('swiss-ai/Apertus-v1.5-8B:publicai','https://router.huggingface.co/v1'),
                         ('swiss-ai/Apertus-v1.5-8B','publicai'))
        with self.assertRaises(ValueError):
            model_route('swiss-ai/Apertus-v1.5-8B','https://router.huggingface.co/v1')
        with self.assertRaises(ValueError):
            model_route('swiss-ai/Apertus-v1.5-8B:publicai','https://api.inference.cscs.ch/v1')

    def test_hf_preflight_checks_live_provider(self):
        model='swiss-ai/Apertus-v1.5-8B:publicai'
        session=Mock()
        reply=Mock(status_code=200)
        reply.json.return_value={'data':[{'id':'swiss-ai/Apertus-v1.5-8B',
                                 'providers':[{'provider':'publicai','status':'live'},
                                              {'provider':'another','status':'unavailable'}]}]}
        session.get.return_value=reply
        check_model_access(session,'https://router.huggingface.co/v1','LOCAL_MOCK_KEY',model,5)
        reply.json.return_value={'data':[{'id':'swiss-ai/Apertus-v1.5-8B',
                                 'providers':[{'provider':'publicai','status':'offline'}]}]}
        with self.assertRaisesRegex(ModelMismatchError,'not live'):
            check_model_access(session,'https://router.huggingface.co/v1','LOCAL_MOCK_KEY',model,5)
        reply.json.return_value={'data':[{'id':'OTHER/model','providers':[]}]}
        with self.assertRaisesRegex(ModelMismatchError,'absent from /models'):
            check_model_access(session,'https://router.huggingface.co/v1','LOCAL_MOCK_KEY',model,5)

    def test_hf_api_reply_can_omit_provider_suffix_not_change_model(self):
        response=Mock(status_code=200)
        response.json.return_value={'model':'swiss-ai/Apertus-v1.5-8B',
            'choices':[{'message':{'content':'{"epistemic_state":"RUMOURED"}'}}]}
        session=Mock();session.post.return_value=response
        r=call_model(session,'https://router.huggingface.co/v1','MOCK_TOKEN',
                     'swiss-ai/Apertus-v1.5-8B:publicai',CASES[0],'neutral',5)
        self.assertEqual(r[3],'swiss-ai/Apertus-v1.5-8B')
        self.assertEqual(session.post.call_args.kwargs['json']['model'],'swiss-ai/Apertus-v1.5-8B:publicai')
        response.json.return_value['model']='swiss-ai/Apertus-v1.5-70B'
        with self.assertRaises(ModelMismatchError):
            call_model(session,'https://router.huggingface.co/v1','MOCK_TOKEN',
                       'swiss-ai/Apertus-v1.5-8B:publicai',CASES[0],'neutral',5)

    def make_hf_fixture(self,td,model):
        base='https://router.huggingface.co/v1'
        sha=validate(DATA,SEEDS)['sha256']
        rid=run_fingerprint(model,'neutral',sha,base)
        canonical,provider=model_route(model,base)
        rows=[]
        for p in make_predictions():
            p.update({'model':model,'served_model':canonical,'requested_provider':provider,
                      'api_base':base,'protocol':'neutral','run_id':rid,
                      'dataset_sha256':sha,'prompt_sha256':prompt_hash()})
            rows.append(p)
        destination=Path(td)/(model.rsplit('/',1)[-1].replace(':','_')+'.jsonl')
        destination.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        return destination,rows

    def test_hf_validates_and_compares_pinned_backend(self):
        from compare_models import compare
        with tempfile.TemporaryDirectory() as td:
            a,_=self.make_hf_fixture(td,'swiss-ai/Apertus-v1.5-8B:publicai')
            b,rows=self.make_hf_fixture(td,'swiss-ai/Apertus-v1.5-70B:publicai')
            self.assertEqual(len(load_verified_model_records(a,DATA)[0]),234)
            result=compare(DATA,a,b,bootstrap=20)
            self.assertEqual(result['backend_provider'],'publicai')
            for r in rows:
                r['model']='swiss-ai/Apertus-v1.5-70B:featherless-ai'
                r['requested_provider']='featherless-ai'
                r['run_id']=run_fingerprint(r['model'],'neutral',validate(DATA,SEEDS)['sha256'],'https://router.huggingface.co/v1')
            b.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            with self.assertRaisesRegex(ValueError,'same HF backend provider'):
                compare(DATA,a,b,bootstrap=10)
            rows[0]['requested_provider']='publicai'
            b.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            with self.assertRaisesRegex(ValueError,'HF provider provenance'):
                load_verified_model_records(b,DATA)

    def test_hf_autodiscovery_suffix_and_same_data_freeze(self):
        from report_results import find_two_runs
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'Apertus-v1.5-8B_publicai__neutral__AAA.jsonl'
            b=Path(td)/'Apertus-v1.5-70B_publicai__neutral__BBB.jsonl'
            a.write_text('{}\n');b.write_text('{}\n')
            self.assertEqual(find_two_runs(Path(td),'neutral'),(a,b))
            self.assertEqual(validate(DATA,SEEDS)['sha256'],'eec19b80367947138a54b9b3e5188a6ccc70811bf722ca3a6eb275d53f574900')

    def test_hf_report_export_and_release_safety(self):
        from report_results import generate
        from release_check import check
        with tempfile.TemporaryDirectory() as td:
            a,_=self.make_hf_fixture(td,'swiss-ai/Apertus-v1.5-8B:publicai')
            b,_=self.make_hf_fixture(td,'swiss-ai/Apertus-v1.5-70B:publicai')
            z=generate(DATA,a,b,Path(td)/'analysis',bootstrap=20)
            self.assertEqual(z['model_a'],'swiss-ai/Apertus-v1.5-8B:publicai')
            self.assertEqual(z['model_b'],'swiss-ai/Apertus-v1.5-70B:publicai')
            self.assertTrue((Path(td)/'analysis'/'RESULTS_SUMMARY.md').is_file())
            self.assertEqual(check()['dataset_sha256'],'eec19b80367947138a54b9b3e5188a6ccc70811bf722ca3a6eb275d53f574900')

if __name__=='__main__':unittest.main()
