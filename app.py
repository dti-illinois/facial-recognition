from flask import Flask
from flask import request
import sys

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"


person = 'Empty'
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
    app.run(debug=True)