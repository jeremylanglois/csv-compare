import pathlib

from setuptools import setup, find_packages

version = {}
path = pathlib.Path.cwd() / 'csv_compare/version.py'
with open("csv_compare/version.py") as fp:
    exec(fp.read(), version)

setup(
    name='table_compare',
    version=version['__version__'],
    packages=find_packages(exclude=[
        'tests',
    ]),
    install_requires=[
        'numpy==1.16.0',
        'pandas==0.24.1'
    ],
    extras_require={
        'tests': [
            # 'nose'
        ],
    },
)
