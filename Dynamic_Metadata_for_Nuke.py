#Dynamic Metadata from SilverStack csv for Nuke 
# v1.2.3
# Kazuki Omata


import csv
import math
import nuke
# import datetime
import re
import pathlib #for file path
import glob #for file search




# ----------
# global variables

check = []
returnP1 = None
bFinish = False
csv_path = ""
csv_data = None

# project fps
framerate = nuke.root().fps()
print(framerate)
# ----function-----

# https://qiita.com/aizwellenstan/items/048fefbcd6052b54dd83
def _seconds(value):
    if isinstance(value, str):  # value seems to be a timestamp
        _zip_ft = zip((3600, 60, 1, 1/framerate), value.split(':'))
        return sum(f * float(t) for f,t in _zip_ft)
    elif isinstance(value, (int, float)):  # frames
        return value / framerate
    else:
        return 0

def _timecode(seconds):
    return '{h:02}:{m:02}:{s:02}:{f:02}'.format(h=int(seconds/3600),m=int(seconds/60%60),s=int(seconds%60),f=round((seconds-int(seconds))*framerate))

def _frames(seconds):
    return seconds * framerate

def timecode_to_frames(timecode, start=None):
    return _frames(_seconds(timecode) - _seconds(start))

def frames_to_timecode(frames, start=None):
    return _timecode(_seconds(frames) + _seconds(start))




# ----------panel setting

read_nodes = nuke.allNodes("Read")
read_nodes.sort()
read_node_names = ""
for n in read_nodes:
    read_node_names += n.name() + " "
print(read_node_names)


p1 = nuke.Panel('Dynamic Metadata setting')
p1.addEnumerationPulldown('Select Read Node', read_node_names)
p1.addBooleanCheckBox("Selected Read Node on Node Graph", True)
# p1.addFilenameSearch('CSV file path', '~/Desktop/')
p1.addFilenameSearch('Searching CSV folder path', '~/Desktop/')
p1.addBooleanCheckBox('Auto CSV Searching', True)
p1.addEnumerationPulldown('CSV type', 'SONY-RawViewer SilverStack')
p1.addBooleanCheckBox('Auto CSV Type Detection', True)
# p1.addSingleLineInput("Start frame", 1001)
p1.addEnumerationPulldown("Keyframe", "StartFrame SourceTimecode" )
p1.addEnumerationPulldown("Type of Camera Rotation order", 'XYZ XZY ZYX ZXY YXZ YZX')


# show Panel
returnP1 = p1.show()

if returnP1:
    pass
else:
    # if user cancel, finish the script
    bFinish = True

# ---------- itnitializing
# get values from panel

# csv_path = p1.value("CSV file path")
csv_path = ""
csv_folder_path = p1.value("Searching CSV folder path")
bCSV_Auto_Searching = p1.value("Auto CSV Searching")

csv_type = p1.value("CSV type")
bCSV_Auto_Detection = p1.value("Auto CSV Type Detection")

rotation_order = p1.value("Type of Camera Rotation order")

# nodegraph上で選択されているread nodeを利用するか？
bSelected_on_node_graph = p1.value("Selected Read Node on Node Graph")
selected_read_node_name = p1.value("Select Read Node")
# print(selected_read_node_name)
# print(type(selected_read_node_name))

EXR_node = None
if(bSelected_on_node_graph):
    EXR_nodes = nuke.selectedNodes("Read")
    print(EXR_nodes)
    
    # 複数選択されたら
    if (len(EXR_nodes) > 1):
        
        print("Multiple Read node are found")

        EXR_nodes.sort()

        Multiple_Read_Node_Panel = nuke.Panel('Multiple Read Node are found/selected')

        read_node_array_str = ""
        for n in EXR_nodes:
            read_node_array_str += n.name() + " "
        # print(csv_path_array_str)
        Multiple_Read_Node_Panel.addEnumerationPulldown("Select Multiple selected Read Node", read_node_array_str )

        returnMultiple_Read_Node_Panel = Multiple_Read_Node_Panel.show()
        if(returnMultiple_Read_Node_Panel):
            _read_node = Multiple_Read_Node_Panel.value("Select Multiple selected Read Node")
            EXR_node = nuke.toNode(_read_node)

        else:
            bFinish = True
            # break 
            # ここのerror処理がまだ未完成状態
        
        
        

    elif(len(EXR_nodes) == 0):
        print("Selected Read Node is not found")
        nuke.message('Selected Read Node is not found. \n Please try again.')
    elif(len(EXR_nodes) == 1):
        EXR_node = EXR_nodes[0]
    else:
        print("EXR_node is unknown pattern")
        nuke.message('EXR_node is unknown pattern. \n Please confirm to developper.')
