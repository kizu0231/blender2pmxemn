# Blender 5.1 検証スクリプト

Blender 5.1 での動作確認や headless 検証に使うスクリプト置き場です。

## 目的

- Blender 5.1 対応で確認したい項目を、再実行しやすい形で残す
- 実機確認と headless 確認を切り分けやすくする
- 調査用スクリプトを必要な間だけ保持し、再利用できるようにする

## 配置方針

- Git 管理する検証スクリプトは `verification/blender51/` 配下に置きます。
- ローカル作業用の addon wrapper は `{forLocalディレクトリの配置場所}/blender-user-scripts/addons/blender2pmxemn/` を使います。
- 作業ディレクトリや生成物は `{forLocalディレクトリの配置場所}/tmp_*` に残します。

## 実行前の前提

- `BLENDER_USER_SCRIPTS` には `{forLocalディレクトリの配置場所}/blender-user-scripts` を設定します。
- `blender.exe` が `PATH` にない場合は、手元の Blender 5.1 実行ファイルを絶対パスで指定します。
- 実行時の絶対パスは環境ごとに異なるので、README には固定値を書かず、手元の配置に合わせて読み替えます。

## 実行例

`run_verification.cmd` を使う例:

```cmd
run_verification.cmd "{Blender 5.1 の blender.exe}" verify_minimum_workflow.py
```

このラッパーが、`BLENDER_USER_SCRIPTS` を `{forLocalディレクトリの配置場所}/blender-user-scripts` に設定してから Blender を起動します。

## スクリプト一覧

- `verify_minimum_workflow.py`
  最低限の総合確認用です。addon 有効化、PMX import/export、XML 作成、Template Append、主要なボーンツール 1 ケースを見ます。
- `verify_xml_and_weight_tools.py`
  XML 連携と WeightType の 1 ケースを確認します。
- `verify_shape_key_and_stance_tools.py`
  import 直後の shape key 初期値と `Aポーズへ` / `Tポーズへ` の確認をまとめて行います。
- `run_verification.cmd`
  検証スクリプト実行用の cmd ラッパーです。旧スクリプト名を渡した場合も新しい名前へ読み替えます。
- `check_pose_selection_headless.py`
  headless 実行時の pose bone 選択状態だけを切り出して確認する調査用です。
- `check_pose_selection_with_view3d.py`
  VIEW_3D 文脈や operator ベースの選択経路で `selected_pose_bones` がどう変わるかを調べる調査用です。
- `minimum_workflow_manual_checklist.md`
  実機確認で使うチェックリストです。headless 検証後の UI 確認に使います。

## 運用方針

- 通常の headless 確認は `verify_minimum_workflow.py` を入口にします。
- 実機確認するときは `minimum_workflow_manual_checklist.md` を使って観点を固定します。
- 調査用スクリプトは、再利用価値がある間は残します。
- 使い捨ての切り分けコードは増やしすぎず、再利用価値が低ければ issue コメントへ要点を残して整理します。
- headless 検証では operator の戻り値 `FINISHED` だけで合格にしません。可能な限り、対象データの実際の変化を確認します。
- 例: ポーズ変更なら `rotation_quaternion` や `matrix_basis`、shape key なら `value`、WeightType なら作成されたカラー属性の有無や件数を見ます。
- 実機確認 issue に書いた期待結果と、headless 検証の期待値はなるべく同じ観点でそろえます。

## 既知の制約

- `BLENDER_USER_SCRIPTS` の指定がないと、ローカル作業中の addon ではなく別のインストール済み addon を読んでしまうことがあります。
- Blender の実行ファイルの場所は README から自動では分かりません。必要なら環境ごとに実行例を補ってください。
- `Aポーズへ` / `Tポーズへ` は headless 実行時に `bpy.ops.pose.copy()` で `Cannot change old file (file saved with @)` となる場合があります。
- 上の制約に当たった場合は、headless の結果だけで不具合と断定せず、Blender の UI 上でも再確認してください。
