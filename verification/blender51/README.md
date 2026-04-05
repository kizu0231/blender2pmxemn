# Blender 5.1 Verification

Blender 5.1 向けの実機確認や headless 確認に使う補助スクリプトを置くディレクトリです。

## Files

- `check_issue13_coverage.py`
  `#13` の確認項目を headless Blender で一通り確認するためのスクリプトです。
  現在のアドオンが Blender に読み込まれる前提で、addon 有効化、PMX import/export、XML 作成、Template Append、ボーンツール確認を実行します。

## Notes

- スクリプトの作業用ファイルは `forLocal/tmp_issue13_*` に作成されます。
- 中間生成物や確認結果をあとから見直せるよう、作業ディレクトリはローカルに残す前提です。
- Blender に現在の作業ツリーを addon として読ませる方法は、環境ごとに変わる可能性があります。
- 実行環境ごとの値は固定せず、スクリプトの配置場所など実行時に取得できる情報から組み立てる前提にしてください。
- コンソール出力を確認するときは、期待する出力も issue やチェックリストに明記してください。
