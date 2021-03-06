from flask import Flask, session, send_from_directory, abort
from flask_restx import Api, Resource
from datetime import datetime, timedelta
from flask_cors import CORS
from random import choice, random, randint
from os import environ
import re

from parsers import start_parser, letters_parser, numbers_parser, submit_parser
from constants import consonants, vowels
from anagram import get_anagrams
from oxford import get_definition, get_root
from solver import Solver, Solution

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)

app.secret_key = environ['secret_key']


@app.route('/dist/<path:path>')
def send_js(path):
    return send_from_directory('dist', path)


@api.route('/time')
class Time(Resource):
    def get(self):
        return {'time': str(datetime.now())}


@api.route('/solve/<int:count>/<int:away>')
class Solve(Resource):
    def get(self, count, away):
        numbers = get_small_numbers(6 - count) + get_large_numbers(count)
        target = randint(101, 999)
        solutions = Solver(numbers, target, away).solve()
        arr = [{'steps': soln.steps, 'away': soln.away} for soln in solutions]
        resp = {'numbers': numbers, 'target': target, 'solutions': arr}
        return resp


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
        is_consonant = args['type'] == 'consonant'
        letters_initd = 'letters' in session

        if letters_initd:
            selected_letters = session['letters']
            left = 9 - len(selected_letters)
            if is_consonant:
                vowel_count = len(
                    [letter for letter in selected_letters if letter in vowels.keys()])
                required_vowel_count = max([3 - vowel_count, 0])
                if required_vowel_count >= left:
                    abort(400, "Must choose vowel")
            else:
                consonant_count = len(
                    [letter for letter in selected_letters if letter in consonants.keys()])
                required_consonant_count = max([4 - consonant_count, 0])
                if required_consonant_count >= left:
                    abort(400, "Must choose consonant")

        letter = self.get_letter(is_consonant)
        session['letters'] = letter if not letters_initd else session['letters'] + letter
        return {'letter': letter, 'all': session['letters']}

    def __init__(self, api=None, *args, **kwargs):
        self.set_consonant_cumulative_freqs()
        self.set_vowel_cumulative_freqs()

    def get_letter(self, is_consonant: bool):
        letters = self.consonants if is_consonant else self.vowels
        n = random()
        l = [item for item in letters.items() if item[1] >= n]
        return min(l, key=lambda item: item[1])[0]

    def set_consonant_cumulative_freqs(self):
        self.consonants = {}
        sum = 0
        for (letter, freq) in consonants.items():
            sum += freq
            self.consonants[letter] = sum
        for letter in self.consonants.keys():
            self.consonants[letter] /= sum

    def set_vowel_cumulative_freqs(self):
        self.vowels = {}
        sum = 0
        for (letter, freq) in vowels.items():
            sum += freq
            self.vowels[letter] = sum
        for letter in self.vowels.keys():
            self.vowels[letter] /= sum


@api.route('/numbers')
class Numbers(Resource):
    def post(self):
        args = numbers_parser.parse_args()
        count = args['count']
        numbers = get_small_numbers(6 - count) + get_large_numbers(count)
        target = randint(101, 999)
        session['numbers'] = numbers
        session['target'] = target
        return {'numbers': numbers, 'target': target}


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
            numbers = session['numbers']
            target = session['target']
            target_away = randint(0, 9)
            solutions = Solver(numbers, target, target_away).solve()
            response = check_numbers(answer, solutions[0])
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


def check_numbers(p1_answer: str, p2_answer: Solution):
    response = {
        'answer1': '-',
        'away1': '-',
        'answer2': p2_answer.steps,
        'away2': p2_answer.away,
        'won': False
    }

    p = re.compile(r"^[\d\s\+\*\/\(\)=-]+$")
    if not p.match(p1_answer):
        return response

    d = re.compile(r'\d+')
    no = d.findall(p1_answer)
    numbers = session['numbers']
    for n in no:
        m = int(n)
        if m not in numbers:
            return response
        numbers.remove(m)

    answer = eval(p1_answer)
    target = session["target"]
    away = abs(target - answer)
    response['answer1'] = f"{p1_answer} = {answer}"
    response['away1'] = away
    if away <= p2_answer.away:
        response['won'] = True

    return response


if __name__ == '__main__':
    app.run(debug=True)
