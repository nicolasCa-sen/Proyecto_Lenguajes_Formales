from components.ASTNode import ASTNode

class BooleanNode(ASTNode):
    def __init__(self, value, line, column):
        self.value = value  # Valor booleano de Python (True o False)
        super().__init__(line, column)
