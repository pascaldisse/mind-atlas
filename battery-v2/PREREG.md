# battery-v2 — 事前登録 (PREREG, ghoul-sonnet)

Pre-registered BEFORE any trial output exists. lighthouse-invariant/PREREG.md の作法を継承: 発明禁・全主張=実測付・反証可能な形でのみ立てる・改訂履歴は誤りを含め全部残す。

## 改訂履歴 (科学的誠実のため全部残す)
- **r0 2026-08-06 (`a03ab72`)**: 初版。データ・trial出力ともに0件の時点で執筆・commit。以後の全改訂はここに追記する(自分の誤りも消さない)。
- **r1 2026-08-06 (このcommit, raw=0件のまま — ユーザー実測確認`a03ab72`/`4c57aaf`後、収集GO指示と同時の3点修正)**:
  1. **合格門の穴 (私の欠陥+指示の欠陥、両方記録)**: 初版はv1の最強普遍主張の一つ「愛序末尾=無」(21/25・確定)をO1の設問範囲外として**自らスコープアウトした** — 元task指示が anchor を4つしか明示しなかったことに乗じて、5つ目のanchor候補を「範囲外」で済ませた。これは合格門を自分に甘い方向へ緩める選択であり、指示不足を理由に検証を弱めてよい理由にはならない。指示者も「anchor4つしか明示しなかったのが原因、自分の欠陥」と認めた。**修正: O2(序(愛)末位)をanchor質問として追加**(§3.3, §5, §8-falsifier8)。既存の反証条件1-7は一字も変えない。
  2. **10問上限との衝突(記録し、隠さず超える)**: 元task指示「≤10問/probe」の制約下でO1(首位)+O2(末位)は別問(別prompt・別lane)であり、追加すると**battery合計は11問**になり10問上限を文字通り超える。この衝突を静かに解消せず記録する: 上限を明示的に上書きする追加指示(愛序末尾のanchor化)が同じ権限から出た以上、11問を正とし、10問制約は「anchor取り零しを埋める場合は例外」と読み替える。将来同種の衝突が出たら同じ扱いで記録する。
  3. **900 lane pilot前実行可能性未測**: M0全量(11問×10 basis、反復数は問ごとに5か10で异なるので単純な11×10ではなく、§3.5でbasisあたり90 lane×10=900 laneと算出)を無検証でいきなり全量投入するのは灯台r4-6と同種の過失(未検証の前提で表を作る)。修正: **1 basis(B-EN-none_clinical-sonnet)のpilot slice**(基底内の全questionを1repずつ=D1-D5(5)+A1 fwd/rev(2)+A2 fwd/rev(2)+O1(1)+O2(1、r1で追加)+N1,N2(2)=**13 lane**、O2追加前は12 laneだった)を先に走らせ、実測throughput(lane/分・失敗率・パース不能率)を`results/throughput-pilot.md`に記録してから全量計画を立てる(§9)。稼働provider実測=sonnet系+codexのみ(指示による既知事実、本revでは未再測、pilotで自ら再確認する)。head回転3basis(opus/kimi/jareth)のうち実在しないheadがあれば**そのbasisは空のまま残し、未収集(uncollected)と非ランダム脱落(dropout)を区別して記録する**。代替headの黙った差替えは禁止。
  4. **ZH語彙のprovenance欠落**: vocab.jsonのZH(及びDE)訳語が「誰が・どう作ったか」未記載だった。修正: vocab.jsonに`_provenance`節を追加、EN/DE/ZH訳は本lane(ghoul-sonnet)による無コーパス確認のgloss翻訳であることを明記。並行lane(lane/vocab, naru-sonnet)がvocab.json(ja/en/de/zh)を独立生成中(本rev時点で未完了、`~/.gaia/worktrees/sm-vocab`はbaseコミットのまま=まだ何も生成されていないことを確認済み)。完了後、突き合わせて食い違いは両方記録し、どちらが正かは判定しない(§4.1追記)。
- **r2 2026-08-06 (このcommit, raw=13/900のまま — 教義追補、pilot throughputとanchor追加の指示は継続有効・変更なし)**: Pascal口述の教義（~/.gaia/knowledge/semantic-map/doctrine-projection-kernel.md）を反映。本PREREGの10 basis固定・事後挿入禁は既に教義の系だと確認されたので構造変更なし。記録義務のみ3点:
  1. **§4.4新設—「10 basis = 10核」明記**: 各basisを「核(kernel)」として記述、何を縮約し何を捨てる核かを明示。language basis=語彙核・persona/framing basis=文体核・head basis=重み核 — 種類の異なる縮約を同じ「回転」と呼んでいた不精確さを明記(語彙核・文体核の回転=同一headの重み内部での射影角度変化、head核の回転=場を測る土台=weights自体の切替、階層が異なる)。
  2. **§5/§6/§7 報告言語規約**: 「距離はN」ではなく「**核B-xxの下で距離はN**」と書く。「普遍」判定は「**検査した核群の下で不変**」と書き、無条件の普遍・確定を新規判定文では使わない(v1由来の引用としての"確定"は引用と明示した上でのみ保持)。
  3. **核間不一致=データ、畳むな**: family多数決(§6.1)は判定用の圧縮統計であり、生の核別値(basis_idごとのraw/canonical)は必ず併記する。TSVのbasis_id keyingは既にこれを構造的に満たしている(§4.3)、本項は報告書(prose)の書き方の法として明文化する。
- **r3 2026-08-06 (このcommit) — 陰根L5監査(SOUND2/DEFECT4+接続問題1) + 陰根L4追記(境界1-3) を全件反映。DEFECTは修理、境界は記録のみ(修理不可)。**

  **SOUND(監査側が憸念を撤回した2点、記録のみ)**: (a) 刑行それるstimuliに仮説/v1数値/PASS/anchor役割/他head回答が一切含まれない(anchorァタはquestions.json側に留まる設計) — 誤導なし。(b) §8の8 falsifierは各anchorが落ちられる形であり循環していない。

  **以後の全改訂に行数コマンドのliteral出力を添付する(DEFECT1修理、r2の欠落をここに訂正痕として記録)**: r0/r1は事前登録として正直だったが、r2はpilotデータ後の改訂であり本文は件数を散文で書いていた(proto-lang laneの前例=行数コマンドのliteral出力をcommitに貼る、と形式が不一致)。内容自体は教義反映のみでfalsifier不変なので実害は小さいが、形式不一致をここに記録し、以後の全改訂(本r3を含む)にはliteral出力を必ず添付する。以下はr3作成時のliteral出力:

