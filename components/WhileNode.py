from ASTNode import ASTNode

#Nodo para la condicional while, que tiene una condición y un bloque de código a ejecutar mientras la condición sea verdadera
#Ejemplo: while x < 5: print(x)
class WhileNode(ASTNode):
    def __init__(self, condition, body, line, column):
        self.condition = condition  # Nodo que representa la condición (puede ser un BinOpNode, VariableNode, etc.)
        self.body = body          # Nodo del bloque de código a ejecutar mientras la condición sea verdadera (puede ser un BlockNode u otro nodo)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna