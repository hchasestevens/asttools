"""Utilities for AST tools"""

import ast
import builtins


class QuotationValidator(ast.NodeVisitor):
    """
    Ensures that an asttools quotation has no unaccounted for Names (implying
    missing imports).
    """

    def __init__(self):
        self.loaded_names = set()
        self.accounted_for_names = set(dir(builtins))

    def visit_Name(self, node):
        groups = {
            ast.Load: self.loaded_names,
            ast.Store: self.accounted_for_names,
        }
        groups[node.ctx.__class__].add(node.id)

    def visit_Import(self, node):
        self.accounted_for_names |= {alias.asname or alias.name for alias in node.names}

    def visit_ImportFrom(self, node):
        self.accounted_for_names |= {alias.asname or alias.name for alias in node.names}

    def visit_FunctionDef(self, node):
        self.accounted_for_names.add(node.name)
        self.accounted_for_names.update(node.args.args)

    def visit_ClassDef(self, node):
        self.accounted_for_names.add(node.name)

    @property
    def unaccounted_for_names(self):
        return self.loaded_names - self.accounted_for_names

    @classmethod
    def validate(cls, quote_nodes):
        """Validate @quoted functions."""
        validator = QuotationValidator()
        for node in quote_nodes:
            validator.visit(node)
        assert not validator.unaccounted_for_names
        return quote_nodes

    @classmethod
    def validate_template(cls, template_fn):
        """Validated @quoted_template functions."""
        @functools.wraps(template_fn)
        def wrapper(*args, **kwargs):
            template_nodes = template_fn(*args, **kwargs)
            cls.validate(template_nodes)
            return template_nodes
        return wrapper


def get_ast_definitions(module_node, environment={}):
    """Return definitions made within node."""
    code = compile(module_node, filename='', mode='exec')
    env = environment.copy()
    exec(code, env)
    return env
