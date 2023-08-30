import cv2
import time
import configparser
import dlib
from imutils import face_utils
import numpy as np

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

net = cv2.dnn.readNetFromCaffe("caffe/deploy.prototxt.txt", "caffe/res10_300x300_ssd_iter_140000.caffemodel")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

if FACE_DETECTOR == "dlib_hog":
    face_detector = dlib.get_frontal_face_detector()

def detect_face_dlib_hog(frame):
    gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    face_det = face_detector(gray_frame)
    face_boxes = [utils.convert_and_trim_bb(gray_frame, r) for r in face_det]
    return face_boxes

def detect_face_resnet_ssd(frame):
    blob = cv2.dnn.blobFromImage(
    cv2.resize(frame, (300, 300)),
    1.0,
    (300, 300),
    (104.0, 177.0, 123.0)
    )
    net.setInput(blob)
    detections = net.forward()

    # overlay
    detections = np.squeeze(detections)
    face_boxes = utils.get_ssd_bbox(frame,detections)
    return face_boxes

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
    "dlib_hog": detect_face_dlib_hog,
    "resnet_ssd": detect_face_resnet_ssd,
}

def run(q_frame,q_rois):
    while True:
        frame = q_frame.get(True,500)
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

        if not q_rois.full():
            q_rois.put({"face":face_boxes,"forhead":forhead_boxes,"landmark":landmark_points},500)
            
if __name__ == "__main__":
    from device import Rgb_cam
    rgb_cam =  Rgb_cam.Camera()
    while True:
        success,frame = rgb_cam.get_frame()
        if not success:
            break

        frame = frame[0:960,0:720]
        cv2.resize(frame,(640,480))
        face,forhead,landmark = run(frame).values()

        utils.draw_face(frame,face)

        print(face)

        cv2.imshow("face",frame)
        key = cv2.waitKey(1)

        if key == "q":
            rgb_cam.stop()
            break
    

        
         
