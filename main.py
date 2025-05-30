from fastapi import FastAPI
import pickle
import script
import csv
import datetime
from fastapi.responses import StreamingResponse
import cv2

with open('my_dict', 'rb') as f3:
    mydict = pickle.load(f3)

app = FastAPI()

@app.get('/output')
def output():
    anslist , count = script.main()

    # Save to CSV
    now = datetime.datetime.now()
    with open('parking_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now, count, anslist])

    return {'list': anslist, 'count': count}

def generate_video():
    cap = cv2.VideoCapture("carPark.mp4")
    while True:
        success, img = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        script.checkParkingSpace(imgDilate, img)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(generate_video(), media_type='multipart/x-mixed-replace; boundary=frame')
