import math

from services.RuntimeEnvironment import RuntimeEnvironment

#Excepción para capturar fallos dinámicos (división por cero, argumentos, etc).
class RuntimeError(Exception):
    pass
# Excepción para manejar el flujo de retorno en funciones (captura el valor a retornar).
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_env = RuntimeEnvironment()
        self.current_env = self.global_env
        self.functions = {} # Registro global de funciones del usuario: { 'factorial': FuncDefNode }

    def execute(self, node):
        if node is None:
            return None
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name)
        return visitor(node)

    # ESTRUCTURAS DE CONTROL (IF / WHILE / BLOCKS)
    def visit_BlockNode(self, node):
        result = None
        for statement in node.statements:
            result = self.execute(statement)
        return result

    def visit_IfNode(self, node):
        # Evalúa la condición booleana
        if self.execute(node.condition):
            return self.execute(node.true_block)
        elif node.else_block:
            return self.execute(node.else_block)
        return None

    def visit_WhileNode(self, node):
        result = None
        # Semántica del bucle: evalúa en cada iteración
        while self.execute(node.condition):
            result = self.execute(node.body)
        return result

    # ASIGNACIONES Y EXPRESIONES ARITMÉTICAS / LÓGICAS
    def visit_AssignNode(self, node):
        val = self.execute(node.value_node)
        var_name = node.var.name
        self.current_env.set(var_name, val)
        return val

    def visit_NumberNode(self, node):
        return float(node.value) if "." in str(node.value) else int(node.value)

    def visit_VariableNode(self, node):
        return self.current_env.get(node.name, node)

    def visit_BinOpNode(self, node):
        left = self.execute(node.left)
        right = self.execute(node.right)
        op = node.op

        # Control de errores: División por cero
        if op == "/" and right == 0:
            raise RuntimeError(f"Error en tiempo de ejecución [L:{node.line}, C:{node.column}]: División por cero.")

        # Operaciones Matemáticas y de Comparación
        operations = {
            "+": lambda: left + right, "-": lambda: left - right,
            "*": lambda: left * right, "/": lambda: left / right,
            "<": lambda: left < right, ">": lambda: left > right,
            "<=": lambda: left <= right, ">=": lambda: left >= right,
            "==": lambda: left == right, "!=": lambda: left != right,
            "and": lambda: left and right, "or": lambda: left or right
        }
        return operations[op]()

    # LLAMADAS A FUNCIONES Y FUNCIONES MATEMÁTICAS INTEGRADAS
    def visit_FuncDefNode(self, node):
        # Guardamos la definición en nuestro registro de funciones del usuario
        self.functions[node.name] = node
        return None

    def visit_ReturnNode(self, node):
        val = self.execute(node.expression)
        # Lanzamos la excepción para interrumpir el flujo del bloque actual
        raise ReturnException(val)

    def visit_FuncCallNode(self, node):
        # 1. ¿Es una función integrada de la librería Math?
        built_ins = ["sin", "cos", "tan", "sqrt", "log", "abs", "floor", "ceil"]
        if node.name in built_ins:
            if len(node.args) != 1:
                raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: La función '{node.name}' requiere exactamente 1 argumento.")
            
            arg_val = self.execute(node.args[0])
            
            # Control de errores de argumento inválido (ej. raíz de negativo o log de cero)
            if node.name == "sqrt" and arg_val < 0:
                raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Argumento inválido para sqrt (Raíz negativa).")
            if node.name == "log" and arg_val <= 0:
                raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Argumento inválido para log (Menor o igual a cero).")

            math_functions = {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "sqrt": math.sqrt, "log": math.log, "abs": abs,
                "floor": math.floor, "ceil": math.ceil
            }
            return math_functions[node.name](arg_val)

        # 2. ¿Es una función del usuario?
        if node.name not in self.functions:
            raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Función '{node.name}' no encontrada.")

        func_node = self.functions[node.name]

        if len(node.args) != len(func_node.params):
            raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Aridad incorrecta. Se esperaban {len(func_node.params)} argumentos.")

        # Paso de argumentos por valor: Evaluamos los argumentos ANTES de cambiar de contexto
        evaluated_args = [self.execute(arg) for arg in node.args]

        # Crear un entorno de ejecución separado para la función
        function_env = RuntimeEnvironment(parent=self.global_env) # Entorno local apunta al global
        
        # Guardar el entorno previo y cambiar al de la función
        previous_env = self.current_env
        self.current_env = function_env

        try:
            # Mapear parámetros a los valores calculados
            for param, val in zip(func_node.params, evaluated_args):
                self.current_env.set(param, val)
            
            # Ejecutar el cuerpo de la función
            self.execute(func_node.body)
            return None # Si no hay un return explícito
        except ReturnException as e:
            # Capturamos el valor devuelto por el ReturnNode
            return e.value
        finally:
            # Siempre restauramos el entorno previo al salir
            self.current_env = previous_env