else:
    EXR_node = nuke.toNode(selected_read_node_name)

# print(EXR_node)

EXR_first_frame = int(EXR_node["first"].value()) # first frameのときのframe number
EXR_last_frame  = int(EXR_node["last"].value()) # last frameのときのframe number
EXR_duration_frame = EXR_last_frame - EXR_first_frame

# print(first)
# print(last)
# EXR_node_start_frame = timecode_to_frames(EXR_node_start_tc)
# EXR_node_start_frame = int(p1.value("Start frame"))
# nuke.frame(EXR_node_start_frame)#move to start frame

nuke.frame(EXR_first_frame)#move to start frame
EXR_node_start_tc = EXR_node.metadata("input/timecode")# get start timecode , 現在のframeでないとtimecodeが適当なtimecodeになる。
EXR_node_start_tc_to_frame = timecode_to_frames(EXR_node_start_tc)
EXR_node_end_tc_to_frame = EXR_node_start_tc_to_frame + EXR_duration_frame

# EXR_node_start_timecode = frames_to_timecode(EXR_first_frame)
# EXR_node_end_timecode = frames_to_timecode(EXR_last_frame)

# print(EXR_node_start_timecode)
# print(type(EXR_node_start_timecode))
# print(EXR_node_start_frame)
# print(type(EXR_node_start_frame))
EXR_node_reel_name = EXR_node.metadata("exr/reelName")
# print(EXR_node_start_tc)
# print(EXR_node_reel_name)
keyframe = p1.value("Keyframe")


searching_path = None#initialize
# csvをreel nameから探すなら
if(bCSV_Auto_Searching):
    searching_path = pathlib.Path(csv_folder_path)
    print(searching_path)
    # print(type(searching_path))<class 'pathlib.PosixPath'>
    searching_path = str(searching_path)

    csv_path_array = glob.glob('**/' + EXR_node_reel_name +'.csv', recursive=True, root_dir=searching_path)
    # print(csv_path_array)
    if (len(csv_path_array) == 0):
        print("CSV file is not found")
        nuke.message('CSV is not searched. \n Please try again.')

        bFinish = True
    elif(len(csv_path_array) > 1):
        # 複数ヒットした場合
        # 選択させる
        print("Multiple CSV files are found")

        Multiple_CSV_Panel = nuke.Panel('Multiple CSV files are found')

        csv_path_array_str = ""
        for n in csv_path_array:
            csv_path_array_str += searching_path + "/" + n + " "
        print(csv_path_array_str)
        Multiple_CSV_Panel.addEnumerationPulldown("Select Multiple hit CSV", csv_path_array_str )

        returnMultiple_CSV_Panel = Multiple_CSV_Panel.show()
        selected_csv = Multiple_CSV_Panel.value("Select Multiple hit CSV")

        csv_path = selected_csv

    else:
        csv_path = searching_path + "/" + csv_path_array[0]
        print(csv_path)

# csvのpathを直接選ぶなら
else:
    
    csv_path = csv_folder_path




