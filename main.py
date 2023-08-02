import detection.utils
from detection import face
import time
from threading import Thread
from device import RgbCamera as cam
import cv2

face_thd = Thread(target=face.run).start()

while True :
    frame = face.frame_q.get(True,500)
    ROIs = face.ROIs_q.get(True,500)

    cv2.imshow("test frame",frame)
    cv2.waitKey(1)