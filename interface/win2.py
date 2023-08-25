import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import cv2
import numpy as np
from PIL import Image
import PySimpleGUI as sg
import psutil
import detection.utils as det_utils
from manager.process_manager import ProcessManager
import time
from threading import Thread

pm = ProcessManager()
p_frame_rgb,p_frame_flir,p_face,p_temperature = pm.get_all_processes()
q_frame_rgb,q_frame_flir,q_rois,q_temp = pm.get_all_data()
pm.start_all_processes()

def rgb_worker():
    while True:
            loop_start = time.monotonic()
            rgb_frame = q_frame_rgb.get(True,500)
            rois_dict = q_rois.get(True,500)
            face_bbox = rois_dict.get("face")
            forhead_bboxes = rois_dict.get("forhead")
            det_utils.draw_face(rgb_frame,face_bbox)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

            cv2.imshow("rgb frame",rgb_frame)
            key  = cv2.waitKey(1)

            print(f"delay {1000*(time.monotonic()-loop_start):.1f} ms")

            if key == "q":
                pm.terminate_all_processes()

def flir_worker():
    while True:
        flir_frame = q_frame_flir.get(True,500)
        print(flir_frame)

if __name__ == "__main__":
    flir_worker()