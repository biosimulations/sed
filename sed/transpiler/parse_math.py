from parsimonious.grammar import Grammar

grammar = Grammar(
    '''
    expression = group / operation
    group = left_paren expression right_paren
    operation = add / subtract / multiply / divide / exponent / variable / constant
    add = expression plus expression
    subtract = expression minus expression
    multiply = expression times expression
    divide = expression under expression
    exponent = expression caret expression
    variable = hash constant
    constant = ~r"[a-zA-Z0-9_.:]+"
    hash = "#"
    plus = "+"
    minus = "-"
    times = "*"
    under = "/"
    caret = "^"
    left_paren = "("
    right_paren = ")"
    '''
)


grammar = Grammar(
    '''
    atom = group / variable / constant
    group = left_paren expression right_paren
    expression = add_sub
    add_sub = mul_div ((plus / minus) mul_div)*
    mul_div = exponent ((times / under) exponent)*
    exponent = atom (caret exponent)?
    variable = hash constant
    constant = ~r"[a-zA-Z0-9_.:]+"
    hash = "#"
    plus = "+"
    minus = "-"
    times = "*"
    under = "/"
    caret = "^"
    left_paren = "("
    right_paren = ")"
    ''')


tests = {
    'example': '(#tasks:sim1-#data:experiment1)^2'}


def test_math_parser():
    for test_key, test_string in tests.items():
        print(grammar.parse(test_string))


if __name__ == '__main__':
    test_math_parser()
