from components.AssignNode import AssignNode
from components.BinOpNode import BinOpNode
from components.NumberNode import NumberNode
from components.VariableNode import VariableNode
from services.SemanticAnalyzer import SemanticAnalyzer, SemanticError

def probar_analisis_semantico():
    analyzer = SemanticAnalyzer()

    print("--- CASO 1: Operación Válida (Int + Real) ---")
    try:
        # let x = 5 + 3.14
        expr = BinOpNode(VariableNode("x", 1, 9), "+", NumberNode("3.14", 1, 13), 1, 11)
        # Simulamos que x ya existía como Int
        analyzer.current_env.define("x", "Int")
        
        tipo_resultado = analyzer.analyze(expr)
        print(f"Éxito. Tipo inferido del nodo: {expr.inferred_type}\n") # Debe decir Real
    except SemanticError as e:
        print(e)

    print("--- CASO 2: Error de Redeclaración ---")
    try:
        # 1. Creamos el nodo de la variable correctamente
        var_y = VariableNode("y", 2, 5)
        
        # 2. Primera declaración (Válida) -> let y = 10
        nodo_asig1 = AssignNode(var_y, NumberNode(10, 2, 9), 2, 1)
        analyzer.analyze(nodo_asig1)
        print("Primera asignación registrada correctamente.")

        # 3. Segunda declaración (Debería fallar aquí) -> let y = 20
        nodo_asig2 = AssignNode(var_y, NumberNode(20, 3, 9), 3, 1)
        analyzer.analyze(nodo_asig2)
        
    except SemanticError as e:
        # Captura el error semántico controlado que creamos en el analizador
        print(f"Éxito en la prueba. Capturado correctamente -> {e}\n")
    except Exception as e:
        print(f"Error inesperado en la prueba: {e}\n")
if __name__ == "__main__":
    probar_analisis_semantico()