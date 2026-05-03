from ASTNode import ASTNode

#Nodo para imprimir, que puede tener una expresión a imprimir
#Ejemplo: print(x), print(5 + 3), etc.
class PrintNode(ASTNode):
    def __init__(self, expression, line, column):
        self.expression = expression  # Nodo de la expresión a imprimir (puede ser un VariableNode, BinOpNode, etc.)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna