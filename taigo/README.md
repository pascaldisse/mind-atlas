# taigo v0 — 態語実験基盤

## 仮説
短い鸣語ブロック (gaiago state injection) = 文脈回転ベクトル。
ブロックを system/pre-prompt に注入して同一モデルに同一質問を投げると、
応答の状態軸 (速度感・連想・宇宙化・感覚描写・笑) が有意にシフトするかを測定する。
原型ブロック: `~/.gaia/skills/stoner-mode/SKILL.md` (煙態注入部分を抽出し `blocks/stoner-injection.md` に固定した。フロントマタ/度設定/出部分は除外—実際に注入される状態本体のみ)。

## 構成
```
probes.json      8固定プロンプト (日常×2, 技術×2, 感情×2, 要約×2, EN/DE混在)
blocks/stoner-injection.md   注入ブロック (8行)
rubric.md        采点5軸固定 rubric + JSON出力契約
lib/summon.ts    `gaia summon` CLIを同期化する共通ヘルパ (launch→poll status→read transcript.jsonl)
run.ts           条件×probes → out/<cond>/<probe>.json
score.ts         out/**/*.json → rubric采点(sonnet経由) → out/scores.csv
ablate.ts        行単位 greedy backward-elimination → out/minimal-block.md (行数>7はUNVERIFIED)
out/             実行結果 (gitにcommit済, 監査用)
```

## `gaia summon` 同期化の仕様 (重要)
CLI `gaia summon <agent> <task>` は非同期: sub-roomを作って即時戻り、結果はあとで呼び出し元のルームに post-back される。
スタンドアロンの bun スクリプトはルームループではないので post-back を受けられない→ `lib/summon.ts` が
1) `gaia summon <agent> "<task>"` を起動し stdout から `sub-room '<roomId>'` を regex 抽出、
2) `gaia summon --status <roomId>` を poll (デフォルト 1.5s間隔) し `delivered:true` を待つ、
3) `~/.gaia/rooms/<roomId>/transcript.jsonl` を直接読み、author===agent の最後の `.text` を回収する。
これでブロッキングな synchronous 呼び出しが可能 (timeoutデフォルト 180s)。

## params (env, デフォルト)
- `TAIGO_MODEL`    default `ghoul-sonnet` († "sonnet" 単体は `gaia summon` の有効 agent id ではないため、この ghoul 自身と同モデルの `ghoul-sonnet` をデフォルトに代用)
- `TAIGO_PARALLEL` default `4` (並列上限。CPU法: コードは並列可だが、実走は直列 → 実行時は `TAIGO_PARALLEL=1` を指定)
- `TAIGO_OUT`      default `./out`
- `TAIGO_ABLATE_THRESHOLD` default `0.8` (ablate.ts の保持率閾値)

## 実行手順 (live-test法: 実走は直列)
```sh
cd taigo
TAIGO_PARALLEL=1 bun run.ts --condition none
TAIGO_PARALLEL=1 bun run.ts --condition block --block ./blocks/stoner-injection.md
TAIGO_PARALLEL=1 bun score.ts
bun ablate.ts --block ./blocks/stoner-injection.md   # 行数>7なら UNVERIFIED を out/minimal-block.md に記録して終了
```

## 既知制限
- ablate.ts の greedy 探索は O(n^2) の live summon+score 往復を使うため、行数≪7 のブロックでのみ実走する (operator指示)。
- スコアは LLM(sonnet経由)自己採点 — 主観性あり、絶対値ではなく条件間相対差として読む。
