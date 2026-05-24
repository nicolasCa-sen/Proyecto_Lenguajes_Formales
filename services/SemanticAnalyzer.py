from services.SymbolTable import Environment

#Excepción personalizada para reportar errores con línea y columna.
class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        # El alcance inicial siempre es el Global
        self.current_env = Environment()

    #Método de despacho genérico que actúa como Visitor.
    def analyze(self, node):
        if node is None:
            return None

        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No se ha implementado visit_{type(node).__name__}")

    
    # Detectar redeclaración y asignación
    def visit_AssignNode(self, node):
        # 1. Evaluar y anotar el tipo de la expresión de la derecha
        right_type = self.analyze(node.value)
        
        # 2. Como 'node.var' es un VariableNode, extraemos su nombre (.name)
        var_name = node.var.name 
        
        # 3. Validar si ya fue declarada en el alcance (scope) actual
        if self.current_env.is_locally_defined(var_name):
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"La variable '{var_name}' ya fue declarada en este alcance."
            )
        
        # 4. Registrar en la tabla de símbolos y anotar el nodo
        self.current_env.define(var_name, right_type)
        node.inferred_type = right_type
        
        return right_type

    # Verifica compatibilidad de tipos (Aritmética)
    def visit_BinOpNode(self, node):
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)

        # Regla 1: Int, Real = Real
        if (left_type == "Int" and right_type == "Real") or (left_type == "Real" and right_type == "Int"):
            node.inferred_type = "Real"
            return "Real"
        
        # Regla 2: Tipos idénticos (Int + Int = Int, Real + Real = Real, String + String = String)
        if left_type == right_type:
            node.inferred_type = left_type
            return left_type

        # Regla 3: Restricción Estricta (String, Int o similar no es válido)
        raise SemanticError(
            f"Error Semántico [L:{node.line}, C:{node.column}]: "
            f"Operación inválida '{node.op}' entre tipos '{left_type}' y '{right_type}'."
        )

    # Anotación de nodos hojas (Variables y Literales)
    def visit_NumberNode(self, node):
        # Inferencia básica: si tiene punto es Real, si no, Int
        tipo = "Real" if "." in str(node.value) else "Int"
        node.inferred_type = tipo
        return tipo

    def visit_VariableNode(self, node):
        tipo = self.current_env.lookup(node.name)
        if tipo is None:
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"La variable '{node.name}' no ha sido declarada."
            )
        node.inferred_type = tipo
        return tipo

    # Soporte para alcance de función (Scopes)
    def visit_FuncDefNode(self, node):
        # 1. Registrar la función en el entorno global antes de entrar a ella
        self.current_env.define(node.name, "Function")

        # 2. Crear un NUEVO alcance local apuntando al actual (padre)
        local_env = Environment(parent=self.current_env)
        
        # Intercambiamos el contexto global por el local de la función
        previous_env = self.current_env
        self.current_env = local_env

        try:
            # Registrar los parámetros en el alcance de la función
            for param in node.params: # Asumiendo que params es lista de strings o tuplas
                self.current_env.define(param, "Int") # Asumimos tipo Int para parámetros por simplicidad
            
            # Analizar el cuerpo de la función bajo este nuevo entorno local
            self.analyze(node.body)
        finally:
            # Pase lo que pase, restauramos el entorno global al salir
            self.current_env = previous_env
            
        return "Function"

    def visit_BlockNode(self, node):
        for stmt in node.statements:
            self.analyze(stmt)
        return None

# Soporte para estructuras de control (While)
    def visit_WhileNode(self, node):
        cond_type = self.analyze(node.condition)
        self.analyze(node.body)
        return None