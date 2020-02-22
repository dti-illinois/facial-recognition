import cv2
import boto3
import requests


def detect_faces():
    face_cascade = cv2.CascadeClassifier('/Users/abhi/Documents/Projects/ARCFacialRecognition/faces/haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    rekognition = boto3.client("rekognition", "us-west-2")
    server_url = "http://127.0.0.1:5000/person"

    while True:
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        output = ""
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            # cv2.imshow('img', img[y:y + h, x:x + w])
            try:
                response = rekognition.search_faces_by_image(
                    Image={
                        "Bytes": bytearray(cv2.imencode('.jpg', img[y:y + h, x:x + w])[1])
                    },
                    CollectionId="arc-face-rec-test",
                    FaceMatchThreshold=80,
                )
                if len(response['FaceMatches']) == 0:
                    print("Unrecognized face detected:")
                    continue

                face = response['FaceMatches'][0]['Face']
                output += "Face Detected: " + face['ExternalImageId'] + ", Confidence: " + str(face['Confidence']) + '<br>'
            except rekognition.exceptions.InvalidParameterException:
                pass
            except Exception as e:
                print(e)
                pass
        
        try:
            print(output)
            requests.post(server_url, data=output)
        except requests.exceptions.ConnectionError:
            print('Server not available.')
        
        # k = cv2.waitKey(30) & 0xff
        # if k==27:
        #     break
    cap.release()

if __name__ == '__main__':
    detect_faces()