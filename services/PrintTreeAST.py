from components.AssignNode import AssignNode
from components.BlockNode import BlockNode
from components.FuncCallNode import FuncCallNode
from components.FuncDefNode import FuncDefNode
from components.ReturnNode import ReturnNode
from components.IfNode import IfNode
from components.WhileNode import WhileNode
from components.PrintNode import PrintNode
from components.VariableNode import VariableNode
from components.BinOpNode import BinOpNode
from components.NumberNode import NumberNode
from components.StringNode import StringNode
from components.BooleanNode import BooleanNode
from components.UnaryOpNode import UnaryOpNode

def print_ast(node, indent="", is_last=True):
    if node is None:
        return ""

    marker = "└── " if is_last else "├── "
    pos = f" [L:{node.line}, C:{node.column}]" if hasattr(node, 'line') else ""
    line = indent + (marker if indent else "") + get_node_label_clean(node) + pos
    print(line)

    children = get_children(node)
    new_indent = indent + ("    " if is_last else "│   ")

    if children:
        for i, child in enumerate(children):
            if child is not None:
                last_child = (i == len(children) - 1)
                print_ast(child, new_indent, last_child)

def get_node_label_clean(node):
    if isinstance(node, NumberNode): return f"Número: {node.value}"
    if isinstance(node, StringNode): return f"Cadena: \"{node.value}\""
    if isinstance(node, BooleanNode): return f"Booleano: {'true' if node.value else 'false'}"
    if isinstance(node, UnaryOpNode): return f"Op Unaria: {node.op}"
    if isinstance(node, VariableNode): return f"Variable: {node.name}"
    if isinstance(node, BinOpNode): return f"Op Binaria: {node.op}"
    if isinstance(node, AssignNode): return f"let {node.var.name}"
    if isinstance(node, PrintNode): return "print"
    if isinstance(node, IfNode): return "if"
    if isinstance(node, WhileNode): return "while"
    if isinstance(node, FuncDefNode): return f"def {node.name}"
    if isinstance(node, FuncCallNode): return f"Llamada: {node.func_name}"
    if isinstance(node, ReturnNode): return "return"
    if isinstance(node, BlockNode): return "Bloque"
    return "?"

def get_children(node):
    if isinstance(node, BinOpNode): return [node.left, node.right]
    if isinstance(node, UnaryOpNode): return [node.expr]
    if isinstance(node, AssignNode): return [node.value]
    if isinstance(node, IfNode):
        children = [node.condition, node.true_block]
        if node.false_block: children.append(node.false_block)
        return children
    if isinstance(node, WhileNode): return [node.condition, node.body]
    if isinstance(node, BlockNode): return node.statements
    if isinstance(node, FuncDefNode): return [node.body]
    if isinstance(node, ReturnNode): return [node.expression]
    if isinstance(node, PrintNode): return [node.expression]
    if isinstance(node, FuncCallNode): return node.args
    return []

# Convierte el AST en un diccionario/JSON para que la interfaz web lo dibuje.
def ast_to_dict(node):
    if node is None:
        return None
        
    label = get_node_label_clean(node)

    if hasattr(node, 'inferred_type') and node.inferred_type:
        label += f" ({node.inferred_type})"
        
    children_nodes = get_children(node)
    
    return {
        "name": label,
        "children": [ast_to_dict(child) for child in children_nodes if child is not None] if children_nodes else []
    }