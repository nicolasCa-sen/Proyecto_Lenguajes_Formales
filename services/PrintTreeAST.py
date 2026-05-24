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

def print_ast(node, indent="", is_last=True):
    if node is None:
        return

    marker = "└── " if is_last else "├── "
    
    pos = f" [L:{node.line}, C:{node.column}]" if hasattr(node, 'line') else ""
    print(indent + (marker if indent else "") + get_node_label_clean(node) + pos)

    children = get_children(node)
    new_indent = indent + ("    " if is_last else "│   ")

    if children:
        for i, child in enumerate(children):
            last_child = (i == len(children) - 1)
            print_ast(child, new_indent, last_child)

def get_node_label_clean(node):
    if isinstance(node, NumberNode): return f"Value: {node.value}"
    if isinstance(node, VariableNode): return f"Id: {node.name}"
    if isinstance(node, BinOpNode): return f"Op: {node.op}"
    if isinstance(node, AssignNode): return f"let {node.name}"
    if isinstance(node, PrintNode): return "print"
    if isinstance(node, IfNode): return "if"
    if isinstance(node, WhileNode): return "while"
    if isinstance(node, FuncDefNode): return f"def {node.name}"
    if isinstance(node, FuncCallNode): return f"call {node.name}"
    if isinstance(node, ReturnNode): return "return"
    if isinstance(node, BlockNode): return "block"
    return "?"

def get_children(node):
    if isinstance(node, BinOpNode): return [node.left, node.right]
    if isinstance(node, AssignNode): return [node.value]
    if isinstance(node, IfNode):
        children = [node.condition, node.if_block]
        if node.else_block: children.append(node.else_block)
        return children
    if isinstance(node, WhileNode): return [node.condition, node.body]
    if isinstance(node, BlockNode): return node.statements
    if isinstance(node, FuncDefNode): return [node.body]
    if isinstance(node, ReturnNode): return [node.expression]
    if isinstance(node, PrintNode): return [node.expression]
    if isinstance(node, FuncCallNode): return node.args
    return []

#Convierte el AST en un diccionario/JSON para que la interfaz web lo dibuje.
def ast_to_dict(node):
    if node is None:
        return None
        
    label = get_node_label_clean(node)

    if hasattr(node, 'inferred_type'):
        label += f" ({node.inferred_type})"
        
    children_nodes = get_children(node)
    
    return {
        "name": label,
        "children": [ast_to_dict(child) for child in children_nodes] if children_nodes else []
    }