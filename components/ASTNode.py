#Clase base
class ASTNode:
    def __init__(self, line, column):
        self.line = line
        self.column = column