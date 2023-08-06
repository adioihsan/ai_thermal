import cv2
import dlib
import time
from imutils import face_utils
from queue import Queue

try:
    import detection.utils as utils
    import device.Rgb_cam as cam
except ImportError:        
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import utils
    import device.Rgb_cam as cam

# detect face using dlib hog+svm linear
face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
def detect_face_hog(frame):
    gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    face_det = face_detector(gray_frame)
    face_boxes = [utils.convert_and_trim_bb(gray_frame, r) for r in face_det]
    return face_boxes

# detect face using dlib cnn
cnn_detector = dlib.cnn_face_detection_model_v1('mmod_human_face_detector.dat')
def detect_face_cnn(frame):
        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        face_det = face_detector(rgb_frame)
        face_boxes = [utils.convert_and_trim_bb(frame, r) for r in face_det]
        return face_boxes


#detect face landmarks containt 68 points in x,y cordinate
def detect_landmark(frame,x,y,w,h):
        gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        face_ROI = dlib.rectangle(x,y,(x+w),(y+h))
        landmark = landmark_detector(gray_frame,face_ROI)
        landmark = face_utils.shape_to_np(landmark)
        return landmark

# locate forhead based on face_landmarks point
def detect_forhead(frame,landmarks,face_height):
        xl1,yl1 = landmarks[20]
        xl2,yl2 = landmarks[23]
        forhead_ROI = utils.forhead_ROI_dynamic(xl1,yl1,xl2,yl2,face_height)
        xf,yf,wf,hf = forhead_ROI
        return forhead_ROI


def run(frame_q,rois_q) :
    while True:
        frame = frame_q.get(True)
        face_boxes = detect_face_cnn(frame)
        # initiate array
        forhead_boxes = []
        landmark_points = []
        for (x, y, w, h) in face_boxes:
            # detect face landmark
            landmark = detect_landmark(frame,x,y,w,h)
            landmark_points.append(landmark)

            # detect forhead 
            forhead = detect_forhead(frame,landmark,h)
            forhead_boxes.append(forhead)

        # put detections result into queue
        if not rois_q.full():
            rois_q.put({"face":face_boxes,"forhead":forhead_boxes,"landmark":landmark_points})


if __name__ == "__main__":
    from multiprocessing import Process , Queue , Value, sharedctypes

    ROIs_q = Queue(2)
    frame_q = Queue(2)

    p = Process(target=run,args=(frame_q,ROIs_q,))
   
    p.start()

  
    camera = cam.RgbCamera(1).start()

    while True:
        success,frame = camera.get_frame()
        if success:
            frame_q.put(frame)
            if not ROIs_q.empty():
                rval = ROIs_q.get(True)
                # face_bbox = rval.get("face")
                # landmark_point = rval.get("landmark")
                forhead_bboxes = rval.get("forhead")
                # utils.draw_face(frame,face_bbox)
                # utils.draw_landmark(frame,landmark_point)
                utils.draw_forhead(frame,forhead_bboxes)
                
            cv2.imshow("face",frame)
            key = cv2.waitKey(1)

            if key == 27:
                camera.stop()
                p.kill()
                cv2.destroyAllWindows()
                exit()
