from components.NumberNode import NumberNode
from components.VariableNode import VariableNode
from components.BinOpNode import BinOpNode
from components.AssignNode import AssignNode
from components.BlockNode import BlockNode
from components.IfNode import IfNode
from components.WhileNode import WhileNode
from components.PrintNode import PrintNode
from components.ReturnNode import ReturnNode
from components.FuncDefNode import FuncDefNode
from components.FuncCallNode import FuncCallNode
from components.StringNode import StringNode
from components.BooleanNode import BooleanNode
from components.UnaryOpNode import UnaryOpNode

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def previous(self):
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        return None

    def is_at_end(self):
        return self.peek() is None

    def advance(self):
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def check(self, type_):
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def match(self, *types):
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def consume(self, type_, message):
        if self.check(type_):
            return self.advance()
        token = self.peek()
        line = token.line if token else (self.previous().line if self.previous() else 1)
        col = token.column if token else (self.previous().column if self.previous() else 1)
        err = f"Error Sintáctico [L:{line}, C:{col}]: {message}"
        self.errors.append(err)
        raise SyntaxError(err)

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous() and self.previous().type == 'RBRACE':
                return
            if self.peek().type in ['LET', 'DEF', 'WHILE', 'IF', 'PRINT', 'RETURN']:
                return
            self.advance()

    def parse(self):
        statements = []
        start_line = self.tokens[0].line if self.tokens else 1
        start_col = self.tokens[0].column if self.tokens else 1
        
        while not self.is_at_end():
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except SyntaxError:
                self.synchronize()
        
        return BlockNode(statements, start_line, start_col)

    def statement(self):
        if self.match('LET'):
            return self.var_declaration()
        elif self.check('ID') and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'ASSIGN':
            var_token = self.advance()
            assign_token = self.advance()
            expr = self.expression()
            var_node = VariableNode(var_token.value, var_token.line, var_token.column)
            return AssignNode(var_node, expr, var_token.line, var_token.column)
        elif self.match('DEF'):
            return self.func_declaration()
        elif self.match('WHILE'):
            return self.while_statement()
        elif self.match('IF'):
            return self.if_statement()
        elif self.match('PRINT'):
            return self.print_statement()
        elif self.match('RETURN'):
            return self.return_statement()
        else:
            return self.expression_statement()

    def var_declaration(self):
        let_token = self.previous()
        var_token = self.consume('ID', "Se esperaba un nombre de variable después de 'let'.")
        self.consume('ASSIGN', "Se esperaba '=' después del nombre de la variable.")
        expr = self.expression()
        
        var_node = VariableNode(var_token.value, var_token.line, var_token.column)
        return AssignNode(var_node, expr, let_token.line, let_token.column)

    def func_declaration(self):
        def_token = self.previous()
        name_token = self.consume('ID', "Se esperaba el nombre de la función después de 'def'.")
        self.consume('LPAREN', "Se esperaba '(' después del nombre de la función.")
        
        params = []
        if not self.check('RPAREN'):
            param_token = self.consume('ID', "Se esperaba el nombre del parámetro.")
            params.append(param_token.value)
            while self.match('COMMA'):
                p_tok = self.consume('ID', "Se esperaba el nombre del parámetro después de ','.")
                params.append(p_tok.value)
                
        self.consume('RPAREN', "Se esperaba ')' después de los parámetros.")
        self.consume('LBRACE', "Se esperaba '{' para iniciar el cuerpo de la función.")
        
        statements = []
        body_line = self.peek().line if self.peek() else def_token.line
        body_col = self.peek().column if self.peek() else def_token.column
        
        while not self.check('RBRACE') and not self.is_at_end():
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except SyntaxError:
                self.synchronize()
                
        self.consume('RBRACE', "Se esperaba '}' al cerrar el cuerpo de la función.")
        body_node = BlockNode(statements, body_line, body_col)
        
        return FuncDefNode(name_token.value, params, body_node, def_token.line, def_token.column)

    def while_statement(self):
        while_token = self.previous()
        cond = self.expression()
        self.consume('LBRACE', "Se esperaba '{' para iniciar el cuerpo del ciclo while.")
        
        statements = []
        body_line = self.peek().line if self.peek() else while_token.line
        body_col = self.peek().column if self.peek() else while_token.column
        
        while not self.check('RBRACE') and not self.is_at_end():
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except SyntaxError:
                self.synchronize()
                
        self.consume('RBRACE', "Se esperaba '}' al cerrar el cuerpo del while.")
        body_node = BlockNode(statements, body_line, body_col)
        
        return WhileNode(cond, body_node, while_token.line, while_token.column)

    def if_statement(self):
        if_token = self.previous()
        cond = self.expression()
        self.consume('LBRACE', "Se esperaba '{' para iniciar el bloque if.")
        
        true_statements = []
        true_line = self.peek().line if self.peek() else if_token.line
        true_col = self.peek().column if self.peek() else if_token.column
        
        while not self.check('RBRACE') and not self.is_at_end():
            try:
                stmt = self.statement()
                if stmt:
                    true_statements.append(stmt)
            except SyntaxError:
                self.synchronize()
                
        self.consume('RBRACE', "Se esperaba '}' al cerrar el bloque if.")
        true_block = BlockNode(true_statements, true_line, true_col)
        
        false_block = None
        if self.match('ELSE'):
            self.consume('LBRACE', "Se esperaba '{' para iniciar el bloque else.")
            false_statements = []
            false_line = self.peek().line if self.peek() else if_token.line
            false_col = self.peek().column if self.peek() else if_token.column
            
            while not self.check('RBRACE') and not self.is_at_end():
                try:
                    stmt = self.statement()
                    if stmt:
                        false_statements.append(stmt)
                except SyntaxError:
                    self.synchronize()
                    
            self.consume('RBRACE', "Se esperaba '}' al cerrar el bloque else.")
            false_block = BlockNode(false_statements, false_line, false_col)
            
        return IfNode(cond, true_block, if_token.line, if_token.column, false_block)

    def print_statement(self):
        print_token = self.previous()
        self.consume('LPAREN', "Se esperaba '(' después de 'print'.")
        expr = self.expression()
        self.consume('RPAREN', "Se esperaba ')' después de la expresión en 'print'.")
        return PrintNode(expr, print_token.line, print_token.column)

    def return_statement(self):
        return_token = self.previous()
        expr = self.expression()
        return ReturnNode(expr, return_token.line, return_token.column)

    def expression_statement(self):
        expr = self.expression()
        return expr

    def expression(self):
        return self.logic_or()

    def logic_or(self):
        expr = self.logic_and()
        while self.match('OR'):
            op_token = self.previous()
            right = self.logic_and()
            expr = BinOpNode(expr, 'or', right, op_token.line, op_token.column)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.match('AND'):
            op_token = self.previous()
            right = self.equality()
            expr = BinOpNode(expr, 'and', right, op_token.line, op_token.column)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.check('OP') and self.peek().value in ['==', '!=']:
            self.advance()
            op_token = self.previous()
            right = self.comparison()
            expr = BinOpNode(expr, op_token.value, right, op_token.line, op_token.column)
        return expr

    def comparison(self):
        expr = self.term()
        while self.check('OP') and self.peek().value in ['<', '>', '<=', '>=']:
            self.advance()
            op_token = self.previous()
            right = self.term()
            expr = BinOpNode(expr, op_token.value, right, op_token.line, op_token.column)
        return expr

    def term(self):
        expr = self.factor()
        while self.check('OP') and self.peek().value in ['+', '-']:
            self.advance()
            op_token = self.previous()
            right = self.factor()
            expr = BinOpNode(expr, op_token.value, right, op_token.line, op_token.column)
        return expr

    def factor(self):
        expr = self.power()
        while self.check('OP') and self.peek().value in ['*', '/', '%']:
            self.advance()
            op_token = self.previous()
            right = self.power()
            expr = BinOpNode(expr, op_token.value, right, op_token.line, op_token.column)
        return expr

    def power(self):
        expr = self.unary()
        if self.check('OP') and self.peek().value == '^':
            self.advance()
            op_token = self.previous()
            right = self.power()
            expr = BinOpNode(expr, '^', right, op_token.line, op_token.column)
        return expr

    def unary(self):
        if self.match('NOT') or (self.check('OP') and self.peek().value in ['-', '+']):
            if self.previous().type != 'NOT':
                self.advance()
            op_token = self.previous()
            expr = self.unary()
            return UnaryOpNode(op_token.value, expr, op_token.line, op_token.column)
        return self.primary()

    def primary(self):
        if self.match('TRUE'):
            t = self.previous()
            return BooleanNode(True, t.line, t.column)
        if self.match('FALSE'):
            t = self.previous()
            return BooleanNode(False, t.line, t.column)
        if self.match('INT') or self.match('REAL'):
            t = self.previous()
            return NumberNode(t.value, t.line, t.column)
        if self.match('STRING'):
            t = self.previous()
            return StringNode(t.value, t.line, t.column)
            
        built_ins = {'sin', 'cos', 'tan', 'sqrt', 'log', 'abs', 'floor', 'ceil'}
        if self.check('ID') and self.peek().value in built_ins:
            func_token = self.advance()
            self.consume('LPAREN', f"Se esperaba '(' después de la función integrada '{func_token.value}'.")
            expr = self.expression()
            self.consume('RPAREN', f"Se esperaba ')' después de la expresión en la función '{func_token.value}'.")
            return FuncCallNode(func_token.value, [expr], func_token.line, func_token.column)
            
        if self.match('ID'):
            id_token = self.previous()
            if self.match('LPAREN'):
                args = []
                if not self.check('RPAREN'):
                    args.append(self.expression())
                    while self.match('COMMA'):
                        args.append(self.expression())
                self.consume('RPAREN', "Se esperaba ')' después de los argumentos de la función.")
                return FuncCallNode(id_token.value, args, id_token.line, id_token.column)
            else:
                return VariableNode(id_token.value, id_token.line, id_token.column)
                
        if self.match('LPAREN'):
            expr = self.expression()
            self.consume('RPAREN', "Se esperaba ')' al cerrar la expresión entre paréntesis.")
            return expr
            
        token = self.peek()
        line = token.line if token else (self.previous().line if self.previous() else 1)
        col = token.column if token else (self.previous().column if self.previous() else 1)
        val = f"'{token.value}'" if token else "fin de archivo"
        err = f"Error Sintáctico [L:{line}, C:{col}]: Expresión inválida en {val}."
        self.errors.append(err)
        raise SyntaxError(err)
