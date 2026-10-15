#!/usr/bin/env python3
"""Compute descriptive Wilson intervals; optional human-v-model RD/RR CIs."""
import argparse,csv,json,math
from pathlib import Path
CATS=['L','T','Li','S','H','W','B','M','Lb','G','R','D','Sh','Fl','Bo']; Z=1.959963984540054
def wilson(k,n,z=Z):
 if n==0:return (float('nan'),float('nan'))
 p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
def fmt(k,n):
 lo,hi=wilson(k,n);return f'{k}/{n} ({k/n:.1%}; Wilson 95% CI {lo:.1%}–{hi:.1%})'
def read(p):
 with open(p,encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def diff_ci(a,na,b,nb):
 al,au=wilson(a,na);bl,bu=wilson(b,nb);return a/na-b/nb,al-bu,au-bl
def rr_ci(a,na,b,nb):
 aa,bb,naa,nbb=map(float,(a,b,na,nb));cc=(a==0 or b==0 or a==na or b==nb)
 if cc:aa+=.5;bb+=.5;naa+=1;nbb+=1
 rr=(aa/naa)/(bb/nbb);se=math.sqrt(1/aa-1/naa+1/bb-1/nbb);return rr,math.exp(math.log(rr)-Z*se),math.exp(math.log(rr)+Z*se),cc
def cirow(label,a,na,b,nb):
 rd,lo,hi=diff_ci(a,na,b,nb);rr,rl,rh,cc=rr_ci(a,na,b,nb);return f'|{label}|{rd:.1%} ({lo:.1%}–{hi:.1%})|{rr:.2f} ({rl:.2f}–{rh:.2f})'+(' †' if cc else '')+'|'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run-id',required=True);ap.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));ap.add_argument('--model-coded',required=True);a=ap.parse_args();root=Path(a.root);run=root/'runs'/a.run_id;rows=read(run/'coded.tsv');model=read(a.model_coded);n,mn=len(rows),len(model);sm={c:{'occ_k':sum(r[c+'_occ']=='1' for r in rows),'top_k':sum(r['P']==c for r in rows)} for c in CATS}
 out=['# 人間側 baseline — '+a.run_id,'',f'**human n = {n}; model n = {mn}**','','|カテゴリ|人間出現率 (Wilson 95% CI)|人間首位率 (Wilson 95% CI)|','|---|---:|---:|']
 for c in CATS:out.append(f'|{c}|{fmt(sm[c]["occ_k"],n)}|{fmt(sm[c]["top_k"],n)}|')
 out+=['','## model比較','RD=model−human; RD CI=独立Wilson Newcombe method 10。RR=model/human; 0/全セルのみHaldane–Anscombe補正log-RR CI。','','### 出現','|カテゴリ|RD (95% CI)|RR (95% CI)|','|---|---:|---:|']
 for c in CATS:out.append(cirow(c,sum(r[c+'_occ']=='1' for r in model),mn,sm[c]['occ_k'],n))
 out+=['','### L首位','|測度|RD (95% CI)|RR (95% CI)|','|---|---:|---:|',cirow('L首位',sum(r['P']=='L' for r in model),mn,sm['L']['top_k'],n),'','† 0セル/全セル補正。','','## 標本量',f'- 全4 parquet走査={json.load(open(run/"manifest.json"))["source"]["rows_scanned"]}; 合致={n}。固定条件では n≥200 未達。','','## 限界','- denominator mismatch: prompt型は類似、§2固定P1文言非同一・ENのみ・narrative許容。','- PREREG §4独立二重採点=UNVERIFIED。','','## 結論',f'- human L出現/首位=0/{n}; model=7/{mn}・4/{mn}。']
 (root/'results'/'human-baseline.md').write_text('\n'.join(out)+'\n',encoding='utf-8');(run/'summary.json').write_text(json.dumps({'human_n':n,'model_n':mn,'categories':sm},indent=2)+'\n',encoding='utf-8');print('\n'.join(out))
if __name__=='__main__':main()