# csv reader
if (bCSV_Auto_Detection):# csv type auto detection
    
    try:

        with open(csv_path) as f:
            # https://note.com/shirotabistudy/n/n2a9b0a8edba0
            dialect = csv.Sniffer().sniff(f.read(1024)) #サンプルとして1024バイト読み込む
            # print(dialect.delimiter)
            f.seek(0) #ファイルの先頭に戻る

            reader = csv.DictReader(f, dialect=dialect) # Snifferで判定した設定を使って読み込む
            csv_data = [row for row in reader]

            # https://nikkie-ftnext.hatenablog.com/entry/python-csv-reader-dialect-parameter-introduction

            if(dialect.delimiter == ","):
                print("Silver Stack")
                csv_type = "SilverStack"
            elif(dialect.delimiter == "\t"):
                print("SONY RAW Viewer")
                csv_type = "SONY-RawViewer"
            else:
                print("unknown csv format")
                bFinish = True
            
    except FileNotFoundError:
        print("file is no found")
        bFinish = True
        # sys.exit(0)
    except PermissionError:
        print("no permission to access the file")
        bFinish = True
        # sys.exit(0)
    
    
else:#csv type manual
    try:
        if(csv_type == "SilverStack"):
            with open(csv_path) as f:
                # reader = csv.reader(f)
                # csv_data = [row for row in reader]
                reader = csv.DictReader(f)
                csv_data = [row for row in reader]
        elif(csv_type == "SONY-RawViewer"):
            with open(csv_path) as f:
                # reader = csv.reader(f)
                # csv_data = [row for row in reader]
                reader = csv.DictReader(f, delimiter='\t')
                csv_data = [row for row in reader]
        else:
            print("csv type is not valid")
            bFinish = True
            # sys.exit(0)

    except FileNotFoundError:
        print("file is no found")
        bFinish = True
        # sys.exit(0)
    except PermissionError:
        print("no permission to access the file")
        bFinish = True
        # sys.exit(0)


