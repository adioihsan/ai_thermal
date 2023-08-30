import cv2
import sys
import os
import numpy as np

def import_from_parent():
    # getting the name of the directory
    # where the this file is present.
    current = os.path.dirname(os.path.realpath(__file__))
    
    # Getting the parent directory name
    # where the current directory is present.
    parent = os.path.dirname(current)
    
    # adding the parent directory to
    # the sys.path.
    sys.path.append(parent)


def convert_and_trim_bb(image, rect):
	# extract the starting and ending (x, y)-coordinates of the
	# bounding box
	startX = rect.left()
	startY = rect.top()
	endX = rect.right()
	endY = rect.bottom()
	# ensure the bounding box coordinates fall within the spatial
	# dimensions of the image
	startX = max(0, startX)
	startY = max(0, startY)
	endX = min(endX, image.shape[1])
	endY = min(endY, image.shape[0])
	# compute the width and height of the bounding box
	w = endX - startX
	h = endY - startY
	# return our bounding box coordinates
	return (startX, startY, w, h)

def get_ssd_bbox(frame,detections):
		# loop over the detections
	h, w = frame.shape[:2]
	scores = detections[:,2]

	boxes = []

	for (_, _, score, x1, y1, x2, y2) in detections[scores > 0.5]:
		
		# scale box
		box = np.array([x1, y1, x2, y2]) * np.array([w, h, w, h])
		
		# cast to int
		(x1, y1, x2, y2) = box.astype("int")
		boxes.append([x1,y1,x2-x1,y2-y1])
	return boxes
		

def forhead_ROI_static(x,y,w,h):
    ROI_x = round(x + 2*(w/6))
    ROI_y =round(y + 2*(h/10))
    ROI_w = round(2*(w/6))
    ROI_h = round(h/10)
    return [ROI_x,ROI_y,ROI_w,ROI_h]

def forhead_ROI_dynamic(x1,y1,x2,y2,face_height):
	#(x1,y1) is a point above left eyebrow and x2,y2 is a point above right eyebrow
	ROI_h  = int( face_height/10 )
	ROI_x = x1
	ROI_y = y1-ROI_h
	ROI_w = x2-x1
	return [ROI_x,ROI_y,ROI_w,ROI_h]

#  to draw face and forhead box
def draw_box(frame,x,y,w,h):
	cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

def draw_face(frame,face_bboxes,cam_name=None):
	# if len 
	for (x, y, w, h) in face_bboxes:
		if cam_name == "flir":
			x= x-50
			y= y+10
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
def draw_landmark(frame,landmarks,cam_name=None):
	for landmark in landmarks:
		for(x,y) in landmark:
			if cam_name == "flir":
				x= x-50
				y= y+10
			cv2.circle(frame,(x,y),2,(0,255,0),-1)

def draw_forhead(frame,forhead_bboxes,cam_name=None):

	for forhead in forhead_bboxes:
		x,y,w,h = forhead
		if cam_name == "flir":
			x= x-50
			y= y+10
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		   
def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def conv_169(frame):

	target_aspect_ratio = 4 / 3
		# Get the dimensions of the input image
	height, width = frame.shape[:2]

	# Calculate the new width based on the target aspect ratio
	new_width = int(height * target_aspect_ratio)

	# Resize the image while maintaining the aspect ratio
	resized_image = cv2.resize(frame, (new_width, height))

	# Calculate the width padding needed for 4:3 aspect ratio
	padding = (new_width - width) // 2

	# Crop the resized image to get the final 4:3 aspect ratio
	final_frame = resized_image[:, padding:padding+width]

	# Save the final image
	return final_frame

def draw_temp(frame,face_bboxes,text,cam_name):
	for (x, y, w, h) in face_bboxes:
		if cam_name == "flir":
			x= x-50
			y= y+10
		cv2.putText(  
			img = frame,
			text = text,
			org = (x,y),
			fontFace = cv2.FONT_HERSHEY_DUPLEX,
			fontScale = 1,
			color = (125, 246, 55),
			thickness = 1)



# def draw_rectangle(frame,x,y,w,h):
      