#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 12:04:26 2019

@author: jax
"""
from setuptools import setup # , find_packages
from distutils.dir_util import copy_tree
setup(
    name="qis_job",
    version="3.0",
    description="Run Qiskit jobs from command line",
    url="hhtps://github.com/jwoehr/qis_job",
    author="Jack Woehr",
    author_email="jwoehr@softwoehr.com",
    license="Apache 2.0",
    packages=['qis_job'],
    include_package_data=True,
    package_data={ 'qis_job' : ['share/*examples'] },
    scripts=['scripts/qisjob'],
    zip_safe=False
)

copy_tree('share/qasm_examples', '/share/qis_job')
copy_tree('share/qc_examples', '/share/qis_job')
