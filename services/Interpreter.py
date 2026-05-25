import math
from services.RuntimeEnvironment import RuntimeEnvironment

class RuntimeError(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_env = RuntimeEnvironment()
        self.current_env = self.global_env
        self.functions = {}
        self.stdout = [] # Buffer de salida estándar para la función print()

    def execute(self, node):
        if node is None:
            return None
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name)
        return visitor(node)

    def visit_BlockNode(self, node):
        result = None
        for statement in node.statements:
            result = self.execute(statement)
        return result

    def visit_IfNode(self, node):
        if self.execute(node.condition):
            return self.execute(node.true_block)
        elif node.false_block:
            return self.execute(node.false_block)
        return None

    def visit_WhileNode(self, node):
        result = None
        while self.execute(node.condition):
            result = self.execute(node.body)
        return result

    def visit_AssignNode(self, node):
        val = self.execute(node.value)
        var_name = node.var.name
        self.current_env.set(var_name, val)
        return val

    def visit_NumberNode(self, node):
        return float(node.value) if "." in str(node.value) else int(node.value)

    def visit_StringNode(self, node):
        return str(node.value)

    def visit_BooleanNode(self, node):
        return bool(node.value)

    def visit_UnaryOpNode(self, node):
        expr_val = self.execute(node.expr)
        op = node.op

        if op == "not":
            return not expr_val
        if op == "-":
            return -expr_val
        if op == "+":
            return +expr_val
        
        raise RuntimeError(f"Error en tiempo de ejecución [L:{node.line}, C:{node.column}]: Operador unario desconocido '{op}'.")

    def visit_VariableNode(self, node):
        return self.current_env.get(node.name, node)

    def visit_BinOpNode(self, node):
        left = self.execute(node.left)
        right = self.execute(node.right)
        op = node.op

        # Control de errores: División por cero y módulo por cero
        if op == "/" and right == 0:
            raise RuntimeError(f"Error en tiempo de ejecución [L:{node.line}, C:{node.column}]: División por cero.")
        if op == "%" and right == 0:
            raise RuntimeError(f"Error en tiempo de ejecución [L:{node.line}, C:{node.column}]: Módulo por cero.")

        # Operaciones Matemáticas, de Comparación y Lógicas
        operations = {
            "+": lambda: left + right, 
            "-": lambda: left - right,
            "*": lambda: left * right, 
            "/": lambda: left / right,
            "%": lambda: left % right,
            "^": lambda: left ** right,
            "<": lambda: left < right, 
            ">": lambda: left > right,
            "<=": lambda: left <= right, 
            ">=": lambda: left >= right,
            "==": lambda: left == right, 
            "!=": lambda: left != right,
            "and": lambda: left and right, 
            "or": lambda: left or right
        }

        if op not in operations:
            raise RuntimeError(f"Error en tiempo de ejecución [L:{node.line}, C:{node.column}]: Operador binario desconocido '{op}'.")
            
        return operations[op]()

    def visit_FuncDefNode(self, node):
        self.functions[node.name] = node
        return None

    def visit_ReturnNode(self, node):
        val = self.execute(node.expression)
        raise ReturnException(val)

    def visit_PrintNode(self, node):
        val = self.execute(node.expression)
        if isinstance(val, bool):
            val_str = "true" if val else "false"
        else:
            val_str = str(val)
        self.stdout.append(val_str)
        return val

    def visit_FuncCallNode(self, node):
        func_name = node.func_name

        # 1. Funciones matemáticas integradas
        built_ins = ["sin", "cos", "tan", "sqrt", "log", "abs", "floor", "ceil"]
        if func_name in built_ins:
            if len(node.args) != 1:
                raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: La función '{func_name}' requiere exactamente 1 argumento.")
            
            arg_val = self.execute(node.args[0])
            
            # Validaciones de argumentos para funciones matemáticas
            if func_name == "sqrt" and arg_val < 0:
                raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Argumento inválido para sqrt (Raíz negativa).")
            if func_name == "log" and arg_val <= 0:
                raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Argumento inválido para log (Menor o igual a cero).")

            math_functions = {
                "sin": math.sin, 
                "cos": math.cos, 
                "tan": math.tan,
                "sqrt": math.sqrt, 
                "log": math.log, 
                "abs": abs,
                "floor": math.floor, 
                "ceil": math.ceil
            }
            return math_functions[func_name](arg_val)

        # 2. Funciones de usuario
        if func_name not in self.functions:
            raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Función '{func_name}' no encontrada.")

        func_node = self.functions[func_name]

        if len(node.args) != len(func_node.params):
            raise RuntimeError(f"Error [L:{node.line}, C:{node.column}]: Aridad incorrecta en la llamada a '{func_name}'. Se esperaban {len(func_node.params)} argumentos.")

        evaluated_args = [self.execute(arg) for arg in node.args]

        # Crear un nuevo entorno local para la ejecución de la función
        function_env = RuntimeEnvironment(parent=self.global_env)
        previous_env = self.current_env
        self.current_env = function_env

        try:
            for param, val in zip(func_node.params, evaluated_args):
                self.current_env.set(param, val)
            
            self.execute(func_node.body)
            return None
        except ReturnException as e:
            return e.value
        finally:
            self.current_env = previous_env