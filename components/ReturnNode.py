from ASTNode import ASTNode

#Nodo para return, que puede tener una expresión a retornar
#Ejemplo: return x + 5, return "Hello", etc.
class ReturnNode(ASTNode):
    def __init__(self, expression, line, column):
        self.expression = expression  # Nodo de la expresión a retornar (puede ser un VariableNode, BinOpNode, etc.)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna