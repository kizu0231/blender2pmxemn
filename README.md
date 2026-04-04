# blender2pmxemn

Blender 5.1 系での動作を目指して調整している `blender2pmxem` の fork です。

## 概要

PMX 形式ファイルのインポート・エクスポートを行う Blender アドオンです。

KAGAYAS 氏の改変 Blender2Pmxe をもとに、Blender 2.80 向けへ移植された
[`matunnkazumi/blender2pmxem`](https://github.com/matunnkazumi/blender2pmxem) を、さらに Blender 5.1 で動作させることを目的に調整しています。

## ライセンス

改変前のライセンスに従います。

新規追加したファイルは、特に記載がない限り [CC0](https://creativecommons.org/publicdomain/zero/1.0/legalcode) とします。

## Blender 5.1 対応メモ

現時点では、まず以下を優先して確認・対応しています。

- アドオン登録
- PMX のインポート / エクスポート
- XML 作成と連携
- テンプレート追加と主要ツール

以下の旧機能は Blender 5.1 の API 変更が大きいため、初期対応の対象外としています。

- Blender Internal 前提の Solidify Edge 補助機能
- `texface` / `texture_slots` 前提の旧補助機能

Blender 5.1 上では、以下の順で確認する想定です。

- アドオンを有効化できる
- PMX をインポートできる
- XML を作成できる
- PMX をエクスポートできる
- Template Append と主要ツールが最低 1 ケース動く

## Branch Strategy

このリポジトリは [`matunnkazumi/blender2pmxem`](https://github.com/matunnkazumi/blender2pmxem) の fork です。
fork 元の実装と差分管理をしやすくするため、追跡用ブランチと本リポジトリ独自の開発ブランチを分けて運用します。

- `upstream-master`: fork 元 `master` の追跡用
- `upstream-develop`: fork 元 `develop` の追跡用
- `main`: 本リポジトリの安定ブランチ
- `develop`: 本リポジトリの開発ブランチ

詳しくは [docs/branch-strategy.md](docs/branch-strategy.md) を参照してください。