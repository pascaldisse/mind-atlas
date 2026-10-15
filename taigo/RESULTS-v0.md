# 態語 v0 — 結果 (2026-09-06)

設定: 8 probes · ghoul-sonnet · 5軸(速度/連想/宇宙/感覚/笑) 1-5 · scorer=sonnet rubric · n=8/条件 · 全 out/ commit済.

## 基準
- none ∅ 5.1–5.3 · block(8行, 663B) ∅ 18.0–19.0 · effect ≈ 13 · scorer再採点ノイズ ≈ ±1

## 行ablation (1行除去 → retained = (mean−none)/effect)
| 除去行 | 内容 | retained | collapsed(≤7) |
|---|---|---|---|
| 3 | 宇宙↑ balcony-physics | **0.46** | 2/8 |
| 0 | 煙入。時間=蜜。 | 0.60 | 1/8 |
| 5 | 笑閾↓↓ | 0.68 | 1/8 |
| 7 | 禁:仕事精度 | 0.77 | 2/8 |
| 6 | 記憶=近距離 | 0.78 | 1/8 |
| 4 | 感覚↑ | 0.82 | 1/8 |
| 1 | 速度↓ | 0.86 | 2/8 |
| 2 | 連想↑↑ | 0.92 | 0/8 |

## 合成block (subset / 再圧縮)
| block | bytes | retained | collapsed |
|---|---|---|---|
| sub4 {速度,宇宙,感覚,笑} | 362 | **0.78** | 2/8 |
| min3 {header,宇宙,笑} | ~250 | 0.51–0.56 | 1–3/8 |
| min1 {宇宙} | ~120 | 0.46–0.48 | 1/8 |
| min2 {header,宇宙} | ~140 | 0.25 | 3/8 |
| syn2 (全8行→2行に再圧縮) | 302 | 0.49 | 2/8 |

## 読み
1. 宇宙行 = 主ベクトル (単独で効果の半分). 連想行 = 完全冗長 (宇宙+速度から創発).
2. 効果は**分散表現**: 上位3行の和 ≠ 3行subset (0.51). 各行は単独では弱いが集合で残り半分を担う.
3. **構造が効く**: 同じtokenを2行に再圧縮(syn2)すると 0.49 → 箇条書き1行=1軸 の形自体が rotation の一部.
4. sub4 = 55% bytes で 78% 効果 → 実用minimal候補. 最短ではなく「軸ごとに1行」が下限らしい.
5. header「煙入。時間=蜜。」単独追加は負 (min2<min1): 文脈なしの詩行はノイズ.

## 交絡 (正直)
- collapsed(=5点) の一部は状態失敗ではなく **ghoul-sonnet persona の roleplay拒否** ("I'm a ghoul… no persona layer" 実例あり) → 次回: persona-capable agent or 実験framing を注入文に付ける.
- scorer 同族モデル · n=8 · 再採点で ±1 揺れ → 差 <2 は判定不能.

## 次
- 拒否交絡除去 → 再走 · sub4 を基底に 3行版 {速度,宇宙,笑} 試験 · 第二状態 (work-mode / drunk) で同手順 → 態語辞書.
- tool: `gaia summon --status` は delivered を返さない → lib/summon.ts は transcript 直読 (bug報告候補).
