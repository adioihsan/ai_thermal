# import required libraries
from vidgear.gears import NetGear
from threading import Thread
from queue import Queue
import cv2

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


def load_frame(q_frame):
        cap = cv2.VideoCapture(gstreamer_pipeline(),cv2.CAP_GSTREAMER)
        while True:
            try:
                grabbed,frame = cap.read()

                if not grabbed :
                    break
                if not  q_frame.full():
                    q_frame.put(frame)
            except KeyboardInterrupt:
                 cap.release()
            
        



def send_rgb_frame(q_frame):
    # Open suitable video stream, such as webcam on first index(i.e. 0)

    # define tweak flags
    options = {"flag": 0, "copy": False, "track": False}

    # Define Netgear Client at given IP address and define parameters 
    # !!! change following IP address '192.168.x.xxx' with yours !!!
    server = NetGear(
        address="192.168.43.171",
        port="5454",
        protocol="tcp",
        pattern=1,
        logging=True,
        max_retries=1000,
        jpeg_compression=False,
        **options
    )



    # loop over until KeyBoard Interrupted
    while True:
     
        # read frames from stream
        
        if not q_frame.empty():
             frame = q_frame.get(True,500)
             server.send(frame)
        else:
             print("frame empty")
       
        # check for frame if not grabbed
        # if not grabbed:
        #     break

        # {do something with the frame here}

        # send frame to server
        # server.send(frame)
        # cv2.imshow("test cam 1",frame)
        # key = cv2.waitKey(1)
        # if key == "q":

        #      quit()
         




    # safely close video stream
    # stream.release()

    # safely close server
    # server.close()

if __name__ == "__main__":
    q_frame = Queue(2)

    Thread(target=load_frame,args=(q_frame,)).start()
    Thread(target=send_rgb_frame,args=(q_frame,)).start()


