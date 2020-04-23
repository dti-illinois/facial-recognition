from flask import Flask, render_template, request, session
import boto3
import base64
import os

application = Flask(__name__, static_url_path='')
application.secret_key = str(os.urandom(16))
rekognition = boto3.client("rekognition", "us-west-2")


@application.route('/')
def main_page():
    return render_template("index.html")


@application.route('/login')
def login_page():
    return render_template("login.html")


@application.route('/detect', methods=['POST'])
def detect_faces():
    # Send image to AWS Rekognition and process result
    output = ""
    faceImages = str(request.get_data()).split("data:image/png;base64,")
    for i in range(1, len(faceImages)):
        try:
            response = rekognition.search_faces_by_image(
                Image={
                    "Bytes": base64.b64decode(str.encode(faceImages[i]))
                },
                CollectionId="arc-face-rec-test"
            )

            if len(response['FaceMatches']) == 0:
                output = "Unrecognized Face<br>"
                continue

            resp = response['FaceMatches'][0]
            output += resp['Face']['ExternalImageId'] + \
                ", Similarity: " + str(resp['Similarity']) + '<br>'
        except rekognition.exceptions.InvalidParameterException:
            # Catches exception when no faces are detected in the input image
            output = "Recognition did not detect face<br>"

    return output


if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0")
