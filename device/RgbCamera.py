import cv2
from queue import Queue
import threading

def gstreamer_pipeline(
    capture_width=800,
    capture_height=600,
    display_width=800,
    display_height=600,
    framerate=30,
    flip_method=2
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink drop=True"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

class RgbCamera:
    instance_count=0
    instance =  None
    def __init__(self,camera_source=0):
        if self.instance_count == 0 :
            try:
                self.cam = cv2.VideoCapture(gstreamer_pipeline(),cv2.CAP_GSTREAMER)
                # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,320)
                # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
                # read intial frame
                (self.success,self.frame) = self.cam.read()
                self.q = Queue(2)
                self.instance_count = 1
                self.instance = self 
                self.running = True
            except:
                print(f"Cant open camera on given source {camera_source}")
        else :
            print("Camera already open")
        
    # def __new__(cls,name):
    #     if self.instance_count == 0:
    #         return self 
    #     else:
    #         return self.instance

    def start(self,callback=None):
        self.rgbcam_thread = threading.Thread(target=self.__stream_loop,args=(callback,))
        self.rgbcam_thread.start()
        return self
    
    def get_frame(self):
        return self.q.get(True,500)

    def __stream_loop(self,callback=None):
        while self.running:
            self.success,self.frame = self.cam.read()
            if self.success and not self.q.full():
                self.q.put(self.frame)
            if callback is not None:
                callback(self.frame)
            
    
    def stop(self):
        print("Stoping camera streaming...")
        self.running = False
        self.cam.release()
        self.rgbcam_thread.join()
       


if __name__ == "__main__":
        # using thread
    camera = RgbCamera().start()
    while True :
        frame = camera.get_frame()
        cv2.imshow("test frame",frame)
        key = cv2.waitKey(1)
        print(key)
        if key == 27:
            camera.stop()
    
        # using callback

    