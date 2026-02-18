"""
Python 3.12 language reference (frozen).
Source: docs.python.org/3.12 (keywords, builtins, exceptions),
        docs.python.org/3.12/reference/datamodel.html (special method names).
Use these sets for analytics so results are version-stable regardless of
the interpreter running the script.
"""

# --- Keywords (3.12): Lib/keyword.py from cpython 3.12 ---
# hard keywords
PY312_KWLIST = frozenset({
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
})
# soft keywords (3.10+); in 3.12: _, case, match, type (no 'lazy' - that's 3.13)
PY312_SOFTKWLIST = frozenset({"_", "case", "match", "type"})
PY312_KEYWORDS = PY312_KWLIST | PY312_SOFTKWLIST

# --- Built-in names (3.12): library/functions.html + types + exceptions ---
# Functions (68 + __import__, __build_class__)
PY312_BUILTIN_FUNCTIONS = frozenset({
    "abs", "aiter", "all", "anext", "any", "ascii", "bin", "bool", "breakpoint",
    "bytearray", "bytes", "callable", "chr", "classmethod", "compile", "complex",
    "delattr", "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter",
    "float", "format", "frozenset", "getattr", "globals", "hasattr", "hash",
    "help", "hex", "id", "input", "int", "isinstance", "issubclass", "iter",
    "len", "list", "locals", "map", "max", "memoryview", "min", "next",
    "object", "oct", "open", "ord", "pow", "print", "property", "range",
    "repr", "reversed", "round", "set", "setattr", "slice", "sorted",
    "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip",
    "__import__", "__build_class__",
})
# Constants / types exposed in builtins (3.12; no frozendict - 3.13)
PY312_BUILTIN_CONSTANTS_AND_TYPES = frozenset({
    "None", "Ellipsis", "NotImplemented", "False", "True",
    "bool", "memoryview", "bytearray", "bytes", "classmethod", "complex",
    "dict", "enumerate", "filter", "float", "frozenset", "property", "int",
    "list", "map", "object", "range", "reversed", "set", "slice",
    "staticmethod", "str", "super", "tuple", "type", "zip",
})
# Built-in exceptions (3.12): library/exceptions.html
PY312_BUILTIN_EXCEPTIONS = frozenset({
    "BaseException", "Exception", "ArithmeticError", "AssertionError",
    "AttributeError", "BlockingIOError", "BrokenPipeError", "BufferError",
    "BytesWarning", "ChildProcessError", "ConnectionAbortedError",
    "ConnectionError", "ConnectionRefusedError", "ConnectionResetError",
    "DeprecationWarning", "EOFError", "EncodingWarning", "EnvironmentError",
    "FileExistsError", "FileNotFoundError", "FloatingPointError",
    "FutureWarning", "GeneratorExit", "OSError", "ImportError",
    "ImportWarning", "IndentationError", "IndexError", "InterruptedError",
    "IsADirectoryError", "KeyError", "KeyboardInterrupt", "LookupError",
    "MemoryError", "ModuleNotFoundError", "NameError", "NotImplementedError",
    "OverflowError", "PendingDeprecationWarning", "PermissionError",
    "ProcessLookupError", "RecursionError", "ReferenceError", "ResourceWarning",
    "RuntimeError", "RuntimeWarning", "StopAsyncIteration", "StopIteration",
    "SyntaxError", "SyntaxWarning", "SystemError", "SystemExit", "TabError",
    "TimeoutError", "TypeError", "UnboundLocalError", "UnicodeDecodeError",
    "UnicodeEncodeError", "UnicodeError", "UnicodeTranslateError", "UnicodeWarning",
    "UserWarning", "ValueError", "Warning", "ZeroDivisionError",
    "BaseExceptionGroup", "ExceptionGroup",
})
# All built-in names (union; exclude keywords that are also in builtins like True/False/None)
PY312_BUILTINS = (
    PY312_BUILTIN_FUNCTIONS
    | PY312_BUILTIN_CONSTANTS_AND_TYPES
    | PY312_BUILTIN_EXCEPTIONS
)

# --- Special (dunder) method names (3.12): reference/datamodel.html ---
PY312_SPECIAL_METHODS = frozenset({
    # Basic customization
    "__init__", "__new__", "__del__", "__repr__", "__str__", "__bytes__",
    "__format__", "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__hash__", "__bool__", "__getattribute__", "__getattr__", "__setattr__",
    "__delattr__", "__dir__", "__set_name__", "__init_subclass__", "__prepare__",
    "__instancecheck__", "__subclasscheck__", "__class_getitem__",
    # Descriptors
    "__get__", "__set__", "__delete__", "__set_name__",
    # Callable
    "__call__",
    # Container / sequence
    "__len__", "__length_hint__", "__getitem__", "__setitem__", "__delitem__",
    "__iter__", "__reversed__", "__contains__", "__missing__",
    # Numeric (binary)
    "__add__", "__sub__", "__mul__", "__matmul__", "__truediv__", "__floordiv__",
    "__mod__", "__divmod__", "__pow__", "__lshift__", "__rshift__", "__and__",
    "__xor__", "__or__",
    "__radd__", "__rsub__", "__rmul__", "__rmatmul__", "__rtruediv__",
    "__rfloordiv__", "__rmod__", "__rdivmod__", "__rpow__", "__rlshift__",
    "__rrshift__", "__rand__", "__rxor__", "__ror__",
    "__iadd__", "__isub__", "__imul__", "__imatmul__", "__itruediv__",
    "__ifloordiv__", "__imod__", "__ipow__", "__ilshift__", "__irshift__",
    "__iand__", "__ixor__", "__ior__",
    # Numeric (unary / conversion)
    "__neg__", "__pos__", "__abs__", "__invert__", "__complex__", "__int__",
    "__float__", "__index__", "__round__", "__trunc__", "__floor__", "__ceil__",
    # Context manager
    "__enter__", "__exit__",
    # Async
    "__await__", "__aiter__", "__anext__", "__aenter__", "__aexit__",
    # Coroutine
    "__coroutine__",
    # Buffer / memoryview
    "__buffer__", "__release_buffer__",
    # Module / class
    "__mro_entries__", "__getnewargs__", "__getnewargs_ex__",
    # Copy / reduce
    "__reduce__", "__reduce_ex__", "__copy__", "__deepcopy__",
    # String (legacy format)
    "__format__",
    # Slot names used by C API / internals (optional for analytics)
    "__doc__", "__module__", "__name__", "__qualname__", "__class__",
    "__dict__", "__weakref__", "__bases__", "__mro__", "__subclasses__",
    "__sizeof__", "__fspath__",
})
