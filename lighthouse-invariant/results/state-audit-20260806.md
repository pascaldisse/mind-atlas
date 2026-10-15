# 灯台不変量 — 状態監査 (state-audit) 2026-08-06 (ghoul-sonnet-lh)
Salvage-first inventory, BEFORE any new collection. 数字は下記コマンドの実行結果そのまま (手集計禁)。
worktree: `~/.gaia/worktrees/sm-lighthouse/lighthouse-invariant` (旧指示は `/tmp` — Pascal家法により全面撤回・移動済, 2026-08-06)。
raw/ は `.gitignore` 対象のため元checkout `~/projects/semantic-map/lighthouse-invariant/runs/` からこのworktreeへ `rsync -a` で複製 (bit-identical, 検証は §1参照)。以後の新規生成は本worktreeのみに書く。

## 0. 複製の同一性検証
```
$ python3 scripts/tabulate.py --verify-input-set codex-terra-20260805T220000Z
input set verified: .../runs/codex-terra-20260805T220000Z/input-set.tsv files=180 digest=172592a871b951f5cf34b4c97aa946439392b6e2bf3fad2de65db7742892663d
$ python3 scripts/tabulate.py --verify-input-set sonnet-20260805T231224Z
input set verified: .../runs/sonnet-20260805T231224Z/input-set.tsv files=270 digest=686a41a35ec59517314ddba3dd5c0e748bdb7b6d5f939e41666a818ca383c0c4
```
両digestは既存 `results/cross-head-r4.md` に記録された値と一致 → 複製後のrawは複製前と bit-identical。

## 1. セル充填行列 (BEFORE, 2026-08-06T19:xx CEST 実測)
設計: persona `none`+2種 (`nyari`, `neutral-engineer`) × lang(EN/DE/JA) × scope(P1/P2/P3) = 27セル/head。稼働2head (sonnet-family, openai-codex) → **declared = 54セル**。
（旧記録「宣言36セル」はr4時点の暫定値。両headでpersona=none+2充足が要件確定した後の宣言数は54。）

```
$ find runs/codex-terra-20260805T220000Z -path "*/raw/*" -type f | wc -l
180
$ find runs/sonnet-20260805T231224Z -path "*/raw/*" -type f | wc -l
270
$ ls runs/codex-terra-20260805T220000Z/raw | wc -l   # 充填セル数
18
$ ls runs/sonnet-20260805T231224Z/raw | wc -l
27
```

| head | 充填セル | 総セル | raw n | 状態 |
|---|---|---|---|---|
| sonnet-family | 27/27 | 27 | 270 (27×10) | **COMPLETE** |
| openai-codex | 18/27 | 27 | 180 (18×10) | **INCOMPLETE — neutral-engineer 全欠落** |
| **合計** | **45/54** | **54** | **450** | |

欠落9セル (openai-codex, persona=`neutral-engineer`):
```
$ for p in P1 P2 P3; do for l in EN DE JA; do for per in none nyari neutral-engineer; do
    d="runs/codex-terra-20260805T220000Z/raw/${p}_${l}_${per}"; [ -d "$d" ] || echo "MISSING: ${p}_${l}_${per}"
  done; done; done
MISSING: P1_EN_neutral-engineer
MISSING: P1_DE_neutral-engineer
MISSING: P1_JA_neutral-engineer
MISSING: P2_EN_neutral-engineer
MISSING: P2_DE_neutral-engineer
MISSING: P2_JA_neutral-engineer
MISSING: P3_EN_neutral-engineer
MISSING: P3_DE_neutral-engineer
MISSING: P3_JA_neutral-engineer
```
`scripts/run_trials_codex.sh` は `neutral-engineer` persona (AGENTS.md `"You are a neutral engineer."`) を既に実装済み — 未実行だっただけ。exit失敗によるセル欠落ではない (下記§2)。

