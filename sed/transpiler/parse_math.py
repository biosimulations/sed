from sympy import symbols

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


math_grammar = Grammar(
    '''
    expression = term ((plus / minus) term)*
    term = factor ((times / slash) factor)*
    factor = (variable / number / left_paren expression right_paren) (caret expression)?
    variable = hash symbol
    symbol = ~r"[a-zA-Z0-9_.:]+"
    number = ~r"[0-9]+"
    hash = "#"
    plus = "+"
    minus = "-"
    times = "*"
    slash = "/"
    caret = "^"
    left_paren = "("
    right_paren = ")"
    '''
)


class MathVisitor(NodeVisitor):
    def __init__(self, variables):
        self.variables = variables
        self.allocate_index = 0
        self.symbols = dict(zip(
            self.variables,
            symbols(' '.join(self.variables))))
        self.path_symbols = {}
        self.symbol_paths = {}

    def visit_expression(self, node, visit):
        base = visit[0]
        sequence = visit[1]

        result = base
        if sequence:
            for step in sequence:
                operation = step[0][0]
                target = step[1]
                result = operation(result, target)

        return result

    def visit_term(self, node, visit):
        base = visit[0]
        sequence = visit[1:]
            
        result = base
        if sequence:
            for step in sequence[0]:
                operation = step[0][0]
                target = step[1]
                result = operation(result, target)

        return result

    def visit_factor(self, node, visit):
        base = visit[0][0]
        if isinstance(base, list):
            base = base[1]

        exponent = visit[1]

        result = base
        if exponent:
            operation = exponent[0][0]
            power = exponent[0][1]
            result = operation(base, power)

        return result

    def visit_variable(self, node, visit):
        return self.symbols[visit[1]]

    def visit_symbol(self, node, visit):
        path = tuple(node.text.split(':'))

        if path not in self.path_symbols:
            if self.allocate_index >= len(self.variables):
                raise Exception(f'all variables already allocated! no more for {path}')

            new_variable = self.variables[self.allocate_index]
            new_symbol = self.symbols[new_variable]
            self.allocate_index += 1

            self.path_symbols[path] = (new_variable, new_symbol)
            self.symbol_paths[new_variable] = path

        return self.path_symbols[path][0]

    def visit_number(self, node, visit):
        return float(node.text)

    def visit_plus(self, node, visit):
        return lambda x, y: x + y

    def visit_minus(self, node, visit):
        return lambda x, y: x - y

    def visit_times(self, node, visit):
        return lambda x, y: x * y

    def visit_slash(self, node, visit):
        return lambda x, y: x / y

    def visit_caret(self, node, visit):
        return lambda x, y: x ** y

    def visit_number(self, node, visit):
        return float(node.text)

    def generic_visit(self, node, visit):
        return visit


def visit_expression(expression, visitor):
    strip = expression.replace(' ', '')
    parsed = math_grammar.parse(strip)
    return visitor.visit(parsed)


def default_math_visitor():
    variables = ['a', 'b', 'c', 'd', 'e', 'x', 'y', 'z', 'w', 'i', 'j', 'k', 'm', 'n']
    visitor = MathVisitor(variables)
    return visitor


def parse_expression(expression):
    variables = ['a', 'b', 'c', 'd', 'e', 'x', 'y', 'z', 'w', 'i', 'j', 'k', 'm', 'n']
    visitor = MathVisitor(variables)
    return visit_expression(expression, visitor)


tests = [
    '(#tasks:sim1-#data:experiment1)^2',
    '((#x:y:z*#e:f:g:h)-(#y:z/#m:n:o*#k:l:m))^(#x:y+#a:b-#x:y:z)',
]


def test_math_parser():
    for test_string in tests:
        visitor = default_math_visitor()
        result = visit_expression(test_string, visitor)

        print(f"{test_string} --> {result}")
    

if __name__ == '__main__':
    test_math_parser()
