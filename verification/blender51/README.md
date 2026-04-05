# Blender 5.1 検証

Blender 5.1 向けの headless 検証スクリプトと実機確認メモです。

## 使い方

- 通常の入口は `verify_minimum_workflow.py` です。
- 実行には `run_verification.cmd` を使います。
- 実機確認するときは `minimum_workflow_manual_checklist.md` を使います。

```cmd
run_verification.cmd "{Blender 5.1 の blender.exe}" verify_minimum_workflow.py
```

`run_verification.cmd` は `BLENDER_USER_SCRIPTS` を `forLocal/blender-user-scripts` に向けてから Blender を起動します。

## スクリプト一覧

- `verify_minimum_workflow.py`
  最低限の総合確認です。addon 有効化、PMX import/export、XML 作成、Template Append、主要なボーンツール 1 ケースを見ます。
- `verify_xml_and_weight_tools.py`
  XML 連携と WeightType を確認します。
- `verify_shape_key_and_stance_tools.py`
  shape key 初期値と `Aポーズへ` / `Tポーズへ` を確認します。
- `check_pose_selection_headless.py`
  headless での pose bone 選択状態を調べる調査用です。
- `check_pose_selection_with_view3d.py`
  VIEW_3D 文脈での選択状態を調べる調査用です。
- `minimum_workflow_manual_checklist.md`
  実機確認用のチェックリストです。

## 前提

- Blender 5.1 の `blender.exe` を指定して実行します。
- 作業ディレクトリや生成物は `forLocal/tmp_*` に作られます。
- `BLENDER_USER_SCRIPTS` を指定しないと、作業中の addon ではなく別のインストール済み addon を読むことがあります。

## 補足

- headless 検証では `FINISHED` だけでなく、対象データの実際の変化も確認します。
- headless と UI で結果が食い違う場合は、Blender の UI 上でも再確認してください。
