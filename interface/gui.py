import PySimpleGUI as sg
import cv2
import numpy as np
from PIL import Image
import detection.utils as det_utils


def image_ppm(path,width=640,height=480):
    img = Image.fromarray(path)
    ppm = ('P6 %d %d 255 ' % (width, height)).encode('ascii') + img.tobytes()
    
    return ppm

def run(q_frame_rgb,q_frame_flir,q_rois,q_temp):
    sg.theme('DarkTanBlue')
    # define globa layout setting
    font=("Arial",12)
    font_bold=("Arial Bold",12)
    font_med=("Arial",16)
    font_big=("Arial",21)
    # define elements
        #camera el
    cam_rgb= [[sg.Text('FPS:',font=font)],[sg.Image(filename='cam_placeholder.png', key='frame_rgb')]]
    cam_flir= [[sg.Text('FPS:',font=font)],[sg.Image(filename='cam_placeholder.png',key='frame_flir')]]

        # result el
    # result_col_1_item = [[sg.Text('Face',font=font_bold)],[sg.Text('average:',font=font),sg.Text('-',key='face_average',font=font)]]
    # result_col_2_item = [[sg.Text('Forhead',font=font_bold)]]
    result_face = [
            [sg.Text('average:',font=font),sg.Text('-',key='face_average',font=font)],
            [sg.Text('highest:',font=font),sg.Text('-',key='face_highest',font=font)]
        ]
    result_forhead = [
        [sg.Text('average:',font=font),sg.Text('-',key='forhead_average',font=font)],
        [sg.Text('highest:',font=font),sg.Text('-',key='forhead_highest',font=font)]
    ]
    

    # define frame
    camera_frame_1 = sg.Frame("RGB Camera",cam_rgb)
    camera_frame_2 = sg.Frame("Flir Camera",cam_flir)
    result_face_frame = sg.Frame("Face",result_face)
    result_forhead_frame = sg.Frame("Forhead",result_forhead)

    layout = [
             [camera_frame_1,camera_frame_2],
             [sg.Text('Temperature'),sg.HorizontalSeparator(key='sep'),sg.Text('Setting',),sg.HorizontalSeparator(key='sep')],
             [result_face_frame,result_forhead_frame],
             [sg.Button('Start', size=(10, 1), font=font),
               sg.Button('Stop', size=(10, 1), font=font),
               sg.Button('Exit', size=(10, 1), font=font), ]]
    
    can=sg.Canvas(size=(700,500), background_color='grey', key='canvas')

    # create the window and show it without the plot
    window = sg.Window('Temperature Cam',
                       layout)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(1)
    recording = False

    while True:
        event, values = window.read(timeout=20)
        rgb_frame = q_frame_rgb.get(True)
        flir_frame = q_frame_flir.get(True)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            return

        elif event == 'Start':
            recording = True

        elif event == 'Stop':
            recording = False
            img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['frame_rgb'].update(data=imgbytes)
            window['frame_flir'].update(data=imgbytes)
            

        if recording:
            rois_dict = q_rois.get(True)
            face_bbox = rois_dict.get("face")
            landmark_point = rois_dict.get("landmark")
            forhead_bboxes = rois_dict.get("forhead")
            #draw into frame
            det_utils.draw_face(rgb_frame,face_bbox)
            det_utils.draw_landmark(rgb_frame,landmark_point)
            det_utils.draw_forhead(rgb_frame,forhead_bboxes)

            # if not q_frame_rgb.empty():
            # imgbytes_rgb = cv2.imencode('.png', rgb_frame)[1].tobytes()
            imgbytes_rgb = image_ppm(rgb_frame)
            window['frame_rgb'].update(data=imgbytes_rgb) 

            flir_frame = cv2.resize(flir_frame[:,:], (640, 480))
            flir_8_bit_frame = det_utils.raw_to_8bit(flir_frame)

            det_utils.draw_face(flir_8_bit_frame,face_bbox,"flir")
            det_utils.draw_landmark(flir_8_bit_frame,landmark_point,"flir")
            det_utils.draw_forhead(flir_8_bit_frame,forhead_bboxes,"flir")

            imgbytes_flir =  image_ppm(flir_8_bit_frame)
            window['frame_flir'].update(data=imgbytes_flir)

            temp_dict = q_temp.get(True)
            face_temp = temp_dict.get("face")
            if len(face_temp) != 0:
                window['face_highest'].update(face_temp[0])
        
            

if __name__ == "__main__":
    run()