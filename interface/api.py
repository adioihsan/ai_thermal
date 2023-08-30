import os
import sys
import cv2
from vidgear.gears import NetGear
from vidgear.gears import VideoGear
from threading import Thread

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import detection.utils as det_utils
from manager.process_manager import ProcessManager


pm = ProcessManager()
q_frame_rgb,q_frame_flir,q_rois,q_temp = pm.get_all_data()
pm.start_all_processes()


def server_rgb():
    # activate multiserver_mode
    options = {"flag": 0, "copy": False, "track": False, "multiserver_mode" :True}

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
    while True:
        frame = q_frame_rgb.get(True,500)
        try:
            # check for frame if Nonetype
            if frame is None:
                break

            # let's prepare a text string as data
            target_data = "I'm Server-1 at Port: 5577"

            rois_dict = q_rois.get(True,500)
            face_bbox = rois_dict.get("face")
            landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")


            det_utils.draw_face(frame,face_bbox)
            det_utils.draw_landmark(frame,landmark_point)
            det_utils.draw_forhead(frame,forhead_bboxes)

            # send frame and data through server
            frame = cv2.resize(frame,(160,120))
            server.send(frame, message=target_data)


            

        except KeyboardInterrupt:
            break

    # safely close video stream

    # safely close server
    server.close()

def server_flir():
    # Define NetGear Server at Client's IP address and assign a unique port address and other parameters
    # !!! change following IP address '192.168.x.xxx' with yours !!!
    options = {"flag": 0, "copy": False, "track": False, "multiserver_mode" :True}
    server = NetGear(
        address="192.168.1.32",
        port="5578",
        protocol="tcp",
        pattern=1,
        logging=True,
        max_retries=100,
        **options
    )

    # loop over until Keyboard Interrupted
    while True:
        try:
            # read frames from stream
            frame = q_frame_flir.get(True,500)

            # check for frame if Nonetype
            if frame is None:
                break

            # {do something with frame and data(to be sent) here}

            # let's prepare a text string as data
            
            text = "I'm Server-2 at Port: 5578"
            
            flir_8_bit_frame = det_utils.raw_to_8bit(frame)
            # send frame and data through server
            server.send(flir_8_bit_frame, message=text)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    Thread(target=server_rgb).start()
    Thread(target=server_flir).start()
        