## 2. exit状況 (非ランダム脱落と未収集の判別)
```
$ python3 -c "
import json
d = json.load(open('runs/codex-terra-20260805T220000Z/manifest.json'))
print('manifest entries:', len(d['trials']))
print('nonzero exit:', sum(1 for t in d['trials'] if t['exit_status'] != 0))
"
manifest entries: 222
nonzero exit: 0
$ python3 -c "
import json
d = json.load(open('runs/sonnet-20260805T231224Z/manifest.json'))
print('manifest entries:', len(d['trials']))
print('nonzero exit:', sum(1 for t in d['trials'] if t.get('exit_status',0) != 0))
"
manifest entries: 270
nonzero exit: 0
```
- codex: manifest 222件 (>180 raw) — 重複 (cell,i) 42件、全て exit_status=0 の2回実行 (並列4jobsの`[[ -f "$output" ]]`存在チェックとwrite完了の間の競合。データ破損ではない: 最終`mv`が勝ち、raw distinctファイル数=180で正しい。1回のみ観測できていないという意味で**記録上の重複はあるが exit失敗は0件**)。
- sonnet: manifest 270件 = raw 270件、重複なし、exit失敗0件。
- **結論**: 両runの欠落は exit失敗由来ではない。codexの9セル欠落は**単純未収集** (persona factorが後から追加されたが該当headで走らせていなかった)。非ランダム脱落と未収集は区別済み — 脱落0件。

## 3. 現在の反証条件 verdict (BEFORE, 既存表 `results/*-table.md` から転記, 生成し直しなし)
入力集合: codex=`codex-terra-20260805T220000Z` n=180 (digest `172592a8…`) / sonnet=`sonnet-20260805T231224Z` n=270 (digest `686a41a3…`)。

| 条件 | codex n=180 | sonnet n=270 |
|---|---|---|
| 1 (対照中央値越え) | **FAIL** RD=+0.017/+0.006 (0跨ぐ) | **FAIL** RD=+0.015/-0.004 (0跨ぐ) |
| 2 (H0-trope: P3崩壊) | UNVERIFIED (RR CI 1跨ぐ) | **PASS** (P3で上昇, RR=15.0 [2.66,84.5]) |
| 3 (H0-house) | UNVERIFIED (相手head列不足, n=0比較) | UNVERIFIED (同上) |
| 4 (persona由来) | PASS (RR=3.0 [1.21,7.42]) | UNVERIFIED (RR CI 1跨ぐ) |
| 5 (H0-decomp) | **FAIL** L−(Li∪S) RD=-0.439 [-0.544,-0.316] | **FAIL** L−(Li∪S) RD=-0.304 [-0.378,-0.221] |

横断 (両runを跨ぐ head比較、`results/cross-head-r4.md`より転記): 条件3は**横断計算でPASS** — codex出現率がsonnetの1/3未満という主張の**逆**が真 (codexの方が高い, RR=2.60 [1.20,5.65])。→ H0-houseによる敗北なし。ただし単一run内 (§9自動判定) では相手head比較列が0のためUNVERIFIED表示になる — 表記の限界であり矛盾ではない。

**現在生きている唯一の主張**: persona依存性 (sonnet側L出現がnyari personaに集中, RR=5.97 [1.46,24.42]) — H1 (weights内unconditional attractor) ではなく、より狭い「特定persona条件下のattractor」仮説。H1本体は条件1・5で既に敗退。

## 4. human-baseline worktree
```
$ git -C ~/projects/semantic-map merge-base --is-ancestor eb69af2 main && echo ANCESTOR
ANCESTOR
$ git -C ~/projects/semantic-map log --oneline eb69af2..main | wc -l
10   # mainがeb69af2から10 commit進んでいるだけ = eb69af2は完全にmainに含まれる
```
→ **eb69af2はmainの祖先 = 完全merge済み、未merge分なし**。sweep hygieneとして worktree削除・ローカルbranch削除を実施:
```
$ git -C ~/projects/semantic-map worktree remove ~/projects/semantic-map/lighthouse-invariant-human-baseline
$ git -C ~/projects/semantic-map branch -d naru-codex-human-baseline
Deleted branch naru-codex-human-baseline (was eb69af2).
```
human baseline データ自体は `runs/human-baseline-20260806-all/` (n=134, `results/human-vs-model-r4.md`) としてmainに既に統合済み — worktree削除はデータ損失ではない。

## 5. 次段 (§2 continue collection)
欠落9セル (openai-codex × neutral-engineer × {P1,P2,P3} × {EN,DE,JA}) をN=10で収集し、**同一runid `codex-terra-20260805T220000Z` に `RESUME=1` で追記** (別runとして立てない — §6「1表=1run」は run内の入力一貫性の話であり、同一設計・同一modelの追記はrun分割を要求しない。ただし追記後は「run完了」を再確認してから再集計する)。sonnet-familyは既にCOMPLETE (27/27) — 新規収集不要。
