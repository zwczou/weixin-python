# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(
    name='weixin-python',
    description='Weixin for python',
    long_description=open("README.md").read(),
    license = 'BSD',
    packages = find_packages(),
    version='0.2.1',
    author='zwczou',
    author_email='zwczou@gmail.com',
    url='https://github.com/zwczou/weixin-python',
    keywords=['weixin', 'weixin pay', 'weixin login'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
    ],
    classifiers=[],
)
