from setuptools import setup, find_packages
from codecs import open

from os import path

current_path = path.abspath(path.dirname(__file__))

with open(path.join(current_path, 'README,rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='basecode',
    version='0.1.1',
    long_description='web application base',
    url='http://',
    author='d.s.',
    author_email='',
    license='MIT',
    classifiers=[
                    'Development Status :: 5 - Production/Stable',
            'Intended Audience :: xiaoyang web application developer',
            'License :: .... :: ....',
            'Programming Language :: Python :: 2.7'
    ],

    keywords='basecode',
    packages=find_packages(exclude=['settings']),
    install_requires=['falcon == 0.3.0', 'requests == 2.8.1', 'pyjwt == 1.4.0', 'redis == 2.10.5',
                      'pymongo >= 3.0.3', 'jsonschema == 2.5.1'],
)
