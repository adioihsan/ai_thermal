import cv2
from queue import Queue
import threading

# Global variable

def gstreamer_pipeline(
    capture_width=640,
    capture_height=480,
    display_width=640,
    display_height=480,
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


class Camera:
    def __init__(self,camera_source=None):
        try:
            if camera_source is None :
                self.cam = cv2.VideoCapture(gstreamer_pipeline(),cv2.CAP_GSTREAMER)
            else :
                self.cam = cv2.VideoCapture(camera_source)
            # read intial frame
        except:
            print(f"Cant open camera on given source {camera_source}")
    
    def get_frame(self):
        try:
            return self.cam.read()
        except:
            print("Cant read rgb frame")

            
    def stop(self):
        print("Stoping camera streaming...")
        self.running = False
        self.cam.release()
        self.rgbcam_thread.join()
       

if __name__ == "__main__":
    import time
    from multiprocessing import Process
    

    def cam1(): 
        camera = Camera(1)
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
        