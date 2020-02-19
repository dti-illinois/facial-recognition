from flask import Flask, render_template      
from flask import request
import sys
import threading
from poll_sqs import poll

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template("display_faces.html")

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

if __name__ == '__main__':
    threading.Thread(target=poll, daemon=True).start()
    app.run(debug=True)