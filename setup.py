"""A setuptools based setup module.
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='json_builder',
    version='1.0.0',
    description='A utility for Autodesk Maya that can be used to assemble scene objects and attributes '
                'and output their names and values as a JSON file.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ldlafontaine/json_assembler',  # Optional
    author='Lucas LaFontaine',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=2.7, <3',
)
