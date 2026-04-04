# blender2pmxem

Blender2PmxeをBlende5.10系に対応させるよ

## 概要

PMX形式のファイルのインポート・エクスポートを行うBlenderアドオンです。

KAGAYAS氏の改変Blender2Pmxe([配布ミラー](https://bowlroll.net/file/145391))を、Blenderの2.80向けに改変したものです。

## 使いかたなど

https://blender2pmxem.netlify.app/

## ライセンス
改変元のライセンスに従います。

それ以外の完全に新規に作成したファイルは [CC0](https://creativecommons.org/publicdomain/zero/1.0/legalcode) です。

## 更新履歴
[CHANGELOG](CHANGELOG.md)

## Blender 5.1 対応メモ

初回対応では、以下を優先しています。

* アドオン登録
* PMX のインポート / エクスポート
* XML 作成と連携
* テンプレート追加と主要な骨ツール

以下の旧機能は Blender 5.1 の API 変更が大きいため、今回は本線対応の対象外です。

* Blender Internal 前提の Solidify Edge 補助機能
* texface / texture_slots 前提の旧補助機能

動作確認は Blender 5.1 上で次を順に行ってください。

* アドオンを有効化できる
* PMX をインポートできる
* XML を作成できる
* そのまま PMX をエクスポートできる
* Template Append と主要骨ツールが最低 1 ケース動く

## 進捗
とりあえず動いているっぽい。

## Blender2Pmxeからの移行について

Blender 2.79以前 + Blender2Pmxe の.blendファイルとXMLファイルをそのままでは正常にエクスポートできません。仕様の変更点を元にモデルの修正を行ってください。

XMLファイルはインポートもしくは「XMLファイル作成」機能で作り直すことを推奨します。

## Blender2Pmxe からの仕様の変更点

* インポート・エクスポート
  * PMX形式の材質の設定は、BlenderのマテリアルのプリンシプルBSDFノードと対応させています
    * 拡散色 → ベースカラー
    * テクスチャファイル → ベースカラーの画像テクスチャノードのファイル
  * 材質色、スフィアマップ設定は、モデル情報のXMLに保存・取得するようにしました
  * 状態検証を行い、処理できない場合にエラーになるようにしました
* ツールのUI
  * ツールシェルフからサイドバーに移動しました
  * 以下を削除しました
    * 輪郭線機能
    * Mat to tex
    * 「陰影なし」チェックボックス
    * 「裏面を非表示」チェックボックス
* XML
  * ボーンの並び順をXMLの順番でエクスポートするようにしました
  * constraints要素のbody_Aとbody_Bを剛体名に変更しました
  * 材質モーフ・ボーンモーフ・グループモーフをXMLに保存するようにしました
