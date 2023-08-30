import os
import sys
import cv2
from vidgear.gears import NetGear
from vidgear.gears import VideoGear

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
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
# activate multiserver_mode
options = {"flag": 0, "copy": False, "track": False, "multiserver_mode" :True,"jpeg_compression": True, "jpeg_compression_fastupsample": True,"jpeg_compression_quality": 50}

# Define NetGear Server at Client's IP address and assign a unique port address and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
server = NetGear(
    address="192.168.1.32",
    port="5577",
    protocol="tcp",
    pattern=1,
    logging=True,
    max_retries=100,
    **options
)

# loop over until Keyboard Interrupted
cap = cv2.VideoCapture(1)
while True:
    ret,frame = cap.read()
    frame = cv2.resize(frame,(160,120))

    try:
        # check for frame if Nonetype
        if not ret:
            break

        # let's prepare a text string as data
        target_data = "I'm Server-1 at Port: 5577"

        # send frame and data through server
        server.send(frame, message=target_data) # 

    except KeyboardInterrupt:
        break
    



# safely close server
cap.release()
server.close()


        
