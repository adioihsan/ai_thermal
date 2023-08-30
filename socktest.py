import cv2
import base64
import socketio

# create a Socket.IO server
sio = socketio.Server()

# wrap with a WSGI application
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ, auth):
    print('connect ', sid)



def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=2
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink drop=True"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
# activate multiserver_mode

def send_frame(socketio,frame,port):
        # ret, buffer = cv2.imencode('.jpg', frame)
        frame_buffer = cv2.imencode('.jpg', frame)[1].tobytes()
        stream_frame =  base64.encodebytes(frame_buffer).decode("utf-8")
        if port == "5577":
            socketio.emit("rgb_video",stream_frame)
        if port == "5578":
             socketio.emit("flir_video",stream_frame)
        socketio.sleep(0)

# loop over until Keyboard Interrupted
cap = cv2.VideoCapture(1)
while True:
    ret,frame = cap.read()
    try:
        # check for frame if Nonetype
        if not ret:
            break

        # let's prepare a text string as data
        send_frame(sio,frame,"5577")
        # send frame and data through server
        

    except KeyboardInterrupt:
        break
    



# safely close server
cap.release()


        
