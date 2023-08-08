import PySimpleGUI as sg
import cv2
import numpy as np


def main():
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
    result_col_1_item = [[sg.Text('Face',font=font_bold)],[sg.Text('average:',font=font),sg.Text('-',key='face_average',font=font)]]
    result_col_2_item = [[sg.Text('Forhead',font=font_bold)]]
    result_face = [
            [sg.Text('Face',font=font_bold)],
            [sg.Text('average:',font=font),sg.Text('-',key='face_average',font=font)],
            [sg.Text('highest:',font=font),sg.Text('-',key='face_highest',font=font)]
        ]
    result_forhead = [
        [sg.Text('Forhead',font=font_bold)],
        [sg.Text('average:',font=font),sg.Text('-',key='forhead_average',font=font)],
        [sg.Text('highest:',font=font),sg.Text('-',key='forhead_highest',font=font)]
    ]
    

    # define frame
    camera_frame_1 = sg.Frame("RGB Camera",cam_rgb)
    camera_frame_2 = sg.Frame("Flir Camera",cam_flir)
    # result_face_frame = sg.Frame("Temperature - Face",result_face)

    layout = [
             [camera_frame_1,camera_frame_2],
            #  [result_face_frame,result_forhead_frame],
             [sg.Text('Temperature'),sg.HorizontalSeparator(key='sep'),sg.Text('Setting',),sg.HorizontalSeparator(key='sep')],
              [sg.Button('Start', size=(10, 1), font=font),
               sg.Button('Stop', size=(10, 1), font=font),
               sg.Button('Exit', size=(10, 1), font=font), ]]
    
    can=sg.Canvas(size=(700,500), background_color='grey', key='canvas')

    # create the window and show it without the plot
    window = sg.Window('Demo Application - OpenCV Integration',
                       layout)

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(1)
    recording = False

    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            return

        elif event == 'Record':
            recording = True

        elif event == 'Stop':
            recording = False
            img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['frame_rgb'].update(data=imgbytes)
            window['frame_flir'].update(data=imgbytes)
            

        if recording:
            ret, frame = cap.read()
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['frame_rgb'].update(data=imgbytes)
            window['frame_flir'].update(data=imgbytes)


main()