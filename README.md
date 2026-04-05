# blender2pmxemn

Blender 5.1 での動作改善を進めている `blender2pmxem` の fork です。

## 概要

PMX 形式ファイルのインポート / エクスポートを扱う Blender アドオンです。

元になったアドオンは KAGAYAS 氏の Blender2Pmxe で、このリポジトリでは
[`matunnkazumi/blender2pmxem`](https://github.com/matunnkazumi/blender2pmxem)
をベースに Blender 5.1 対応を進めています。

## ライセンス

改変履歴のライセンスに従います。
新規追加したファイルは、特に注記がない限り [CC0](https://creativecommons.org/publicdomain/zero/1.0/legalcode) とします。

## Blender 5.1 対応メモ

現時点では、まず次を優先して確認・対応しています。

- アドオン登録
- PMX のインポート / エクスポート
- XML 作成と連携
- Template Append と主要なボーンツール

最低限の確認には、次の検証スクリプトを使います。

- addon を有効化できる
- PMX をインポートできる
- XML を作成できる
- PMX をエクスポートできる
- 「アーマチュアの雛形をアペンド」と主要なボーンツールを 1 ケース確認できる

検証スクリプトと実機確認の流れは
[verification/blender51/README.md](verification/blender51/README.md) を参照してください。

## Branch Strategy

このリポジトリは [`matunnkazumi/blender2pmxem`](https://github.com/matunnkazumi/blender2pmxem)
の fork です。fork 側の同期元と本リポジトリ独自の作業ブランチを分けて運用します。

- `upstream-master`: fork 元 `master` の追従用
- `upstream-develop`: fork 元 `develop` の追従用
- `main`: 本リポジトリの安定ブランチ
- `develop`: 本リポジトリの統合ブランチ
- `master`: fork 作成時に残る互換用ブランチ。通常運用では使いません

詳しくは [docs/branch-strategy.md](docs/branch-strategy.md) を参照してください。

## Development Policy

当面の改善方針や、main ブランチへ入れるかどうかの判断基準は
[docs/development-policy.md](docs/development-policy.md) にまとめています。
