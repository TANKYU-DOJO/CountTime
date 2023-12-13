import numpy
import cv2

box_size = 32

class Checker:
    # カメラのIDを指定
    def __init__(self, deviceID) -> None:
        self.cap = cv2.VideoCapture(deviceID)
        self.frame = self.cap.read()[1]
        self.height, self.width, _ = self.frame.shape

        self.top = round(self.height / 2 - box_size / 2)
        self.bottom = round(self.height / 2 + box_size / 2)
        self.left = round(self.width / 2 - box_size / 2)
        self.right = round(self.width / 2 + box_size / 2)

        self.last_frame = self.frame[self.top:self.bottom, self.left:self.right]

        self.recording = False

    def read(self) -> None:
        self.frame = self.cap.read()[1]

    def check(self) -> None:
        pre_frame = self.frame[self.top:self.bottom, self.left:self.right]

        diff = cv2.absdiff(pre_frame, self.last_frame)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # To grayscale
        im_diff_bin = (diff > 32) * 255 # diffを2値化

        #平均して白か黒か判断
        if numpy.average(im_diff_bin) > 128:
            self.recording = False

        self.last_frame = pre_frame
    
    def view(self) -> cv2.Mat:
        return cv2.rectangle(
            self.frame,
            (self.left, self.top),
            (self.right, self.bottom),
            (0,0,255) if self.recording else (0, 255, 0)
        )