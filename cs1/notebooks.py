"""This module contains functions related to Jupyter notebooks 
on the rhodes-notebook.org environment.
"""

import ast
import builtins
import os
import sys

from client.api.notebook import Notebook
from IPython.display import display, Markdown, Latex

# The ok control variable.
_ok = None


def _maybe_login(okfile):
    """Authenticate to OK, if necessary."""
    global _ok
    if not _ok:
        _force_login(okfile)
        
def _force_login(okfile):
    """Authenticate to OK, even if we are already logged in."""
    global _ok
    _ok = None
    _ok = Notebook(okfile)
    _ok.auth(inline=True)

def ok_login(okfile):
    """Authenticate to the OK submission website.
    This is a wrapper around creating a Notebook object and calling auth().
    Will re-authenticate even if we are already logged in.
    
    okfile: the .ok file that describes the OK assignment we are using.
    """
    
    global _ok
    _force_login(okfile)
    
def ok_runtests(okfile, question):
    """Run test cases and grade them using OK.
    
    okfile: the .ok file that describes the OK assignment we are using.
    question: the test file to use.
    """
    
    global _ok
    _maybe_login(okfile)
    _ok.grade(question)
    
def ok_submit(okfile):
    """Submit the current notebook and auxiliary files specified in the .ok file.
    
    okfile: the .ok file that describes the OK assignment we are using.
    """
    
    global _ok
    _maybe_login(okfile)
    _ok.submit()
    display(Markdown('<font size=+1>⚠️ To make sure your submission was successful, '
                     + 'make sure there are no error messages in the output above, and '
                     + 'then click on the URL '
                     + ' to make sure your submission looks correct. ⚠️</font>'))

def reload_functions(filename, verbose=False):
    """Import/re-import all functions from a filename into the __main__ namespace.  
    Python typically ignores subsequent import commands after the first one, this
    function forces the specified file to be re-read and re-imported.  However, 
    any function *calls* are ignored.  
    
    This function came about for two reasons.  First, we typically have students
    call main() at the end of their programs, and when one does "from _____ import *"
    that will end up calling main() when all you want to do is import the functions
    into a notebook so they can be tested.  Furthermore, the IPython %autoreload magic
    is buggy at times, and doesn't always seem to reload the functions, and when it
    does, it still ends up calling main().  Hence this function was designed to solve
    both of those problems: it effectively executes the given Python file in the
    __main__ namespace, but ignores any function calls.  Therefore, function definitons,
    other imports, and global variables/constants will be imported correctly into the
    main notebook space.

    In a notebook cell, one can put:

    from cs1.notebooks import *
    reload_functions("student_project_file.py")

    and then all the functions in the .py file should be available in that notebook
    cell, and any calls to main() or other functions in the .py file will be ignored.

    PS: This functions is also an end-run around us never teaching the 
    if __name__ == "__main__" trick, and now we're paying the price.  :-)
    """
    
    if verbose: print("Reloading functions from", filename)

    with open(filename) as f:
        p = ast.parse(f.read(), filename=filename)

        for node in p.body[:]:
            # accept everything except a function call
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):   
                p.body.remove(node)
                if verbose: print("rejecting", node)
            else:
                if verbose: print("accepting", node)

    # Compile the code and exec it in the __main__ namespace, which contains
    # all the variables for the notebook cells.
    obj = compile(p, filename=filename, mode="exec")
    exec(obj, sys.modules["__main__"].__dict__)
    
_BYTE_LIMIT = 100_000_000 # ~100MB

def open(*args):
    f = builtins.open(*args)
    return _LimitedFile(f, _BYTE_LIMIT)

class FileSizeException(Exception):
    pass

class _LimitedFile(object):
    """A byte-limited file object.
    
    Behaves exactly like File, except for write. All functions delegated to the file supplied
    in the constructor via delegating __getattr__ and __iter__.  Supports `with` using 
    __enter__ and __exit__.
    """
    
    def __init__(self, f, byte_limit):
        """Create a LimitedFile
        
        Args:
            f: file object to wrap.
            byte_limit: total bytes that may be written to file (including existing size).
        """
        self.file = f
        self.byte_count = os.path.getsize(f.name)
        self.byte_limit = byte_limit
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        exit = getattr(self.file, '__exit__', None)
        if exit:
            return exit(*args, **kwargs)
        else:
            exit = getattr(self.file, 'close', None)
            if exit:
                exit()
                
    def __getattr__(self, attr):
        return getattr(self.file, attr)
    
    def __iter__(self):
        return iter(self.file)
        
    def write(self, obj):
        assert isinstance(obj, str), "Cannot write {} (must be string)".format(type(obj))
        size = len(obj.encode('utf-8')) # TODO: this could be optimized. string is encoded twice.
        
        if self.byte_limit > 0 and self.byte_count + size > self.byte_limit:
            raise FileSizeException(
                "Writing would exceed max file size of 100MB ({})".format(self.byte_count+size))
            
        self.byte_count += size
        self.file.write(obj)