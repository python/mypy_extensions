Mypy Extensions
===============

The `mypy_extensions` module defines extensions to the Python standard
library `typing` module that are supported by the mypy type checker and
the mypyc compiler.

Type declarations are bundled with the package (PEP 561). Mypy versions that
ship their own mypy-extensions stubs continue to use those declarations. The
bundled declarations are adapted from typeshed under Apache-2.0; the runtime
implementation remains MIT-licensed. See LICENSE and LICENSE.typeshed.
