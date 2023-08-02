import cv2
import sys
import os

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

def forhead_ROI_static(x,y,w,h):
    ROI_x = round(x + 2*(w/6))
    ROI_y =round(y + 2*(h/9))
    ROI_w = round(2*(w/6))
    ROI_h = round(h/9)
    return [ROI_x,ROI_y,ROI_w,ROI_h]

def forhead_ROI_dynamic(x1,y1,x2,y2):
	ROI_x = x1
	ROI_y = y1-14
	ROI_w = x2-x1
	ROI_h  = 14
	return [ROI_x,ROI_y,ROI_w,ROI_h]

# def draw_rectangle(frame,x,y,w,h):
      