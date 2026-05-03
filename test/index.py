from BinOpNode import BinOpNode
from NumberNode import NumberNode
from VariableNode import VariableNode
from WhileNode import WhileNode
from BlockNode import BlockNode
from PrintNode import PrintNode
from PrintTreeAST import print_ast

# index.py
# ... (tus imports permanecen igual)

def run_test():
    print(" Simulando AST para: while x != 5 { print(x) } ")
    
    try:
        # 1. Construir la condición: x != 5
        var_x = VariableNode("x", 1, 7)         # Línea 1, Columna 7
        num_5 = NumberNode(5, 1, 12)            # Línea 1, Columna 12
        
        condicion = BinOpNode(
            left=var_x,
            op="!=",
            right=num_5,
            line=1, column=10                  # Ubicación del operador
        )
        
        # 2. Construir el cuerpo: print(x)
        val_print = VariableNode("x", 2, 11)
        print_stmt = PrintNode(val_print, 2, 5)
        
        cuerpo = BlockNode([print_stmt], 2, 1) # Inicio del bloque
        
        # 3. Nodo raíz: while
        arbol_while = WhileNode(condicion, cuerpo, 1, 1)
        
        # 4. Visualizar
        print_ast(arbol_while)
        
    except Exception as e:
        print(f"Error al construir o imprimir el AST: {e}")

if __name__ == "__main__":
    run_test()