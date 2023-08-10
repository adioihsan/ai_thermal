import cv2
from config import *
import detection.utils as det_utils
from detection import face,temperature
from device import Rgb_cam,Flir_cam 
from multiprocessing import Process , Queue


# create queue for data exchange
q_frame_rgb = Queue(2)
q_rois = Queue(2)  # queue for bounding boxes (face,forhead and face landmark) 
q_frame_flir = Queue(2)
q_frame_temp = Queue(2) # queue for save tempertature 

# create process for face detection
p_face = Process(target=face.run,args=(q_frame_rgb,q_rois,))
p_temperature = Process(target=temperature.run,args=(q_frame_flir,q_rois,q_frame_temp))

# process to load frame
def load_rgb_frame(q_frame_rgb):
    rgb_cam =  Rgb_cam.Camera().start()
    while True:
        success,frame = rgb_cam.get_frame()
        if not success:
            break
        if  not q_frame_rgb.full():
            q_frame_rgb.put(frame)    

def load_flir_frame(q_frame_flir):
    Flir_cam.start()
    while True:
        frame = Flir_cam.q.get(True)
        q_frame_flir.put(frame)

p_rgb_frame = Process(target=load_rgb_frame,args=(q_frame_rgb,))
p_flir_frame = Process(target=load_flir_frame,args=(q_frame_flir,))

# get frame
def rgb_run():
    p_rgb_frame.start()
    p_face.start()
    running = True
    while running:
        rgb_frame = q_frame_rgb.get(True,500)
        #get ROIs from face detection process
        if not  q_rois.empty():
            # get rois from face module process
            rois_dict = q_rois.get(True)
            face_bbox = rois_dict.get("face")
            landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")
            #draw into frame
            det_utils.draw_face(rgb_frame,face_bbox)
            det_utils.draw_landmark(rgb_frame,landmark_point)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

        if SHOW_VIEW:
            cv2.imshow("face",rgb_frame)
            key = cv2.waitKey(1)
            # press esc to stop
            if key == 27:
                p_rgb_frame.join()
                p_face.join()
                cv2.destroyAllWindows()
                exit()

def flir_run():
    p_flir_frame.start()
    while True:
        frame = q_frame_flir.get(True)
        if frame is None:
            break
        frame = cv2.resize(frame[:,:], (640, 480))
        frame_8_bit = det_utils.raw_to_8bit(frame)
        cv2.imshow('flir cam',frame_8_bit)
        cv2.waitKey(1)

def run_both():
    p_flir_frame.start()
    p_rgb_frame.start()
    p_face.start()
    while True:
        rgb_frame = q_frame_rgb.get(True,500)
        flir_frame = q_frame_flir.get(True,500)

        if rgb_frame is None or flir_frame is None:
            break

        flir_frame = cv2.resize(flir_frame[:,:], (640, 480))
        flir_frame = det_utils.raw_to_8bit(flir_frame)

        if not  q_rois.empty():
        # get rois from face module process
            rois_dict = q_rois.get(True)
            face_bbox = rois_dict.get("face")
            # landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")

            det_utils.draw_face(flir_frame,face_bbox,"flir")
            # det_utils.draw_landmark(flir_frame,landmark_point)
            det_utils.draw_forhead(flir_frame,forhead_bboxes,"flir")

            det_utils.draw_face(rgb_frame,face_bbox)
            # det_utils.draw_landmark(rgb_frame,landmark_point)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

        cv2.imshow('flir cam',flir_frame)
        cv2.imshow('rgb cam',rgb_frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_both).start()
    # Thread(target=flir_run()).start()
    # Thread(target=rgb_run()).start()
 
    
import cv2
from config import *
import detection.utils as det_utils
from detection import face,temperature
from device import Rgb_cam,Flir_cam 
from multiprocessing import Process , Queue


# create queue for data exchange
q_frame_rgb = Queue(2)
q_rois = Queue(2)  # queue for bounding boxes (face,forhead and face landmark) 
q_frame_flir = Queue(2)
q_frame_temp = Queue(2) # queue for save tempertature 

# create process for face detection
p_face = Process(target=face.run,args=(q_frame_rgb,q_rois,))
p_temperature = Process(target=temperature.run,args=(q_frame_flir,q_rois,q_frame_temp))

# process to load frame
def load_rgb_frame(q_frame_rgb):
    rgb_cam =  Rgb_cam.Camera().start()
    while True:
        success,frame = rgb_cam.get_frame()
        if not success:
            break
        if  not q_frame_rgb.full():
            q_frame_rgb.put(frame)    

def load_flir_frame(q_frame_flir):
    Flir_cam.start()
    while True:
        frame = Flir_cam.q.get(True)
        q_frame_flir.put(frame)

p_rgb_frame = Process(target=load_rgb_frame,args=(q_frame_rgb,))
p_flir_frame = Process(target=load_flir_frame,args=(q_frame_flir,))

# get frame
def rgb_run():
    p_rgb_frame.start()
    p_face.start()
    running = True
    while running:
        rgb_frame = q_frame_rgb.get(True,500)
        #get ROIs from face detection process
        if not  q_rois.empty():
            # get rois from face module process
            rois_dict = q_rois.get(True)
            face_bbox = rois_dict.get("face")
            landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")
            #draw into frame
            det_utils.draw_face(rgb_frame,face_bbox)
            det_utils.draw_landmark(rgb_frame,landmark_point)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

        if SHOW_VIEW:
            cv2.imshow("face",rgb_frame)
            key = cv2.waitKey(1)
            # press esc to stop
            if key == 27:
                p_rgb_frame.join()
                p_face.join()
                cv2.destroyAllWindows()
                exit()

def flir_run():
    p_flir_frame.start()
    while True:
        frame = q_frame_flir.get(True)
        if frame is None:
            break
        frame = cv2.resize(frame[:,:], (640, 480))
        frame_8_bit = det_utils.raw_to_8bit(frame)
        cv2.imshow('flir cam',frame_8_bit)
        cv2.waitKey(1)

def run_both():
    p_flir_frame.start()
    p_rgb_frame.start()
    p_face.start()
    while True:
        rgb_frame = q_frame_rgb.get(True,500)
        flir_frame = q_frame_flir.get(True,500)

        if rgb_frame is None or flir_frame is None:
            break

        flir_frame = cv2.resize(flir_frame[:,:], (640, 480))
        flir_frame = det_utils.raw_to_8bit(flir_frame)

        if not  q_rois.empty():
        # get rois from face module process
            rois_dict = q_rois.get(True)
            face_bbox = rois_dict.get("face")
            # landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")

            det_utils.draw_face(flir_frame,face_bbox,"flir")
            # det_utils.draw_landmark(flir_frame,landmark_point)
            det_utils.draw_forhead(flir_frame,forhead_bboxes,"flir")

            det_utils.draw_face(rgb_frame,face_bbox)
            # det_utils.draw_landmark(rgb_frame,landmark_point)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

        cv2.imshow('flir cam',flir_frame)
        cv2.imshow('rgb cam',rgb_frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_both).start()
    # Thread(target=flir_run()).start()
    # Thread(target=rgb_run()).start()
 
    
