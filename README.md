from setuptools import setup, find_packages

from table_compare._version import __version__
setup(
    name='table_compare',
    version=__version__,
    packages=find_packages(exclude=[
        'test',
    ]),
    install_requires=[
        'pandas',
        'openpyxl',
        'numpy'
    ],
    extras_require={
        'test': [
        'nose'
        ],
    },
)