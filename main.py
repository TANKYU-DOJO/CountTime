import numpy as np
import cv2
import time

box_size = 32
cap = cv2.VideoCapture(0)
status = 0 #0=ready,1=recording
frame = cap.read()[1]
height, width, _ = frame.shape
timer = 0
start_time = 0

top = round(height / 2 - box_size / 2)
bottom = round(height / 2 + box_size / 2)
left = round(width / 2 - box_size / 2)
right = round(width / 2 + box_size / 2)
last_frame = frame[top:bottom, left:right]

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    pre_frame = frame[top:bottom, left:right]
    diff = cv2.absdiff(pre_frame, last_frame)
    #to grayscale
    diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    #diffを2値化
    im_diff_bin = (diff > 32) * 255
    
    #平均して白か黒か判断
    if np.average(im_diff_bin) > 128:
        status = 0

    last_frame = pre_frame
    # Display the resulting frame
    if status == 0:
        view = cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0))
        view = cv2.putText(view, "Press S to start", (30, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if status == 1:
        view = cv2.rectangle(frame, (left, top), (right, bottom),(0,0,255))
        timer = time.time() - start_time

    view = cv2.putText(view, str(timer), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    view = cv2.putText(view, "Press Q to quit", (30, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('frame', view)
    k = cv2.waitKey(1)
    if k == 113:
        break
    if k ==115:
        status = 1
        start_time = time.time()

cv2.destroyAllWindows()