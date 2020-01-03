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
    data_files=[('share/qisjob/qasm_examples',
                 ['share/qasm_examples/ghzstate3q.qasm',
                  'share/qasm_examples/ghzxxx.qasm',
                  'share/qasm_examples/ghzxyx.qasm',
                  'share/qasm_examples/ghzxyy.qasm',
                  'share/qasm_examples/ghzyxy.qasm',
                  'share/qasm_examples/ghzyyx.qasm',
                  'share/qasm_examples/mermin_inequality_a.qasm',
                  'share/qasm_examples/mermin_inequality_b.qasm',
                  'share/qasm_examples/mermin_inequality_c.qasm',
                  'share/qasm_examples/mermin_inequality_d.qasm',
                  'share/qasm_examples/yiqing.qasm',
                  'share/qasm_examples/yiqing_simple.qasm']),
                ('share/qisjob/qc_examples',
                 ['share/qc_examples/google_quantum_supremacy.py'])],
    scripts=['scripts/qisjob'],
    zip_safe=False,
    ext_modules=cythonize("qis_job/qis_job.pyx",
                          compiler_directives={'language_level': "3"})
)
