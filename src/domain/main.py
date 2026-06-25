class User:
    def __init__(self, id, name, role):
        self.id = id
        self.name = name
        self.role = role


class Role:
    def __init__(self, id, name, position, salary):
        self.id = id
        self.name = name
        self.position = position
        self.salary = salary


class Brand:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name
