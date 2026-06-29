# Phase 8：中国語パスのバッチ移行

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 8
BATCH_ID=<Oracleから渡された実バッチ番号>
WORK_BRANCH=chore/ja-paths-batch-<BATCH_ID>
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
MAX_RENAMES=80
```

## 目的

中国語を含むファイル名とディレクトリ名を、安定した機械可読パスへ段階的に移行する。本文の日本語タイトルと機械用パスを分離し、機械用パスは原則としてASCIIの安定したslugを使用する。

例：

```text
reports/腾讯/ -> reports/tencent/
reports/美团/ -> reports/meituan/
reports/茅台/ -> reports/kweichow-moutai/
```

## Path map

`docs/localization/path-map.csv`を使用する。BATCH 001で存在しない場合は全対象の候補mapを作成する。

列は次のとおりとする。

- `old_path`
- `new_path`
- `entity_type`
- `mapping_reason`
- `status`
- `batch_id`
- `reference_update_status`
- `collision_status`
- `notes`

## 命名方針

優先順位：

1. 企業の公式英語名または一般的ticker slug
2. 国際的に定着したローマ字表記
3. 誤解の少ないASCII kebab-case
4. 日本語タイトルは本文のH1へ保持

次を避ける。

- 意味不明な自動拼音
- 同名衝突
- Windowsの予約名
- 大文字小文字だけで区別する名前
- 極端に長いパス
- 日付やtickerの消失

## 実装

- `git mv`を使用する。
- 1バッチ最大`MAX_RENAMES`とする。
- ディレクトリ単位の移行を優先する。
- README、README_EN、Skill、Codex生成物、docs、reports内相互リンク、ツール例、監査コマンド例の参照を更新する。
- `report-manifest.json`のpathも更新する。
- 本文の意味は変更せず、リンク修正だけを行う。

## 禁止事項

- 本文を再翻訳しない。
- 投資判断を変更しない。
- パス衝突を上書きで解決しない。
- リンク切れを残したまま完了扱いしない。
- OS依存の絶対パスへ変更しない。
- 外部URLを書き換えない。

## 検証

- 旧パス参照が残っていない。
- 新パスが存在する。
- 大文字小文字衝突がない。
- MarkdownリンクとREADMEリンクが解決する。
- Skill内の出力先例が正しい。
- manifestとpath mapが更新されている。
- `common.md`のGit差分確認を実行する。

## Commit

```text
中国語パスを整理 batch <BATCH_ID>
```

1コミット作成後、integration branchへff-only統合する。

## 次Phaseの分岐

未処理パスが残る場合は、`BATCH_ID`を1増やし、統合後SHAを使って同じ`08-paths.md`をOracleへ送信する。

全パス移行が完了した場合は、統合後SHAを使って`09-final.md`をOracleへ送信する。

## 追加報告項目

- `RENAMED_PATHS`
- `UPDATED_REFERENCES`
- `COLLISIONS`
- `BROKEN_LINKS`
- `PATH_MAP_REMAINING`
