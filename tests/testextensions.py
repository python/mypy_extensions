import collections.abc
import pickle
import sys
import typing
import warnings
from contextlib import contextmanager
from unittest import TestCase, main
from mypy_extensions import TypedDict, i64, i32, i16, u8


class BaseTestCase(TestCase):

    def assertIsSubclass(self, cls, class_or_tuple, msg=None):
        if not issubclass(cls, class_or_tuple):
            message = '%r is not a subclass of %r' % (cls, class_or_tuple)
            if msg is not None:
                message += ' : %s' % msg
            raise self.failureException(message)

    def assertNotIsSubclass(self, cls, class_or_tuple, msg=None):
        if issubclass(cls, class_or_tuple):
            message = '%r is a subclass of %r' % (cls, class_or_tuple)
            if msg is not None:
                message += ' : %s' % msg
            raise self.failureException(message)


with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)

    Label = TypedDict('Label', [('label', str)])

    class Point2D(TypedDict):
        x: int
        y: int

    class LabelPoint2D(Point2D, Label): ...

    class Options(TypedDict, total=False):
        log_level: int
        log_path: str


class TypedDictTests(BaseTestCase):
    @contextmanager
    def assert_typeddict_deprecated(self):
        with self.assertWarnsRegex(
            DeprecationWarning, "mypy_extensions.TypedDict is deprecated"
        ):
            yield

    def test_basics_iterable_syntax(self):
        with self.assert_typeddict_deprecated():
            Emp = TypedDict('Emp', {'name': str, 'id': int})
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections.abc.Sequence)
        jim = Emp(name='Jim', id=1)
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, __name__)
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})
        self.assertEqual(Emp.__total__, True)

    def test_basics_keywords_syntax(self):
        with self.assert_typeddict_deprecated():
            Emp = TypedDict('Emp', name=str, id=int)
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections.abc.Sequence)
        jim = Emp(name='Jim', id=1)  # type: ignore # mypy doesn't support keyword syntax yet
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, __name__)
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})
        self.assertEqual(Emp.__total__, True)

    def test_typeddict_errors(self):
        with self.assert_typeddict_deprecated():
            Emp = TypedDict('Emp', {'name': str, 'id': int})
        self.assertEqual(TypedDict.__module__, 'mypy_extensions')
        jim = Emp(name='Jim', id=1)
        with self.assertRaises(TypeError):
            isinstance({}, Emp)  # type: ignore
        with self.assertRaises(TypeError):
            isinstance(jim, Emp)  # type: ignore
        with self.assertRaises(TypeError):
            issubclass(dict, Emp)  # type: ignore
        with self.assertRaises(TypeError), self.assert_typeddict_deprecated():
            TypedDict('Hi', x=())
        with self.assertRaises(TypeError), self.assert_typeddict_deprecated():
            TypedDict('Hi', [('x', int), ('y', ())])
        with self.assertRaises(TypeError):
            TypedDict('Hi', [('x', int)], y=int)

    def test_py36_class_syntax_usage(self):
        self.assertEqual(LabelPoint2D.__name__, 'LabelPoint2D')  # noqa
        self.assertEqual(LabelPoint2D.__module__, __name__)  # noqa
        self.assertEqual(LabelPoint2D.__annotations__, {'x': int, 'y': int, 'label': str})  # noqa
        self.assertEqual(LabelPoint2D.__bases__, (dict,))  # noqa
        self.assertEqual(LabelPoint2D.__total__, True)  # noqa
        self.assertNotIsSubclass(LabelPoint2D, typing.Sequence)  # noqa
        not_origin = Point2D(x=0, y=1)  # noqa
        self.assertEqual(not_origin['x'], 0)
        self.assertEqual(not_origin['y'], 1)
        other = LabelPoint2D(x=0, y=1, label='hi')  # noqa
        self.assertEqual(other['label'], 'hi')

    def test_py36_class_usage_emits_deprecations(self):
        with self.assert_typeddict_deprecated():
            class Foo(TypedDict):
                bar: int

    def test_pickle(self):
        global EmpD  # pickle wants to reference the class by name
        with self.assert_typeddict_deprecated():
            EmpD = TypedDict('EmpD', name=str, id=int)
        jane = EmpD({'name': 'jane', 'id': 37})
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)
            self.assertEqual(jane2, {'name': 'jane', 'id': 37})
            ZZ = pickle.dumps(EmpD, proto)
            EmpDnew = pickle.loads(ZZ)
            self.assertEqual(EmpDnew({'name': 'jane', 'id': 37}), jane)

    def test_optional(self):
        with self.assert_typeddict_deprecated():
            EmpD = TypedDict('EmpD', name=str, id=int)

        self.assertEqual(typing.Optional[EmpD], typing.Union[None, EmpD])
        self.assertNotEqual(typing.List[EmpD], typing.Tuple[EmpD])

    def test_total(self):
        with self.assert_typeddict_deprecated():
            D = TypedDict('D', {'x': int}, total=False)
        self.assertEqual(D(), {})
        self.assertEqual(D(x=1), {'x': 1})
        self.assertEqual(D.__total__, False)

        self.assertEqual(Options(), {})  # noqa
        self.assertEqual(Options(log_level=2), {'log_level': 2})  # noqa
        self.assertEqual(Options.__total__, False)  # noqa


native_int_types = [i64, i32, i16, u8]


class MypycNativeIntTests(TestCase):
    def test_construction(self):
        for native_int in native_int_types:
            self.assert_same(native_int(), 0)

            self.assert_same(native_int(0), 0)
            self.assert_same(native_int(1), 1)
            self.assert_same(native_int(-3), -3)
            self.assert_same(native_int(2**64), 2**64)
            self.assert_same(native_int(-2**64), -2**64)

            self.assert_same(native_int(1.234), 1)
            self.assert_same(native_int(2.634), 2)
            self.assert_same(native_int(-1.234), -1)
            self.assert_same(native_int(-2.634), -2)

            self.assert_same(native_int("0"), 0)
            self.assert_same(native_int("123"), 123)
            self.assert_same(native_int("abc", 16), 2748)
            self.assert_same(native_int("-101", base=2), -5)

    def test_isinstance(self):
        for native_int in native_int_types:
            assert isinstance(0, native_int)
            assert isinstance(1234, native_int)
            assert isinstance(True, native_int)
            assert not isinstance(1.0, native_int)

    def test_docstring(self):
        for native_int in native_int_types:
            # Just check that a docstring exists
            assert native_int.__doc__

    def assert_same(self, x, y):
        assert type(x) is type(y)
        assert x == y


class DeprecationTests(TestCase):
    def test_no_return_deprecation(self):
        del sys.modules["mypy_extensions"]
        with self.assertWarnsRegex(
            DeprecationWarning, "'mypy_extensions.NoReturn' is deprecated"
        ):
            import mypy_extensions
            mypy_extensions.NoReturn

        del sys.modules["mypy_extensions"]
        with self.assertWarnsRegex(
            DeprecationWarning, "'mypy_extensions.NoReturn' is deprecated"
        ):
            from mypy_extensions import NoReturn  # noqa: F401


if __name__ == '__main__':
    main()
