import cv2
from config import *
import detection.utils as det_utils
from detection import face,temperature
from device import Rgb_cam,Flir_cam
from interface import gui as app_gui, api
from multiprocessing import Process , Queue ,active_children


# create queue for data exchange
q_frame_rgb = Queue(2)
q_rois = Queue(2)  # queue for bounding boxes (face,forhead and face landmark) 
q_frame_flir = Queue(2)
q_temp = Queue(2) # queue for save tempertature 

# create process for face detection
p_face = Process(target=face.run,args=(q_frame_rgb,q_rois,))
p_temperature = Process(target=temperature.run,args=(q_frame_flir,q_rois,q_temp))
p_api = Process(target=api.send_rgb_frame,args=(q_frame_rgb,))

# process to load frame
def load_rgb_frame(q_frame_rgb):
    rgb_cam =  Rgb_cam.Camera(1).start()
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

def stop_all():
    children_proc = active_children()
    for child in children_proc:
        child.terminate()


if __name__ == "__main__":
    p_rgb_frame.start()
    # p_flir_frame.start()
    # p_face.start()
    # p_temperature.start()

    p_api.start()

    
    # p_gui = Process(target=app_gui.run,args=(q_frame_rgb,q_frame_flir,q_rois,q_temp,))
    # p_gui.start()

 
    
