"""Worked example: see a real AST with Python's built-in ast module. Runs offline."""
import ast

code = """
class Cart:
    def add(self, item):
        self.items.append(item)

    def total(self):
        return sum(i.price for i in self.items)
"""
tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
        print(type(node).__name__, node.name,
              "lines", node.lineno, "to", node.end_lineno)
