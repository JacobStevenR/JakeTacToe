#This package has not been distributed to PyPI

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="JakeTacToe"

    version="0.1.0"

    author="Jake Rebe"

    packages=['JakeTacToe']

    install_requires=['nose']

    url='https://github.com/JacobStevenR/JakeTacToe'

    

)
