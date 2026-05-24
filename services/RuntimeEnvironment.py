class RuntimeEnvironment:
    def __init__(self, parent=None):
        self.variables = {}  # { 'x': 5, 'pi': 3.14 }
        self.parent = parent # Ámbito superior (Scope)

    #Asigna o actualiza una variable en el entorno actual.
    def set(self, name, value):
        self.variables[name] = value

    #Busca el valor de una variable de forma recursiva hacia arriba.
    def get(self, name, node):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name, node)
        # Seguridad extra por si acaso
        raise RuntimeError(f"Error en tiempo de ejecución [L:{node.line}, C:{node.column}]: Variable '{name}' no definida.")