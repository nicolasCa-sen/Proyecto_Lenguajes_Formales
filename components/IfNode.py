from ASTNode import ASTNode

#Nodo para las sentencias if, que pueden tener una condición, un bloque de código para el caso verdadero y opcionalmente un bloque de código para el caso falso
#Ejemplo: if x > 5: print("Mayor que 5")
class IfNode(ASTNode):
    def __init__(self, condition, true_block,line,column, false_block=None):
        self.condition = condition  # Nodo que representa la condición (puede ser un BinOpNode, VariableNode, etc.)
        self.true_block = true_block  # Nodo del bloque de código a ejecutar si la condición es verdadera (puede ser un BlockNode u otro nodo)
        self.false_block = false_block  # Nodo del bloque de código a ejecutar si la condición es falsa (puede ser un BlockNode u otro nodo), opcional
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna