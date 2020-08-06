from flask_restx import reqparse

start_parser = reqparse.RequestParser()
start_parser.add_argument('round', required=True, help="Round cannot be empty.")

letters_parser = reqparse.RequestParser()
letters_parser.add_argument('type', required=True, help="Type cannot be empty.")

numbers_parser = reqparse.RequestParser()
numbers_parser.add_argument('count', type=int, required=True, help="Count cannot be empty.")

submit_parser = reqparse.RequestParser()
submit_parser.add_argument('answer', required=True, help="Answer cannot be empty.")
