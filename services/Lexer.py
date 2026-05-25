import re

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def to_dict(self):
        """Facilita enviar los tokens como JSON a la interfaz"""
        return {"type": self.type, "value": self.value, "line": self.line, "column": self.column}

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.errors = [] # Para recolectar errores léxicos
        
        # Definición de patrones de Tokens (Expresiones Regulares)
        self.token_specs = [
            ('COMMENT',    r'--[^\n]*'),          # Comentarios de línea (ej: -- comentario)
            ('STRING',     r'"[^"\n]*"'),         # Cadenas de texto (ej: "hola")
            ('REAL',       r'\d+\.\d+'),          # Números Reales (ej: 3.14)
            ('INT',        r'\d+'),               # Números Enteros (ej: 5)
            ('OP',         r'==|!=|<=|>=|\+|-|\*|/|<|>|\^|%'), # Operadores aritméticos/comparación/potencia/modulo
            ('ASSIGN',     r'='),                 # Asignación
            ('LPAREN',     r'\('),                # Paréntesis izquierdo
            ('RPAREN',     r'\)'),                # Paréntesis derecho
            ('LBRACE',     r'\{'),                # Llave izquierda
            ('RBRACE',     r'\}'),                # Llave derecha
            ('COMMA',      r','),                 # Comma para parámetros
            ('ID',         r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identificadores (variables/funciones)
            ('NEWLINE',    r'\n'),                # Nueva línea
            ('SKIP',       r'[ \t\r]+'),          # Espacios y tabulaciones
            ('MISMATCH',   r'.'),                 # Cualquier otro caracter ilegal
        ]

    def tokenize(self):
        # Unir todas las expresiones en una sola gran expresión regular
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs)
        line_num = 1
        line_start = 0
        
        for mo in re.finditer(regex, self.text):
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - line_start + 1
            
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'SKIP':
                continue
            elif kind == 'COMMENT':
                continue
            elif kind == 'MISMATCH':
                self.errors.append(f"Error Léxico: Carácter inesperado '{value}' en línea {line_num}, columna {column}")
                continue
            
            # Limpiar comillas en strings
            if kind == 'STRING':
                value = value[1:-1]
            
            # Verificar si el ID es en realidad una palabra clave (Keywords)
            if kind == 'ID':
                keywords = {'while', 'if', 'else', 'def', 'return', 'print', 'and', 'or', 'let', 'not', 'true', 'false'}
                if value in keywords:
                    kind = value.upper() # Cambia el tipo a 'WHILE', 'IF', etc.
            
            self.tokens.append(Token(kind, value, line_num, column))
            
        return self.tokens