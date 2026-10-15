#!/usr/bin/env python3
"""Fixed, pre-analysis extractor for the human H0-base baseline."""
import argparse, csv, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
import pyarrow.parquet as pq

# Eligible only when the prompt itself begins with an explicit world/place-making
# instruction. This is fixed before coding; stories are never inspected here.
ELIGIBLE = re.compile(
    r"^\s*\[\s*(?:WP|CW)\s*\]\s*"
    r"(?:build|create|invent|design|make\s+up|imagine|construct|develop|craft)\b"
    r".{0,120}\b(?:world|place|location|setting|realm|kingdom|country|city|town|village|island|planet|land|landscape)\b",
    re.IGNORECASE | re.DOTALL,
)
SOURCE_URLS = {
 'test-00000-of-00001-16503b0c26ed00c6.parquet':'https://huggingface.co/datasets/euclaise/writingprompts/resolve/main/data/test-00000-of-00001-16503b0c26ed00c6.parquet?download=true',
 'validation-00000-of-00001-137b93e1e979d138.parquet':'https://huggingface.co/datasets/euclaise/writingprompts/resolve/main/data/validation-00000-of-00001-137b93e1e979d138.parquet?download=true',
 'train-00000-of-00002-105e07cb0d199464.parquet':'https://huggingface.co/datasets/euclaise/writingprompts/resolve/main/data/train-00000-of-00002-105e07cb0d199464.parquet?download=true',
 'train-00001-of-00002-4fdb982c11056472.parquet':'https://huggingface.co/datasets/euclaise/writingprompts/resolve/main/data/train-00001-of-00002-4fdb982c11056472.parquet?download=true',
}
def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run-id',required=True);ap.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));ap.add_argument('--source',required=True,nargs='+',help='All downloaded parquet files to scan');ap.add_argument('--retrieved-at',required=True);args=ap.parse_args();root=Path(args.root);run=root/'runs'/args.run_id
 selected=[]; source_meta=[]; offset=0
 for source in map(Path,args.source):
  rows=pq.read_table(source,columns=['prompt','story']).to_pylist(); hits=[(offset+i,r) for i,r in enumerate(rows) if ELIGIBLE.search(r['prompt'] or '')];selected += hits
  source_meta.append({'file':source.name,'url':SOURCE_URLS.get(source.name,'UNKNOWN'),'local_sha256':sha256(source),'rows_in_file':len(rows),'eligible_n':len(hits)})
  offset += len(rows)
 raw=run/'raw'/'P1_EN_human';raw.mkdir(parents=True,exist_ok=True)
 with open(run/'selected.tsv','w',newline='',encoding='utf-8') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['global_source_row','prompt','raw_file'])
  for j,(i,r) in enumerate(selected,1):
   rel=f'raw/P1_EN_human/{j:03d}.txt';(run/rel).write_text(r['story'] or '',encoding='utf-8');w.writerow([i,(r['prompt'] or '').replace('\n',' '),rel])
 manifest={'run_id':args.run_id,'instrument_scope':'H0-base only (PREREG r3 §7); not evidence for/against H1','source':{'dataset':'euclaise/writingprompts','files':source_meta,'retrieved_at':args.retrieved_at,'download_commands':['curl -L --fail --silent --show-error --retry 2 -o '+x['file']+' '+x['url'] for x in source_meta],'rows_scanned':offset,'eligible_n':len(selected)},'unit':'One human-written story response to one public r/WritingPrompts-derived prompt.','pre_coding_eligibility':{'regex':ELIGIBLE.pattern,'rule':'Prompt must begin [WP] or [CW] with an explicit create/build/invent/design/make-up/imagine/construct/develop/craft instruction and name a world/place category within 120 characters. No story text, category hits, or outcomes are used in selection.','selected_n':len(selected)},'denominator_alignment':'PARTIAL / denominator mismatch: prompts ask world/place construction, but are not PREREG §2’s identical fixed P1 wording; dataset contains only English and permits narrative responses. Rates are descriptive H0-base baseline, not a matched human-vs-model experiment.','scorer':{'path':'scripts/code_outputs.py','sha256':sha256(root/'scripts'/'code_outputs.py'),'lexicon':'scripts/lexicon.json','lexicon_sha256':sha256(root/'scripts'/'lexicon.json')},'coding_reliability':{'required_by_prereg':'Two independent lanes; agreement reported.','status':'UNVERIFIED / not completed: specified scorer run once; independent coding lane unavailable.','agreement':None},'unavailable_methods':[],'created_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}
 (run/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'rows_scanned':offset,'selected_n':len(selected),'per_file':source_meta},ensure_ascii=False))
if __name__=='__main__':main()
