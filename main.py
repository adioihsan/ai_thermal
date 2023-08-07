import cv2
from config import *
import detection.utils as det_utils
from detection import face
from device import Rgb_cam
from multiprocessing import Process , Queue


# create queue for data exchange
q_frame_rgb = Queue(2)
q_rois = Queue(2)  # queue for bounding boxes (face,forhead and face landmark) 

# create process for face detection
p_face = Process(target=face.run,args=(q_frame_rgb,q_rois,))
# p_temperature = Process()

# process to load frame
def load_rgb_frame(q_frame_rgb):
    rgb_cam =  Rgb_cam.Camera(1).start()
    while True:
        success,frame = rgb_cam.get_frame()
        if not success:
            break
        if  not q_frame_rgb.full():
            q_frame_rgb.put(frame)

p_rgb_frame = Process(target=load_rgb_frame,args=(q_frame_rgb,))

# get frame
def run():
    p_rgb_frame.start()
    p_face.start()
    running = True
    while running:
        rgb_frame = q_frame_rgb.get(True,500)
        #get ROIs from face detection process
        if not  q_rois.empty():
            # get rois from face module process
            rois_dict = q_rois.get(True)
            face_bbox = rois_dict.get("face")
            landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")
            #draw into frame
            det_utils.draw_face(rgb_frame,face_bbox)
            det_utils.draw_landmark(rgb_frame,landmark_point)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

        if SHOW_VIEW:
            cv2.imshow("face",rgb_frame)
            key = cv2.waitKey(1)
            # press esc to stop
            if key == 27:

                p_rgb_frame.kill()
                p_face.kill()
                cv2.destroyAllWindows()
                exit()


if __name__ == "__main__":
    run()
