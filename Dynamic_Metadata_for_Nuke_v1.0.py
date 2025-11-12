#Dynamic Metadata from SilverStack csv for Nuke 
# v1.0
# Kazuki Omata


import csv
import math
import nuke
import datetime
import re



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
    return '{h:02f}:{m:02f}:{s:02f}:{f:02f}'.format(h=int(seconds/3600),m=int(seconds/60%60),s=int(seconds%60),f=round((seconds-int(seconds))*framerate))

def _frames(seconds):
    return seconds * framerate

def timecode_to_frames(timecode, start=None):
    return _frames(_seconds(timecode) - _seconds(start))

def frames_to_timecode(frames, start=None):
    return _timecode(_seconds(frames) + _seconds(start))




# ----------panel setting


p1 = nuke.Panel('Dynamic Metadata setting')

p1.addFilenameSearch('CSV file path', '~/Desktop/')
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

csv_path = p1.value("CSV file path")
rotation_order = p1.value("Type of Camera Rotation order")

# csv parser
try:
    with open(csv_path) as f:
        # reader = csv.reader(f)
        # csv_data = [row for row in reader]
        reader = csv.DictReader(f)
        csv_data = [row for row in reader]
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
            
           
            print("check[i]")
            print(check[i])
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


 
    csv_data = None
    samples = []

    




    for i, row in enumerate(csv_data):


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

    for i, sample in enumerate(samples):
      
        samples[i]['frames'] = timecode_to_frames(samples[i]['Timecode'])
     
            
        write_frame = int(samples[i]['frames'])

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


