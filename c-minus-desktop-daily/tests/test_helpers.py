"""Synthetic fixtures only; never capture, send, or load real configuration."""
import concurrent.futures, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
class Helpers(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.cfg={'output_dir':'data','runtime_dir':'runtime','timezone':'America/Los_Angeles','source_guild_id':'1','source_channel_id':'2','author_id':'3','destination_account':'fixture','destination_channel_id':'4','cdp_endpoint':'http://127.0.0.1:9232'}
        self.config=self.root/'config.json'; self.config.write_text(json.dumps(self.cfg))
        self.env={**os.environ,'C_MINUS_CONFIG':str(self.config),'PYTHONDONTWRITEBYTECODE':'1'}
    def run_script(self,name,*args,ok=True):
        r=subprocess.run([sys.executable,str(SCRIPTS/name),*args],env=self.env,text=True,capture_output=True)
        if ok:self.assertEqual(r.returncode,0,r.stderr)
        return r
    def msg(self,text,day='2025-01-07',hour='14',**kwargs):
        return {'id':str(len(text)),'author':{'id':'3'},'time':f'{day}T{hour}:00:00Z','content':text,'attachments':[],**kwargs}
    def full(self,day='2025-01-07'):
        return [self.msg(h+' '+('evidence '*60)+(' Overall close' if h=='Levels' else ''),day) for h in ['Macro Regime & Setup','Top Signals','Earnings Digest','Extra Alpha Playbook','Levels']]
    def assemble(self,rows):
        out=self.root/'data/2025-01-07';out.mkdir(parents=True,exist_ok=True)
        (out/'raw-fixture.json').write_text(json.dumps(rows)); (out/'capture-latest.json').write_text(json.dumps({'raw_file':'raw-fixture.json','captured_at':'fixture'}))
        result=json.loads(self.run_script('assemble.py','2025-01-07').stdout)
        p=out/'assembled-latest.json'
        return result,json.loads(p.read_text()) if p.exists() else None
    def test_full_baseline_versions_and_manual_preservation(self):
        out=self.root/'data/2025-01-07';out.mkdir(parents=True);(out/'report.json').write_text('manual')
        rows=self.full('2025-01-06')+self.full()+[self.msg('intraday news')]
        result,report=self.assemble(rows)
        self.assertTrue(result['complete']);self.assertEqual(result['baseline'],'2025-01-06');self.assertEqual(len(report['source_messages']),5)
        self.assertTrue(report['standard_five_sections_complete']);self.assertEqual((out/'report.json').read_text(),'manual')
        self.assemble(rows);self.assertEqual(len(list(out.glob('report-*.json'))),1)
        rows[6]['content']+=' edit';self.assemble(rows);self.assertEqual(len(list(out.glob('report-*.json'))),2)
    def test_short_complete_and_late_rejected(self):
        short=self.msg('keep this short $TEST '+ 'conditional level '*40+' Overall closing')
        result,report=self.assemble([short]);self.assertTrue(result['complete']);self.assertEqual(report['report_format'],'short_commentary');self.assertFalse(report['standard_five_sections_complete']);self.assertEqual(len(report['missing_sections']),5)
        # New capture without a valid opening yields no current result (old artifact must not be used).
        short['time']='2025-01-07T18:00:00Z';result,_=self.assemble([short]);self.assertFalse(result['complete'])
    def test_missing_closure_attachment_unknown_author(self):
        rows=self.full();rows[-1]['content']='Levels some levels';self.assertFalse(self.assemble(rows)[0]['complete'])
        rows=self.full();rows[-1]['attachments']=['https://example.invalid/attachment'];self.assertFalse(self.assemble(rows)[0]['complete'])
        rows=self.full()+[self.msg('unidentified',author=None)];result,report=self.assemble(rows);self.assertFalse(result['complete']);self.assertTrue(report['coverage_gaps'])
    def test_wrong_author_and_news_rejected(self):
        rows=self.full()
        for row in rows:row['author']={'id':'9'}
        self.assertFalse(self.assemble(rows)[0]['complete'])
        self.assertFalse(self.assemble([self.msg('brief update $TEST Overall')])[0]['complete'])
    def test_delivery_concurrency_reconciliation_and_receipts(self):
        self.assertEqual(json.loads(self.run_script('delivery.py','status','2025-01-07').stdout)['status'],'not_sent');self.assertFalse((self.root/'data').exists())
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results=list(pool.map(lambda _:self.run_script('delivery.py','claim','2025-01-07','fixture-hash',ok=False),range(6)))
        self.assertEqual(sum(r.returncode==0 for r in results),1)
        self.assertEqual(json.loads(self.run_script('delivery.py','status','2025-01-07').stdout)['status'],'pending')
        self.run_script('delivery.py','commit','2025-01-07','receipt-fixture');self.run_script('delivery.py','commit','2025-01-07','receipt-fixture')
        self.assertNotEqual(self.run_script('delivery.py','commit','2025-01-07','conflict',ok=False).returncode,0)
        self.assertNotEqual(self.run_script('delivery.py','claim','2025-01-07','new-hash',ok=False).returncode,0)
        self.assertEqual(json.loads(self.run_script('delivery.py','status','2025-01-07').stdout)['message_id'],'receipt-fixture')
    def test_invalid_config_dates_and_missing_claim(self):
        for day in ('../escape','2025-02-30'):
            self.assertNotEqual(self.run_script('delivery.py','status',day,ok=False).returncode,0)
        self.assertNotEqual(self.run_script('delivery.py','commit','2025-01-07','fixture',ok=False).returncode,0)
        self.cfg['destination_channel_id']='2';self.config.write_text(json.dumps(self.cfg))
        self.assertNotEqual(self.run_script('delivery.py','status','2025-01-07',ok=False).returncode,0)
if __name__=='__main__':unittest.main()
