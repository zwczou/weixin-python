# -*- coding: utf-8 -*-


import re
import ast
import os

from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('weixin/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')
    ).group(1)))


def fread(fname):
    filepath = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(filepath):
        with open(filepath) as f:
            return f.read()

setup(
    name='weixin-python',
    description='Weixin for Python',
    long_description=fread('docs/quickstart.rst'),
    license='BSD',
    packages=find_packages(),
    version=version,
    author='zwczou',
    author_email='zwczou@gmail.com',
    url='https://github.com/zwczou/weixin-python',
    keywords=['weixin', 'weixin pay', 'weixin login', 'weixin mp', 'weixin python'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        "requests",
        "lxml"
    ],
    classifiers=[],
)
