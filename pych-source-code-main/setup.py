from setuptools import setup, find_packages

VERSION = '2.2'

setup(
    name='PyCh',
    version=VERSION,
    url='https://github.com/Nickp1993/4DC10',
    license='MIT',
    author='N. Paape',
    author_email='n.paape@tue.nl',
    description='Discrete-event simulation tool for 4DC10',
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        'simpy',
        'dataclasses',
        'numpy',
        'matplotlib'
    ]
)
