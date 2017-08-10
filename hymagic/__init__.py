import argparse
import code
import ast
import sys

import hy

from hy.lex import LexException, PrematureEndOfInput, tokenize
from hy.compiler import hy_compile, HyTypeError
from hy.importer import ast_compile, import_buffer_to_module
from hy.completer import completion
from hy.macros import macro, require
from hy import HyExpression, HyString, HySymbol
from hy._compat import builtins

from IPython.core import magic


SIMPLE_TRACEBACKS = True



@magic.magics_class
class HylangMagics(magic.Magics):
    """Magic for the hylang lisp language
    """
    def __init__(self, shell):
        """
        Parameters
        ----------
        shell : IPython shell

        """
        super(HylangMagics, self).__init__(shell)

    @magic.line_cell_magic
    def hylang(self, line, cell=None, filename='<input>', symbol='single'):
        """ Ipython magic function for running hylang code in ipython
        Use %hylang one line of code or
            %%hylang for a block or cell
            Note that we pass the AST directly to IPython."""

        global SIMPLE_TRACEBACKS
        source = cell if cell else line

        try:
            tokens = tokenize(source)
        except PrematureEndOfInput:
            print( "Premature End of Input" )
        except LexException as e:
            if e.source is None:
                e.source = source
                e.filename = filename
            print(str(e))

        try:
            _ast = hy_compile(tokens, "__console__", root=ast.Interactive)
            self.shell.run_ast_nodes(_ast.body,'<input>',compiler=ast_compile)
        except HyTypeError as e:
            if e.source is None:
                e.source = source
                e.filename = filename
            if SIMPLE_TRACEBACKS:
                print(str(e))
            else:
                self.shell.showtraceback()
        except Exception:
            self.shell.showtraceback()

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(HylangMagics)
    # magic_kind='line_cell' is not supported any more for some reason
    ip.magics_manager.register_alias('hy', 'hylang', magic_kind='line')
    ip.magics_manager.register_alias('hy', 'hylang', magic_kind='cell')
