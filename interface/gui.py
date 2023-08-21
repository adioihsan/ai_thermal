import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import cv2
import numpy as np
from PIL import Image
import PySimpleGUI as sg
import psutil
import detection.utils as det_utils
from manager.process_manager import ProcessManager


def run():
    sg.theme('DarkTanBlue')
    # define globa layout setting
    font=("Arial",12)
    font_bold=("Arial Bold",12)
    font_med=("Arial",16)
    font_big=("Arial",21)
    cam_placeholder = "cam_placeholder.png"
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

    # extract process and queues
    pm = ProcessManager()
    p_frame_rgb,p_frame_flir,p_face,p_temperature = pm.get_all_processes()
    q_frame_rgb,q_frame_flir,q_rois,q_temp = pm.get_all_data()

    running = False
    while True:
        event, values = window.read(timeout=100)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            pm.terminate_all_processes()
            return

        elif event == 'Start':
            pm.start_all_processes()
            running = True

        elif event == 'Stop':
            running = False
            # this is faster, shorter and needs less includes
            p_face.terminate()
            p_frame_rgb.terminate()
            p_face.join()
            p_frame_rgb.join()
            window['frame_rgb'].update(filename=cam_placeholder)
            window['frame_flir'].update(filename=cam_placeholder)
            
        if running:
            rgb_frame = q_frame_rgb.get(True,500)
            # if len(rgb_frame) > 0:
            #         rois_dict = q_rois.get(True,500)
            #         face_bbox = rois_dict.get("face")
            #         landmark_point = rois_dict.get("landmark")
            #         forhead_bboxes = rois_dict.get("forhead")
            #         det_utils.draw_face(rgb_frame,face_bbox)
            #         det_utils.draw_landmark(rgb_frame,landmark_point)
            #         det_utils.draw_forhead(rgb_frame,forhead_bboxes)
            
            imgbytes_rgb = cv2.imencode('.ppm',rgb_frame)[1].tobytes()  
            window['frame_rgb'].update(data=imgbytes_rgb) 
                # print(len(rgb_frame))

            # flir_frame = cv2.resize(flir_frame[:,:], (640, 480))
            # flir_8_bit_frame = det_utils.raw_to_8bit(flir_frame)

            # det_utils.draw_face(flir_8_bit_frame,face_bbox,"flir")
            # det_utils.draw_landmark(flir_8_bit_frame,landmark_point,"flir")
            # det_utils.draw_forhead(flir_8_bit_frame,forhead_bboxes,"flir")

            # imgbytes_flir =  image_ppm(flir_8_bit_frame)
            # window['frame_flir'].update(data=imgbytes_flir)

            # temp_dict = q_temp.get(True)
            # face_temp = temp_dict.get("face")

            # if len(face_temp) != 0:
            #     window['face_highest'].update(face_temp[0])

if __name__ == "__main__":
    run()