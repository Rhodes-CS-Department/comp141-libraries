"""This module contains functions related to Jupyter notebooks 
on the rhodes-notebook.org environment.
"""

import ast
import builtins
import json
import os
import sys
import urllib

from client.api.notebook import Notebook
from IPython.display import display, Markdown, Latex

# The ok control variable.
_ok = None

# Configs for rewriting ok files.
# If an ok file is not found during at attempted load, a template can be
# used to generate one. This allows for different endpoints for the same
# general ok config without modifying the okpy library.
# The user is presented with the option of choosing a professor (and associated
# endpoint), which are loaded either from a config file in the filesystem,
# or from a url.
# Endpoint options should be a JSON-encoded map. e.g.,
# {
#  "Lang": "rhodes/comp141-01/sp21",
#  "Kirlin": "rhodes/comp141-02/sp21"
# }
_OPTIONS_URL = 'https://storage.googleapis.com/comp141-public/options.json'
_OPTIONS_FNAME = '.options'
_TEMPLATE_FNAME = '.template.ok'
_EP_FNAME = '.141_endpoint'
_EP_PLACEHOLDER = '<#endpoint#>'

def _get_endpoints_file(fname):
    """Returns prof->endpoint map from file, or None."""
    try:
        data = json.load(open(fname))
    except:
        return None
    return data

def _get_endpoints_url(url):
    """Returns prof->endpoint map from url, or None."""
    try:
        data = json.load(urllib.request.urlopen(url))
    except Exception as e:
        return None
    return data

def _get_endpoints():
    """Returns prof->endpoint map from file or url or raises runtime exception."""
    ep = _get_endpoints_file(_OPTIONS_FNAME)
    if not ep:
        ep = _get_endpoints_url(_OPTIONS_URL)
    if not ep:
        raise Exception('No endpoint options loaded, contact your professor.')
    return ep

def _rewrite_template(fname, endpoint):
    """Writes the given ok file from a template.
    
    Replaces any placeholder with the given endpoint.
    """
    if not os.path.isfile(_TEMPLATE_FNAME):
        raise Exception("no template file!")
    ok_contents = open(_TEMPLATE_FNAME).read()
    ok_contents = ok_contents.replace(_EP_PLACEHOLDER, endpoint)
    out = open(fname, "w")
    out.write(ok_contents)
    out.close()

def _validate_or_create(fname, ignore_cache):
    """Validates the existence of .ok file, or creates it.
    
    First checks whether the file exists. If so, nothing is done.
    If the file doesn't exist, an endpoint file in the user's home is looked
    for. If found, a template ok file is re-written with the endpoint.
    If the endpoint does not exist, the user is prompted to chose from a list
    of endpoints, and the chosen endpoint is cached before the file is written.
    """
    if os.path.isfile(fname) and not ignore_cache:
        return
    ep_file = os.path.join(os.path.expanduser("~"), _EP_FNAME)
    if os.path.isfile(ep_file) and not ignore_cache:
        ep = open(ep_file).read()
    else:
        opts = _get_endpoints()
        print("Select a class:")
        ii = dict()
        for i, cls in enumerate(opts):
            print("\t", i, ". ", cls, sep="")
            ii[i] = cls
        choice = int(input())
        if choice not in ii:
            raise Exception("invalid choice")
        ep = opts[ii[choice]]
        out = open(ep_file, 'w')
        out.write(ep)
        out.close()
    _rewrite_template(fname, ep)

def _maybe_login(okfile):
    """Authenticate to OK, if necessary."""
    global _ok
    if not _ok:
        _force_login(okfile, ignore_cache=False)
        
def _force_login(okfile, ignore_cache):
    """Authenticate to OK, even if we are already logged in."""
    global _ok
    _ok = None
    _validate_or_create(okfile, ignore_cache)
    _ok = Notebook(okfile)
    _ok.auth(inline=True)

def ok_login(okfile, ignore_cache=False):
    """Authenticate to the OK submission website.
    This is a wrapper around creating a Notebook object and calling auth().
    Will re-authenticate even if we are already logged in.
    
    okfile: the .ok file that describes the OK assignment we are using.
    ignore_cache: whether to ignore .ok files and endpoint selection.
    """
    
    global _ok
    _force_login(okfile, ignore_cache)
    
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