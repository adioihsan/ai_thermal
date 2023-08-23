import cv2
import detection.utils as det_utils
from detection import face,temperature
from device import Rgb_cam
from multiprocessing import Process , Queue ,active_children


class ProcessManager:
    def __init__(self):
        self.q_frame_rgb = Queue(2)
        self.q_frame_rgb_copy = Queue(2)
        self.q_rois = Queue(2) 
        self.q_frame_flir = Queue(2)
        self.q_temperature = Queue(2) 
        self.__factory()

    def __factory(self):
        self.p_frame_rgb = Process(target=self.__load_rgb_frame)
        self.p_frame_flir = Process(target=self.__load_flir_frame)
        self.p_face = Process(target=face.run,args=(self.q_frame_rgb_copy,self.q_rois,))
        self.p_temperature = Process(target=temperature.run,args=(self.q_frame_flir,self.q_rois,self.q_temperature,))


    def __load_rgb_frame(self):
        rgb_cam =  Rgb_cam.Camera(1)
        while True:
            success,frame = rgb_cam.get_frame()
            if not success:
                break
            if  not self.q_frame_rgb.full():
                self.q_frame_rgb.put(frame)
            if not self.q_frame_rgb_copy.full():
                self.q_frame_rgb_copy .put(frame)    

    def __load_flir_frame(self):
        Flir_cam.start()
        while True:
            frame = Flir_cam.q.get(True)
            if  not self.q_frame_flir.full():
                self.q_frame_flir.put(frame)

    def start_all_processes(self):
            self.p_frame_rgb.start()
            self.p_face.start()
            # self.p_frame_flir.start()
            # self.p_temperature.start()

    def get_all_data(self):
            return [self.q_frame_rgb,self.q_frame_flir,self.q_rois,self.q_temperature]

    def get_all_processes(self):
            return [self.p_frame_rgb,self.p_frame_flir,self.p_face,self.p_temperature]

    def terminate_all_processes(self):
            children_proc = active_children()
            for child in children_proc:
                child.terminate()

    def restart_active_processes(self):
        children_proc = active_children()
        for child in children_proc:
                child.terminate()
        self.factory()
    
        


# def run_proc():

#     processes = [p_frame_rgb,p_frame_flir,p_face,p_temperature]
#     data = [q_frame_rgb,q_frame_flir,q_rois,q_temperature]

#     app_gui.run(processes,data)

# if __name__ == "__main__":
#     import os
#     import sys
#     current = os.path.dirname(os.path.realpath(__file__))
#     parent = os.path.dirname(current)
#     sys.path.append(parent)

#     run_proc()
