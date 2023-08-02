import cv2
import numpy as np

try:
    import detection.utils as utils
    import device.FlirCamera as cam
except ImportError:
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import utils
    import device.FlirCamera as cam


def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def get_temp(frame):
    frame = cv2.resize(frame[:,:], (640, 480))
    frame = raw_to_8bit(frame)
    cv2.imshow("test flir",frame)
    cv2.waitKey(1)


def run():
    camera = cam.start(get_temp)

if __name__ == "__main__":
    run()
    