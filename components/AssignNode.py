from components.ASTNode import ASTNode

#Nodo para asignaciones 
#Ejemplo: let x = 5, base = 3.14, etc.
class AssignNode(ASTNode):
    def __init__(self, var, value_node, line, column):
        self.var = var    # Nodo de variable
        self.value = value_node  # Nodo de la expresión a asignar (puede ser un NumberNode, BinOpNode, etc.)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna

    @property
    def name(self):
        return self.var.name