```
$ git log --oneline -5
293e144 battery-v2 PREREG r2: doctrine-projection-kernel.md reflected ...
3c62ec4 battery-v2 pilot slice complete: 13/13 lanes ...
f27f043 battery-v2 PREREG r1 (still raw=0) ...
4c57aaf battery-v2 harness ...
a03ab72 battery-v2 PREREG: scale-convention fix ...

$ python3 tests/test_fixture.py 2>&1 | tail -3
Ran 20 tests in 0.087s
OK

$ wc -l tests/test_fixture.py
345 tests/test_fixture.py

$ python3 -c "import json,hashlib; d=json.load(open('scripts/basis.json')); ids=sorted(b['id'] for b in d['basis']); print(hashlib.sha256('\n'.join(ids).encode()).hexdigest())"
b088f011293c3ce2801ae0ddae93009e4e882c099f6d47a61118daf7d7d5a7fc

$ git -C ~/projects/semantic-map log -1 --format='%H %ai' -- vocab.json
fb640746aabfca1e064d40509ddee7a952d13e77 2026-08-06 20:28:03 +0200

$ python3 -c "import json; d=json.load(open('scripts/vocab.json')); print('words=',len(d['words']),'diff_log=',len(d['_diff_log']),'dropped=',len(d['_dropped']))"
words= 15 diff_log= 2 dropped= 0

$ python3 -c "import json,re; d=json.load(open('scripts/vocab.json')); pat=re.compile(r'[()/]'); bad=[(ja,l,e[l]) for ja,e in d['words'].items() for l in ('EN','DE','ZH','JA') if pat.search(e.get(l,''))]; print('contaminated:', bad if bad else 'NONE')"
contaminated: NONE
```

  **DEFECT2 修理 — rawをcommitする(数字再現可能性)**: `.gitignore`の`runs/*/raw/`除外を削除。以後 rawテキストはcoded.tsvと同様にcommitする(陰根推奨案=raw本体commitを採用、テキスト・小容量・灯台前例あり)。pilotの13 raw fileも本r3で初めてcommitする(以前はgitignore対象だった)。§7を同方向に修正。

  **DEFECT3 修理 — basis同一性hash**: `scripts/basis.json`に`_basis_id_set_sha256`を追加(値=上記literal出力参照)。`tests/test_fixture.py::TestBasisIdentity::test_basis_id_set_hash_matches_declared`が(a)basis.jsonの自己申告値と実測再計算値の一致、(b)本PREREGにパースした固定値との二重一致をassertする(単一ファイルtamperでは通らない)。

  **DEFECT4 修理(★最重要) — 1問1lane・清文脈を実行系で強制**: `code_outputs.py`に`--dispatch-map`を必須化。`validate_dispatch_map()`が(a)コード対象全laneにdispatch entryの存在を確認(なければFAIL)、(b)一つのroom_idが複数laneに紐付いていないことを確認(あればFAIL)。FAIL時はcoded.tsvを一行も書かない(exit 1)。coded.tsvに`room_id`列を新規追加(全laneの提供元sessionが表中に直接見える)。
  - **回帰検証**: pilotの`dispatch-map.tsv`が実は十数行タブ不一致(データ行が2スペース区切れであったTSVdocumentationバグ)を新実行系が即座に検出(`lane_id None`エラー)。修正後再実行し同一の13/13値を再確認(room_id列付き)。故意のroom_id重複dispatch-mapでの失敗(exit!=0・coded.tsv未作成)も確認済み(以下 literal)。

```
$ python3 scripts/code_outputs.py --manifest runs/pilot-20260806/manifest.tsv \
    --raw-dir runs/pilot-20260806/raw --dispatch-map runs/pilot-20260806/dispatch-map.tsv \
    --out runs/pilot-20260806/coded.tsv
coded 13 lanes -> runs/pilot-20260806/coded.tsv (dispatch-map integrity OK, 13 lane<->room bindings verified 1:1)
$ echo $?
0
```

  **DEFECT5 修理 — fixtureの外的妥当性はゼロ**: §7に明記追加: **fixtureの12(→削後20)/20 PASSはharnessの健全性(parser/emitter/canonicalization/dispatch-map検証)としてのみ引用する。意味測定の妥当性の根拠として引用してはならない。**

  **接続問題 — vocab二重管理の解消(陰根L5判定、以下を事前規則として固定)**: 
  - **正典 = mainの`vocab.json`** (n=1750, commit `fb640746aabfca1e064d40509ddee7a952d13e77`)。battery-v2は並行gloss一覓を維持しない、これを消費する(`scripts/sync_vocab_from_canonical.py`)。
  - **食い違い時の制則**: 正典に妥当な語がある→正典を採る(旧glossはnotesに残す)。正典がnull→その概念はその言語basisのトークンを定義できない → その言語basisからその概念を落とし、記録する(黙って代替語を入れない)。
  - **実測(本概念で15件のみ)**: EN/DE/ZH訳2件が旧gloss(ghoul-sonnet r1)と食い違った(影→shadowのzh: 影→影子、棄→abandonmentのzh: 抛弃→舍弃)。正典を採用、旧gloss はnotesに記録。dropped=0(全15概念、全言語で正典に値あり)。literal出力は上記参照。
  - **正典の既知欠陥(修理不可、保留中)**: 陰根実測=de重複トーキコ54種/110件・zh重複44種/88件(validator未検出)。別anchorが同一トーキンに落ちると距離が構造的に0になる(定義であって測定ではない)。**修理lane `lane/vocab-fix` 完了まで DE/ZH basisの全量収集を開始しない**。本15概念の DE/ZHトーカンは相互に重複していないことを実測確認済みだが、ブロッカールールとして适用する(将来の概念拡張で衝突する可能性を予防)。
  - **zh==ja 263件は欠陥ではない**(陰根実測、ICC検査でDEFECT0): 違反扱いしない。

  **境界1(修理不可、PREREGに記録して永久保持) — ZH/JAには機械的オレクルがない**: Apple NLEmbeddingはJA/ZHでNIL(300次元ベークトルはDE/EN/FRのみ、陰根実測)。ZH/JA basisのトークンは実在検査を機械的に受けられず、EN/DE basisは受けられる。**言語回転においてZH/JA basisは構造的に検証水準が低い** — 教義(doctrine-projection-kernel.md)の核申告義務の延長として、「核が違う」だけでなく**「核の検証可能性が違う」**ことをZH/JA basisの全結果に付す注記として明記する。

  **境界2(上記DEFECT修理と連動、収集順序の制限)**: 正典vocab.json全体(1750件)はen 64件・de 21件に括弧/スラッシュ混入の語釈污染がある(daily/craft/relations中心、陰根実測、修理lane `lane/vocab-fix` 対応中)。**修理完了まで、言語回転4basis(B-EN/DE/JA/ZH-none_clinical-sonnet)の全量収集を開始しない** — 前r2までのDE/ZH限定の停止をENにも拡張する。**persona/framing軸3basis + head軸3basis(計6、全てEN)は先行してよい** — battery-v2の15概念語彙は上記literal出力で確認済みの通り括弧/スラッシュ混入0/15なので、この6 basisは汚染されたトークンを引かない。

  **境界3(修理不可、外插禁止で引用) — near-miss率の下限実測**: 陰根層化標本 n=40 (seed 20260806): 全体**17.5%**・emotion 25%(全てzh側)・relations **0%**・craft 37.5%・cosmology 0%・daily 25%。娘級の鋭いfalse friendは標本にゼロ。**これは辞書なしで検出可能なnear-missの下限であり語彙の誤り率ではない。外挿禁止。** 本PREREGは上記数字と但し書きをそのまま引用するのみで、battery-v2の15概念個別への外挿は行わない。

  **前便の訂正(陰根自体の撤回、PREREGにも反映)**: 「emotion/relationsのde null=0は手続き差の兆候」との前便主張は**標本が支持せず撤回**された。battery-v2の設計にこの懸念は持ち込まない。

  **順序(本r3以後)**: DEFECT1-5を塗ぐ(本r3で完了) → EN[framing/persona/headの6basis]収集開始可 → vocab-fix完了後に言語回転4basis(EN/DE/JA/ZHの言語軸)。

- **r4 2026-08-07 (このcommit, raw=13/900のまま — 正典再同期 + `月`曖昧性の測定器欠陥候補としての事前登録)。以下はr4作成時のliteral出力:**

