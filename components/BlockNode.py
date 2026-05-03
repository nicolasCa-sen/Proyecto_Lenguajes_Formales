from ASTNode import ASTNode

#Nodo para bloques de codigo, que pueden contener múltiples sentencias
#Ejemplo: { let x = 5; let y = 3.14; x + y; }
class BlockNode(ASTNode):
    def __init__(self, statements, line, column):
        self.statements = statements  # Lista de sentencias en el bloque
        super().__init__(line, column)  # Llamamos al constructor de la clase base para asignar línea y columna