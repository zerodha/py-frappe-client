#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open as codecs_open


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = codecs_open('README.rst', encoding="utf8").read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


version = '1.3.0'

setup(
    name='py-frappe-client',
    version=version,
    install_requires=requirements,
    author='Karan Sharma',
    author_email='karansharma1295@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/zerodhatech/py-frappe-client/',
    license='MIT',
    description='Python wrapper for Frappe API',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
