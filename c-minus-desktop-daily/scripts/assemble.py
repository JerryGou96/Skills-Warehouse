#!/usr/bin/env python3
"""Assemble evidence only; never send or infer completed trades."""
import json, hashlib, re, sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from config import load_config, valid_date
cfg=load_config(); ROOT=Path(cfg['output_dir'])
date=sys.argv[1] if len(sys.argv)>1 else datetime.now(ZoneInfo(cfg['timezone'])).date().isoformat()
valid_date(date)
out=ROOT/date
meta=json.loads((out/'capture-latest.json').read_text());raw=json.loads((out/meta['raw_file']).read_text())
heads=['Macro Regime & Setup','Top Signals','Earnings Digest','Extra Alpha Playbook','Levels']
bydate={}
for m in raw:
 if (m.get('author') or {}).get('id')!=cfg['author_id'] or not m.get('time'):continue
 d=datetime.fromisoformat(m['time'].replace('Z','+00:00')).astimezone(ZoneInfo(cfg['timezone'])).date().isoformat()
 bydate.setdefault(d,[]).append(m)
reports=[]
unknown_authors=any(not (m.get('author') or {}).get('id') for m in raw)
for d,messages in sorted(bydate.items()):
 current=None;sections={};selected=[];closed=False;report_format='five_section'
 short_intro=re.compile(r"(?:keep (?:this|it) short|short (?:post|update|comment)|brief (?:post|update))",re.I)
 for m in messages:
  text=m.get('content') or ''
  heading=next((h for h in heads if h.lower() in text[:100].lower()),None)
  if heading:
   if heading==heads[0] and selected:break
   current=heading
  if not current and short_intro.search(text[:500]) and len(text)>500 and '$' in text:
   local=datetime.fromisoformat(m['time'].replace('Z','+00:00')).astimezone(ZoneInfo(cfg['timezone']))
   if local.hour<9:current='Short Commentary';report_format='short_commentary'
  if not current:continue
  if closed:break
  sections.setdefault(current,[]).append(m);selected.append(m)
  if current in ('Levels','Short Commentary') and re.search(r'\bOverall\b',text,re.I) and len(text)>400:closed=True
 missing=[h for h in heads if h not in sections]
 complete=not unknown_authors and (not missing or report_format=='short_commentary') and closed and not any(m.get('attachments') for m in selected)
 digest=hashlib.sha256(json.dumps(selected,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 report={'report_date':d,'timezone':cfg['timezone'],'author_id':cfg['author_id'],'source_messages':selected,'sections':sections,'content_hash':digest,'complete':complete,'report_format':report_format,'standard_five_sections_complete':not missing and complete,'missing_sections':missing,'closing_passage_detected':closed,'coverage_gaps':(['Unidentified author in capture; inspect continuity'] if unknown_authors else []) + ([] if closed else ['Closing passage not confirmed; inspect raw DOM before declaring complete']),'attachment_links':[a for m in selected for a in m.get('attachments',[])],'captured_at':meta['captured_at']}
 if selected:
  p=ROOT/d;p.mkdir(parents=True,exist_ok=True)
  (p/f'report-{digest[:16]}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
  # Preserve the original manual report.json; scheduled consumer uses assembled-latest.json.
  (p/'assembled-latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));reports.append(report)
current=next((r for r in reports if r['report_date']==date),None)
baseline=next((r for r in reversed(reports) if r['report_date']<date and r['complete'] and r.get('report_format')=='five_section'),None)
print(json.dumps({'date':date,'complete':bool(current and current['complete']),'report_format':current['report_format'] if current else None,'sections':len(current['sections']) if current else 0,'messages':len(current['source_messages']) if current else 0,'baseline':baseline['report_date'] if baseline else None,'missing_sections':current['missing_sections'] if current else heads},ensure_ascii=False))
