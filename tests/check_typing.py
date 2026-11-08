"""Check installed declarations and built artifacts (run via tox -e typing)."""
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
wheel, = (root / 'dist').glob('*.whl')
sdist, = (root / 'dist').glob('*.tar.gz')
with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
    for asset in ['__init__.py', '__init__.pyi', 'py.typed']:
        assert f'mypy_extensions/{asset}' in names
    assert any(n.endswith('/licenses/LICENSE.typeshed') for n in names)
with tarfile.open(sdist) as archive:
    names = archive.getnames()
    assert any(n.endswith('/mypy_extensions/__init__.pyi') for n in names)
    assert any(n.endswith('/LICENSE.typeshed') for n in names)

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    # Running outside the checkout prevents a source-tree import from hiding
    # packaging problems. Tox installs a built package into its environment.
    probe = subprocess.check_output(
        [sys.executable, '-c', 'import mypy_extensions; print(mypy_extensions.__file__)'],
        cwd=directory, text=True,
    ).strip()
    assert 'site-packages' in Path(probe).parts
    assert Path(probe).with_suffix('.pyi').is_file()
    positive = directory / 'positive.py'
    positive.write_text('''from mypy_extensions import mypyc_attr, trait, i64
@trait
class Example:
    pass
@mypyc_attr("trait")
class Decorated:
    pass
number: int = i64(3)
''')
    negative = directory / 'negative.py'
    negative.write_text('from mypy_extensions import mypyc_attr, i64\n'
                        'mypyc_attr(123)\nnumber: str = i64(3)\n')
    for checker in ['mypy', 'pyright']:
        command = [sys.executable, '-m', checker]
        if checker == 'mypy':
            command += ['--strict', '--no-incremental']
        else:
            command += ['--pythonpath', sys.executable]
        subprocess.run(command + [str(positive)], cwd=directory, check=True)
        if checker == 'mypy':
            trace = subprocess.run(command + ['--verbose', str(positive)], cwd=directory,
                                   capture_output=True, text=True, check=True)
            assert 'typeshed/stubs/mypy-extensions/mypy_extensions.pyi' in trace.stderr
        result = subprocess.run(command + [str(negative)], cwd=directory,
                                capture_output=True, text=True)
        assert result.returncode == 1, result.stdout + result.stderr
        assert '2 errors' in result.stdout, result.stdout
    # Trace Pyright's resolution to ensure it uses the installed stub rather
    # than bundled typeshed. Mypy deliberately retains its bundled declarations.
    result = subprocess.run(
        [sys.executable, '-m', 'pyright', '--dependencies', '--verbose', '--pythonpath',
         sys.executable, str(positive)], cwd=directory, capture_output=True, text=True,
        check=True,
    )
    assert str(Path(probe).with_suffix('.pyi')) in result.stdout, result.stdout
print('Installed declarations and wheel/sdist assets verified')
