from flask import Flask, render_template      
from flask import request
import sys
import threading
import cv2
import boto3
import requests
import base64
import numpy as np

# bower install tracking.js --save
# https://github.com/Tastenkunst/brfv5-browser.git
# export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

app = Flask(__name__, static_url_path='', static_folder='static/picojs')

@app.route('/')
def main_page():
    return render_template("index.html")

@app.route('/test')
def test_page():
    return render_template("index.html")

person = 'None'
@app.route('/person', methods=['POST'])
def process_person():
    global person
    person = str(request.data)
    sys.stderr.write(person + '\n\n')
    return person

@app.route('/person', methods=['GET'])
def return_person():
    return person

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
rekognition = boto3.client("rekognition", "us-west-2")
processing = False

def process_image(data):
    global person
    global processing
    encoded_data = data[22:]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    output = ""
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        response = rekognition.search_faces_by_image(
            Image={
                "Bytes": bytearray(cv2.imencode('.png', img[y:y + h, x:x + w])[1])
            },
            CollectionId="arc-face-rec-test",
            FaceMatchThreshold=80,
        )
        if len(response['FaceMatches']) == 0:
            print("Unrecognized face detected:")
            continue

        face = response['FaceMatches'][0]['Face']
        output += "Face Detected: " + face['ExternalImageId'] + ", Confidence: " + str(face['Confidence']) + '<br>'
    person = output
    sys.stderr.write(output + '\n\n')
    processing = False
    return output

@app.route('/detect', methods=['POST'])
def detect_faces():
    global processing
    if not processing:
        processing=True
        print("Recognizing Faces")
        th = threading.Thread(target=process_image, args=[request.get_data()])
        th.start()
    return "Success"

if __name__ == '__main__':
    app.run(debug=True, threaded=False)