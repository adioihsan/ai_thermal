import cv2
from queue import Queue
import threading

# Global variable

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

# def start(camera_source=None):
#     print("Starting rgb camera...")
#     if camera_source is None :
#         camera = cv2.VideoCapture(gstreamer_pipeline(),cv2.CAP_GSTREAMER)
#     else:
#        camera =  cv2.VideoCapture(camera_source)
#     try:
#         while started:
#             success,frame = camera.read()
#             if success:
#                 if frame_q.not_full:
#                     frame_q.put(frame)
#     except Exception as error:
#         print("Cant open RGB camera !")
#         print(f"Error details :{error}")
#         exit()
#     finally:
#         camera.release()

# def stop():
#     started = False


# def stream_loop(camera,callback=None):
#     while is_running:
#         success,frame = 


class RgbCamera:
    def __init__(self,camera_source=None):
        try:
            if camera_source is None :
                self.cam = cv2.VideoCapture(gstreamer_pipeline(),cv2.CAP_GSTREAMER)
            else :
                self.cam = cv2.VideoCapture(camera_source)
            # read intial frame
            (self.success,self.frame) = self.cam.read()
            self.q = Queue(2)
            self.running = True
        except:
            print(f"Cant open camera on given source {camera_source}")

    def start(self,callback=None):
        self.rgbcam_thread = threading.Thread(target=self.__stream_loop,args=(callback,))
        self.rgbcam_thread.start()
        return self
    
    def get_frame(self):
        try:
            return [True,self.q.get(True)]
        except:
            return [False,[]]

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
    import time
    from multiprocessing import Process

    

    def cam1():
        print("starting cam1")
        camera = RgbCamera(1).start()
        while True :
            success,frame = camera.get_frame()
            if success:
                cv2.imshow("test frame 1",frame)
                key = cv2.waitKey(1)
                if key == 27:
                    camera.stop()
                    cv2.destroyAllWindows()
                    break

    Process(target=cam1).start()
        