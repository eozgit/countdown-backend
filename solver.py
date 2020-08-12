from itertools import combinations
from random import randint
from attr import attrs


@attrs(auto_attribs=True, repr=False)
class Step:
    operation: str
    value: int

    def __repr__(self):
        return self.operation


class Solver:
    def __init__(self, numbers: list, target: int, away: int):
        self.wrappers = [Step(str(number), number) for number in numbers]
        self.target = target
        self.solutions = []
        self.default_away = away

    def solve(self):
        path = []
        self.recurse(self.wrappers, path)
        return self.solutions

    def recurse(self, wrappers: list, path: list):
        if self.solutions:
            return
        pairs = combinations(wrappers, 2)
        for pair in pairs:
            a = pair[0]
            b = pair[1]
            if b.value > a.value:
                a, b = b, a

            if a.value != 0 and b.value != 0 and self.should_include(len(path)):
                self.execute(a, b, self.add, "{} + {}", wrappers, path)

            if b.value != 0 and self.should_include(len(path)):
                self.execute(a, b, self.subtract, "{} - {}", wrappers, path)

            if a.value != 0 and b.value != 0 and a.value != 1 and b.value != 1 and self.should_include(len(path)):
                self.execute(a, b, self.multiply, "{} * {}", wrappers, path)

            if b.value != 0 and a.value != 1 and b.value != 1 and a.value % b.value == 0 and self.should_include(len(path)):
                self.execute(a, b, self.divide, "{} / {}", wrappers, path)

    def execute(self, a: Step, b: Step, op, tmpl: str, wrappers: list, path: list):
        if self.solutions:
            return
        c = op(a, b)
        away = abs(c - self.target)
        path_copy = path.copy()
        s = tmpl.format(int(a.value), int(b.value))
        step = Step(s, c)
        path_copy.append(step)
        if away == self.default_away:
            steps = ', '.join(
                [f"{repr(path)} = {int(path.value)}" for path in path_copy])
            self.solutions.append(Solution(steps, away))
            return
        if len(wrappers) > 2:
            wrappers_copy = wrappers.copy()
            wrappers_copy.remove(a)
            wrappers_copy.remove(b)
            wrappers_copy.append(step)
            self.recurse(wrappers_copy, path_copy)

    def add(self, a: int, b: int):
        return a.value + b.value

    def subtract(self, a: int, b: int):
        return a.value - b.value

    def multiply(self, a: int, b: int):
        return a.value * b.value

    def divide(self, a: int, b: int):
        return a.value / b.value

    def should_include(self, depth: int):
        inverse = 5 - depth
        away = self.default_away + 1
        return randint(0, 100) > 25 + inverse * away


@attrs(auto_attribs=True)
class Solution:
    steps: str
    away: int
