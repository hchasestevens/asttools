import re
import ast
import copy
import inspect
import functools

import astor
from meta.decompiler import decompile_func


class NameReplacer(ast.NodeTransformer):
    def __init__(self, replacements):
        self.replacements = replacements

    def visit_Name(self, node):
        if node.id in self.replacements:
            replacement = self.replacements[node.id]
            if isinstance(replacement, list):
                if len(replacement) > 1:
                    return ast.If(
                        test=ast.Num(n=1),
                        body=replacement,
                        orelse=[]
                    )
                return replacement[0]
            return replacement
        return self.generic_visit(node)


def get_source(fn):
    # type: (Callable) -> str
    """Return source code of given function."""
    raw_source = inspect.getsource(fn)
    initial_whitespace = re.match(r'^\s+', raw_source)
    if initial_whitespace is None:
        return raw_source

    indentation_len = len(initial_whitespace.group())
    return '\n'.join(
        line[indentation_len:]
        for line in raw_source.splitlines()
    )


def get_ast(fn):
    # type: (Callable) -> ast.FunctionDef
    """Return FunctionDef AST node for given function."""
    try:
        return ast.parse(get_source(fn)).body[0]
    except IOError:
        return decompile_func(fn)


def quoted(fn):
    # type: (Callable) -> List[ast.AST]
    """
    Return the code literal represented in the function body.
    """
    return get_ast(fn).body


def quoted_template(fn):
    # type: (Callable) -> Callable[..., List[ast.AST]]
    """
    Return a function which, supplied with AST nodes, will
    populate and return the specified template body.
    """
    fn_node = get_ast(fn)
    argnames = [
        name.id
        if hasattr(name, 'id')
        else name.arg
        for name in fn_node.args.args
    ]

    @functools.wraps(fn)
    def wrapper(*args):
        argdict = dict(zip(argnames, args))
        populated_template = NameReplacer(argdict).visit(copy.deepcopy(fn_node))
        # round-robin AST -> source -> AST conversion to fix type mismatches
        return ast.parse(
            astor.to_source(
                ast.Module(
                    body=populated_template.body
                )
            )
        ).body

    return wrapper
