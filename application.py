from flask import Flask, render_template, request, session, redirect, flash, url_for
import boto3
import base64
import os
from application.forms import *
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin

application = Flask(__name__, static_url_path='')
admin_pass = os.environ.get('FACIAL_RECOGNITION_ADMIN_PASS', "default")
application.secret_key = os.environ.get('FLASK_APP_SECRET_KEY', str(os.urandom(16)))
rekognition = boto3.client("rekognition", "us-west-2")
login_manager = LoginManager()
login_manager.init_app(application)


@application.route('/')
def main_page():
    return render_template("index.html")


@application.route('/add_face')
@login_required
def add_face_page():
    return render_template("add_face.html")


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


class User(UserMixin):
    def get_id(self):
        self.id = "admin"
        return self.id


AdminUser = User()


@login_manager.user_loader
def load_user(user_id):
    return AdminUser


@login_manager.unauthorized_handler
def unauthorized():
    flash('Must be logged in first.')
    return login_page()


@application.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "admin" and form.password.data == admin_pass:
            login_user(AdminUser)
            return redirect(url_for('main_page'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login_page'))
    return render_template("login.html", form=form)


@application.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0")
