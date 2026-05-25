from components.ASTNode import ASTNode

class StringNode(ASTNode):
    def __init__(self, value, line, column):
        self.value = value  # Cadena de texto limpia (sin comillas)
        super().__init__(line, column)
