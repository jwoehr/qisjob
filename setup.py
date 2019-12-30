#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 12:04:26 2019

@author: jax
"""
import sys
from setuptools import setup  # , find_packages
# from distutils.dir_util import copy_tree

try:
    from Cython.Build import cythonize
except ImportError:
    import subprocess
    subprocess.call([sys.executable, '-m', 'pip', 'install', 'Cython>=0.27.1'])
    from Cython.Build import cythonize

setup(
    name="qis_job",
    version="3.0",
    description="Run Qiskit jobs from command line",
    url="https://github.com/jwoehr/qis_job",
    author="Jack Woehr",
    author_email="jwoehr@softwoehr.com",
    license="Apache 2.0",
    packages=['qis_job'],
    include_package_data=True,
    package_data={'qis_job': ['share/*examples']},
    scripts=['scripts/qisjob'],
    zip_safe=False,
    ext_modules=cythonize("qis_job/qis_job.pyx",
                          compiler_directives={'language_level': "3"})
)

# copy_tree('share/qasm_examples', '/share/qis_job')
# copy_tree('share/qc_examples', '/share/qis_job')
