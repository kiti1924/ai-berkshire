# Global Market Adaptation Installation Contract Specification

- 文書ID: `ABG-INSTALLATION-CONTRACT-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、Claude Code および Codex 環境における各種Skillおよび参照資料の導入スクリプト（Shell / PowerShell）、動作環境変数 `AI_BERKSHIRE_HOME`、ならびに `install-manifest.json` の仕様を定義する。

## 2. インストールエントリーポイント

元リポジトリの導入操作との完全互換性を維持する。

- Shell (Linux / macOS):
  - `scripts/install-claude-commands.sh`
  - `scripts/install-codex-skills.sh`
- PowerShell (Windows):
  - `scripts/install-claude-commands.ps1`
  - `scripts/install-codex-skills.ps1`

## 3. 動作環境変数 `AI_BERKSHIRE_HOME`

未設定時のOS別既定パス:
- Linux: `${XDG_DATA_HOME:-$HOME/.local/share}/ai-berkshire`
- macOS: `$HOME/Library/Application Support/ai-berkshire`
- Windows: `%LOCALAPPDATA%\ai-berkshire`

## 4. 契約要件

1. **冪等性**: スクリプトを連続実行しても重複登録やファイル破壊を発生させない。
2. **クローン先非依存**: インストール後の実行において、リポジトリの絶対パス（`~/ai-berkshire/...` 等）に依存してはならない。
3. **無鍵導入**: インストール処理中に `EDINET_API_KEY` や他秘密情報の入力を要求・保存してはならない。
4. **他プロジェクト非破壊**: 既存のユーザー独自 commands / skills を削除・上書きしてはならない。
