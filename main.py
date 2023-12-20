import cv2
import time
import PySimpleGUI as psg

import numpy
import cv2

box_size = 32

class Checker:
    # 第1引数: カメラのID
    # 第2引数: カメラの命名
    def __init__(self, deviceID: int, name: str) -> None:
        self.name = name
        self.cap = cv2.VideoCapture(deviceID)
        self.frame = self.cap.read()[1]
        self.height, self.width, _ = self.frame.shape

        self.top = round(self.height / 2 - box_size / 2)
        self.bottom = round(self.height / 2 + box_size / 2)
        self.left = round(self.width / 2 - box_size / 2)
        self.right = round(self.width / 2 + box_size / 2)

        self.last_frame = self.frame[self.top:self.bottom, self.left:self.right]

        self.recording = False

    def check(self) -> None:
        self.frame = self.cap.read()[1]
        pre_frame = self.frame[self.top:self.bottom, self.left:self.right]
        if self.recording:

            diff = cv2.absdiff(pre_frame, self.last_frame)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # To grayscale
            im_diff_bin = (diff > 32) * 255 # diffを2値化

            #平均して白か黒か判断
            if numpy.average(im_diff_bin) > 128:
                self.recording = False

        self.last_frame = pre_frame

        # 計測部分に矩形を描画
        self.frame = cv2.rectangle(
            self.frame,
            (self.left, self.top),
            (self.right, self.bottom),
            (0,0,255) if self.recording else (0, 255, 0)
        )

    def putText(self, text: str, pos, color) -> None:
        self.frame = cv2.putText(
            self.frame,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

    def imshow(self) -> None:
        cv2.imshow(self.name, self.frame)

startID = 0
endID = 0

layout = [
    [psg.Text("始点:"), psg.Input("0")],
    [psg.Text("終点:"), psg.Input("1")],
    [psg.Button("計測")]
]

window = psg.Window("デバイスIDを入力", layout)

while True:
    event, values = window.read()

    if event == "計測":
        startID = int(values[0])
        endID = int(values[1])
        break
    elif event == psg.WINDOW_CLOSED:
        quit()

window.close()

startCam = Checker(startID, "Start")
endCam = Checker(endID, "End")

startTime = 0
endTime = 0

status = 2 # 0=待機中, 1=始点を通過, 2=終点も通過

startCam.recording = False

while True:
    key = cv2.waitKey(1)
    if key == ord('r'):
            status = 0
            startCam.recording = True
            endCam.recording = False
    elif key == ord('q'):
        break

    startCam.check()
    endCam.check()

    if status == 0 and not startCam.recording:
        startTime = time.time()
        status = 1
        endCam.recording = True

    elif status == 1:
        endTime = time.time()
        if not endCam.recording:
            status = 2

    startCam.putText("Waiting..." if status == 0 else str(endTime - startTime), (30, 30), (0, 0, 255))

    endCam.putText("Press Q to quit", (30, 30), (0, 255, 0))
    
    if status != 0:
        endCam.putText("Press R to reset", (30, 60), (0, 255, 0))

    startCam.imshow()
    endCam.imshow()

cv2.destroyAllWindows()
