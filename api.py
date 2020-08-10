from flask import Flask, session
from flask_restx import Api, Resource
from datetime import datetime, timedelta
from flask_cors import CORS
from random import choice


from parsers import start_parser, letters_parser, numbers_parser, submit_parser
from constants import consonants, vowels
from anagram import get_anagrams
from oxford import get_definition, get_root

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)

app.secret_key = b'\xb3A\x942\x0fO\x91\x92\x7f\xf7$\xcf=\xa3\xe1R'


@api.route('/time')
class Time(Resource):
    def get(self):
        return {'time': str(datetime.now())}


@api.route('/start')
class Start(Resource):
    def post(self):
        args = start_parser.parse_args()
        session['round'] = args['round']
        session['time'] = datetime.now().isoformat()
        session.pop('letters', None)
        session.pop('numbers', None)
        return {'time': session['time']}


@api.route('/letters')
class Letters(Resource):
    def post(self):
        args = letters_parser.parse_args()
        letters = consonants if args['type'] == 'consonant' else vowels
        letters = list(letters.keys())
        letter = choice(letters)
        session['letters'] = letter if 'letters' not in session else session['letters'] + letter
        return {'letter': letter, 'all': session['letters']}


@api.route('/numbers')
class Numbers(Resource):
    def post(self):
        args = numbers_parser.parse_args()
        count = args['count']
        numbers = get_small_numbers(6 - count) + get_large_numbers(count)
        session['numbers'] = numbers
        return {'numbers': numbers}


@api.route('/submit')
class Submit(Resource):
    def post(self):
        time = datetime.strptime(session['time'], "%Y-%m-%dT%H:%M:%S.%f")
        if time < datetime.now() - timedelta(minutes=1):
            return {'status': 'expired'}

        args = submit_parser.parse_args()
        answer = args['answer']
        if session['round'] == 'letters':
            anagrams = get_anagrams(session['letters'])
            opponents_answer = choice(anagrams) if anagrams else ''
            response = check_letters(answer, opponents_answer)
        else:
            response = check_numbers(answer)
        session.clear()
        return response


def get_large_numbers(count: int):
    available = [25, 50, 75, 100]
    numbers = []
    for _ in range(count):
        number = choice(available)
        numbers.append(number)
        available.remove(number)
    return numbers


def get_small_numbers(count: int):
    available = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
    numbers = []
    for _ in range(count):
        number = choice(available)
        numbers.append(number)
        available.remove(number)
    return numbers


def check_letters(p1_answer: str, p2_answer: str):
    defn_1 = search_definition(p1_answer)
    defn_2 = search_definition(p2_answer)
    won = True
    if not defn_1:
        won = False
    if defn_2 and len(p2_answer) > len(p1_answer):
        won = False
    return {
        'answer1': p1_answer,
        'defn1': defn_1,
        'answer2': p2_answer,
        'defn2': defn_2,
        'won': won
    }


def search_definition(word: str):
    defn = get_definition(word)
    if not defn:
        root = get_root(word)
        if root and root != word:
            defn = get_definition(root)
    return defn


def check_numbers(answer: str):
    return 'won' if len(answer) > 0 else 'lost'


if __name__ == '__main__':
    app.run(debug=True)