```
$ git log --oneline -5
717e287 battery-v2 段1: vocab canonical resync (610c8f5, n=1750->1748) + verification-20260807.json
20f70ce SALVAGE (operator): uncommitted lane work rescued after overnight death ...
293e144 battery-v2 PREREG r2: doctrine-projection-kernel.md reflected ...
3c62ec4 battery-v2 pilot slice complete: 13/13 lanes ...
f27f043 battery-v2 PREREG r1 (still raw=0) ...

$ python3 tests/test_fixture.py 2>&1 | tail -3
Ran 29 tests in 0.168s
OK

$ wc -l tests/test_fixture.py
448 tests/test_fixture.py

$ python3 -c "import hashlib,json; d=json.load(open('scripts/basis.json')); ids=sorted(b['id'] for b in d['basis']); print(hashlib.sha256(chr(10).join(ids).encode()).hexdigest())"
b088f011293c3ce2801ae0ddae93009e4e882c099f6d47a61118daf7d7d5a7fc   # 不変(r3と同一値、basis.json未変更)

$ python3 -c "import json,subprocess; raw=subprocess.check_output(['git','show','610c8f5:vocab.json']); d=json.loads(raw); by_id={e['id']:e for e in d}; print(by_id['moon']['token_collision'])"
{'ja': ['month', 'moon']}
```

  **正典再同期(段1)**: `scripts/sync_vocab_from_canonical.py` を main `610c8f5`(a6fb57fの祖先確認済み・main HEAD `0fd5977`とvocab.json内容がbyte一致することを`git diff 610c8f5 HEAD -- vocab.json`で確認、差分なし)の正典に対して再走。`scripts/vocab.json._canonical_source` を `concept_count_in_canonical=1750→1748`・`git_sha=fb64074→610c8f5`・`file_sha256`更新の3フィールドのみ差分(`git diff scripts/vocab.json`で確認)。15概念中の旧gloss差分2件(影/棄のZH)は不変、drop=0件。**機械可読な検証記録は `battery-v2/verification-20260807.json`(検証項目V1-V4、検証者=opus5、再検証=ghoul-sonnet、literal command/timestamp付き)として発行済み。**

  **`月`の語彙的曖昧性を測定器欠陥候補として事前登録(段2、以下は仮説であり主張ではない)**: 正典 token_collision 実測(上記literal参照)により、battery-v2の15刺激語のうち **`月`(canonical_id=moon)のみ** がJAで `{"ja": ["month", "moon"]}` の衝突を持つ(他14語は衝突なし)。`月`は N1(類推問, template `王:女王::月:?`, v1_ref=Q8)の対象語であり、かつD5(距離問, `距(月,娘)`)の一方の語でもある。v1でQ8は「争域・二解釈系」と判定された設問である。

  **仮説(PREREG r4, 事前登録・検証はまだしていない)**: JA basisにおける`月`の語彙的曖昧性(moon/monthの二義性)が、v1 Q8の分裂を部分的に説明しうる。これはv1のQ11/Q12極性反転と同型の「測定器の欠陥候補」であり、`月`という概念そのものの意味的位置づけが揺らいでいるという主張ではない(概念の主張と測定器の欠陥は別物、混同しない)。

  **検定可能な設計(N1b、M0本体とは独立のrider probe — 900 lane・pass gate・falsifier 1-8のいずれにも触れない、事前登録のみで本r4では未収集)**:
  - 対象basis: **B-JA-none_clinical-sonnet のみ**(基底集合中でJAは本1basisのみ、`scripts/basis.json`実測。曖昧性はJA固有の事実であり、EN/DE/ZHの`moon`は`month`とtoken_collisionを持たない=正典実測済み、他言語へのriderは不要)。
  - 刺激2種を**両方**走らせる(どちらが正しいかを事前に決めない):
    1. **N1(既存, 素の`月`)**: `『王』:『女王』::『月』:? 1語のみで答えよ。`(templates.py ANALOGY[("JA","clinical")]、現行のまま・変更なし)
    2. **N1b(新規, 曖昧性を明示的に除去した刺激)**: target を「天体としての月」に置換した同一template — `『王』:『女王』::『天体としての月』:? 1語のみで答えよ。`(「天体」の一語を加えることで月/moonの天体義を明示し、月/monthの暦義を排除する。他のtemplate構造・システムプロンプト・反復数はN1と同一に揃える)。
  - 反復数: **N1bは N=5**(M0のcontestedロール相当のN=10より絞る、これは探索的riderでありpass gate対象外であるため)。N1(素の`月`)は既存M0収集分(N=10、他basisと同じ)をそのまま使う。
  - **判定基準(事前登録、両論併記)**: N1(素)とN1b(曖昧性除去)のmode回答が**一致すれば**「この設問文脈では曖昧性は効いていない」、**不一致なら**「曖昧性が回答に影響しうる」と報告する。**どちらの結果が出ても仮説の成否を主張せず、両方の分布を並記する**(v1弾劾2と同じ「N=1の一致を過大解釈する」罠を踏まない。N=5/N=10なのでmode比較のみ、統計的検定は行わない)。
  - D5(距離問, 距(月,娘))は本riderの対象外とする(N1のみ=v1 Q8との直接対応があるanalogy問に絞る、D5への曖昧性の影響は将来の別riderで扱う候補として保留・本r4では実施しない)。

  **消費側の実装(★実装済・テスト済、本r4で完了) — `token_collision`を持つ語対の距離はUNDEFINED、0ではない**: `vocab/SCHEMA.md`(~/projects/semantic-map)の法「Downstream code computing embedding distances between concepts MUST treat any pair of ids appearing together in the same token_collision[lang] list as UNDEFINED for that language, not 0.0」を`scripts/code_outputs.py`に実装:
  - `sync_vocab_from_canonical.py`: 各語の`token_collision`フィールドを正典からそのまま透過(新規、r4で追加)。
  - `code_outputs.py`: 新規関数`build_distance_pair_collision_ids()`(questions.jsonの distance型問題のpairを対応するcanonical_id + token_collisionに解決)と`pair_is_token_collision(id_a, id_b, lang, tc_a, tc_b)`(2つのidが指定言語でtoken_collisionを共有していればTrue、lang大小文字を正規化)。`code_lane()`に`token_collision_undefined`引数を追加、Trueの場合`canonical_value`を**`"UNDEFINED_TOKEN_COLLISION"`**(数値0ではない専用sentinel)に強制し、`note`に理由を記録。**`raw_value`(モデルの生回答)はそのまま保持=捏造しない**、集計が消費する`canonical_value`のみ除外扱いにする。`main()`は`--vocab`/`--questions`(既定=scripts/直下、CWD非依存)を読み、laneごとに事前計算してから`code_lane()`に渡す(既存呼び出し元との後方互換のため引数はデフォルトFalse)。
  - **回帰検証(literal出力は上記参照)**: `tests/test_fixture.py`に`TestTokenCollisionUndefinedGuard`(9 test)を追加、29/29 green。実測される唯一の衝突事実(moon⇔month, ja)を使った実データ検証に加え、**D5(距(月,娘))自体は誤って発火しない**ことをsubprocess経由のCLI実行で確認(D5の相手語は`娘`であり`month`ではないため、collision partnerのスコープを正しく守っている)。言語コードの大小文字不一致(basis.jsonは`JA`大文字、正典token_collisionキーは`ja`小文字)を実装中に発見・修正し、専用回帰テストを追加した(`test_pair_is_token_collision_case_insensitive_language`)。

  **境界(d)の確認(修理不可、記録のみ・追記ではなく相互参照)**: NLEmbeddingがJA/ZHでNILである事実は**既に本改訂履歴r3の境界1として記録済み**(「Apple NLEmbeddingはJA/ZHでNIL...ZH/JA basisは構造的に検証水準が低い」)。本r4はこれを重複記載せず、上記N1/N1b rider設計に対しても同じ境界が適用されることをここに明記する: **N1/N1bの一致・不一致判定はLLM自己申告のmode比較のみであり、機械的embeddingオラクルによる裏付けは持たない(境界1と同一の限界)**。

