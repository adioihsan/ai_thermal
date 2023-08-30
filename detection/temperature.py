import cv2
import numpy as np

try:
    import detection.utils as utils
except ImportError:
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import utils


def temp_to_c(val_k,unit="C"):
    val=val_k
    if unit == "C":
        val = (val - 27315) / 100.0
    elif unit == "F":
        val = ((val - 27315)*9/5 + 32) / 100
    elif unit == "R":
        val = ((val - 27315)*4/5) / 100
    else:
        val = val_k
    return val

def get_temp(frame,bbox):
    for (x,y,w,h) in bbox:
        area = frame[y:y+h,x:x+w].copy()
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(area)

        temp_max = temp_to_c(maxVal)
        temp_avg = temp_to_c((maxVal+minVal)/2)
        temp_min = temp_to_c(minVal)

        return [temp_max,temp_avg,temp_min]


def run(q_frame_flir,q_rois,q_temp):
    while True:
        data = q_frame_flir.get(True)
        frame = cv2.resize(data[:,:], (640, 480))
        
        rois_dict = q_rois.get(True)
        face_bbox = rois_dict.get("face")
        forhead_bbox = rois_dict.get("forhead")

        face_temps = get_temp(frame,face_bbox)
        forhead_temps =  get_temp(frame,forhead_bbox)

        if not q_temp.full():
            q_temp.put({"face":face_temps,"forhead":forhead_temps})

if __name__ == "__main__":
    run()
    