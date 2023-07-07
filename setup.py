from setuptools import setup

version = '1.0.0-dev'
description = 'Type system extensions for programs checked with the mypy type checker.'
long_description = '''
Mypy Extensions
===============

The "mypy_extensions" module defines extensions to the standard "typing" module
that are supported by the mypy type checker and the mypyc compiler.
'''.lstrip()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Topic :: Software Development',
]

setup(
    name='mypy_extensions',
    python_requires='>=3.7',
    version=version,
    description=description,
    long_description=long_description,
    author='The mypy developers',
    author_email='jukka.lehtosalo@iki.fi',
    url='https://github.com/python/mypy_extensions',
    license='MIT License',
    py_modules=['mypy_extensions'],
    classifiers=classifiers,
)
