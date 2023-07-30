import cv2
from queue import Queue
import threading

class init:
    instance_count=0
    instance =  None
    def __init__(self,camera_source=0):
        if self.instance_count == 0 :
            try:
                self.cam = cv2.VideoCapture(camera_source)
                self.cam.set(3,480)
                self.cam.set(4,640)
                # read intial frame
                (self.success,self.frame) = self.cam.read()
                self.q = Queue(2)
                self.instance_count = 1
                self.instance = self 
            except:
                print(f"Cant open camera on given source {camera_source}")
        else :
            print("Camera already open")
        
    # def __new__(cls,name):
    #     if self.instance_count == 0:
    #         return self 
    #     else:
    #         return self.instance

    def start(self):
        rgbcam_thread = threading.Thread(target=self.__stream_loop)
        rgbcam_thread.start()
        return self
    
    def get_frame(self):
        return self.q.get(True,500)

    def __stream_loop(self):
        while True:
            self.success,self.frame = self.cam.read()
            if self.success and not self.q.full():
                self.q.put(self.frame)