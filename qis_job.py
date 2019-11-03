#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qis_job.py
Core routines for qasm_job and qc_job
Created on Sat Nov  2 18:05:21 2019

@author: jax
"""

import datetime
import pprint
import sys
from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit.compiler import transpile
from qiskit.tools.monitor import job_monitor


class QisJob: #pylint: disable-msg=too-many-instance-attributes
    """Embody preparation, execution, display of Qiskit job or jobs"""
    def __init__(self, filepaths=None, #pylint: disable-msg=too-many-arguments, too-many-locals
                 provider_name="IBMQ", backend_name=None,
                 token=None, url=None,
                 num_qubits=5, shots=1024, max_credits=3,
                 outfile=None, one_job=False, qasm=False,
                 use_aer=False, use_qasm_simulator=False, use_unitary_simulator=False,
                 qcgpu=False,
                 print_job=False, memory=False, result=False,
                 jobs_status=False, job_id=False, job_result=False,
                 show_backends=False, show_configuration=False, show_properties=False,
                 print_histogram=False, print_state_city=0, figure_basename='figout',
                 show_q_version=False, verbose=0):
        """Initialize factors from commandline options"""
        self.provider_name = provider_name
        self.filepaths = filepaths
        self.backend_name = backend_name
        self.token = token
        self.url = url
        self.num_qubits = num_qubits
        self.shots = shots
        self.max_credits = max_credits
        self.outfile = outfile
        self.one_job = one_job
        self.qasm = qasm
        self.use_aer = use_aer
        self.use_qasm_simulator = use_qasm_simulator
        self.use_unitary_simulator = use_unitary_simulator
        self.qcgpu = qcgpu
        self.print_job = print_job
        self.memory = memory
        self.result = result
        self.jobs_status = jobs_status
        self.job_id = job_id
        self.job_result = job_result
        self.show_backends = show_backends
        self.show_configuration = show_configuration
        self.show_properties = show_properties
        self.print_histogram = print_histogram
        self.print_state_city = print_state_city
        self.figure_basename = figure_basename
        self.show_q_version = show_q_version
        self.verbose = verbose
        self._pp = pprint.PrettyPrinter(indent=4, stream=sys.stdout)


_PP = pprint.PrettyPrinter(indent=4, stream=sys.stdout)


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
                   token=None, url=None,
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
            verbosity('b_end provider.get_backend() returns ' + str(backend), 3, verbose)

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


def fig_name_str(filepath, backend):
    """Create name consisting of filepath, backend and timestamp"""
    return filepath + '_' + str(backend) + '_' + datetime.datetime.now().isoformat()


def save_fig(figure, filepath, backend, tail):
    """Write a figure to an algorithmically named destination file"""
    figure.savefig(fig_name_str(filepath, backend) + '.' + tail)


def state_city_plot(result_exp, circ, figure_basename, backend, decimals=3):
    """Plot state_city style the output state
    result_exp - experiment result
    circ - the circuit
    figure_basename - base file name of output
    backend - backend run on
    decimals - how many decimal places
    """
    from qiskit.visualization import plot_state_city
    outputstate = result_exp.get_statevector(circ, decimals)
    fig = plot_state_city(outputstate)
    save_fig(fig, figure_basename, backend, 'state_city.png')


def do_histogram(result_exp, circ, figure_basename, backend):
    """Plot histogram style the counts of
    result_exp - experiment result
    circ - the circuit
    figure_basename - base file name of output
    backend - backend run on
    """
    from qiskit.tools.visualization import plot_histogram
    outputstate = result_exp.get_counts(circ)
    fig = plot_histogram(outputstate)
    save_fig(fig, figure_basename, backend, 'histogram.png')


def process_result(result_exp, circ, backend, qasm_source, ofh,
                   write_qasm=False, memory=False,
                   plot_state_city=None, histogram=False,
                   figure_basename=None, verbose=0):
    """Process the result of one circuit circ
    from result result_exp
    printing to output file handle ofh
    passing original qasm filepath for figure output filename generation
    """
    # Write qasm if requested
    if write_qasm:
        ofh.write(qasm_source + '\n')

    # Raw data if requested
    if memory:
        print(result_exp.data(circ))

    # Print counts if any measurment was taken
    if 'counts' in result_exp.data(circ):
        counts_exp = result_exp.get_counts(circ)
        verbosity(counts_exp, 1, verbose)
        sorted_keys = sorted(counts_exp.keys())
        sorted_counts = []
        for i in sorted_keys:
            sorted_counts.append(counts_exp.get(i))

        # Generate CSV
        output = csv_str(str(backend) + ' ' + datetime.datetime.now().isoformat(),
                         sorted_keys, sorted_counts)

        # Write CSV
        for line in output:
            ofh.write(line + '\n')

        if plot_state_city:
            state_city_plot(result_exp, circ, figure_basename,
                            backend, decimals=plot_state_city)
        if histogram:
            histogram(result_exp, circ, figure_basename, backend)


def one_exp(backend, filepath=None, outfile=None, xpile=False, j_b=False,
            shots=1024, max_credits=3,
            memory=False, res=False, verbose=0):
    """Load qasm and run the job, print csv and other selected output"""

    if filepath is None:
        filepath = sys.stdin
    if outfile is None:
        outfile = sys.stdout

    if backend is None:
        print("No backend available, quitting.")
        sys.exit(100)

    # Get file
    verbosity("File path is " + ("stdin" if filepath is sys.stdin else filepath), 2, verbose)
    ifh = filepath if filepath is sys.stdin else open(filepath, "r")
    verbosity("File handle is " + str(ifh), 3, verbose)

    # Read source
    qasm_source = ifh.read()
    if filepath is not sys.stdin:
        ifh.close()
    verbosity("qasm source:\n" + qasm_source, 1, verbose)

    circ = QuantumCircuit.from_qasm_str(qasm_source)
    verbosity(circ.draw(), 2, verbose)

    if xpile:
        print(transpile(circ, backend=backend))

    job_exp = execute(circ, backend=backend, shots=shots,
                      max_credits=max_credits, memory=memory)
    if j_b:
        _PP.pprint(job_exp.to_dict())

    job_monitor(job_exp)
    result_exp = job_exp.result()

    if res:
        print(result_exp)

    # Open outfile
    verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2, verbose)
    ofh = outfile if outfile is sys.stdout else open(outfile, "a")
    verbosity("File handle is " + str(ofh), 3, verbose)

    process_result(result_exp, circ, memory, backend, qasm_source, ofh)

    if outfile is not sys.stdout:
        ofh.close()


def multi_exps(backend, filepaths, outfile=None, xpile=False, j_b=False,
               shots=1024, max_credits=3,
               memory=False, res=False, verbose=0):
    """Load qasms and run all as one the job,
    print csvs and other selected output
    """

    if outfile is None:
        outfile = sys.stdout

    if backend is None:
        print("No backend available, quitting.")
        sys.exit(100)

    circs = []

    for fpath in filepaths:
        # Get file
        verbosity("File path is " + ("stdin" if fpath is sys.stdin else fpath), 2, verbose)
        ifh = fpath if fpath is sys.stdin else open(fpath, "r")
        verbosity("File handle is " + str(ifh), 3, verbose)

        # Read source
        qasm_source = ifh.read()
        ifh.close()
        verbosity("qasm source:\n" + qasm_source, 1, verbose)

        # Create circuit
        circ = QuantumCircuit.from_qasm_str(qasm_source)
        verbosity(circ.draw(), 2, verbose)

        if xpile:
            try:
                print(transpile(circ, backend=backend))
            except NameError:
                print('Transpiler not available this Qiskit level.', file=sys.stderr)

        circs.append(circ)

    job_exp = execute(circs, backend=backend, shots=shots,
                      max_credits=max_credits, memory=memory)
    if j_b:
        _PP.pprint(job_exp.to_dict())

    job_monitor(job_exp)
    result_exp = job_exp.result()

    if res:
        print(result_exp)

    # Open outfile
    verbosity("Outfile is " + ("stdout" if outfile is sys.stdout else outfile), 2, verbose)
    ofh = outfile if outfile is sys.stdout else open(outfile, "a")
    verbosity("File handle is " + str(ofh), 3, verbose)

    for circ in circs:
        process_result(result_exp, circ, memory, backend, qasm_source, ofh)

    if outfile is not sys.stdout:
        ofh.close()


def get_statuses(provider, backend):
    """Return backend status tuple(s)"""
    stat = ''
    if backend:
        stat = backend.status()
    else:
        for b_e in provider.backends():
            stat += str(b_e.status())
    return stat
