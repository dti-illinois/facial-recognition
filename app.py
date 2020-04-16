from flask import Flask, render_template, request, session
import boto3
import base64
import os

app = Flask(__name__, static_url_path='', static_folder='static/picojs')
app.secret_key = str(os.urandom(16))
rekognition = boto3.client("rekognition", "us-west-2")


@app.route('/')
def main_page():
    return render_template("index.html")


@app.route('/detect', methods=['POST'])
def detect_faces():
    # Send image to AWS Rekognition and process result
    output = ""
    try:
        response = rekognition.search_faces_by_image(
            Image={
                "Bytes": base64.b64decode(request.get_data()[22:])
            },
            CollectionId="arc-face-rec-test",
            FaceMatchThreshold=80,
        )

        for resp in response['FaceMatches']:
            face = resp['Face']
            output += "Face Detected: " + \
                face['ExternalImageId'] + ", Confidence: " + \
                str(face['Confidence']) + '<br>'
    except rekognition.exceptions.InvalidParameterException:
        # Catches exception when no faces are detected in the input image
        output = "None"

    return output


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
