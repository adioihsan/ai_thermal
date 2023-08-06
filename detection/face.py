import cv2
import dlib
import time
from imutils import face_utils
from queue import Queue

try:
    import detection.utils as utils
    import device.Rgb_cam as cam
except ImportError:        # if  not frame_q.full():
        #     frame_q.put(frame)
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import utils
    import device.Rgb_cam as cam


# cnn_detector = dlib.cnn_face_detection_model_v1('mmod_human_face_detector.dat')

def run(frame_q,ROIs_q) :
    face_detector = dlib.get_frontal_face_detector()
    landmark_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    while True:
        frame = frame_q.get(True)
    # detect face using dlib hog+svm linear
        gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        face_det = face_detector(gray_frame)

        #detec face using dlib cnn
        # rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        # rects = face_detector(rgb_frame)

        #get boxes
        face_boxes = [utils.convert_and_trim_bb(gray_frame, r) for r in face_det]
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
            forhead_boxes.append([xf,yf,wf,hf])

            #draw forhead
            # cv2.rectangle(frame,(xf,yf),(xf+wf,yf+hf),(0,255,0),2)
            
            #draw face landmarks
            # for(x,y) in landmarks:
            #     cv2.circle(frame,(x,y),2,(0,255,0),-1)

            # put things to queue
        if not ROIs_q.full():
            ROIs_q.put({"face":face_boxes,"forhead":forhead_boxes,"landmark":landmark_points})


if __name__ == "__main__":
    from multiprocessing import Process , Queue , Value, sharedctypes

    ROIs_q = Queue(2)
    frame_q = Queue(2)

    p = Process(target=run,args=(frame_q,ROIs_q,))
   
    p.start()

    def draw_face(frame,x,y,w,h):
         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
  
    camera = cam.RgbCamera(1).start()

    while True:
        success,frame = camera.get_frame()
        if success:
            frame_q.put(frame)
            if not ROIs_q.empty():
                rval = ROIs_q.get(True)
                face_bbox = rval.get("face")
                for (x, y, w, h) in face_bbox:
                        draw_face(frame,x,y,w,h)
            cv2.imshow("face",frame)
            key = cv2.waitKey(1)

            if key == 27:
                camera.stop()
                p.kill()
                cv2.destroyAllWindows()
                exit()
    # while True:
    #     success,pure_frame = camera.get_frame()
    #     if success:
    #         print(ROIs_q.get(True))
    #         # if not ROIs_q.empty():
    #         #     rval = ROIs_q.get(True)
    #         #     face_bbox = rval.get("face")
    #         #     for (x, y, w, h) in face_bbox:
    #         #          draw_face(pure_frame,x,y,w,h)
        
    #         cv2.imshow("face",pure_frame)
    #         key = cv2.waitKey(1)
    #         if key == 27:
    #             camera.stop()
    #             p.kill()
    #             cv2.destroyAllWindows()
    #             exit()

        # using calbacl
