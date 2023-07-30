import cv2
import dlib
from imutils import face_utils

try:
    import detection.utils as utils
    import device.RgbCamera as cam
except ImportError:
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import utils
    import device.RgbCamera as cam

try:
  from queue import Queue
except ImportError:
  from Queue import Queue


face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
# cnn_detector = dlib.cnn_face_detection_model_v1('mmod_human_face_detector.dat')

frame_q = Queue(2)
bbox_q = Queue(2)

def run() :
    camera = cam.init().start()
    while True:
        frame = camera.get_frame()

        # detect face using dlib hog+svm linear
        gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        rects = face_detector(gray_frame)

        #detec face using dlib cnn
        # rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        # rects = face_detector(rgb_frame)

        #get boxes
        face_boxes = [utils.convert_and_trim_bb(gray_frame, r) for r in rects]
        forhead_boxes = []
        landmark_points = []
        for (x, y, w, h) in face_boxes:
            # draw face rectangle
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # detect face landmark
            face_ROI = dlib.rectangle(x,y,(x+w),(y+h))
            landmarks = landmark_detector(gray_frame,face_ROI)
            landmarks = face_utils.shape_to_np(landmarks)
            landmark_points.append(landmarks)

            # detect forhead 
                # get points between top eyes from landmarks
            xl1,yl1 = landmarks[20]
            xl2,yl2 = landmarks[23]

            forhead_ROI = utils.forhead_ROI_dynamic(xl1,yl1,xl2,yl2)
            xf,yf,wf,hf = forhead_ROI
            #draw forhead
            cv2.rectangle(frame,(xf,yf),(xf+wf,yf+hf),(0,255,0),2)
            
            #draw face landmarks
            for(x,y) in landmarks:
                cv2.circle(frame,(x,y),2,(0,255,0),-1)
                
        # put things to queue
        if  not frame_q.full():
            frame_q.put(frame)
        if not bbox_q.full():
            bbox_q.put({"face":face_boxes,"forhead":forhead_boxes,"landmark":landmark_points})

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run).start()
    while True:
        frame = frame_q.get(True,500)
        cv2.imshow("face",frame)
        cv2.waitKey(1)
