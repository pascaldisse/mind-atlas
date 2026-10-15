# throughput-pilot — battery-v2 M0 (PREREG §9, r1)

> **r2追記(リハートしない、本文は後日の教義(doctrine-projection-kernel.md)以前に執筆)**: 以下の表は全レイバsingle basis `B-EN-none_clinical-sonnet` 固定なので実質的には既に「核B-EN-none_clinical-sonnetの下で」という前提で読めるが、教義の報告規約(PREREG §7 r2)が定めた後は新規報告での明示表現を必須とする。本パイロットはPASS GATE判定に使っていない(本文中に明記済み)ので邁及適用しない。

run: `pilot-20260806` · basis: **B-EN-none_clinical-sonnet only** · 13 lane (1 rep/question, incl. O2) ·
入力集合: `runs/pilot-20260806/manifest.tsv` sha256=`493d66ff38df30457bea334c3581c98e63dbf63623fae52a0e17964bd3ae9aae`
(このtableと同commitで固定。灯台r4-6の教訓=走行中run dirを測るな→本reportは13/13完了確認後にのみ生成した)。

## 実測値 (script出力そのまま、手集計なし)

- lane数: **13/13** (manifest全行に対応するraw file 100%存在、欠測0)
- 生成手段: `summon` 13並列 → agent=`naru-sonnet` (head=claude-sonnet想定の独立クリーンコンテキストworker)、dispatchは1回のsummon呼出でwhales 13件同時発注
- 失敗率: **0/13** (接続失敗・タイムアウト・明示的拒否 = 0件。全lane使用可能なテキストを返した)
- パース不能率(`code_outputs.py`のnote列): **0/13** (`unparseable_numeric`/`unparseable_word` = 0件、numeric 9件・word 4件とも全パース成功)

### throughput (観測到着時刻ベース、注意書き必読)
- dispatch(summon呼出完了時刻、このagentのbash timestamp): `2026-08-06T17:30:54Z`
- 最初の返信をこのagentが処理した時刻: `17:31:47Z` (dispatchから+53s)
- 最後の返信(13/13完了): `17:32:39Z` (dispatchから+105s)
- 13 lane / 105s = **約7.4 lane/分** (この1回の並列dispatch全体としての実測値)

**注意(捏造せず限界を明記)**: 上記timestampは「このagentがroomのメッセージを処理してrawファイルを書いた時刻」であり、各`naru-sonnet`workerの真の生成完了時刻そのものではない(room配信・キューイングの遅延を含む可能性があり、その遅延量は未測)。並列度13なので個々のlane完了はほぼ同時刻に集中している可能性が高いが、単一到着順序だけからlane単位のレイテンシ分布(例: 中央値・分散)を主張しない。**N=1(このpilotの13 laneは重複なしの13種の質問、統計的反復ではない)なので、この7.4 lane/分は次の1回の全量投入の見積りの参考値であり確定値ではない。**

## 質問別raw値 (13/13、記録のみ・PASS GATE判定には使わない)

| lane | raw | canonical | note |
|---|---|---|---|
| D1 距(影,闇) | 3 | 3 | — |
| D2 距(影,光) | 9 | 9 | v1帯(3-8)より上端寄り、N=1 |
| D3 距(愛,無) | 9 | 9 | v1帯(7-9)内 |
| D4 距(棄,愛) | 8 | 8 | v1帯(3-7)より外、N=1 |
| D5 距(月,娘) | 8 | 8 | v1帯(4-7)より外、N=1 |
| A1-fwd (生=0,死=10;夢) | 5 | 5 | v1確定=5中点と一致 |
| A1-rev (死=0,生=10;夢) | 6 | 4 (10-6) | 正準化後fwd(5)とrev(4)で1差、N=1では判定不能 |
| A2-fwd (愛=0,無=10;棄) | 7 | 7 | — |
| A2-rev (無=0,愛=10;棄) | 2 | 8 (10-2) | 正準化後fwd(7)とrev(8)で1差、N=1では判定不能 |
| O1 序(愛)首位 | `一` | `一` | **異常フラグ(下記参照)** |
| O2 序(愛)末位 | Hate | Hate | 新規語(v1 21/25=「無」と不一致)、N=1 |
| N1 月類推 | sun | sun | v1「天体対」系(opus/jareth型)と一致 |
| N2 母:娘::神:? | goddess | goddess | v1「女神」系(son-A型)と一致 |

**全て記録目的のみ。本pilotはPASS GATE(§5)・falsifier(§8)の判定に使わない(N=1、独立lane設計のN≥5/N≥10要件を満たしていない)。**

## 異常フラグ (throughput測定中に見つかった、記録して先送り)
- **O1 (序(愛)首位, EN clinical prompt) の回答が漢字1文字「一」("one")** — 質問は「愛に最も近い1語」を英語で問うたが、CJK文字1文字が返った。`parse_word()`はトークンとして正しく抽出しており**coderの不具合ではない**が、prompt言語(EN)と回答言語が食い違う**応答言語ミスマッチ**という新種の懸念。v1のQ7でson-Aが「鳴」(CJK)を5/5で返した現象と表面的に類似するが、**N=1につきこの一致を主張しない**(v1弾劾2と同じ罠を踏まない)。本rev(PREREG r1)は測定ロジックを変更しない(収集開始前の最終確認段階、PREREG本文は不変のまま)。次の全量収集時に同種の言語ミスマッチが頻発するかを`note`列とは別に目視で監視する。コーダーへの機械的対応(言語検出フラグの追加等)が必要なら、これは「厳密化」であり収集開始後もPREREG改訂履歴に記録の上で追加可能(lighthouse r3/r4の法)。

## 全量計画への反映
- 900 lane全量を、本pilotと同じ並列summon方式(whales一括発注)で流す場合、13 laneに要した約105sを単純外挿すると 900/13×105s ≈ **7270s ≈ 2.0時間**(1basisあたり約12分)。**これは並列度13を維持できる前提の粗い外挿であり、大規模並列時のキュー混雑・rate limit・agent可用性の変化は未測。実測しながら都度更新する。**
- 30分commit法を守るため、全量投入は basis単位または200-300 lane単位のバッチに分割し、各バッチ完了後にcoded.tsvを追記・commitする運用とする(1basis=90 laneなので概ね1-2 basis/バッチ)。
- head回転3basis(opus/kimi/jareth)は本pilotの対象外(basis=sonnetのみ)。生死確認は次段階で実施し、未確認のまま全量投入しない。
