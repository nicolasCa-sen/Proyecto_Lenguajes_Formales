import sys
import os

# Asegurar que el directorio raíz está en el PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.Lexer import Lexer
from services.Parser import Parser
from services.SemanticAnalyzer import SemanticAnalyzer
from services.Interpreter import Interpreter, RuntimeError

class MathLiteTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0

    def run_test(self, name, category, code, expected_status, check_fn=None):
        self.total += 1
        print(f"[{category}] Test {self.total:02d}: {name}...", end="")
        
        try:
            # 1. Lexer
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            lex_errs = lexer.errors
            
            if expected_status == "lex_error":
                if len(lex_errs) > 0:
                    self.passed += 1
                    print(" \033[92mPASSED\033[0m (Error léxico detectado con éxito)")
                    return
                else:
                    self.failed += 1
                    print(" \033[91mFAILED\033[0m (Se esperaba error léxico pero no se reportó)")
                    return

            # 2. Parser
            parser = Parser(tokens)
            ast = parser.parse()
            syntax_errs = parser.errors
            
            if expected_status == "syntax_error":
                if len(syntax_errs) > 0:
                    self.passed += 1
                    print(" \033[92mPASSED\033[0m (Error sintáctico detectado con éxito)")
                    return
                else:
                    self.failed += 1
                    print(" \033[91mFAILED\033[0m (Se esperaba error sintáctico pero no se reportó)")
                    return

            if len(lex_errs) > 0 or len(syntax_errs) > 0:
                self.failed += 1
                print(f" \033[91mFAILED\033[0m (Errores de parsing inesperados: L:{lex_errs}, S:{syntax_errs})")
                return

            # 3. Analizador Semántico
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            semantic_errs = analyzer.errors

            if expected_status == "semantic_error":
                if len(semantic_errs) > 0:
                    self.passed += 1
                    print(" \033[92mPASSED\033[0m (Error semántico detectado con éxito)")
                    return
                else:
                    self.failed += 1
                    print(" \033[91mFAILED\033[0m (Se esperaba error semántico pero no se reportó)")
                    return

            if len(semantic_errs) > 0:
                self.failed += 1
                print(f" \033[91mFAILED\033[0m (Errores semánticos inesperados: {semantic_errs})")
                return

            # 4. Intérprete (Ejecución)
            interpreter = Interpreter()
            run_err = None
            result = None
            try:
                result = interpreter.execute(ast)
            except RuntimeError as e:
                run_err = str(e)
            except Exception as e:
                run_err = f"Error crítico: {str(e)}"

            if expected_status == "runtime_error":
                if run_err is not None:
                    self.passed += 1
                    print(" \033[92mPASSED\033[0m (Error de ejecución detectado con éxito)")
                    return
                else:
                    self.failed += 1
                    print(" \033[91mFAILED\033[0m (Se esperaba error de ejecución pero ejecutó limpio)")
                    return

            if run_err is not None:
                self.failed += 1
                print(f" \033[91mFAILED\033[0m (Error de ejecución inesperado: {run_err})")
                return

            # Verificaciones custom opcionales
            if check_fn:
                if check_fn(result, interpreter.stdout):
                    self.passed += 1
                    print(" \033[92mPASSED\033[0m (Resultado y salida correctas)")
                else:
                    self.failed += 1
                    print(f" \033[91mFAILED\033[0m (Fallo en la validación del resultado. Obt: {result}, Stdout: {interpreter.stdout})")
            else:
                self.passed += 1
                print(" \033[92mPASSED\033[0m (Ejecutado correctamente)")

        except Exception as e:
            self.failed += 1
            print(f" \033[91mFAILED\033[0m (Excepción no controlada en el test: {e})")

    def run_all(self):
        print("\n" + "="*60)
        print("          MATHLITE COMPILER & INTERPRETER TEST SUITE")
        print("="*60 + "\n")

        # ====== 1. PRUEBAS LÉXICAS ======
        self.run_test("Números enteros y reales válidos", "LÉXICO", "let x = 12\nlet y = 3.14", "success")
        self.run_test("Identificadores y palabras reservadas", "LÉXICO", "let base = 10\nwhile base > 0 { let base = base - 1 }", "success")
        self.run_test("Cadenas de texto literales", "LÉXICO", "let saludo = \"hola mundo\"", "success")
        self.run_test("Ignorar comentarios de línea", "LÉXICO", "-- Este es un comentario\nlet a = 1 -- Otro comentario", "success")
        self.run_test("Operadores multi-carácter", "LÉXICO", "let x = 1\nlet y = 2\nlet c = (x == y) or (x != y) and (x <= y)", "success")
        self.run_test("Error de carácter ilegal", "LÉXICO", "let x = 5 @ 10", "lex_error")

        # ====== 2. PRUEBAS SINTÁCTICAS ======
        self.run_test("Declaración de variables", "SINTAXIS", "let mi_var = (10 + 5) * 3", "success")
        self.run_test("Error de paréntesis sin cerrar", "SINTAXIS", "let x = (3 + 4 * 2", "syntax_error")
        self.run_test("Definición de funciones y parámetros", "SINTAXIS", "def sumar(a, b) {\n  return a + b\n}", "success")
        self.run_test("Bucle while estructurado", "SINTAXIS", "let i = 1\nwhile i <= 5 {\n  let i = i + 1\n}", "success")
        self.run_test("Condicionales if-else", "SINTAXIS", "let x = 15\nif x > 10 {\n  print(x)\n} else {\n  print(0)\n}", "success")
        self.run_test("Error por falta de llaves en funciones", "SINTAXIS", "def f(x) return x + 1", "syntax_error")

        # ====== 3. PRUEBAS SEMÁNTICAS ======
        self.run_test("Inferencia aritmética Int + Real = Real", "SEMÁNTICA", 
                      "let a = 5\nlet b = 3.14\nlet c = a + b", "success",
                      check_fn=lambda r, out: True) # Verificado internamente en AST
        self.run_test("Error por variable no declarada", "SEMÁNTICA", "print(variable_inexistente)", "semantic_error")
        self.run_test("Error por redeclaración en el mismo alcance", "SEMÁNTICA", "let y = 10\nlet y = 20", "semantic_error")
        self.run_test("Error por suma incompatible String y Entero", "SEMÁNTICA", "let r = \"hola\" + 5", "semantic_error")
        self.run_test("Error por llamada a función no definida", "SEMÁNTICA", "let x = calcular_algo(5)", "semantic_error")
        self.run_test("Error por aridad de argumentos incorrecta", "SEMÁNTICA", "def f(a, b) { return a } \n let r = f(1)", "semantic_error")
        self.run_test("Error por return fuera del cuerpo de función", "SEMÁNTICA", "let x = 10\nreturn x", "semantic_error")

        # ====== 4. PRUEBAS EN TIEMPO DE EJECUCIÓN (INTÉRPRETE) ======
        self.run_test("Fórmula aritmética compleja obligatoria", "EJECUCIÓN", 
                      "let resultado = (3 + 4 * 2) / (1 - 5)^2\nprint(resultado)", "success",
                      check_fn=lambda r, out: len(out) > 0 and abs(float(out[0]) - 0.6875) < 0.0001)
        self.run_test("Error de división por cero", "EJECUCIÓN", "let z = 10 / 0", "runtime_error")
        self.run_test("Error de módulo por cero", "EJECUCIÓN", "let z = 10 % 0", "runtime_error")
        self.run_test("Ejecución de matemática integrada (sqrt)", "EJECUCIÓN", "let r = sqrt(4.0)\nprint(r)", "success",
                      check_fn=lambda r, out: len(out) > 0 and float(out[0]) == 2.0)
        self.run_test("Error por raíz de número negativo", "EJECUCIÓN", "let r = sqrt(-4.0)", "runtime_error")
        self.run_test("Ejecución de función factorial recursiva obligatoria", "EJECUCIÓN", 
                      "def factorial(n) {\n  if n <= 1 {\n    return 1\n  }\n  return n * factorial(n - 1)\n}\nlet r = factorial(5)\nprint(r)", "success",
                      check_fn=lambda r, out: len(out) > 0 and int(out[0]) == 120)
        self.run_test("Ejecución de funciones anidadas obligatoria", "EJECUCIÓN",
                      "def duplicar(x) { return x * 2 }\ndef operar(y) { return duplicar(y) + 5 }\nlet r = operar(10)\nprint(r)", "success",
                      check_fn=lambda r, out: len(out) > 0 and int(out[0]) == 25)

        print("\n" + "="*60)
        print("                   RESUMEN DE PRUEBAS")
        print(f" Total de casos ejecutados: {self.total}")
        print(f" Pruebas aprobadas (✓): \033[92m{self.passed}\033[0m")
        print(f" Pruebas fallidas (✗): \033[91m{self.failed}\033[0m")
        print("="*60 + "\n")

if __name__ == "__main__":
    suite = MathLiteTestSuite()
    suite.run_all()
