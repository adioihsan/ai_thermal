import cv2
import time
import configparser
import dlib
from deepface import DeepFace
from imutils import face_utils,resize
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

# parse config file
config = configparser.ConfigParser()
config.read("config.ini")
config_d = config["FaceDetection"]
FACE_DETECTOR = config_d["detector"]
SHOW_LANDMARK = config_d.getboolean("landmark")
print(SHOW_LANDMARK)

if FACE_DETECTOR == "dlib_hog":
    face_detector = dlib.get_frontal_face_detector()
elif FACE_DETECTOR == "dlib_cnn":
    face_detector = dlib.cnn_face_detection_model_v1('mmod_human_face_detector.dat')

def detect_face_dlib_hog(frame):
    gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    face_det = face_detector(gray_frame)
    face_boxes = [utils.convert_and_trim_bb(gray_frame, r) for r in face_det]
    return face_boxes

def detect_face_dlib_cnn(frame):
    rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    rgb_frame = resize(frame, width=600)
    face_det = face_detector(rgb_frame)
    face_boxes = [utils.convert_and_trim_bb(frame, r.rect) for r in face_det]
    return face_boxes

def detect_face_deepface_ssd(frame):
    face_dets = DeepFace.extract_faces(frame,align=False,detector_backend="ssd",enforce_detection=False)
    face_boxes = map(lambda detection:[i for i in detection['facial_area'].values()],face_dets)
    return list(face_boxes)


#detect face landmarks containt 68 points in x,y cordinate
landmark_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
def detect_landmark(frame,x,y,w,h):
    gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    face_ROI = dlib.rectangle(x,y,(x+w),(y+h))
    landmark = landmark_detector(gray_frame,face_ROI)
    landmark = face_utils.shape_to_np(landmark)
    return landmark

# locate forhead based on face_landmarks point
def detect_forhead(frame,face_box,landmark=None):
    forhead_ROI = []
    x,y,w,h = face_box
    if landmark is None:
        forhead_ROI = utils.forhead_ROI_static(x,y,w,h)
    else:
        xl1,yl1 = landmark[20]
        xl2,yl2 = landmark[23]
        forhead_ROI = utils.forhead_ROI_dynamic(xl1,yl1,xl2,yl2,h)
    return forhead_ROI

FACE_DETECTOR_DICT = {
    "dlib_cnn": detect_face_dlib_cnn,
    "dlib_hog": detect_face_dlib_hog,
    "deepface_ssd": detect_face_deepface_ssd
}

def run(q_frame,q_rois) :
    while True:
        frame = q_frame.get(True)
        face_boxes = FACE_DETECTOR_DICT[FACE_DETECTOR](frame)
        # initiate array
        forhead_boxes = []
        landmark_points = []
        for (x, y, w, h) in face_boxes:
            # detect face landmark
            if SHOW_LANDMARK:
                landmark = detect_landmark(frame,x,y,w,h)
                landmark_points.append(landmark)
                forhead = detect_forhead(frame,[x,y,w,h],landmark)
                forhead_boxes.append(forhead)
            else:
                forhead = detect_forhead(frame,[x,y,w,h])
                forhead_boxes.append(forhead)

        # put detections result into queue
        if not q_rois.full():
            q_rois.put({"face":face_boxes,"forhead":forhead_boxes,"landmark":landmark_points})
            
if __name__ == "__main__":
    from multiprocessing import Process , Queue
    from threading import Thread

    def show_cam(q_frame,q_rois):
        while True:
            frame = q_frame.get(True) 
            if not q_rois.empty():
                rval = q_rois.get(True)
                # face_bbox = rval.get("face")
                # landmark_point = rval.get("landmark")
                forhead_bboxes = rval.get("forhead")
                # utils.draw_face(frame,face_bbox)
                # utils.draw_landmark(frame,landmark_point)
                utils.draw_forhead(frame,forhead_bboxes)
            cv2.imshow("face",frame)
            key = cv2.waitKey(1)
            if key == 27:
                # camera.stop()
                # p.join()
                # p.kill()
                cv2.destroyAllWindows()
                exit()

    def load_frame(q_frame):
        camera = cam.Camera(1).start()
        while True:
            success,frame = camera.get_frame()
            q_frame.put(frame)

    q_rois = Queue(2)
    q_frame = Queue(2)
    
    p_frame = Process(target=load_frame,args=(q_frame,))
    p_cam = Process(target=show_cam,args=(q_frame,q_rois))
    p_face = Process(target=run,args=(q_frame,q_rois,))

    p_frame.start()
    p_cam.start()
    p_face.start()
    # p_face.start()
   
    # p_proc.start()
         
