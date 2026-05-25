import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from services.Lexer import Lexer
from services.Parser import Parser
from services.SemanticAnalyzer import SemanticAnalyzer, SemanticError
from services.Interpreter import Interpreter, RuntimeError
from services.PrintTreeAST import ast_to_dict

app = Flask(__name__, template_folder="templates")
CORS(app)

# RUTA PRINCIPAL: Sirve la aplicación web académica
@app.route('/')
def index():
    return render_template('index.html')


# ENDPOINT DE EJECUCIÓN INTEGRADO COMPLETO (Pipeline completo)
@app.route('/api/run', methods=['POST'])
def run_pipeline():
    data = request.json or {}
    code = data.get("code", "")
    
    if not code.strip():
        return jsonify({
            "status": "error",
            "message": "Código vacío",
            "lex_errors": [],
            "syntax_errors": ["Error Sintáctico: El código fuente está vacío."],
            "semantic_errors": [],
            "runtime_error": None,
            "stdout": [],
            "ast_tree_ui": None,
            "result": None
        }), 200

    # 1. Fase Léxica
    lexer = Lexer(code)
    try:
        tokens = lexer.tokenize()
    except Exception as e:
        return jsonify({
            "status": "error",
            "lex_errors": [f"Error Léxico Crítico: {str(e)}"],
            "syntax_errors": [],
            "semantic_errors": [],
            "runtime_error": None,
            "stdout": [],
            "ast_tree_ui": None,
            "result": None
        }), 200

    lex_errors = lexer.errors

    # 2. Fase Sintáctica (Parser)
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        return jsonify({
            "status": "error",
            "lex_errors": lex_errors,
            "syntax_errors": [f"Error Sintáctico Crítico: {str(e)}"],
            "semantic_errors": [],
            "runtime_error": None,
            "stdout": [],
            "ast_tree_ui": None,
            "result": None
        }), 200

    syntax_errors = parser.errors

    if syntax_errors:
        return jsonify({
            "status": "error",
            "lex_errors": lex_errors,
            "syntax_errors": syntax_errors,
            "semantic_errors": [],
            "runtime_error": None,
            "stdout": [],
            "ast_tree_ui": ast_to_dict(ast) if ast else None,
            "result": None
        }), 200

    # 3. Fase Semántica
    semantic_analyzer = SemanticAnalyzer()
    try:
        semantic_analyzer.analyze(ast)
    except Exception as e:
        return jsonify({
            "status": "error",
            "lex_errors": lex_errors,
            "syntax_errors": syntax_errors,
            "semantic_errors": [f"Error Semántico Crítico: {str(e)}"],
            "runtime_error": None,
            "stdout": [],
            "ast_tree_ui": ast_to_dict(ast),
            "result": None
        }), 200

    semantic_errors = semantic_analyzer.errors

    if semantic_errors:
        return jsonify({
            "status": "error",
            "lex_errors": lex_errors,
            "syntax_errors": syntax_errors,
            "semantic_errors": semantic_errors,
            "runtime_error": None,
            "stdout": [],
            "ast_tree_ui": ast_to_dict(ast),
            "result": None
        }), 200

    # 4. Fase de Ejecución (Intérprete)
    interpreter = Interpreter()
    runtime_error = None
    result = None
    try:
        result = interpreter.execute(ast)
    except RuntimeError as e:
        runtime_error = str(e)
    except Exception as e:
        runtime_error = f"Error Crítico en Tiempo de Ejecución: {str(e)}"

    status = "error" if runtime_error else "success"

    return jsonify({
        "status": status,
        "lex_errors": lex_errors,
        "syntax_errors": syntax_errors,
        "semantic_errors": semantic_errors,
        "runtime_error": runtime_error,
        "stdout": interpreter.stdout,
        "ast_tree_ui": ast_to_dict(ast),
        "result": str(result) if result is not None else None
    }), 200


