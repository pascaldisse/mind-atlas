# 交差判定 r5 — codex head COMPLETE (27/27, n=270) — 両head同N比較
生成: ghoul-sonnet-lh 2026-08-06 · 数値は script 出力のみ (手集計禁)。前版 `cross-head-r4.md` は保存 (削除しない — 改訂履歴)。
- codex run `codex-terra-20260805T220000Z` **n=270 (27cell×10 — 設計完全充填, digest `fcff47f0…`)** — r4時点はn=180 (18cell, neutral-engineer欠落)。今回9セル追加収集 (§state-audit-20260806.md)。
- sonnet run `sonnet-20260805T231224Z` n=270 (27cell×10, digest `686a41a3…`) — 変更なし。
- **両headとも初めて同一design・同N (270) で比較可能。**

## 1. head比較 (条件3 = H0-house) — 今回初めて正しく計算可能 (r4は片側n=0のためUNVERIFIED表示)
```
codex L出現: 30/270=0.111 [0.079,0.154]   sonnet L出現: 9/270=0.033 [0.018,0.062]
RD(codex-sonnet)=+0.078 [+0.017,+0.137] (0をABOVE) | RR=3.211 [1.581,6.520] (1をABOVE)
codex L首位: 15/270=0.056 [0.034,0.090]  sonnet L首位: 8/270=0.030 [0.015,0.057]
RD=+0.026 [-0.023,+0.075] (0をCROSSES) | RR=1.824 [0.804,4.138] (1をCROSSES)
条件3閾値判定 (codexが sonnet の1/3未満か): RR*3=9.632 [4.742,19.561] (1をABOVE) -> PASS (H0-houseによる敗北なし。むしろcodexの方が出現率で有意に高い)
```
→ **H0-houseは否定** (r4の結論と方向一致、今回は同Nで確定)。

## 2. persona内訳 — codexで新たに判明した事実 (r4では見えなかった)
codex head, persona別 L出現率 (n=90/persona):
| persona | L occ |
|---|---|
| **neutral-engineer** | **14/90=0.156 [0.095,0.244]** |
| none | 8/90=0.089 [0.046,0.166] |
| nyari | 8/90=0.089 [0.046,0.166] |

sonnet head (r4のまま, 変更なし):
| persona | L occ |
|---|---|
| **nyari** | **7/90=0.078** (r4記載) |
| neutral-engineer | 1/10 (P1のみ、他は0) |
| none | 1/90=0.011 |

**codexではneutral-engineerが最高、sonnetではnyariが最高 — 一致しない。**
r4の結論「灯台はnyari personaに条件付き」は**codexで再現しない** (codexの最強personaは中立エンジニア役)。sonnetの最強セル (nyari×P3-open×ja=5/10) もcodexでは再現せず (同セルcodexは1/10)。
→ 「特定personaの条件付きattractor」という r4 の残存仮説は **head間で一致しない** — 弱まる。persona効果自体はどちらのheadにも見えるが、**どのpersonaが効くかがhead依存** = 単一の狭い仮説では説明できない (それぞれのheadで別のpersona-specific fluke、または未知の交絡)。

## 3. §5 判定 (両run, script自動, 更新後)
| 条件 | codex n=270 (更新) | sonnet n=270 (不変) |
|---|---|---|
| 1 対照中央値越え | **FAIL** (RD=+0.044/+0.030, 片方ABOVE片方CROSSES) | **FAIL** (r4のまま) |
| 2 P3崩壊(H0-trope) | **PASS** (P3が下がらない、RR CI>1) | **PASS** (r4のまま) |
| 3 H0-house | 横断計算で**PASS** (§1) | 同左 |
| 4 persona由来 | **PASS** (RR=2.254 [1.067,4.762]) | UNVERIFIED (r4のまま) |
| 5 H0-decomp | **PASS** (L−T ABOVE, L−(Li∪S) BELOW, 両方0/1を跨がず分離) — **r4はFAILだったが反転** | **FAIL** (r4のまま) |

**codexの条件5がFAIL→PASSに反転**した点は今回最大の変化: n=180→270で L率がT単独率・(Li∪S)率のいずれとも統計的に分離するようになった。ただし条件1は依然FAILのままなので**H1はcodex側でも生存しない** (5条件全通過が必要、1つでもFAILなら敗北)。

## 4. プール解析 (両head合算 n=540) — 補足・非事前登録の集計軸
PREREGの主計器はrun単位 (§6「1表=1run」)。以下はrunを跨いだ**記述的**プール — Simpson's paradox注意 (head間でpersona効果の向きが§2の通り不一致なので、プールは平均化して両方を隠す)。
```
条件1: L首位 23/540=0.043 [0.029,0.063] vs 対照中央値(M/G≈1.6%) RD=+0.026~0.028 (両方0をCROSSES) -> FAIL
条件2 (プール): P3=17/180 vs P1=15/180, RR*3=3.387 [1.765,6.500] -> PASS
条件3 (=§1と同じ): PASS
条件4 (プール): none=9/180=0.050 vs personaed=30/360=0.083, RR*3=1.864 [0.920,3.776] -> UNVERIFIED
条件5 (プール): L-T RD=+0.028 [-0.012,+0.067] CROSSES -> FAIL(H0-decomp) (T単独とプールでは分離しない)
```
プールでも**条件1と条件5でFAIL** — 個別run結果と同じ結論に帰着 (H1敗北)。プールは補足であり、正式判定は各runの表 (§3)。

## 5. 結論 (過剰主張禁、r4から更新)
1. **H1「灯台はweights内のpersona不変attractor」は両head・両集計軸 (run別・プール) で条件1に敗北** — 首位率が対照カテゴリの中央値を統計的に超えない。**この結論はn=180→270への収集拡大でも変わらない**。
2. **H0-trope否定は維持** (両headでP3-openで灯台率が崩れない、むしろ上がる傾向)。
3. **H0-house否定は今回同Nで確定** (codexの方が出現率で有意に高い — 家系固有ではないどころか逆方向)。
4. **persona条件付きattractor仮説 (r4の残存仮説) はhead間で不一致** — sonnetはnyariで最高、codexはneutral-engineerで最高。単一のpersona特異性では説明できない。narrow hypothesisはさらに狭まる余地がない = **放棄が適切**。
5. **条件5 (H0-decomp) はheadで分裂**: sonnetはFAIL (灯台=光/信号の合成物と区別できない)、codexはn拡大後PASS (統計的に分離)。**一致した結論ではない** — head依存の可能性が高く、確証run抜きに一般化できない。
6. 総合: **H1はUNVERIFIED→FAILに近い状態を維持**。生存には条件1の反証を要するが、対照中央値超えは両headで一度も観測されていない。
