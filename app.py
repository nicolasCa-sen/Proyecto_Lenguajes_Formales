from flask import Flask, request, jsonify
from flask_cors import CORS
from services.Lexer import Lexer
from services.Interpreter import Interpreter
from services.SemanticAnalyzer import SemanticAnalyzer, SemanticError
from services.PrintTreeAST import ast_to_dict

app = Flask(__name__)
CORS(app) # Permite la conexión con la interfaz de Flask de tu compañero

# Instancia persistente para la Fase 5 (Mantiene las variables vivas en el REPL)
interpreter_instance = Interpreter()

# ENDPOINT 1: FASE LÉXICA
# Recibe: Código plano. Devuelve: Lista de Tokens y Logs.
@app.route('/api/lex', methods=['POST'])
def run_lexer():
    data = request.json or {}
    code = data.get("code", "")
    
    if not code.strip():
        return jsonify({"status": "error", "message": "Código vacío"}), 400
        
    logs = [" Iniciando Fase 1: Análisis Léxico..."]
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        for t in tokens:
            logs.append(f"lex: Encontrado -> {t.type}('{t.value}') en [L:{t.line}, C:{t.column}]")
        logs.append("lex: OK - Todos los tokens identificados correctamente.")
        
        return jsonify({
            "status": "success",
            "logs": logs,
            "tokens": [t.to_dict() for t in tokens] # Tu compañero usará esta lista para su Parser
        }), 200
    except Exception as e:
        logs.append(f"ERROR LÉXICO: {str(e)}")
        return jsonify({"status": "error", "logs": logs}), 200


# ENDPOINT 2: FASE SINTÁCTICA (Nicolas)
# Recibe: La lista de tokens (o el código). Devuelve: El árbol AST en JSON y Logs.
@app.route('/api/syntax', methods=['POST'])
def run_parser():
    data = request.json or {}
    code = data.get("code", "")
    
    logs = ["Iniciando Fase 2 y 3: Análisis Sintáctico..."]
    try:
        # AQUI TU COMPAÑERO CONECTARÁ SU PARSER:
        # lexer = Lexer(code)
        # tokens = lexer.tokenize()
        # parser = Parser(tokens)
        # ast = parser.parse()
        
        logs.append("sin: OK - Gramática correcta. Árbol AST generado.")
        
        # Simulación del árbol que el Parser de tu compañero debería retornar en JSON:
        ast_simulado = {
            "type": "WhileNode", "line": 1, "column": 1,
            "condition": {"type": "BinOpNode", "op": "!=", "left": {"type": "VariableNode", "name": "x"}, "right": {"type": "NumberNode", "value": "5"}},
            "body": {"type": "BlockNode", "statements": [{"type": "PrintNode", "expression": {"type": "VariableNode", "name": "x"}}]}
        }
        
        return jsonify({
            "status": "success",
            "logs": logs,
            "ast": ast_simulado # Este JSON representa la estructura pura del árbol
        }), 200
    except Exception as e:
        logs.append(f"ERROR SINTÁCTICO: {str(e)}")
        return jsonify({"status": "error", "logs": logs}), 200

# ENDPOINT 3: FASE SEMÁNTICA Y DIBUJO
# Recibe: El AST JSON del endpoint anterior. Devuelve: Logs semánticos y Formato UI.
@app.route('/api/semantic', methods=['POST'])
def run_semantic():
    data = request.json or {}
    ast_json = data.get("ast", None)
    
    logs = [">>> Iniciando Fase 4: Análisis Semántico..."]
    if not ast_json:
        return jsonify({"status": "error", "message": "No se recibió estructura AST"}), 400
        
    try:
        # 1. Convertimos el JSON que mandó el cliente a nodos reales de Python
        # (Aquí se usaría la función dict_to_node que mapea a tus clases de nodos)
        # ast_real = dict_to_node(ast_json)
        
        # 2. Corremos tu analizador semántico sobre el árbol
        # semantic_analyzer = SemanticAnalyzer()
        # semantic_analyzer.analyze(ast_real)
        
        logs.append("sem: OK - Variables validadas. Tipos anotados e inferidos con éxito.")
        
        # 3. Convertimos el árbol anotado al formato que la librería web necesita para dibujar círculos y líneas
        # ast_para_grafico = ast_to_dict(ast_real)
        
        # Simulación de respuesta para la UI gráfica (círculos y líneas del panel derecho)
        ast_para_grafico = {
            "name": "while",
            "children": [
                {"name": "Op: != (Bool)"},
                {"name": "block", "children": [{"name": "print"}]}
            ]
        }
        
        return jsonify({
            "status": "success",
            "logs": logs,
            "ast_tree_ui": ast_para_grafico # Tu compañero toma esto para dibujar el árbol gráfico
        }), 200
    except SemanticError as e:
        logs.append(f"ERROR SEMÁNTICO DETECTADO: {str(e)}")
        return jsonify({"status": "error", "logs": logs}), 200
    except Exception as e:
        logs.append(f"ERROR CRÍTICO SEMÁNTICO: {str(e)}")
        return jsonify({"status": "error", "logs": logs}), 200


# ENDPOINT 4: FASE 5 - EJECUCIÓN / INTERPRETE
# Recibe: El AST JSON. Devuelve: Resultado de la ejecución en tiempo de real.

@app.route('/api/interpreter', methods=['POST'])
def run_interpreter():
    data = request.json or {}
    ast_json = data.get("ast", None)
    
    logs = [">>> Iniciando Fase 5: Entorno de Ejecución (REPL)..."]
    if not ast_json:
        return jsonify({"status": "error", "message": "No se recibió estructura AST"}), 400
        
    try:
        # Reconstruimos el AST a objetos Python
        # ast_real = dict_to_node(ast_json)
        
        # Ejecutamos usando tu clase Interpreter (que se mantiene viva en memoria)
        # resultado = interpreter_instance.execute(ast_real)
        resultado = "Ejecución Completada con éxito" # Simulación temporal
        
        logs.append(f"int: OK - Código ejecutado en el entorno. Fin de la traza.")
        
        return jsonify({
            "status": "success",
            "logs": logs,
            "result": resultado
        }), 200
    except Exception as e:
        logs.append(f"ERROR EN TIEMPO DE EJECUCIÓN (Runtime): {str(e)}")
        return jsonify({"status": "error", "logs": logs, "result": None}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)