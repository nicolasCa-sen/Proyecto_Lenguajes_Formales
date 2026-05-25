from components.ASTNode import ASTNode

class UnaryOpNode(ASTNode):
    def __init__(self, op, expr, line, column):
        self.op = op      # Operador unario ('not', '-', '+')
        self.expr = expr  # Expresión sobre la que actúa
        super().__init__(line, column)
