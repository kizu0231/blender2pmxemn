# ブランチ運用方針

## 方針

- fork 元の確認用に `upstream-master` / `upstream-develop` を置きます。
- 本リポジトリの作業は `main` / `develop` で進めます。
- 通常の作業は `develop` から feature ブランチを切って進めます。

## 役割

- `upstream-master`
  fork 元 `master` の追跡用です。独自コミットは入れません。
- `upstream-develop`
  fork 元 `develop` の追跡用です。独自コミットは入れません。
- `main`
  本リポジトリの安定ブランチです。
- `develop`
  本リポジトリの開発ブランチです。

## 流れ

- 開発は `develop` から feature ブランチを切って進めます。
- feature ブランチは確認後に `develop` へマージします。
- 安定した内容を `develop` から `main` へ反映します。
- upstream を取り込むときは、まず追跡用ブランチを更新して差分を確認します。
