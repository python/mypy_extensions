# Adapted from typeshed (Apache-2.0); see LICENSE.typeshed.
import abc
from collections.abc import ItemsView, KeysView, Mapping, ValuesView
from typing import Any, ClassVar, Generic, Protocol, TypeVar, overload, type_check_only
from typing_extensions import Never, Self, deprecated

_T = TypeVar("_T")
_U = TypeVar("_U")

class _IdentityFunction(Protocol):
    def __call__(self, arg: _T, /) -> _T: ...

# Internal mypy fallback type for all typed dicts (does not exist at runtime)
# N.B. Keep this mostly in sync with typing(_extensions)._TypedDict
@type_check_only
@deprecated("Use typing._TypedDict instead")
class _TypedDict(Mapping[str, object], metaclass=abc.ABCMeta):
    __total__: ClassVar[bool]
    # Unlike typing(_extensions).TypedDict,
    # subclasses of mypy_extensions.TypedDict do NOT have the __required_keys__ and __optional_keys__ ClassVars
    def copy(self) -> Self: ...
    # Using Never so that only calls using mypy plugin hook that specialize the signature
    # can go through.
    def setdefault(self, k: Never, default: object) -> object: ...
    # Mypy plugin hook for 'pop' expects that 'default' has a type variable type.
    def pop(self, k: Never, default: _T = ...) -> object: ...  # pyright: ignore[reportInvalidTypeVarUse]
    def update(self, m: Self, /) -> None: ...
    def items(self) -> ItemsView[str, object]: ...
    def keys(self) -> KeysView[str]: ...
    def values(self) -> ValuesView[object]: ...
    def __delitem__(self, k: Never) -> None: ...

    @overload
    def __or__(self, value: Self, /) -> Self: ...
    @overload
    def __or__(self, value: dict[str, Any], /) -> dict[str, object]: ...

    @overload
    def __ror__(self, value: Self, /) -> Self: ...
    @overload
    def __ror__(self, value: dict[str, Any], /) -> dict[str, object]: ...

    # supposedly incompatible definitions of `__or__` and `__ior__`:
    def __ior__(self, value: Self, /) -> Self: ...  # type: ignore[misc]

@deprecated("Use typing.TypedDict or typing_extensions.TypedDict instead")
def TypedDict(typename: str, fields: dict[str, type[Any]], total: bool = ...) -> type[dict[str, Any]]: ...

@overload
def Arg(type: _T, name: str | None = ...) -> _T: ...
@overload
def Arg(*, name: str | None = ...) -> Any: ...

@overload
def DefaultArg(type: _T, name: str | None = ...) -> _T: ...
@overload
def DefaultArg(*, name: str | None = ...) -> Any: ...

@overload
def NamedArg(type: _T, name: str | None = ...) -> _T: ...
@overload
def NamedArg(*, name: str | None = ...) -> Any: ...

@overload
def DefaultNamedArg(type: _T, name: str | None = ...) -> _T: ...
@overload
def DefaultNamedArg(*, name: str | None = ...) -> Any: ...

@overload
def VarArg(type: _T) -> _T: ...
@overload
def VarArg() -> Any: ...

@overload
def KwArg(type: _T) -> _T: ...
@overload
def KwArg() -> Any: ...

# Return type that indicates a function does not return.
@deprecated("Use typing.Never instead")
class NoReturn: ...

# This is consistent with implementation. Usage intends for this as
# a class decorator, but mypy does not support type[_T] for abstract
# classes until this issue is resolved, https://github.com/python/mypy/issues/4717.
def trait(cls: _T) -> _T: ...
def mypyc_attr(*attrs: str, **kwattrs: object) -> _IdentityFunction: ...

class FlexibleAlias(Generic[_T, _U]): ...

# Mypy and mypyc treat these native int types as different from 'int', but this is
# a non-standard extension. For other tools, aliasing these to 'int' allows them
# to mostly do the right thing with these types.
i64 = int
i32 = int
i16 = int
i8 = int
u64 = int
u32 = int
u16 = int
u8 = int
