# 共通実行規則

このファイルは、`docs/localization/prompts/phase-*.md`の全Phaseに適用する。
各Phaseでは、このファイルを先に読み、その後に対象Phaseファイルを読むこと。

## 固定情報

```text
CHAIN_ID=AI-BERKSHIRE-JP-L10N-20260628-040F4BA
UPSTREAM_REPOSITORY=https://github.com/xbtlin/ai-berkshire
REPOSITORY=https://github.com/kiti1924/ai-berkshire-JP
LOCAL_REPOSITORY=D:\Documents\repos\ai-berkshire-JP
DEFAULT_BRANCH=main
INTEGRATION_BRANCH=integration/japanese-localization
INITIAL_BASE_SHA=040f4baf989b37bcb6fa757ade6c8097f7c761f2
```

## 作業開始時の確認

OMENで`D:\Documents\repos\ai-berkshire-JP`を開き、少なくとも次を確認する。

```powershell
git status --short
git remote -v
git fetch origin --prune
git fetch upstream --prune
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git rev-parse upstream/main
git worktree list
```

`upstream`が存在しない場合に限り、次を追加する。

```powershell
git remote add upstream https://github.com/xbtlin/ai-berkshire.git
git fetch upstream --prune
```

作業前に次を読む。

- `README.md`
- `README_EN.md`
- `AGENTS.md`
- `CLAUDE.md`
- 対象ディレクトリ内の追加指示

## Git運用

1. 指定された`REQUIRED_BASE_SHA`が実在することを確認する。
2. `INTEGRATION_BRANCH`のHEADが`REQUIRED_BASE_SHA`と一致することを確認する。
3. 一致しない場合、reset、rebase、merge、cherry-pickを勝手に行わず停止する。
4. `REQUIRED_BASE_SHA`からPhase専用branchと専用worktreeを作成する。
5. 同名branchまたはworktreeが別作業に使われている場合、削除、reset、強制再利用をしない。衝突しない代替名を使用し、最終報告に記録する。
6. 未コミット変更を破棄、stash、commitしない。
7. `main`を直接変更しない。
8. 各Phaseは原則として1コミットにまとめる。
9. コミットメッセージはPhaseファイルで指定された日本語を使用する。
10. focused testと差分レビューが成功した後、`INTEGRATION_BRANCH`へ`git merge --ff-only <WORK_BRANCH>`で統合する。
11. `ff-only`できない場合、merge commitやrebaseを作らず停止する。
12. push、Pull Request、`main`へのmergeは行わない。

## 編集規則

- 依頼範囲外のファイルを変更しない。
- 関係のない整形、改名、構造変更をしない。
- `skills/*.md`が存在する場合、それを正本とする。
- `codex-skills/*/SKILL.md`と`codex-prompts/*.md`は、正本が存在する限り自動生成物として扱う。
- 自動生成物だけを直接修正しない。
- Codex専用Skillは、同名の`skills/*.md`がないことを確認して個別に扱う。
- 認証情報、Cookie、Token、APIキー、ブラウザプロファイル、機械固有設定を保存しない。
- 外部金融API、証券口座、実注文経路へ接続しない。
- 既存レポートの数値、通貨、日付、出典を根拠なく変更しない。

## 日本語化の共通品質

- ユーザー向け出力は原則として日本語にする。
- 文体は「だ・である調」を基本とする。
- 結論を先に示す。
- 中国語や英語の語順をそのまま持ち込まない。
- 事実、企業側の説明、市場予想、計算による推定、分析上の仮定、評価を区別する。
- 通貨、単位、基準日、会計期間、会計基準を明記する。
- 中国語資料の検索能力と旧中国語レポートの解析互換性は維持する。
- ファイル名、関数名、コマンド、API名、JSONキー、外部仕様値は必要に応じて原文を維持する。
- `亿元`を「億円」と誤訳しない。人民元なら「億元（CNY）」等、通貨を明示する。
- `万亿`は文脈に応じて「兆」へ変換し、通貨を明示する。

## 検証の共通最低条件

Phase固有の検証に加え、最後に次を実行する。

```bash
git diff --check
git status --short
git diff --stat
git diff
```

実行していないテストを成功と報告しない。失敗がある場合は、コマンド、エラー、原因、未解決部分を記録する。

## Oracleへの次Phase送信

Phase完了後、利用可能な正式なOracle連携を使用し、次Phaseを新規チャットとして送信する。
既存Oracle会話をfollow-upしない。

送信するプロンプトは長文を再掲せず、次の形式にする。

```text
@OMEN

AI Berkshire日本語版の<次Phase名>を実行してください。
次の2ファイルを完全な実行指示として読み、記載順に従って実行してください。

- docs/localization/prompts/common.md
- docs/localization/prompts/<次Phaseファイル名>

CHAIN_ID=AI-BERKSHIRE-JP-L10N-20260628-040F4BA
REQUIRED_BASE_SHA=<統合後の実SHA>
PREVIOUS_PHASE=<完了したPhase>
PREVIOUS_PHASE_RESULT=<完了状態、commit SHA、integration HEAD、重要な未解決事項の要約>

新規チャットとして開始し、別の会話をfollow-upしないでください。
```

Phase 7とPhase 8では、さらに次を含める。

```text
BATCH_ID=<実際の次バッチ番号>
```

### 送信条件

- 統合が成功した場合だけ次Phaseを送信する。
- 実SHAを使用し、プレースホルダーを残さない。
- ブラウザ自動操作、認証回避、非公式な送信経路を使用しない。
- Oracle連携が利用できない、または送信に失敗した場合は、送信済みと報告しない。
- 失敗時は`NEXT_PHASE_SEND_STATUS=error`とし、送信予定だったプロンプト全文を最終報告へ含める。

## 完了報告の共通形式

```text
CHAIN_ID=
PHASE=
BATCH_ID=
STATUS=completed|partially_completed|blocked
BASE_SHA=
WORK_BRANCH=
WORKTREE=
COMMIT_SHA=
INTEGRATION_HEAD=
CHANGED_FILES=
TEST_COMMANDS=
TEST_RESULTS=
REMAINING_ISSUES=
WORKING_TREE_STATUS=
PUSH_STATUS=not_run
PULL_REQUEST_STATUS=not_run
NEXT_PHASE=
NEXT_PHASE_SEND_STATUS=sent|error|not_applicable
```
