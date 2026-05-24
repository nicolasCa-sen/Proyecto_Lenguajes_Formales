from components.ASTNode import ASTNode

#Nodo para números, sean enteros o reales
#Ejemplo: 5, 3.14, etc.
class NumberNode(ASTNode):
    def __init__(self, value, line, column):
        self.value = value  # Valor numérico (int o float)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna