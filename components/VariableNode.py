from ASTNode import ASTNode

#Nodo para variables
#Ejemplo: x, base, etc.
class VariableNode(ASTNode):
    def __init__(self, name, line, column):
        self.name = name  # Nombre de la variable (string)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna