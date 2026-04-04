# ブランチ運用方針

## 基本方針

- fork 元の状態を確認しやすくするため、fork元の`master`および`develop`追跡専用ブランチを用意します。
- 本リポジトリ独自の対応は、独自の `main` / `develop` で進めます。
- 機能追加や Blender 対応、保守改善などの作業は、原則として `develop` から派生した feature ブランチで行います。

## 各ブランチの役割

- `upstream-master`
  fork 元 `master` の追跡用ブランチです。fork 元の `master` の状態確認に使い、独自コミットは入れません。

- `upstream-develop`
  fork 元 `develop` の追跡用ブランチです。fork 元の開発状況確認に使い、独自コミットは入れません。

- `main`
  本リポジトリの安定ブランチです。一定の動作確認を行った内容を反映します。

- `develop`
  本リポジトリの開発ブランチです。日常的な改修はここに集約します。

## 開発の進め方

- 通常の開発は `develop` から feature ブランチを切って進めます。
- feature ブランチで作業した内容は、確認後に `develop` へマージします。
- ある程度まとまった段階で `develop` から `main` へ反映します。

## upstream の取り込み

- fork 元の変更確認には `upstream-master` / `upstream-develop` を使います。
- upstream の更新を取り込む際は、まず追跡用ブランチを更新し、その差分を確認したうえで本リポジトリ側の `main` / `develop` に反映します。

## 補足

この運用はfork 元への追従と本リポジトリ独自の改修を両立しやすくすることを目的としています。