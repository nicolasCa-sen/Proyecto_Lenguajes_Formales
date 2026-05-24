from components.ASTNode import ASTNode

#Nodo para operaciones binarias
#Ejemplo: (5 + 3, x * 2 etc.)
class BinOpNode(ASTNode):
    def __init__(self, left, op, right, line, column):
        self.left = left  # Nodo izquierdo
        self.op = op      # Operador (e.g., '+', '-', '*', '/')
        self.right = right  # Nodo derecho
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna