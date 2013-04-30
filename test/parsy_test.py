from parsy import string, regex, combine
import re
import pdb
import readline

whitespace = regex(r'\s+', re.MULTILINE)
comment = regex(r';.*')
ignore = (whitespace | comment).many()

lexeme = lambda p: p.skip(ignore)

lparen = lexeme(string('('))
rparen = lexeme(string(')'))
number = lexeme(regex(r'\d+')).map(int)
symbol = lexeme(regex(r'[\d\w_-]+'))
true   = lexeme(string('#t')).result(True)
false  = lexeme(string('#f')).result(False)

atom = true | false | number | symbol

@combine
def form():
    yield lparen
    els = yield expr.many()
    yield rparen
    return els

@combine
def quote():
    yield string("'")
    e = yield expr
    return ['quote', e]

expr = form | quote | atom

program = ignore.then(expr.many())

def test_form():
    result = program.parse('(1 2 3)')
    assert result == [[1, 2, 3]]

def test_quote():
    result = program.parse("'foo '(bar baz)")
    assert result == [['quote', 'foo'], ['quote', ['bar', 'baz']]]

def test_boolean():
    result = program.parse('#t #f')
    assert result == [True, False]

def test_comments():
    result = program.parse(
      """
      ; a program with a comment
      (           foo ; that's a foo
      bar )
      ; some comments at the end
      """
    )

    assert result == [['foo', 'bar']]