# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


setup(
    name='weixin-python',
    license = 'BSD',
    ppackages = find_packages(),
    version='0.1.3',
    description='Weixin for python',
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
