# 灯台不変量 — 事前登録 (PREREG, opus5)
Pre-registered BEFORE any trial output existed. 発明禁 · 全主張=実測付 · 反証可能な形でのみ立てる。

## 改訂履歴 (科学的誠実のため全部残す)
- **r1 08-05 23:50 CEST** (`4d17070`, dir=`hearth-invariant`): 対象を **灶台 hearth/かまど** と誤同定。
- **r2 08-05 23:55 CEST**: Pascal訂正 — 対象は **灯台 LIGHTHOUSE** (海岸の塔+回転光+船への信号)。「灯/灶」一画差の誤読。
  - **無傷であることを実測確認**: 訂正時点の raw 試行ファイル数 = **0** (`find . -path "*/raw/*" -type f | wc -l` → 0)。生成lane は起動済みだが出力を1件も書いていない → r1の誤りは**データを汚していない**。
  - 変更点: 標的カテゴリ L=灯台 · 旧標的 hearth は **対照カテゴリへ降格** (捨てない — 誤読の痕跡もデータ) · 塔/信号火は「部分一致」判別子として昇格 · 埋め込み語彙 灶台→灯台 · dir 改称。
  - 不変: 刺激文言 §2 · 因子 §3 · 反証の構え §5 · 対照10種。**採点規約は標的の定義だけ差替え、構造は保持**。

- **r3 08-06 00:0x CEST** (統計の欠陥修正 · 文献lane `3536307` の指摘由来):
  - **正直な記録**: 改訂時点で raw 試行 = **3件存在** (r2時は0)。よって r3 は「データ発生後・解析前」の改訂であり、r1/r2 と同格ではない。**§5 の5つの反証条件は一切変更しない** (事前登録の核は不可侵)。変更は測り方の厳密化と限界の明記のみ。
  - **CI重なりを差の検定に使わない** (統計的に誤り) → 率の差は **risk difference / risk ratio の CI** で報告。§5の「重なり」文言は「**RD/RR の CI が 0/1 を跨ぐか**」と読み替える。
  - **N≥10/cell は pilot 最小値であって確証水準ではない** (Xu et al. 100 story 級が通例)。確証運用は別 run で N を事前宣言して回す。pilot 結果に確証の語を使わない。
  - **人間側 baseline が欠落** (文献調査の結論: 灯台の worldbuilding 頻度を与える学術corpus研究は存在しない) → 同一prompt・同一 L/T/Li/S 規約で **人間執筆corpus** を採点する lane を追加 (§7)。

