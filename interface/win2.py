import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import cv2
import detection.utils as det_utils
from manager.process_manager import ProcessManager

pm = ProcessManager()
p_frame_rgb,p_frame_flir,p_face,p_temperature = pm.get_all_processes()
q_frame_rgb,q_frame_flir,q_rois,q_temp = pm.get_all_data()
pm.start_all_processes()

while True:
    # loop_start = time.monotonic()
    rgb_frame = q_frame_rgb.get(True,500)
    if len(rgb_frame) > 0:
        rois_dict = q_rois.get(True,500)
        face_bbox = rois_dict.get("face")
        landmark_point = rois_dict.get("landmark")
        forhead_bboxes = rois_dict.get("forhead")
        det_utils.draw_face(rgb_frame,face_bbox)
        det_utils.draw_landmark(rgb_frame,landmark_point)
        det_utils.draw_forhead(rgb_frame,forhead_bboxes)

    cv2.imshow("rgb camera",rgb_frame)

    flir_frame = q_frame_flir.get(True,500)
    if len(flir_frame) > 0 :
        flir_frame = cv2.resize(flir_frame[:,:], (640, 480))
        flir_8_bit_frame = det_utils.raw_to_8bit(flir_frame)

        det_utils.draw_face(flir_8_bit_frame,face_bbox,"flir")
        det_utils.draw_landmark(flir_8_bit_frame,landmark_point,"flir")
        det_utils.draw_forhead(flir_8_bit_frame,forhead_bboxes,"flir")
    
        temp_dict = q_temp.get(True)
        if len(temp_dict) > 0:
            face_tempt = temp_dict.get("face")
            forhead_tempt = temp_dict.get("forhead")
        if face_tempt is not None :
            det_utils.draw_temp(flir_8_bit_frame,face_bbox,"Highest{}".format(face_tempt[0]),"flir")
            det_utils.draw_temp(rgb_frame,face_bbox,"Highest{}".format(face_tempt[0]),"flir")
        
    cv2.imshow("flir camera",flir_8_bit_frame)
    cv2.imshow("rgb camera",rgb_frame)
    
    key  = cv2.waitKey(1)

    # print(f"delay {1000*(time.monotonic()-loop_start):.1f} ms")
    if key == "q":
        pm.terminate_all_processes()