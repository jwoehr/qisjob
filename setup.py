#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 12:04:26 2019

@author: jax
"""
from setuptools import setup

setup(
    name="qisjob",
    version="4.1.2.dev0",
    description="Run Qiskit jobs from command line",
    url="https://github.com/jwoehr/qisjob",
    author="Jack Woehr",
    author_email="jwoehr@softwoehr.com",
    license="Apache 2.0",
    packages=["qisjob"],
    data_files=[
        (
            "share/qisjob/qasm_examples",
            [
                "share/qasm_examples/entangle.qasm",
                "share/qasm_examples/ghzstate3q.qasm",
                "share/qasm_examples/ghzxxx.qasm",
                "share/qasm_examples/ghzxyx.qasm",
                "share/qasm_examples/ghzxyy.qasm",
                "share/qasm_examples/ghzyxy.qasm",
                "share/qasm_examples/ghzyyx.qasm",
                "share/qasm_examples/mermin_inequality_a.qasm",
                "share/qasm_examples/mermin_inequality_b.qasm",
                "share/qasm_examples/mermin_inequality_c.qasm",
                "share/qasm_examples/mermin_inequality_d.qasm",
                "share/qasm_examples/multimeasure.qasm",
                "share/qasm_examples/onebit.qasm",
                "share/qasm_examples/yiqing.qasm",
                "share/qasm_examples/yiqing_simple.qasm",
            ],
        ),
        ("share/qisjob/qc_examples", ["share/qc_examples/google_quantum_supremacy.py"]),
    ],
    scripts=["scripts/qisjob"],
    zip_safe=False,
    modules=["qisjob/qisjob, qisjob/qisjobtk"],
)
