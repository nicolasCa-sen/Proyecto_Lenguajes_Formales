from ASTNode import ASTNode

#Nodo para llamar funciones, que pueden tener argumentos
#Ejemplo: add(5, 3), print(x), etc.
class FuncCallNode(ASTNode):
    def __init__(self, func_name, args, line, column):
        self.func_name = func_name  # Nombre de la función a llamar (string)
        self.args = args            # Lista de nodos que representan los argumentos de la función (pueden ser NumberNode, VariableNode, etc.)
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna