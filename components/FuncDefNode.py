from ASTNode import ASTNode

#Nodo para funciones, que pueden tener parámetros y un cuerpo de código
#Ejemplo: def add(a, b): return a + b
class FuncDefNode(ASTNode):
    def __init__(self, name, params, body, line, column):
        self.name = name      # Nombre de la función (string)
        self.params = params  # Lista de nombres de parámetros (strings)
        self.body = body      # Nodo del cuerpo de la función (puede ser un BlockNode u otro nodo)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna