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


def get_temp(val_k,unit="C"):
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


def run(q_frame_flir,q_rois,q_temp):
    while True:
        data = q_frame_flir.get(True)
        frame = cv2.resize(data[:,:], (640, 480))
        
        rois_dict = q_rois.get(True)
        face_bbox = rois_dict.get("face")

        face_temps = []

        # landmark_point = rois_dict.get("landmark")
        forhead_bboxes = rois_dict.get("forhead")
        for (x,y,w,h) in face_bbox:
            face_area = frame[y:y+h,x:x+w].copy()
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(face_area)
            face_temp_max = get_temp(maxVal)
            face_temp_avg = 0
            face_temps.append(face_temp_max)
            face_temps.append(face_temp_avg)
        
        if not q_temp.full():
            q_temp.put({"face":face_temps})

if __name__ == "__main__":
    run()
    