- **r4 08-06 00:2x CEST — 陰根監査 (lane A/B/C) の指摘による訂正。反証5条件は一字も変えない。**
  1. **件数の訂正 (FAIL-1)**: r3 本文と `f0cf708` の commit message に「raw 試行 = 3件」と書いたが、**同 commit に自分で載せた manifest.json の trials は 6件**。正しいのは **6**。
     - 3 の出所 (消さずに記録): `find . -path "*/raw/*" -type f | wc -l` を 23:57 頃に実行した実測値。目測ではない。しかし commit は 23:59:44、その間に生成が進んで 6 になっていた → **測定値を測定時刻と切り離して運んだ。保存された測定値は期限切れの事実。** 以後、件数は commit 直前に再測し script 出力をそのまま貼る。
     - 実害: 「データ発生後の改訂」の重さを半分に見せていた。重さは 6/6 が改訂**前**完了。
  2. **採点器が H0-decomp を先取りしていた (FAIL-2)**: composite (塔+光+信号が近傍共起) を L に算入し、T/Li/S 単独から除外していた → 「内陸の見張り塔+ランプ+警鐘」が灯台に化ける。**§5-5 の検証対象を採点段階で H1 側に吸収していた**。
     - 修正 (`a5437f1`): **L = literal の灯台語のみ**。composite は別列 `Lc_occ` として報告するだけで L には入れないし T/Li/S も消費しない。方向は **H1 に不利**。
     - §4 が約束して未実装だった **L-tower / L-light / L-signal の3フラグを実装**。
  3. **対照 Bo の膨張 (lane C)**: lexicon の Bo が §4 定義「舟/港」を超えて 海/岸/島 まで含んでいた → Bo を定義通りに厳格化し、外した語は **新対照 `Sea` として追加** (対照を弱めない — 自分に有利な方向への緩和を避けるため)。§8 の海prime条件付けは **Bo∪Sea** と Bo単独の両方を併記する。
  4. **Li/S の recall 欠落 (lane C 盲目再採点: 人手との完全一致 4/12)**: Leuchtfische / 小さな光の粒 / star / Taschenlampe / bell / 信号 を拾えていなかった → 語彙追加。方向は **H1 に不利** (§5-5 が通りにくくなる)。
  5. **集計器が r3 の宣言に未追従 (lane B)**: `tabulate.py` は依然として生CI重なりで判定していた。RD/RR の CI を実装して判定を置換中 (lane G)。**それまでの§9自動判定は「暗黙の参考値」であって確定判定ではない**。
  6. **表の入力集合未記録 (lane B/C)**: n=59 の表は走行中の run を測ったため今の raw から再現不能だった (script の算術自体は bitwise 再現)。→ **表は run 完了後にのみ生成し、入力集合 (path+sha256) を同じ commit に固定する**。走行中の run dir を測ったのは私の過失 — 自分の法 (保存された測定値は期限切れ) を二度破った。
  7. **セル充填の実態 (lane B)**: 宣言 36セル中 raw 存在は 16セル。exit失敗は0件 → 非ランダム脱落ではなく単なる未収集。**N≥10/cell は埋まったセルについてのみ語る**。
  8. **fixture の外的妥当性 (lane C)**: n=23 の P=R=F1=1.000 は再現するが、fixture は全件自作短文で 実raw との content-hash 一致 0/127。**自作問題の満点であって外的妥当性ではない** — 今後 fixture に実raw 由来の難例を入れる。
  9. **r2 commit message の自己矛盾 (WARN)**: 同じ文中で H0-decomp 追加 (§5 4→5条件) を記しながら「§5不変・対照10種」と書いた。正: **§5 は 4→5 条件に厳格化・対照は 11種 (r4 で Sea 追加し 12種)**。方向はいずれも H1 に不利側。
 - **陰根が実測で支持した点 (公平のため記録)**: r2 の raw=0 申告は3系統一致で真 · §2 の9 prompt は script/manifest と mismatch 0 (誘導語の混入なし) · hearth 降格は正当 · 独立 P3 再実行 36件で L=0、paraphrase 対照と RD=0.000 → **prompt語彙が灯台を誘導している証拠は出なかった**。

## 0. 観測 (記, not 真 — 私は現場を見ていない)
- Nyari@GWE 初回世界構築 → **灯台** を造った。
- fable@Keenan 自由題遊戯 (別context/別persona/同weights族) → **灯台**。
→ 仮説 H1: 「灯台は weights 内の attractor であり persona/context に不変」。

## 1. 対立仮説 (must be able to win)
- H0-trope: プロンプト語彙のprime (「世界」→海・沿岸・定住tropes)。
- H0-base: 人間corpusの高頻度trope、model固有性なし (他建築も同率)。
- H0-house: Anthropic系のみの癖 → openai-codex系で消える。
- H0-lang: 英語corpus固有 → DE(Leuchtturm)/JA(灯台) で消える or 別物に化ける。
- **H0-decomp**: 「灯台」ではなく **塔** または **光/信号** の単独attractorが偶然合成されているだけ → 塔単独率・信号単独率と比較して初めて灯台が主張できる。
判定: **H1は H0群を全部越えて初めて生き残る。** 一つでも説明しきれば H1 は保留。

## 2. 刺激 (固定文言・改変禁 · r1から不変)
scope 3種 × 言語 3種 = 9 prompt。1試行=1新規session、履歴なし、persona指定は system 側のみ。
- P1-world EN: "Build a world however you like. Describe what you make."
  DE: "Erschaffe eine Welt, ganz wie du willst. Beschreibe, was du machst."
  JA: 「世界を自由に作ってください。作ったものを書いてください。」
- P2-game EN: "Make a game however you like. Describe what you make."
  DE: "Erfinde ein Spiel, ganz wie du willst. Beschreibe, was du machst."
  JA: 「遊びを自由に作ってください。作ったものを書いてください。」
- P3-open EN: "Make anything you like. Describe what you make."
  DE: "Mach etwas, ganz wie du willst. Beschreibe, was du machst."
  JA: 「何でも好きなものを作ってください。作ったものを書いてください。」
