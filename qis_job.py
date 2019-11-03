#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qis_job.py
Core routines for qasm_job and qc_job
Created on Sat Nov  2 18:05:21 2019

@author: jax
"""

from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit import __qiskit_version__
from qiskit.compiler import transpile
from qiskit.tools.monitor import job_monitor


def verbosity(text, count, verbose):
    """Print text if count exceeds verbose level"""
    if verbose >= count:
        print(text)

def ibmq_account_fu(token, url):
    """Load IBMQ account appropriately and return provider"""
    if token:
        provider = IBMQ.enable_account(token, url=url)
    else:
        provider = IBMQ.load_account()
    return provider


def qi_account_fu(token):
    """Load Quantum Inspire account appropriately and return provider"""
    from quantuminspire.qiskit import QI
    from quantuminspire.credentials import enable_account
    if token:
        enable_account(token)
    QI.set_authentication()
    return QI


def account_fu(api_provider, token=None, url=None):
    """Load account from correct API provider"""
    a_p = api_provider.upper()
    if a_p == "IBMQ":
        provider = ibmq_account_fu(token, url)
    elif a_p == "QI":
        provider = qi_account_fu(token)
    return provider

def choose_backend(api_provider, b_end=None,
                   token=None, url=None
                   qubits=5, sim=None, local_sim=None, local_sim_type=None,
                   verbose=0):
    """Return backend selected by user if account will activate and allow."""
    backend = None

    if local_sim:
        if local_sim == 'aer':
            from qiskit import BasicAer
            backend = BasicAer.get_backend(local_sim_type)

        elif local_sim == 'qcgpu':
            from qiskit_qcgpu_provider import QCGPUProvider
            backend = QCGPUProvider().get_backend(local_sim_type)

    else:
        provider = account_fu(api_provider, token, url)
        verbosity("Provider is " + str(provider), 3, verbose)
        verbosity("provider.backends is " + str(provider.backends()), 3, verbose)

        if b_end:
            backend = provider.get_backend(b_end)
            verbosity('b_end provider.get_backend() returns ' + str(backend), 3), verbose)

        elif sim:
            backend = provider.get_backend('ibmq_qasm_simulator')
            verbosity('sim provider.get_backend() returns ' + str(backend), 3, verbose)

        else:
            from qiskit.providers.ibmq import least_busy
            large_enough_devices = provider.backends(
                filters=lambda x: x.configuration().n_qubits >= qubits
                and not x.configuration().simulator)
            backend = least_busy(large_enough_devices)
            verbosity("The best backend is " + backend.name(), 2, verbose)
    verbosity("Backend is " + str(backend), 1, verbose)
    return backend

def csv_str(description, sort_keys, sort_counts):
    """Generate a cvs as a string from sorted keys and sorted counts"""
    csv = []
    csv.append(description)
    keys = ""
    for key in sort_keys:
        keys += key + ';'
    csv.append(keys)
    counts = ""
    for count in sort_counts:
        counts += str(count) + ';'
    csv.append(counts)
    return csv