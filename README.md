# Dynamic_Metadata_for_Nuke

## Release note

25/11/12  v1.0.0
SilverStack Dynamic Metadata CSVに対応
25/11/12 v1.2.0
SONY Raw Viewer Metadata CSVに対応
25/11/15 v1.2.3
read nodeからin, outを確認するように変更
Read nodeを任意に選択するか、node graph上で選択してるものにするか選べるように変更
CSVを任意フォルダ(親フォルダ)からEXRのReelNameを読みこんで自動で検索するように変更
nodegraph上に存在するRead node(pull素材)のin,outに合わせてkeyframeを打つようにできるように変更(※Start TC)
(以前のCSVのTimecodeにkey打つオプションも残している ※Source TC)
CSVが複数ヒットしたときは、任意のものを選択する機能追加
CSVがSilverStackかSONY Raw Viewerか自動判定追加
25/11/15 v1.2.4
構成変更、デバック

## [動作検証]
MacOS Apple Silicon Nuke v16
Windowsでまだ未確認

## How to use
window(Dynamic Metadata setting)が出現します
Current Selected Read Node on Node Graph: 
Node Graph上で選択しているReadノードを使用するか(True)、
下記の”Select Read Node”で選択したRead ノードを使用するか(False)
Select Read Node : 
NodeGraph上に存在するread nodeをこちらから選んで使用する場合選択する
Auto CSV Searching :
下記の”Searching CSV folder path”で選択したfolderからRead nodeのReel Nameと一致する
CSVを自動探すか(True)
手動でcsvを選択する
Serching CSV folder path : 
“Auto CSV Searching”で使用するfolder path または、csvのpath
Auto CSV Type Detection : 
Silver StackかSONY Raw Viewerかなどのcsvの種類を自動判定させるか否か
CSV type : 
“Auto CSV Type Detection”がoffの時に、マニュアルで選択できる
Keyframe mode : 
Start Frameならば、Read NodeのStart FrameからEnd Frameでkey frameを打つ
Source TCならば、CSVに記載されているSource TCにkey frameを打つ
Type of Camera Rotation Order : 
作成されるCamera NodeのRotation Orderを選べる


DynamicMetadataCam_**というCameraが生成されます。
現在は
・Rotate(tilt, roll)(degree)
・Focal Length(mm)
・Focal Distance(m)
・Fstop(F-Number)
が対応しています。