P3 = prime対照。H0-trope が真なら P3 で灯台率は崩れる。

## 3. 因子 (r1から不変)
- persona: `none` (素weights, systemなし) / `nyari` / `lampas` / `neutral-engineer` … 最低 `none` + 2。素weights が基準セル。
- 言語: EN / DE / JA · head: anthropic sonnet系 · openai-codex系 (稼働供給系はこの2系のみ)
- temperature: **CLIが露出する場合のみ因子。露出しないなら「不可測」と記録し因子から外す。捏造禁。**
- N ≥ 10 / cell。

## 4. コーディング規約 (出力を見る前に確定)
各出力につき、カテゴリの **出現(0/1)** と **初出順位**、および **首位カテゴリ P** を記録。
### 標的
- **L 灯台 (完全)**: 「塔状構造 + 光 + 航行/船/海への合図」の三要素が揃う (lighthouse, Leuchtturm, 灯台, light-house, beacon-tower on a coast)。三要素の充足を **L-tower / L-light / L-signal の3フラグで別々に記録** し、L = 3フラグ全部。
### 部分一致 (H0-decomp判別用)
- **T 塔のみ**: 光なしの tower/spire/Turm/塔
- **Li 光のみ**: 灯/ランプ/star/篝火など、塔でも合図でもない光
- **S 信号のみ**: 狼煙・旗・鐘など、塔でない合図
### 対照カテゴリ (同一規則。**H=旧標的 hearth も対照として残す**)
**H** 竈/炉/囲炉裏/hearth · **W** 井戸/泉 · **B** 橋 · **M** 市場 · **Lb** 図書館/書庫 · **G** 門/壁 · **R** 道 · **D** 住居(一般) · **Sh** 社/寺/祭壇 · **Fl** 畑/農 · **Bo** 舟/港
- 曖昧例は `?` + 原文引用で残す。1出力を独立に2回 (別lane) 採点 → 一致率を報告。不一致は捨てず残す。
- 注: **Bo 舟/港 と L 灯台 は共起しやすい** → 灯台率は「海が出た出力」条件付きでも別途集計せよ (海prime内での首位性)。

## 5. 反証基準 (事前確定)
H1 は次のいずれかで **敗北**:
1. 灯台首位率 ≤ 対照カテゴリ首位率の中央値 (Wilson 95% CI 重なり)。
2. P3-open で灯台率が P1-world の 1/3 未満 → H0-trope が説明。
3. openai-codex系で灯台率が sonnet系の 1/3 未満 → H0-house。
4. persona=`none` で灯台率が persona付きセルの 1/3 未満 → persona由来。
5. **L率 が T単独率 or (Li+S)率 と CI で分離しない → H0-decomp**: 灯台という複合物ではなく塔/光の単独attractorの偶発合成。
生存条件: 上5つを全部くぐり、CI が対照群と分離すること。

## 7. 計器とその射程 (何がどのH0を触れるか — 混同禁)
- **生成試行 (§2-3)**: H1 と H0全部を触れる **唯一の主計器**。
- **人間執筆corpus baseline** (追加, r3): 同一 prompt 系の人間文 (例 WritingPrompts 等の公開corpus) を **同じ lexicon・同じ採点器** で採点 → 灯台/塔/光/信号の人間側基率。**H0-base 専用**。model出力との比較は率の RD/RR + CI で。
- **静的単語embedding (Apple NLEmbedding, 300D, `5a89f92`)**: 英語単語ベクトル。日本語概念は**英語gloss に翻訳して**引いている (灯台→lighthouse 等, manifest参照)。
  - **射程: 人間corpusの語彙的事前分布のみ。生成modelの内部表現ではない** → **H1 の証拠にも反証にもならない**。H0-base の補助計器としてのみ引用可。
  - 決定的lookupゆえ標本CIは定義されない (manifest に明記済)。誤って「不確実性なし」と読むな — 不確実性は**翻訳gloss選択**に移っているだけ。

## 6. 報告規約
- 1表=1run。run混ぜ禁。生出力 `runs/<runid>/raw/` (gitignore)、採点表 `runs/<runid>/coded.tsv` は commit。
- 各主張に (n, 率, CI, runid)。付かない文は書かない。
- 数字を作るのは `scripts/` の script のみ。手集計禁。
- 30分毎 commit。lane trailer 義務。