# ENDPOINT 1: FASE LÉXICA INDIVIDUAL
@app.route('/api/lex', methods=['POST'])
def run_lexer():
    data = request.json or {}
    code = data.get("code", "")
    
    if not code.strip():
        return jsonify({"status": "error", "message": "Código vacío", "logs": ["Código vacío"]}), 400
        
    logs = [" Iniciando Fase 1: Análisis Léxico..."]
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        for t in tokens:
            logs.append(f"lex: Encontrado -> {t.type}('{t.value}') en [L:{t.line}, C:{t.column}]")
        
        if lexer.errors:
            for err in lexer.errors:
                logs.append(err)
            return jsonify({"status": "error", "logs": logs, "tokens": []}), 200
            
        logs.append("lex: OK - Todos los tokens identificados correctamente.")
        return jsonify({
            "status": "success",
            "logs": logs,
            "tokens": [t.to_dict() for t in tokens]
        }), 200
    except Exception as e:
        logs.append(f"ERROR LÉXICO CRÍTICO: {str(e)}")
        return jsonify({"status": "error", "logs": logs, "tokens": []}), 200


# ENDPOINT 2: FASE SINTÁCTICA INDIVIDUAL
@app.route('/api/syntax', methods=['POST'])
def run_parser():
    data = request.json or {}
    code = data.get("code", "")
    
    logs = ["Iniciando Fase 2 y 3: Análisis Sintáctico..."]
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            for err in parser.errors:
                logs.append(err)
            return jsonify({"status": "error", "logs": logs, "ast": None}), 200
            
        logs.append("sin: OK - Gramática correcta. Árbol AST generado.")
        return jsonify({
            "status": "success",
            "logs": logs,
            "ast": ast_to_dict(ast)
        }), 200
    except Exception as e:
        logs.append(f"ERROR SINTÁCTICO CRÍTICO: {str(e)}")
        return jsonify({"status": "error", "logs": logs, "ast": None}), 200


# ENDPOINT 3: FASE SEMÁNTICA INDIVIDUAL
@app.route('/api/semantic', methods=['POST'])
def run_semantic():
    data = request.json or {}
    code = data.get("code", "")
    
    logs = [">>> Iniciando Fase 4: Análisis Semántico..."]
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors:
            logs.append("No se puede realizar análisis semántico debido a errores sintácticos.")
            return jsonify({"status": "error", "logs": logs, "ast_tree_ui": None}), 200
            
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        
        if semantic_analyzer.errors:
            for err in semantic_analyzer.errors:
                logs.append(err)
            return jsonify({"status": "error", "logs": logs, "ast_tree_ui": ast_to_dict(ast)}), 200
            
        logs.append("sem: OK - Variables validadas. Tipos anotados e inferidos con éxito.")
        return jsonify({
            "status": "success",
            "logs": logs,
            "ast_tree_ui": ast_to_dict(ast)
        }), 200
    except Exception as e:
        logs.append(f"ERROR SEMÁNTICO CRÍTICO: {str(e)}")
        return jsonify({"status": "error", "logs": logs, "ast_tree_ui": None}), 200


# ENDPOINT 4: FASE EJECUCIÓN INDIVIDUAL
@app.route('/api/interpreter', methods=['POST'])
def run_interpreter():
    data = request.json or {}
    code = data.get("code", "")
    
    logs = [">>> Iniciando Fase 5: Entorno de Ejecución (REPL)..."]
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        if parser.errors or lexer.errors:
            logs.append("No se puede ejecutar debido a errores léxicos o sintácticos.")
            return jsonify({"status": "error", "logs": logs, "result": None}), 200
            
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        
        if semantic_analyzer.errors:
            logs.append("No se puede ejecutar debido a errores semánticos.")
            return jsonify({"status": "error", "logs": logs, "result": None}), 200
            
        interpreter = Interpreter()
        resultado = interpreter.execute(ast)
        
        for print_out in interpreter.stdout:
            logs.append(f"[Stdout]: {print_out}")
            
        logs.append(f"int: OK - Código ejecutado con éxito. Retorno: {resultado}")
        return jsonify({
            "status": "success",
            "logs": logs,
            "result": str(resultado) if resultado is not None else "Ejecutado sin retorno"
        }), 200
    except RuntimeError as e:
        logs.append(f"ERROR EN TIEMPO DE EJECUCIÓN (Runtime): {str(e)}")
        return jsonify({"status": "error", "logs": logs, "result": None}), 200
    except Exception as e:
        logs.append(f"ERROR CRÍTICO EN EJECUCIÓN: {str(e)}")
        return jsonify({"status": "error", "logs": logs, "result": None}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)