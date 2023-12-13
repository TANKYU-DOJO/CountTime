import cv2
import checker
import time
import PySimpleGUI as psg

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

print(startID)
print(endID)
 
startCam = checker.Checker(startID)
endCam = checker.Checker(endID)

startTime = 0
endTime = 0

status = 0 # 0=待機中, 1=始点を通過, 2=終点も通過

startCam.recording = True

while True:
    startCam.read()
    endCam.read()

    if status == 0:
        startCam.check()
        if not startCam.recording:
            startTime = time.time()
            status = 1
            endCam.recording = True
    elif status == 1:
        endCam.check()
        if not endCam.recording:
            endTime = time.time()
            status = 2

    if status == 2:
        cv2.imshow(
            "Start",
            cv2.putText(
                startCam.view(),
                str(endTime - startTime),
                (30, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
        )
    else:
        cv2.imshow("Start", startCam.view())
    
    cv2.imshow(
        "End",
        cv2.putText(
            endCam.view(),
            "Press Q to quit",
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
    )

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('r'):
        status = 0
        startCam.recording = True

cv2.destroyAllWindows()