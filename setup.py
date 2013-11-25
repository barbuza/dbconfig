# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='dbconfig',
    version='0.2.0',
    packages=['dbconfig'],
    package_data={
        '': ['templates/admin/dbconfig_list.html']
    },
    install_requires=[
        'django',
    ],
    author='Viktor Kotseruba',
    author_email='barbuzaster@gmail.com',
    description='store config in database',
    license='MIT',
    keywords='config web django',
    zip_safe=False
)