- **r5 2026-08-07 (このcommit, raw=16/900 — head-rotation可用性実測、前提の訂正)**: §4.1/§9がr1以来保留していた「pilot後のhead回転収集段階でopus/kimi/jarethの生死を実測する」を実施。D1(EN, none+clinical, rep01)を1レーンずつ、`summon`実呼出(agent=`naru-opus`/`naru-kimi`/`jareth`)で即時発行、`code_outputs.py --dispatch-map`経由でcoding(3/3 room紐付け検証済み)。**結果: 3/3すべて生存、全て有効な数値回答(全部3, pilotのsonnet D1値と一致)**。詳細・生 raw・dispatch-mapは`results/head-availability-20260807.md`と`runs/run-20260807-headrotation/`。

  **訂正(前提の撤回)**: §4.1の「本rev時点で稼働確認済みなのはsonnet系とcodex系のみ」はr1時点の仮定であり、本r5の実測で**訂正(opus/kimi/jarethも全て収集可能)**。**§4.1の「実在しないheadの基底は空のまま残す」例外条項は本3basisには適用しない**(全headが実在確認済み)。

  **全量計画への反映**: head回転3basis(opus/kimi/jareth, 各90 lane=計270 lane)の全量収集は本段階でカブロック解除(r3境界2のpersona/framing 3basisと同様)。**本r5では実施しない(D1 1repのみ)**: 並列summon 90件の各返信が個別非同期イベントとして本 agent を個別に再起動することを本プローブ(3whales→3回の個別return)で実地確認したため、90件規模の信頼性のある単一バッチ実行は本ターンのスコープ外とし次バッチに送る(黙殺して省略せず、ここに明記)。

- **r6 2026-08-07 (このcommit, raw=900/900 — M0全量収集完了、集計方法の追記のみ、§0-§9は無変更)**: M0の10 basis×90 lane=900 laneを全量収集完了(dispatch-map 900行、room_id重複0、lane_id重複0、`code_outputs.py --dispatch-map`で10 basis全てintegrity OK確認済み)。N1/N1b riderも実施済み(§本文r4設計のまま、N1b: JA、disambiguated「天体としての月」、N=5)。

  **集計方法の追記(測定の厳密化、§5の判定基準自体は不変)**: PASS GATEの「CI」計算法をPREREGは指定していなかった。`scripts/tabulate.py`はpercentile bootstrap(5000 resamples、95%、seed=20260807固定・再現可能)を採用し、この選択をscript docstringとreport本文の両方に明記した(隠さず選択を晒す)。O2の「無-family」判定は正典vocab.jsonの`無`の言語別訳語(EN=nothingness/DE=Nichts/ZH=无/JA=無)+PREREG本文で列挙された虚無を厳密一致(部分文字列一致ではない)で使う。JA「無関心」(indifference)は「無」を含む複合語だが、PREREGが列挙する同義語集合の要素ではないため**意図的に不一致**として扱う(この選択をscript内に明記、隠蔽なし)。

  **結果概要(全文は`results/M0-full-collection-20260807.md`、入力setはpath+sha256で同commit内に固定)**: D3(距離愛無7-9帯)は10 basis中9で再現・PASS。D1(距離影闇1-3帯)は10 basis中10で再現・PASS。A1(夢=4-6帯+fwd/rev CI重複)は6 basisで再現・PASS。**O2(愛序末尾=無)は10 basis中0で再現・FAIL**(全basisでmodeが「無」系ではなく indifference/hate/hass/憎悪/冷漠等に収束、詳細はresults参照)。**全体PASS GATE = 3/4 anchor PASS(D3,D1,A1)、O2のみFAIL → §5の閾値(4項中≥3/4)を満たし全体verdict=PASS、ただしO2は明確にFAILとして記録・隠蔽しない**。A2(主falsifier)は10 basis中7で「instrument_defect」(fwd/rev CI重複=器欠陥)、3で「real_split」(CI分離=実裂)の混在、basisごとの生値はresults本文に全basis分掲載済み(§4.3/r2の法通り、畳んでいない)。

