from flask import Flask, session
from flask_restx import Api, Resource
from datetime import datetime
from random import choice

from parsers import start_parser, letters_parser
from constants import consonants, vowels

app = Flask(__name__)
api = Api(app)

app.secret_key = b'\xb3A\x942\x0fO\x91\x92\x7f\xf7$\xcf=\xa3\xe1R'

@api.route('/time')
class Time(Resource):
    def get(self):
        return { 'time': str(datetime.now()) }

@api.route('/start')
class Start(Resource):
    def post(self):
        args = start_parser.parse_args()
        session['round'] = args['round']
        session['time'] = str(datetime.now())
        return { 'time': session['time'] }

@api.route('/letters')
class Letters(Resource):
    def post(self):
        args = letters_parser.parse_args()
        letter_type = args['type']
        letters = list(consonants.keys())
        return { 'letter': choice(letters) }

if __name__ == '__main__':
    app.run(debug=True)
