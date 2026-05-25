from services.SymbolTable import Environment

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.current_env = Environment()
        self.errors = []
        self.in_function = False
        # Registro global de funciones del usuario: { 'nombre': { 'param_count': X, 'return_type': Y } }
        self.functions = {}
        # Inicializar funciones matemáticas del sistema
        self.built_ins = {
            "sin": {"param_count": 1, "return_type": "Real"},
            "cos": {"param_count": 1, "return_type": "Real"},
            "tan": {"param_count": 1, "return_type": "Real"},
            "sqrt": {"param_count": 1, "return_type": "Real"},
            "log": {"param_count": 1, "return_type": "Real"},
            "abs": {"param_count": 1, "return_type": "Real"},
            "floor": {"param_count": 1, "return_type": "Real"},
            "ceil": {"param_count": 1, "return_type": "Real"}
        }

    def analyze(self, node):
        if node is None:
            return None

        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        try:
            return visitor(node)
        except SemanticError as e:
            self.errors.append(str(e))
            return "Error"

    def generic_visit(self, node):
        raise NotImplementedError(f"No se ha implementado visit_{type(node).__name__}")

    def visit_BlockNode(self, node):
        # Crear un nuevo entorno local para cada bloque de código
        previous_env = self.current_env
        self.current_env = Environment(parent=self.current_env)
        try:
            for stmt in node.statements:
                self.analyze(stmt)
        finally:
            self.current_env = previous_env
        return None

    def visit_AssignNode(self, node):
        right_type = self.analyze(node.value)
        var_name = node.var.name 
        
        # Validar si ya fue declarada en el alcance actual
        if self.current_env.is_locally_defined(var_name):
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Redeclaración de variable. La variable '{var_name}' ya fue declarada en este alcance."
            )
        
        self.current_env.define(var_name, right_type)
        node.inferred_type = right_type
        return right_type

    def visit_BinOpNode(self, node):
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)
        op = node.op

        # 1. Operadores Aritméticos
        if op in ["+", "-", "*", "/", "%", "^"]:
            if left_type == "String" and right_type == "String" and op == "+":
                node.inferred_type = "String"
                return "String"
            
            if left_type in ["Int", "Real"] and right_type in ["Int", "Real"]:
                tipo = "Real" if (left_type == "Real" or right_type == "Real") else "Int"
                node.inferred_type = tipo
                return tipo
            
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Operación aritmética '{op}' no permitida entre tipos '{left_type}' y '{right_type}'."
            )

        # 2. Operadores de Comparación
        if op in ["<", ">", "<=", ">="]:
            if (left_type in ["Int", "Real"] and right_type in ["Int", "Real"]) or (left_type == "String" and right_type == "String"):
                node.inferred_type = "Bool"
                return "Bool"
            
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Comparación '{op}' no permitida entre tipos '{left_type}' y '{right_type}'."
            )

        # 3. Operadores de Igualdad
        if op in ["==", "!="]:
            node.inferred_type = "Bool"
            return "Bool"

        # 4. Operadores Lógicos
        if op in ["and", "or"]:
            if left_type == "Bool" and right_type == "Bool":
                node.inferred_type = "Bool"
                return "Bool"
            
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Operador lógico '{op}' requiere operandos booleanos, pero recibió '{left_type}' y '{right_type}'."
            )

        raise SemanticError(
            f"Error Semántico [L:{node.line}, C:{node.column}]: "
            f"Operador binario desconocido '{op}'."
        )

    def visit_NumberNode(self, node):
        tipo = "Real" if "." in str(node.value) else "Int"
        node.inferred_type = tipo
        return tipo

    def visit_StringNode(self, node):
        node.inferred_type = "String"
        return "String"

    def visit_BooleanNode(self, node):
        node.inferred_type = "Bool"
        return "Bool"

    def visit_UnaryOpNode(self, node):
        expr_type = self.analyze(node.expr)
        op = node.op

        if op == "not":
            if expr_type == "Bool":
                node.inferred_type = "Bool"
                return "Bool"
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Operador 'not' requiere un booleano, pero recibió '{expr_type}'."
            )
        
        if op in ["-", "+"]:
            if expr_type in ["Int", "Real"]:
                node.inferred_type = expr_type
                return expr_type
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Operador unario '{op}' requiere un número, pero recibió '{expr_type}'."
            )

        raise SemanticError(
            f"Error Semántico [L:{node.line}, C:{node.column}]: "
            f"Operador unario desconocido '{op}'."
        )

    def visit_VariableNode(self, node):
        tipo = self.current_env.lookup(node.name)
        if tipo is None:
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"La variable '{node.name}' no ha sido declarada."
            )
        node.inferred_type = tipo
        return tipo

    def visit_FuncDefNode(self, node):
        # Registrar la función en la tabla global antes de analizar el cuerpo
        self.functions[node.name] = {
            "param_count": len(node.params),
            "return_type": "Real"  # Valor por defecto inferido, se actualizará si hay returns
        }
        self.current_env.define(node.name, "Function")

        # Crear un nuevo alcance local para la función
        local_env = Environment(parent=self.current_env)
        previous_env = self.current_env
        self.current_env = local_env
        
        previous_in_function = self.in_function
        self.in_function = True

        try:
            # Definir parámetros como variables locales dentro de la función (por defecto de tipo Real/Int)
            for param in node.params:
                self.current_env.define(param, "Real")
            
            # Analizar el cuerpo de la función
            self.analyze(node.body)
        finally:
            self.current_env = previous_env
            self.in_function = previous_in_function
            
        node.inferred_type = "Function"
        return "Function"

    def visit_FuncCallNode(self, node):
        func_name = node.func_name
        
        # 1. Comprobar si es integrada
        if func_name in self.built_ins:
            spec = self.built_ins[func_name]
            if len(node.args) != spec["param_count"]:
                raise SemanticError(
                    f"Error Semántico [L:{node.line}, C:{node.column}]: "
                    f"Número incorrecto de argumentos para la función integrada '{func_name}'. Se esperaba {spec['param_count']} pero se recibieron {len(node.args)}."
                )
            # Analizar argumentos
            for arg in node.args:
                arg_type = self.analyze(arg)
                if arg_type not in ["Int", "Real", "Error"]:
                    raise SemanticError(
                        f"Error Semántico [L:{node.line}, C:{node.column}]: "
                        f"Argumento de tipo incompatible para '{func_name}'. Se esperaba un número pero se recibió '{arg_type}'."
                    )
            node.inferred_type = spec["return_type"]
            return spec["return_type"]

        # 2. Comprobar si es del usuario
        if func_name not in self.functions:
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Llamada a función no definida '{func_name}'."
            )
            
        spec = self.functions[func_name]
        if len(node.args) != spec["param_count"]:
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Aridad incorrecta para la función '{func_name}'. Se esperaban {spec['param_count']} argumentos pero se recibieron {len(node.args)}."
            )
            
        # Analizar tipos de argumentos
        for arg in node.args:
            self.analyze(arg)
            
        node.inferred_type = spec["return_type"]
        return spec["return_type"]

    def visit_ReturnNode(self, node):
        if not self.in_function:
            raise SemanticError(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"Uso inválido de 'return' fuera del cuerpo de una función."
            )
            
        expr_type = self.analyze(node.expression)
        node.inferred_type = expr_type
        return expr_type

    def visit_WhileNode(self, node):
        cond_type = self.analyze(node.condition)
        if cond_type != "Bool" and cond_type != "Error":
            self.errors.append(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"La condición del bucle 'while' debe ser de tipo Bool, pero se recibió '{cond_type}'."
            )
        self.analyze(node.body)
        node.inferred_type = "Void"
        return "Void"

    def visit_IfNode(self, node):
        cond_type = self.analyze(node.condition)
        if cond_type != "Bool" and cond_type != "Error":
            self.errors.append(
                f"Error Semántico [L:{node.line}, C:{node.column}]: "
                f"La condición de la sentencia 'if' debe ser de tipo Bool, pero se recibió '{cond_type}'."
            )
        self.analyze(node.true_block)
        if node.false_block:
            self.analyze(node.false_block)
        node.inferred_type = "Void"
        return "Void"

    def visit_PrintNode(self, node):
        self.analyze(node.expression)
        node.inferred_type = "Void"
        return "Void"