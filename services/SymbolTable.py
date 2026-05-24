class Environment:
    def __init__(self, parent=None):
        self.records = {}      # Diccionario: { 'nombre_variable': 'tipo' }
        self.parent = parent    # Referencia al entorno superior (Global)

#Registra una variable en el alcance actual.
    def define(self, name, type_str):
        self.records[name] = type_str
#Busca una variable de forma recursiva hacia arriba.
    def lookup(self, name):
        if name in self.records:
            return self.records[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
#Verifica si ya existe en el alcance actual (para redeclaraciones).
    def is_locally_defined(self, name):
        return name in self.records