if not bFinish:
    
    
    
    bExist_DynamicMetadataCam_node = False
    #check existing all nodes
    for n in nuke.allNodes():
        #add to check=[] nodes name
        _name_counter = 0
        # _exist_cam = False

        # indexをつけて新しいnodeを作りたい
        match_pattern = 'DynamicMetadataCam_\d*'
        repatter = re.compile(match_pattern)
        match_result = repatter.match(n.name())

        if bool(match_result):
            check.append(n.name())
            bExist_DynamicMetadataCam_node = True
    

    check.sort()


    if bExist_DynamicMetadataCam_node:
        node_counter = 0
        for i in range(len(check)):
            
           
            # print("check[i]")
            # print(check[i])
            if 'DynamicMetadataCam_' + str(node_counter) == check[i]:
                # last checkならincrementして作成
                if i + 1 == len(check):
                    DynamicMetadataCam = nuke.nodes.Camera(name="DynamicMetadataCam_"+str(node_counter+1), xpos=-90 + ((node_counter+1) * 90),ypos=-200, rot_order=rotation_order)
                    break
                # 同名ノードがあった場合の考慮 ex:DynamicMetadataCam_1が2つあった場合
                # incrementしない
                if 'DynamicMetadataCam_' + str(node_counter) != check[i+1]:
                    node_counter = node_counter+1

            # 歯抜けで存在しなかったら
            else:
                # print("create_new_cam")
                DynamicMetadataCam = nuke.nodes.Camera(name="DynamicMetadataCam_"+str(node_counter), xpos=-90 + (node_counter * 90),ypos=-200, rot_order=rotation_order)
                break
    #nodeが存在しなかったら
    else:
        DynamicMetadataCam = nuke.nodes.Camera(name="DynamicMetadataCam_0", xpos=-90 ,ypos=-200, rot_order=rotation_order)

        
        

    # set animation keyframe
    # DynamicMetadataCam['translate'].setAnimated()
    DynamicMetadataCam['rotate'].setAnimated()
    # focal length
    DynamicMetadataCam['focal'].setAnimated()
    # focus focal point
    DynamicMetadataCam['focal_point'].setAnimated()
    # iris 
    DynamicMetadataCam['fstop'].setAnimated()
    # DynamicMetadataCam['win_translate'].setAnimated()
    # DynamicMetadataCam['haperture'].setAnimated()
    # DynamicMetadataCam['vaperture'].setAnimated()
    # DynamicMetadataCam['win_scale'].setAnimated(1)


    # .animation()returns AnimationCurveObject
    # animx = DynamicMetadataCam['translate'].animation(0)
    # animy = DynamicMetadataCam['translate'].animation(1)
    # animz = DynamicMetadataCam['translate'].animation(2)
    animrx = DynamicMetadataCam['rotate'].animation(0)
    animry = DynamicMetadataCam['rotate'].animation(1)
    animrz = DynamicMetadataCam['rotate'].animation(2)
    animfocal= DynamicMetadataCam['focal'].animation(0)
    animfocus = DynamicMetadataCam['focal_point'].animation(0)
    animfstop = DynamicMetadataCam['fstop'].animation(0)

    # animcsx = DynamicMetadataCam['win_translate'].animation(0)
    # animcsy = DynamicMetadataCam['win_translate'].animation(1)
    # animhapert = DynamicMetadataCam['haperture'].animation(0)
    # animvapert = DynamicMetadataCam['vaperture'].animation(0)
    # animwscale = DynamicMetadataCam['win_scale'].animation(1)


 
    samples = []


    for i, row in enumerate(csv_data):

        if csv_type == "SilverStack":
            _Timecode = row['Timecode']
            _Focal_Length_meter = row["Focal Length (mm)"]
            if(_Focal_Length_meter == ""):
                _Focal_Length_meter = 0.0
            
            _Aperture = row['Aperture']
            if(_Aperture == ""):
                _Aperture = 0.0
            
            _Focus_Distance_feet = row["Focus Distance (ft)"]
            if(_Focus_Distance_feet == ""):
                _Focus_Distance_feet = 0.0

            _Focus_Distance_meter = float(_Focus_Distance_feet) * 0.3048

            _Camera_Tilt = row['Camera Tilt']
            if(_Camera_Tilt == ""):
                _Camera_Tilt = 0.0
            
            _Camera_Roll = row['Camera Roll']
            if(_Camera_Roll == ""):
                _Camera_Roll = 0.0

        elif csv_type == "SONY-RawViewer":
            _Timecode = row['Timecode']

            _Focal_Length_meter = row["Lens Zoom Actual Focal Length"].replace("mm", "")
            _Focal_Length_meter = float(_Focal_Length_meter)
            if(_Focal_Length_meter == ""):
                _Focal_Length_meter = 0.0

            _Aperture = row["Iris F-Number"]
            _Aperture = float(_Aperture)
            if(_Aperture == ""):
                _Aperture = 0.0
                
            
            _Focus_Distance_meter = row["Focus Position From Image Plane"].replace("m", "")
            _Focus_Distance_meter =float(_Focus_Distance_meter)
            # print(_Focus_Distance_meter)
            # print(type(_Focus_Distance_meter))
            if(_Focus_Distance_meter == ""):
                _Focus_Distance_meter = 0.0

            _Focus_Distance_feet = float(_Focus_Distance_meter) / 0.3048

            _Camera_Tilt = row['Camera Tilt Angle']
            _Camera_Tilt = float(_Camera_Tilt)
            if(_Camera_Tilt == ""):
                _Camera_Tilt = 0.0
            
            _Camera_Roll = row['Camera Roll Angle']
            _Camera_Roll = float(_Camera_Roll)
            if(_Camera_Roll == ""):
                _Camera_Roll = 0.0

        else:
            print("csv type is not valid")
            break

        samples.append({
            'Timecode': _Timecode,
            'Focal_Length_meter': float(_Focal_Length_meter),
            'Aperture': float(_Aperture),
            'Focus_Distance_feet': float(_Focus_Distance_feet),
            'Focus_Distance_meter' : _Focus_Distance_meter,
            'Camera_Tilt': float(_Camera_Tilt),
            'Camera_Roll': float(_Camera_Roll)
        })



    # keysnk1 = []
    # keysnk2 = []
    # keysncsx = []
    # keysncsy = []
    # keysntx = []
    # keysnty = []
    # keysntz = []

    # rotation
    keysnry = []
    keysnrz = []
    keysnrx = []
    # focal length
    keysnfocal = []
    # focus
    keysnfocus = []
    # fstop, iris
    keysnfstop = []
    # keyscamcsx = []
    # keyscamcsy = []
    # keyshapert = []
    # keysvapert = []
    # keyswscale = []

    _keyframe_counter = 0 #initialize

    for i, sample in enumerate(samples):
      
        samples[i]['frames'] = timecode_to_frames(samples[i]['Timecode'])

        # print(EXR_node_start_tc_to_frame)
        # print("vs")
        # print(samples[i]['frames'])

        # EXRのstart TCよりも前にはkeyを打たない, end TCよりも後にkeyを打たない
        if(EXR_node_start_tc_to_frame <= samples[i]['frames'] and samples[i]['frames'] <= EXR_node_end_tc_to_frame):
            
            write_frame = 0 #initialize

            if(keyframe == "StartFrame"):
                # 1001 startとかになる
                write_frame = EXR_first_frame + _keyframe_counter
                # print(write_frame)
                _keyframe_counter = _keyframe_counter + 1
            elif(keyframe == "SourceTimecode"):
                write_frame = int(samples[i]['frames'])
            else:
                print("keyframe is not valid")
                break

            # radian
            # tilt = math.radians(samples[i]['Camera_Tilt'])
            # pan = math.radians(samples[i]['p'])
            # roll = math.radians(samples[i]['Camera_Roll'])
            
        
            #二重配列に結果としてなるように、[wframe, samples[i][]]を配列の中にappendしている。
            # keysnry.append([wframe, pan])
            # radian
            keysnrz.append([write_frame, samples[i]['Camera_Roll']])
            keysnrx.append([write_frame, samples[i]['Camera_Tilt']])
            
            
            # keysnk1.append([wframe, samples[i]['k1']])
            # keysnk2.append([wframe, samples[i]['k2']])
            # keysncsx.append([wframe, samples[i]['csx']])
            # keysncsy.append([wframe, samples[i]['csy']])
            # keysntx.append([wframe, samples[i]['x']])
            # keysnty.append([wframe, samples[i]['y']])
            # keysntz.append([wframe, samples[i]['z']])
            # keysnfocal.append([wframe, samples[i]['pw']/2/math.tan(math.radians(samples[i]['fov'])/2)])
            keysnfocal.append([write_frame, samples[i]['Focal_Length_meter']])
            keysnfocus.append([write_frame, samples[i]['Focus_Distance_meter']])
            keysnfstop.append([write_frame, samples[i]['Aperture']])

        # keyscamcsx.append([wframe, samples[i]['csx']])
        # keyscamcsy.append([wframe, samples[i]['csy']])
        # keyshapert.append([wframe, samples[i]['pw']])
        # keysvapert.append([wframe, samples[i]['pw']/samples[i]['ar']])
        # keyswscale.append([wframe, (float(video_width)/video_height/samples[i]['ar'])])

    #全部のkey配列にデータがはいったら、
    #wframeで入れたframeに、valueをkeyframeとして打ち込む
    # valueは[frames,value]の配列
    # amink1.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnk1])
    # amink2.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnk2])
    # animdcsx.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysncsx])
    # animdcsy.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysncsy])
    # animx.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysntx])
    # animy.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnty])
    # animz.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysntz])
    animrx.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnrx])
    # animry.add    Key([nuke.AnimationKey(frame, value) for (frame,value) in keysnry])
    animrz.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnrz])
    animfocal.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnfocal])
    animfocus.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnfocus])
    animfstop.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysnfstop])

    # animcsx.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keyscamcsx])
    # animcsy.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keyscamcsy])
    # animhapert.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keyshapert])
    # animvapert.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keysvapert])
    # animwscale.addKey([nuke.AnimationKey(frame, value) for (frame,value) in keyswscale])



    #project settingのrangeを設定
    # for check
    # nuke.root()['first_frame'].setValue(timecode_to_frames(samples[0]["Timecode"]))
    # nuke.root()['last_frame'].setValue(timecode_to_frames(samples[len(samples)-1]["Timecode"]))


