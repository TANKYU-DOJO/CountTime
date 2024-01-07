import cv2
import time
from tkinter import messagebox
import PySimpleGUI as psg
import numpy

box_size = 32

def putText(image, text, pos, color):
    return cv2.putText(image, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

# 物体通過検知用クラス
class Checker:

    def __init__(self, cap, name: str) -> None:
        """
        第1引数: カメラのインスタンス
        第2引数: カメラの命名
        """
        self.name = name
        self.cap = cap
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
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # グレースケールに
            im_diff_bin = (diff > 32) * 255 # diffを2値化

            if numpy.average(im_diff_bin) > 128: #平均して白か黒か判断
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
        self.frame = putText(self.frame, text, pos, color)

    def imshow(self) -> None:
        cv2.imshow(self.name, self.frame)

cam = []
for i in range(10): # カメラをポート0~10まで開く試行
    cap = cv2.VideoCapture(i)
    if cap.read()[0]:
        cam.append(cap)

startID = 0 # 始点カメラID
endID = 1 # 終点カメラID

def selectCam() -> int:
    """カメラの選択"""

    viewing = 0
    while True:
        frame = cam[viewing].read()[1]
        frame = putText(frame, "Press C to change camera", (30, 30), (0, 255, 0))
        frame = putText(frame, "Press S to select this camera", (30, 60), (0, 255, 0))
        cv2.imshow("Select camera", frame)

        key = cv2.waitKey(1)
        if key == ord('c'):
            viewing = (viewing + 1) % len(cam)
        elif key == ord('s'):
            cv2.destroyAllWindows()
            return viewing

unselected = "未選択"
selectStartCam = "始点カメラを選択"
selectEndCam = "終点カメラを選択"
layout = [
    [psg.Button(selectStartCam), psg.Text("ID:"), psg.Input(unselected)],
    [psg.Button(selectEndCam), psg.Text("ID:"), psg.Input(unselected)],
    [psg.Text("計測部分の大きさ:"), psg.Input(str(box_size))],
    [psg.Button("計測!")]
]

window = psg.Window("デバイスIDを入力", layout)

startCam = 0
endCam = 0

while True:
    event, values = window.read()

    if event == selectStartCam:
        window[0].update(str(selectCam()))
    elif event == selectEndCam:
        window[1].update(str(selectCam()))
    elif event == "計測!":
        try:
            startID = int(values[0])
            endID = int(values[1])
            box_size = int(values[2])
        except:
            messagebox.showerror("ERROR", "数字を入力してください。")
            continue

        if startID == endID:
            messagebox.showerror("ERROR", "始点カメラIDと終点カメラIDが同じです。")

        else:
            try:
                startCam = Checker(cam[startID], "Start")
                endCam = Checker(cam[endID], "End")
            except:
                messagebox.showerror("ERROR", "カメラIDの範囲外です。")
                continue
            break
    elif event == psg.WINDOW_CLOSED:
        quit()

window.close()

# 使用していないカメラを閉じる
for i in range(len(cam)):
    if i != startID and i != endID:
        cam[i].release()

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