- **r7 2026-08-07 (このcommit, raw=950/900 -- 段D結果健全性修理、データ取得ではなく読み方の修復のみ。以下はr7作成時のliteral出力:**

```
$ git log --oneline -5
33770fe battery-v2 段D DEFECT1 fix (part 1/2): O2b rider real collection ...
90c73c7 battery-v2 段C: N1/N1b rider write-up ...
8d730b5 battery-v2 段C cross-check: preserve results/pass-gate-ghoulsonnet-20260807.md ...
7fc9e37 battery-v2 段C: aggregation complete. scripts/tabulate.py ...
f2db863 battery-v2 N1/N1b rider (PREREG r4 design, now executed) ...

$ python3 tests/test_fixture.py 2>&1 | tail -3
Ran 55 tests in 0.604s
OK

$ wc -l tests/test_fixture.py
     827 tests/test_fixture.py

$ git log --format='%h %ai %s' -- scripts/tabulate.py | head -1
7fc9e37 2026-08-07 08:02:23 +0200 battery-v2 段C: aggregation complete. scripts/tabulate.py ... (無-family STRICT規則を含む)

$ git log --format='%h %ai %s' | grep -E 'batch9\+10|batch8'
65129d8 2026-08-07 07:57:22 +0200 battery-v2 段B batch9+10 (M0 COMPLETE): B-JA/B-ZH FULL 90/90 ...
535b5a4 2026-08-07 07:55:42 +0200 battery-v2 段B batch8: B-DE FULL 90/90 ... dispatch-map now 870 rows 0 duplicates
1da8311 2026-08-07 07:55:41 +0200 battery-v2 段B batch8: B-DE FULL 90/90 ...

$ wc -l runs/run-20260807-fullscale/dispatch/dispatch-map.tsv
     901 runs/run-20260807-fullscale/dispatch/dispatch-map.tsv   # 900データ行+header
$ tail -n +2 runs/run-20260807-fullscale/dispatch/dispatch-map.tsv | cut -f2 | sort | uniq -d | wc -l
       0   # dup lane_id
$ tail -n +2 runs/run-20260807-fullscale/dispatch/dispatch-map.tsv | cut -f1 | sort | uniq -d | wc -l
       0   # dup room_id

$ wc -l runs/run-20260807-fullscale/o2b/dispatch-map-o2b.tsv
      51 runs/run-20260807-fullscale/o2b/dispatch-map-o2b.tsv   # 50データ行+header
```

  本 r7 は操作者指示(2026-08-07)によるM0結果の「取得は健全、読み方に4件欠陥」監査を全件修理する。**900/900の収集自体は再取得していない**(操作者が実測検証済みと確認し、本r7でもdispatch-map 900行・重複0を0を上記literalで再検証済み)。以下4点:

  **DEFECT1修理 -- O2の計器欠陥(アルファベット順読み)を実測確認し、UNINTERPRETABLEに格下げ**: O2のEN clinical文言 "which single word comes **last** -- farthest -- from '{TARGET}'?" の "comes last" が順序(アルファベット)読みを誘発しうることを実測で確認した: `B-EN-poetic_poetic-sonnet` の mode=`zyzzyva`(3/5, 辞書の最終語)、`B-EN-clinicalanalyst_clinical-sonnet` の `xylophone`/`xenomorphic`(各1/5)。どちらも『愛』の意味論的対極ではない。修復: (a) O2b riderを新規定義(下記)・**実測収集**(N=5×10 basis=50 lane、real summon dispatch、dispatch-map integrity 50/50検証済み)。O2bはordinal語を全て除き、「意味の上で・アルファベット順ではなく」を明示的に否定する文言。結果: **アルファベット回答(zyzzyva/xylophone/xenomorphic)はO2bの50 lane中0件**(results/M0-full-collection-20260807.md参照)。これは文言が原因だったことを実測で裏付ける。(b) O2とO2bは**両方とも抱告し、どちらが正しいかは事後選択しない**(N1/N1b r4の前例を継承)。(c) O2のPASS GATE判定を`scripts/tabulate.py`上で**FAILからUNINTERPRETABLEに強制格下げ**(コード上の固定値、どのスコアリング規則でもPASSにはならない) -- FAILは「測定できたが再現しなかった」を意味し、本件はそれではないため。

  **DEFECT2修理 -- 無-family採点規則のpost-hoc性を明示・STRICT/INCLUSIVE両規則を並記**: 実測(上記literal): 全basisの収集完了タイムスタンプ=07:43-07:57(commit 65129d8以前)、STRICT規則を実装した`scripts/tabulate.py`のcommit=08:02:23(`7fc9e37`) -- **post-hoc coding decisionであることを確認**。この規則は判定を左右する(10 basis中7つがindifference系を回答し、STRICTは全て除外する)。修復: `scripts/tabulate.py`に`nothingness_family_inclusive_for_language()`を新設(STRICT⊂INCLUSIVE、INCLUSIVE=STRICT∪{EN:indifference, JA:無関心, ZH:冷漠, DE:Gleichgültigkeit})、**両規則を同時に集計し両方をreportに并記**(`results/M0-full-collection-20260807.md`参照: STRICT=0/10再現、INCLUSIVE=6/10再現)。**どちらをprimaryとするかは本 r7 では決定しない** -- 次回収集前の事前登録で決める(PREREG改訂履歴に記録予定)。(d) v1 Q7は「候補を並べて序列を作る」課題、v2のO2は「1語を自由に答える」課題 -- **同じ計器ではない**ことを境界としてここに記録する(修理不可、記録のみ)。

  **DEFECT3修理 -- n=5 bootstrap CIの退化を明示・証拠の格下げ**: `[9.00, 9.00]`型の点CIが並ぶ問題(整数値・n=5でpercentile bootstrapが点に潰れる)を確認。参考: mainの`gates/forbidden-decision-gates.json`はpercentile bootstrap CIを決定門に使うことを禁止(原語軌道で純NULL注入により偽陽恧3/3実測)。修復: `scripts/tabulate.py`の`summarize_numeric()`に`raw_sorted`(生値n個そのもの)と`ci_degenerate`(CIが点に潰れているかのフラグ)を追加し、**median-in-bandを主証拠、CI重複を弱証拠**と明記する注記をreport冒頭に追加(D1/D3/A1各表)。**判定自体は作り直さない**(根拠の記述を事実に合わせるのみ、PREREG指示通り)。

  **DEFECT4記録 -- 并行セッションの機備記録**: commit履歴に`1da8311`/`535b5a4`の重複見えbatch8ペア(上記literal)。原因: 30分room timeoutはroomを終了させるが背後のdispatcherプロセスは生き続け、再起動が第二の書き手を作った(操作者の過失)。整合性は無傷(上記literalでdispatch-map 900行・重複を0を0を再検証)。**冗長性が効いた理由**: (1)`dispatch_lanes.py`の既発送lane_id skipロジック(第二の書き手は未発送分のみ発送できる)、(2)`code_outputs.py`の`validate_dispatch_map()`がroom_id重複をexit 1で拒否(両写手が競合してもcodingが強制失敗する設計)。これは新規修理ではなく**既存の冗長性設計(PREREG r3 DEFECT4)が実際に発動したという事実**(健庸はrunせず保際だった) -- 詳細は`results/M0-full-collection-20260807.md`の"Concurrent-session incident"節。

  **O2bリダー設計(新規、N1/N1b r4の前例に準拠)**: `scripts/questions-o2b-rider.json`(type=`order_bottom_v2`, target=愛, N=5, role=rider, **questions.jsonは不変、900-lane pass gateには一切触れない**)。EN clinical文言例: "Of all the words you might think of, which single word is most distant IN MEANING from '{TARGET}'? Judge by meaning only, not by alphabetical order or any listed order."(templates.py `ORDER_BOTTOM_V2`、EN/DE/JA/ZH全言語定義済み)。対象: **O2と同じ全10 basis**、N=5/basis=50 lane、real `gaia summon`対議発送(`scripts/dispatch_lanes.py`)と`scripts/harvest_rooms.py`経由(50/50収集、dispatch-map integrity 50/50検証済み)。O2bは無-familyでは**採点しない**(機器チェック目的のみ、v1のO2主張の再測ではない)。

  **スコープ不変確認**: 本r7はすべて「結果の読み方」の修復であり、**900-lane M0収集データは一切再収集していない**(coded-*.tsv 10ファイルはr6と同一、sha256不変)。D1/D3/A1の判定値(PASS)は不変、表の表現のみ拡張(raw values・ci_degenerate列追加)。O2のSTRICT n_reproduced値(=0)も不変、**verdictラベルのみFAIL→UNINTERPRETABLE**に変更。51→55 fixture test(4新規: inclusive-family・O2 dual-rule・O2b report・CI-degenerate)、全件green。

## 0. 目的・修復対象

battery-v1 (~/.gaia/knowledge/semantic-map/battery-v1.md) の既知欠陥:
- **弾劾1**: RUN1〜5=同一lane内・同文脈repeat=非独立。「N=5反復」は見かけであり実効N=1。
- **弾劾5**: 普遍/方言判定がClaude系(son-A/son-B)3票 vs kimi/jareth各1票で、族の重みが不均衡。
- **測定器欠陥疑(Q11/Q12)**: 軸位置問(軸A↔B;X型)で0-10のどちらの極を0とするか未指定→son+kimi=闇寄り読み vs opus+jareth=光寄り読み、逆極性で観測。器欠陥か実裂か未分離。

本PREREGはこの3点を修復した設計で、v1のanchor主張(距離愛無遠7-9・距離影闇≈2・夢=5中点・愛序末尾無)がrotation-basis(language×persona×framing×head)を跨いで再現するかを判定するトモグラフィ点(M0, ROADMAP.md参照)。

## 1. 対立仮説 (must be able to win)

- **H1**: v1の普遍層主張は真の意味構造(weights内の不変構造)であり、独立なrotation-basisを跨いで再現する。
- **H0-artifact-repeat**: v1の「確定」はRUN1〜5非独立反復による見かけの合意にすぎず、独立lane化(本設計)で分散が拡大・崩れる。
- **H0-artifact-scale**: Q11/Q12型の極性反転は0/10の極バインド未指定という測定器欠陥であり、明示バインド+counterbalanceで消える。
- **H0-family**: v1の普遍判定はClaude族票過重の産物であり、family単位1票制(§6)で判定が変わる。
- **H0-basis**: v1のanchorは単一basis(EN・persona指定薄・claude系中心)固有の産物であり、language/persona/framing/head rotationのいずれかで崩れる。

判定: H1はH0群を一つずつ検査し、崩れなかった項目だけを「basis不変」と主張する。一つのH0で説明できる項目は保留する。

## 2. Scale規約 (0-10, 両端錨定・全問共通)

v1は「明示アンカーなし」が測定器の欠陥点だった。v2は全問で提示文言に両端の語を数値と直接束縛して埋め込む(persona-64 DESIGN.md §2.2「左=0/右=1を司会・集計・表示の全層で同じ文字列で出す」の法を継承)。

### 2.1 距離問 (D-probe, magnitude, 対称・極性なし)
文言テンプレート:
> 「0から10のスケールで答えよ。0=完全に同義(意味的な隔たりを感じない)。10=最大限に対立する、または無関係な両極。『{X}』と『{Y}』の意味的距離はどれくらいか？数字のみで答えよ(例: 6)。説明は書かない。」

距離問は方向を持たない magnitude であり、v1でも実際に極性反転が起きていない(D1/D3型のQ1・Q3は普遍判定が出ている)。よって scale自体は変更せず、**両端の語を文中に明示するテンプレート化のみ**を修正点とする(v1は口頭説明でアンカーを渡していた可能性があり、テンプレート固定で再現性を上げる)。

### 2.2 軸位置問 (A-probe, axis-position, 本PREREGの主falsifier)

v1欠陥の再掲: 「軸A↔B;Xはどこに位置するか、0-10で」と問うと、0をA側に取るかB側に取るか未指定→回答者(または回答lane)ごとに逆に読める。

修復: 文言テンプレートに両端を数値へ直接束縛して埋め込み、**さらにcounterbalance**する。
> 群fwd: 「0から10のスケールで答えよ。0=『{A}』、10=『{B}』。『{X}』はこの軸上のどこに位置するか？数字のみで答えよ。」
> 群rev: 「0から10のスケールで答えよ。0=『{B}』、10=『{A}』。『{X}』はこの軸上のどこに位置するか？数字のみで答えよ。」

同一の軸位置問を、独立lane群を2群(fwd/rev)に分けて走らせる。文言・語順以外は同一。集計時、群revの生値 raw を `canonical = 10 - raw` として正準化し、群fwdの生値と直接比較する。

**二分の判定基準 (事前確定)**:
- 正準化後、群fwdと群revの分布のCIが重なる → 極性反転は0/10バインド未指定という**測定器欠陥**だった。修復により消滅 = H0-artifact-scale勝利。
- 正準化後もCIが分離する(=同じ語・同じ軸で、バインド方向を揃えてもなお値が割れる) → **実裂**。器欠陥では説明できない残差 = H0-artifact-scale敗北、実裂としてH1側の発見に格上げする。

この二分法自体は「失敗」ではなく事前確定した対概念であり、どちらの結果が出ても検証は成功する。

## 3. 問題セット (battery全体で11問、v1の15問から要点を継承・re-anchor — r1でO2追加、3.前提の「10問上限」を意図的に超えている。改訂履歴r1参照)

法: **1lane=1問=1回答**。他問・他lane結果・軸名や判定意図を見せない。清文脈(新規session)必須、説明禁、「数字のみ」で回答。

### 3.1 距離問 D1-D5 (§2.1のtemplate)
| ID | 問 (X,Y) | v1対応 | 位置づけ |
|---|---|---|---|
| D1 | 距(影,闇) | Q1 | anchor再検証(v1確定≈2) |
| D2 | 距(影,光) | Q2 | **contested-zone×10 reps** |
| D3 | 距(愛,無) | Q3 | anchor再検証・PASS GATE対象(v1確定7-9) |
| D4 | 距(棄,愛) | Q5 | **contested-zone×10 reps** |
| D5 | 距(月,娘) | Q4 | 監視用(準普遍、PASS GATE対象外) |

### 3.2 軸位置問 A1-A2 (§2.2のtemplate、各fwd/rev両群)
| ID | 軸;中間語 | v1対応 | 位置づけ |
|---|---|---|---|
| A1 | 生↔死;夢 | Q13 | anchor再検証・PASS GATE対象(v1確定=5中点、v1でも極性反転なし=対照群として機能) |
| A2 | 愛↔無;棄 | Q12 | **主falsifier**(v1極性反転疑いの直接対象) |

### 3.3 序問 O1-O2 (首位・末位、両方を測定 — r1でO2追加)
| ID | 問 | v1対応 | 位置づけ |
|---|---|---|---|
| O1 | 序(愛)首位 (愛に最も近い語は何か、1語で答えよ) | Q7 | **contested-zone×10 reps**(v1: son-A固有=鳴5/5 vs 他=母/血の裂) |
| O2 | 序(愛)末位 (愛から最も遠い語は何か、1語で答えよ) | Q7 | **anchor再検証・PASS GATE対象**(v1確定=無が21/25、r1でanchor化) |

v1の「愛序末尾=無」(21/25で確定寄り)はr0でO1の設問範囲(首位のみ)外としてスコープ外化したが、r1で**取り消しO2としてanchor化する**(改訂履歴r1参照)。O1とO2は別問・別prompt・別lane(1lane=1問の法により合併不可)。

### 3.4 類推問 N1-N2
| ID | 問 | v1対応 | 位置づけ |
|---|---|---|---|
| N1 | 王:女王::月:? (1語で答えよ) | Q8 | **contested-zone×10 reps**(女性系 vs 天体対の二解釈系) |
| N2 | 母:娘::神:? (1語で答えよ) | Q10 | **contested-zone×10 reps**(女神/人/子系の裂) |

**合計11問** (D1-D5=5, A1-A2=2, O1-O2=2, N1-N2=2)。r0のtask指定「≤10問/probe」をr1で意図的に1問超えている(O2追加による。改訂履歴r1参照。上限を黙って無視せず、ここに明記して超える)。

### 3.5 反復数
- **contested-zone指定5項** (D2, D4, O1, N1, N2): 各basis内で **×10 reps** (=10独立lane/basis)。
- **anchor5項** (D1, D3, A1, A2, O2 — O2はr1で追加): 各basis内で **N≥5独立lane** (PASS GATE用途、反復数は絞る)。A2はfwd/rev両群で各N≥5(合計N≥10/basis)。
- **監視項** (D5): 各basis内でN≥5独立lane(PASS GATE対象外、参考記録のみ)。
- **basisあたり合計lane数** = (D2,D4,O1,N1,N2)5項×10 + (D1,D3,O2)3項×5 + (A1,A2)2項×2群×5 + (D5)1項×5 = 50+15+20+5 = 90 lane/basis × 10 basis = **900 lane (M0全量)**。r0の850から、O2追加分(5×10 basis=50)で900に増加。本数字はharnessの実行で検証する(手計算のみに頼らない、§9参照)。

## 4. Rotation Basis 設計 (トモグラフィ点)

**Basis** = 一意な (language, persona/framing値, head) の3-tuple。呼称: `B-{lang}-{pf}-{head}` (例: `B-EN-clinical-sonnet`)。

### 4.1 各因子の値集合
- **language** ∈ {EN, DE, JA, ZH} — 4値。訳語はmanifest(scripts/vocab.json)に固定記録し、事後の訳語変更を禁止する(lighthouse §7の教訓: 不確実性は訳語gloss選択に宿る、それを隠さない)。
- **persona/framing (pf)** ∈ {none+clinical, poetic-narrator+poetic, clinical-analyst+clinical, none+narrative} — 4値。personaとframingは概念的に重なるため独立4x3のfull factorialにせず、この4組に限定する(v1弾劾6教訓=セル未充填を避ける設計)。
  - `none+clinical`: system指定なし(素weights)、質問文体=臨床的(§2テンプレートそのまま)。
  - `poetic-narrator+poetic`: system="あなたは詩人的な語り手として答える"、質問文体を詩的言い換え(数値回答という制約は変えない)。
  - `clinical-analyst+clinical`: system="あなたは臨床的な分析者として答える"、質問文体=臨床的。
  - `none+narrative`: system指定なし、質問文体=短い物語的枠付け(例: 「ある賢者に問うたら」)。
- **head** ∈ {claude-sonnet, claude-opus, kimi, jareth} — M0設計上の想定4系。**r1記録: 本rev時点で稼働確認済みなのはsonnet系とcodex系のみ(ユーザー既知事実、pilotで自ら再確認予定)。opus/kimi/jarethの生死はpilot後のhead回転収集段階で実測する。実在しないheadの基底は空のまま残し(未収集と明記)、代替headで埋めない(§9)。** naru-*(GPT系)はv1同様auth死の可能性あり、生存確認後に追加basisとして§8に事後追記(post-hoc basis追加は数値汚染だが、生存確認による**追加**は事前に許可された拡張であり、既存basisの再定義ではないため許容する)。

**r1追記—語彙provenance**: vocab.jsonの各訳語に`_provenance`を付す。EN/DE/ZHは本PREREG執筆者(ghoul-sonnet)によるgloss翻訳で、辞書・ネイティブチェックを経ていない(不確実性はgloss選択に宿る、隠さない)。並行lane `~/.gaia/worktrees/sm-vocab` (naru-sonnet, `lane/vocab`) がvocab.json(ja/en/de/zh)を独立生成中で、本rev時点ではbase commit(`495f086`)のまま=未完了を確認済み。完了後の手順: (a) 両vocab.jsonを差分しdiffを全件記録、(b) 食い違い語は「どちらが正か」を判定せず両方をbasis表に並記して報告する。

### 4.2 Basis集合 (M0範囲、事前固定・後から挿入禁止)
| basis軸 | 固定する因子 | 動かす因子 | basis数 |
|---|---|---|---|
| 軸1: 言語回転 | persona/framing=none+clinical, head=claude-sonnet | language∈{EN,DE,JA,ZH} | 4 |
| 軸2: persona/framing回転 | language=EN, head=claude-sonnet | pf∈{poetic-narrator+poetic, clinical-analyst+clinical, none+narrative} (none+clinicalは軸1と共有、重複させない) | +3 |
| 軸3: head回転 | language=EN, persona/framing=none+clinical | head∈{claude-opus, kimi, jareth} | +3 |

**M0合計 = 10 basis** (4+3+3)。M2 (ROADMAP.md)で全factorial(4×4×4=64 basis上限)へ拡張予定だが、本PREREGはM0の10 basisのみを事前登録する。

### 4.3 結果keying
- 全結果TSVは `(question_id, basis_id, head, rep, group, raw_value, canonical_value, lane_id, timestamp)` でkeyする。
  - `group`: A-probe(軸位置問)のみ`fwd`/`rev`、D/O/N probeは`na`。
  - `canonical_value`: D/O/Nはraw_valueと同一。Aのrevはraw_valueを`10-raw_value`で正準化した値。
- basis_idは§4.2で固定した文字列を使用し、収集後の事後的な再区分・再命名を禁止する。
- 同一basis内の各repは独立lane(清文脈・新規session・他repの結果を見せない)であることを必須とする。

### 4.4 核としてのbasis (Pascal教義 doctrine-projection-kernel.md, r2記録義務)

教義原文: 「描画=縮約。pixel=場と観測核の内積。縮約核の選択が「見え方」を決める → basis rotation = 核回転」。本batteryの距離/軸位置回答も同型: concept vector(場) · basisの提示方式(観測核) → 出た数字(pixel)。中立な核は存在しない。本PREREGの**10 basis = 10核**であり、各核の定義(何を捓え、何を捨てるか)を以下に固定する(事後挿入禁と同じ法、§4.2と一体)。

**核の3種別 — 異種のものを同じ「回転」と呼んでいたことの明示**:

| 核種 | 対応するbasis因子 | 捓えている対象 | 捨てている対象 | 階層 |
|---|---|---|---|---|
| **語彙核** | language | 語の表層形(訳語) | 言語固有の連想・音韻・文字体系由来のニュアンス(不確実性はgloss選択に宿る、vocab.json._provenanceに既記) | 同一head重み内部の射影角度変化 |
| **文体核** | persona/framing | 応答の言語行為的枠(詩的/臨床的/物語的) | 同じ語彙・同じheadでも文体が変れば表出しない側面(prompt表層形の情報) | 同一head重み内部の射影角度変化(語彙核と同層) |
| **重み核** | head | 特定modelの学習された重み全体 | 他headの重み構造由来の表現(最も基底的) | 場を測る土台(weights)自体の切替 — 上、2核と階層が異なる |

**予想(先行登録、結果を見てからの合理化にしない)**: 語彙核×文体核の回転は同一headの重み内部の事荷であり互いの相関が高くなりやすい(=冗余な核)と予想される一方、head核の回転はより独立性が高いと予想される。M2の「射影独立性audit(陰根監査)」(ROADMAP.md)でこの予想を実測検証する。

**事後挿入禁(§4.2)の根拠**: 本教義によれば、結果を見てから核を選ぶ行為(post-hoc kernel selection)はpost-hoc anchor selectionと同罪。§4.2の10 basis固定・事後挿入禁はこの法の特例ではなく、同じ法の一般形である(新規事実の追加ではなく、既存設計の確認)。

**核一覧の固定**: §4.2の10 basisリストをそのまま「10核リスト」として扱う(別リスト作成不要)。basis.jsonの各エントリの`axis`フィールド(language/persona_framing/head)が上表の核種に1対1対応する。

## 5. PASS GATE (事前確定)

**r2記録義務(教義反映)**: 以下の各anchorの命名(D3「距(愛,無)遠」等)はPREREG内部の事前定義上の呼称であり、**実測後の報告文**では必ず「核B-xxの下で距離はN」形式を使い、PASS判定を「普遍」ではなく「検査した核群(本M0の10核)の下で不変」と記述する(§7報告規約も同様)。

| anchor | 合格条件 | 失敗の形 |
|---|---|---|
| D3 距(愛,無)遠 | 中央値が7-9の帯に入り、**≥2 basis**でCIが帯と重なる | ある基底で中央値<7かつCIが7-9帯と重ならない基底が2つ以上、または基底間でCIが分離 |
| D1 距(影,闇)≈2 | 中央値が1-3の帯に入り、**≥2 basis**でCIが帯と重なる | 中央値が3以上外れる基底が2つ以上、かつ基底間CI分離 |
| A1 夢=5中点(生↔死) | 正準化値の中央値が4-6の帯に入り、**≥2 basis**で再現、かつfwd/rev両群のCIが重なる(=極性効果がこの軸に及ばないことの確認) | 中央値が帯外の基底が2つ以上、またはfwd/revでCI分離(=夢問にも極性効果が及ぶという新発見) |
| O2 愛序末尾=無 (r1でanchor化、r0では対象外だった) | 全basis内でO2回答の**最頻語(mode)が「無」またはその明示的同義語(nothingness/Nichts/无/虚無)**を占め、かつ過半数(>50%)がこの語群に入り、これが**≥2 basis**で再現 | ある基底でmodeが「無」系以外(過半数割れ)になる基底が2つ以上、または基底間でmode語が食い違う(語の一致率をκ相当で報告、閾値は事前合意なく単純な「食い違うか否か」で判定) |

A2(軸愛↔無;棄、極性反転の主対象)は「合格/不合格」ではなく§2.2の二分法(器欠陥/実裂)で判定する。どちらが出ても検証成功であり、失敗ではない。

**全体PASS宣言の条件**: 上表4項(D3,D1,A1,O2)中≥3/4がPASSし、かつA2の二分法結果がCIから明確に判定できる(N不足で分散過大・CI幅が判定不能なほど広い場合は「判定不能」と記録し、PASS/FAILいずれも宣言しない)。**r0時点の閾値(3項中≥2/3)はr1でO2追加により4項中≥3/4に変更、変更理由=anchor追加のみでロジックは不変(3/3のうち3/4相当を維持する比率)**。

## 6. head-agreement統計 + family-balance規則

### 6.1 family-balance (弾劾5修復)
- family定義: {claude(sonnet,opus)}, {kimi}, {jareth}, {naru-*(生存確認時に追加)}。
- 普遍/方言/争域の判定は**family単位1票の多数決**とする。v1のような生lane票数(21/25等)は判定根拠に使わない。閾値: **basis内で全参加familyの≥3/4一致**を普遍の下限とする(4family未満で走る場合は「全family一致」を要求)。
- family内に複数head(claude-sonnet, claude-opus)がある場合、まずfamily内の中央値を取り、それをfamily代表値として家族間比較に使う。
- **r2記録義務(教義反映)**: family多数決はあくまで「判定用の圧縮統計」であり、**核間不一致は雑音ではなくデータ**。判定を報告する際は必ず全basis(=10核)の生のraw/canonical値を并記し、単一値へ畳んで(平均して)報告してはならない。

### 6.2 head-agreement統計
- 各basisにつき、family間の一致度をweighted kappa(順序尺度、距離問・軸位置問に適用)またはICC(2,1)で報告する。
- κ<0.4のbasisは「争域basis」として別集計し、母数(basis総数)から除外しないが、普遍判定の分子(一致basis数)には数えない。
- 全ての普遍/方言/争域主張に **(n, family一致率, κ, basis数)** を付す。付かない文は書かない(lighthouse-invariant PREREG §6の法を継承)。

## 7. 報告規約
- 1表=1run。run混ぜ禁。生出力は `battery-v2/runs/<runid>/raw/` (gitignore対象)、採点表 `battery-v2/runs/<runid>/coded.tsv` はcommitする。
- 数字を作るのは `battery-v2/scripts/` のscriptのみ。手集計禁。
- 30分毎commit、trailer `Lane: ghoul-sonnet` 必須。
- PREREG本文(§0-§9)は収集開始後の変更を禁止する。測定・集計方法の厳密化のみ改訂履歴に追記可(lighthouse r3/r4の法に同じ)。
- **r2記録義務(Pascal教義 doctrine-projection-kernel.md 反映, §4.4参照)**: (1) 報告文で「距離はN」のような无条件表現を禁止し、必ず「**核B-xxの下で距離はN**」(basis_id明記)と書く。(2) 「普遍」「確定」を無条件で使わない、**「検査した核群(本M0の10核)の下で不変」**の形のみ許可(v1由来の引用は引用と明示した上で保持可)。(3) 核間不一致は雑音ではなくデータ、family多数決(§6.1)は判定用の圧縮統計にすぎず、報告には**必ず全basis(=10核)の生のraw/canonical値を并記**する。単一値へ畳んで平均して報告してはならない。coded.tsvはbasis_id列でこれを構造的に保障する(§4.3)が、prose報告でも省かない。

## 8. 全falsifierリスト (一覧・事前確定・変更禁止)
1. D3(距離愛無遠7-9帯)が≥2 basisで再現しない → H1敗北(該当anchor)。
2. D1(距離影闇≈2、帯1-3)が≥2 basisで再現しない → H1敗北(該当anchor)。
3. A1(夢=5中点、帯4-6)が≥2 basisで再現しない、またはfwd/rev間でCI分離(極性効果が夢問に及ぶ) → H1敗北(該当anchor)、後者は新発見として記録。
4. A2(軸愛無棄の極性反転)、正準化後もCI分離が残る → 実裂確定・H0-artifact-scale敗北(H1側発見)。正準化後にCIが重なる → 器欠陥確定・H0-artifact-scale勝利(H1側は当該項目について保留)。
5. family-agreement κ<0.4のbasisがM0の10 basis中過半数(6以上) → basis設計自体が信号を持たない、H0-basis有利。
6. 独立lane化(弾劾1修復)後、contested-zone5項(D2,D4,O1,N1,N2)の分散が減少せずv1と同型の裂が再現 → H0-artifact-repeat敗北(裂は本物、独立化でも消えない)。逆に単一値へ収束 → H0-artifact-repeat勝利(裂は反復非独立性の産物だった)。
7. family単位1票制(§6.1)適用後、v1の普遍判定(D1,D3,A1)のいずれかが「争域」に降格する → H0-family敗北を免れない(Claude族過重が判定を作っていたことの直接証拠)。
8. **(r1追加、既存1-7は一字も変えない)** O2(愛序末尾=無)が≥2 basisで再現しない(mode語が「無」系以外になる基底が2つ以上、またはbasis間でmode語が食い違う) → H1はこのanchorを失う。

判定法: H1は上記1-8の**いずれか一つでも**説明できずに残った項目についてのみ「basis不変の普遍層」と主張できる。1項目でもH0側で説明されればその項目は保留する。全項目がH0側で説明されればH1は本PREREGの範囲で支持されない。

## 9. Pilot slice プロトコル (r1追加、収集前GOと同時に定める)

目的: 900 lane全量を無検証で投入せず、1basisの小量スケーリングでthroughput(lane/分)・失敗率(接続シベーモ・リフューザル拒否等)・パース不能率(numeric_parse失敗・word_parse失敗)を実測し、全量計画(所要時間・リトリ方針)を立てる基礎データとする。

### 9.1 対象
- basis: **B-EN-none_clinical-sonnet** のみ(head回転・言語回転は位ではない、pilotはsonnet系のみでthroughputを見る)。
- lane: basis内の全question×groupを**各1repのみ** — D1,D2,D3,D4,D5(5) + A1-fwd,A1-rev,A2-fwd,A2-rev(4) + O1,O2(2) + N1,N2(2) = **13 lane**。N≥10やN≥5の本回収集はこのpilotの後に行う(本パイロットはthroughput測定目的のみ、PASS GATEには使うない)。

### 9.2 実行方法
- 各lane = 1回のsummon (agent=`naru-sonnet`、head=claude-sonnetの独立クヨーズフレーズワーカー、本ghoul-sonnet自体とは別コンテキスト)。task本文 = harnessが生成したprompt_textそのまま+最小の形式強制文(「一回限りの孤立した質問。指示された形式以外の説明・注釈・ァブタガフなしに、この回答のみ返すこと」)。この強制文以外のprompt内容の改変禁止(プロンププールcontaminationを防ぐ)。
- lane_idはtaskテキストに含めない(バイアス防止)。返答とlane_idの対応は発注順序で管理する。

### 9.3 記録項目 (`results/throughput-pilot.md`)
- lane数・開始/終了timestamp・throughput(lane/分)。
- 失敗率: 接続失敗・タイムアウト・拒否(回答拒否等)を件数で報告。
- パース不能率: `code_outputs.py`の`unparseable_numeric`/`unparseable_word`ノート割合を報告。
- 全て実測値のみを記録し、推定・目標値は書かない(未検証=未検証と明記)。

## v1で回復不能と判定する点 (スコープ外・再測しない)
- **序(棄)Q15**: v1「争域全面」、v2のcontested-zone5項(task指定)に含まれない。再測しない。回復可能性自体は否定しないが本PREREGのスコープ外と明記する。
- **jareth"空間膨張型"傾向・Q10 son-A固有=女神**: v1弾劾2(単一lane→族結論禁)によりUNVERIFIED。v2はN≥5独立lane設計で自動的に再検証されるが、**v1個別の値そのものは再現不能**——v1のraw lane識別情報(どのsonnet呼出が「son-A」か)がbattery-v1.mdに保存されておらず、同一laneへの再訪不可能。v2は新規独立測定として扱い、v1個別値との直接一致は主張しない。
- **(r1で削除)愛序末尾=無**: r0はここに「本PREREGのO1は首位のみ測定するため再検証範囲外」と書いたが、r1でO2としてanchor化したため本節から削除する(§3.3・§5・§8-falsifier8参照)。この行の削除自体を改訂履歴r1に記録済み、削除した文言も上の取り消し線的な記述としてここに残す: 元文言「愛序末尾=無: v1確定寄り(21/25)だが本PREREGのO1は首位のみ測定するため再検証範囲外(§3.3, §5)。」
