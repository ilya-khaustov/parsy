from parsy import string, regex, generate
import re
from sys import stdin

whitespace = regex(r'\s*', re.MULTILINE)

lexeme = lambda p: p << whitespace

rb_left = lexeme(string('('))
rb_right = lexeme(string(')'))
comma = lexeme(string(','))
true = lexeme(string('true')).result(True)
false = lexeme(string('false')).result(False)
null = lexeme(string('null')).result(None)

number = lexeme(
  regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
).map(float)

def resolve(varname):
  return {
    'x': lambda: 1,
    'y': lambda: 2,
    'sum': lambda x, y: x+y
  }.get(varname)

variable = lexeme(
  regex(r'([a-zA-Z0-9_]+)')
).map(resolve)

string_part = regex(r'[^"\\]+')
string_esc = string('\\') >> (
  string('\\')
  | string('/')
  | string('b').result('\b')
  | string('f').result('\f')
  | string('n').result('\n')
  | string('r').result('\r')
  | string('t').result('\t')
  | regex(r'u[0-9a-fA-F]{4}').map(lambda s: chr(int(s[1:], 16)))
)

@lexeme
@generate
def quoted():
    yield string('"')
    body = yield (string_part | string_esc).many()
    yield string('"')
    return ''.join(body)

@generate
def args():
    yield rb_left
    first = yield value
    other = yield (comma >> value).many()
    yield rb_right
    other.insert(0, first)
    return other

@generate
def expression():
    func = yield variable
    fargs = yield args
    if callable(func):
      return func(*(arg() if callable(arg) else arg for arg in fargs))

value = expression | args | variable | quoted | number | true | false | null

func = whitespace >> value

if __name__ == '__main__':
    print(repr(func.parse(stdin.read())))
