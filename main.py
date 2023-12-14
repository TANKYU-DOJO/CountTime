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

window.close()

startCam = checker.Checker(startID)
endCam = checker.Checker(endID)

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

    startView = startCam.view()

    if status == 0 and not startCam.recording:
        startTime = time.time()
        status = 1
        endCam.recording = True

    elif status == 1:
        endTime = time.time()
        if not endCam.recording:
            status = 2

    startView = cv2.putText(
        startView,
        "Waiting..." if status == 0 else str(endTime - startTime),
        (30, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    cv2.imshow("Start", startView)
    cv2.imshow(
        "End",
        cv2.putText(
            endCam.view(),
            #"Press Q to quit",
            str(status),
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
    )

cv2.destroyAllWindows()
