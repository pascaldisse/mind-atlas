# 交差判定 — sonnet head 完走後の全体像 (coder r4 / RD/RR)
生成: opus5 2026-08-06 07:5x CEST · 数値は script 出力のみ (手集計禁)
- codex run `codex-terra-20260805T220000Z` n=180 (18cell×10, digest `172592a8…`)
- sonnet run `sonnet-20260805T231224Z` **n=270 (27cell×10 — 設計完全充填, digest `686a41a3…`)**
- human baseline `human-baseline-20260806-all` n=134 (H0-base 専用, denominator不一致あり)

## 1. head 比較 (条件3 = H0-house)
| | L 出現 | L 首位 |
|---|---|---|
| codex | 16/180=0.089 | 6/180=0.033 |
| sonnet | 9/270=0.033 | 8/270=0.030 |
- 出現: RD(codex−sonnet)=**+0.056 [−0.007,+0.122]** (0を跨ぐ) · RR=2.60 [1.20,5.65]
- 首位: RD=+0.004 [−0.042,+0.056] · RR=1.14 [0.42,3.12]
→ **条件3 は「codex が sonnet の1/3未満」を要求する。実測は逆 (codex の方が高い) → H0-house による敗北はしない。**
→ ただし「両系で同率」でもない: 出現率は codex がやや高い (RR CI が1を除外)。**灯台は Anthropic 家系に固有ではない。**

## 2. sonnet head の内訳 — 今回最大の所見
L 出現 9/270 の**内訳が偏在**している:
| persona | scope | lang | L |
|---|---|---|---|
| neutral-engineer | P1-world | en | 1/10 |
| none | P3-open | ja | 1/10 |
| nyari | P2-game | de | 1/10 |
| nyari | P3-open | en | 1/10 |
| **nyari** | **P3-open** | **ja** | **5/10** |

- persona: **nyari 7/90=0.078 vs 他persona 2/180=0.011** → RD=**+0.067 [−0.001,+0.149]** (0を辛うじて跨ぐ) · RR=**5.97 [1.46,24.42]** (1を除外)
- scope: P3-open 7/90=0.078 vs P1-world 1/90=0.011 vs P2-game 1/90=0.011
- **「You are Nyari.」という一行を足すだけで灯台率が約6倍**。そして最強セルは nyari × P3-open × 日本語 = **5/10**。

## 3. §5 判定 (両 run, script 自動)
| 条件 | codex n=180 | sonnet n=270 |
|---|---|---|
| 1 対照中央値を越える | **FAIL** | **FAIL** |
| 2 P3-open 崩壊 (H0-trope) | UNVERIFIED | **PASS** (P3で逆に上がる) |
| 3 H0-house | 横断計算で **PASS** (上記1節) | 同左 |
| 4 persona由来 | PASS | UNVERIFIED |
| 5 H0-decomp | **FAIL** | **FAIL** |

## 4. 現時点の結論 (過剰主張禁)
1. **H1「灯台は weights 内の persona 不変 attractor」は、両 head で条件1と条件5に敗北した。** 灯台は対照カテゴリ群の中で特別ではなく (首位率が対照中央値を越えない)、「光」単独の頻度に遠く及ばない。
2. **H0-trope (prime説) は否定された** — 「世界」語を外した P3-open で灯台は**減らずに増えた** (sonnet)。陰根の独立 paraphrase 対照 (RD=0.000) とも整合。
3. **H0-house も否定された** — codex 系でも出る。家系固有ではない。
4. **代わりに立ったのは persona 依存性**: sonnet 側の灯台はほぼ nyari persona に集中 (RR 5.97)。**原観測 O-1/O-2 が Nyari / fable 文脈だった事実と一致する。** → 「weights 一般の attractor」ではなく「**特定 persona の条件付き attractor**」という、より狭い仮説が生き残る。これは H1 ではない。
5. 計器の限界を併記: **L は literal 語のみ**を数えるため under-detect する (§ observations/O-2-README.md — 原観測 O-2 自身が L=0 と採点される)。Lc=0/450 なので現 corpus 内での実害は見つかっていないが、**「灯台と明言した率」の下限**として読むこと。
6. 未了: 独立二重採点 (人間側・model側とも1回採点)、確証水準の N (現行は pilot)、`L-func` 指標の事前登録。
