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
import warnings
from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit.compiler import transpile
from qiskit.providers.ibmq.job.exceptions import IBMQJobFailureError
from qiskit.tools.monitor import job_monitor
try:
    from quantuminspire.api import QuantumInspireAPI
    from quantuminspire.qiskit import QI
    from quantuminspire.credentials import enable_account
except ImportError:
    warnings.warn("QuantumInspire not installed.")
try:
    from quantastica.qiskit_forest import ForestBackend
except ImportError:
    warnings.warn("Rigetti Forest not installed.")


class QisJob:  # pylint: disable-msg=too-many-instance-attributes
    """Embody preparation, execution, display of Qiskit job or jobs"""
    def __init__(self, filepaths=None,  # pylint: disable-msg=too-many-arguments, too-many-locals
                 provider_name="IBMQ", backend_name=None,
                 token=None, url=None,
                 num_qubits=5, shots=1024, max_credits=3,
                 outfile_path=None, one_job=False, qasm=False,
                 use_aer=False, use_qasm_simulator=False, use_unitary_simulator=False,
                 qcgpu=False, use_sim=False, qvm=False,
                 qc_name=None, xpile=False,
                 print_job=False, memory=False, show_result=False,
                 jobs_status=None, job_id=None, job_result=None,
                 show_backends=False, show_configuration=False, show_properties=False,
                 show_statuses=False, date_time=None,
                 print_histogram=False, print_state_city=0, figure_basename='figout',
                 show_q_version=False, verbose=0):
        """Initialize factors from commandline options"""
        self.provider_name = provider_name.upper()
        self.provider = None
        self.filepaths = filepaths
        self.backend_name = backend_name
        self.backend = None
        self.token = token
        self.url = url
        self.num_qubits = num_qubits
        self.shots = shots
        self.max_credits = max_credits
        self.outfile_path = outfile_path
        self.one_job = one_job
        self.qasm = qasm
        self.use_aer = use_aer
        self.use_qasm_simulator = use_qasm_simulator
        self.use_unitary_simulator = use_unitary_simulator
        self.qcgpu = qcgpu
        self.use_sim = use_sim
        self.qvm = qvm
        self.qc_name = qc_name
        self.xpile = xpile
        self.print_job = print_job
        self.memory = memory
        self.show_result = show_result
        self.jobs_status = jobs_status
        self.job_id = job_id
        self.job_result = job_result
        self.show_backends = show_backends
        self.show_configuration = show_configuration
        self.show_properties = show_properties
        self.show_statuses = show_statuses
        self.date_time = date_time
        self.print_histogram = print_histogram
        self.print_state_city = print_state_city
        self.figure_basename = figure_basename
        self.show_q_version = show_q_version
        self.verbose = verbose
        self._pp = pprint.PrettyPrinter(indent=4, stream=sys.stdout)

    def do_it(self):  # pylint: disable-msg=too-many-branches, too-many-statements
        """Run the whole program given ctor args from the driver script"""

        if self.show_q_version:
            from qiskit import __qiskit_version__  # pylint: disable-msg=import-outside-toplevel
            self._pp.pprint(__qiskit_version__)
            sys.exit(0)

        elif self.provider_name == "IBMQ" and ((self.token and not self.url)
                                               or (self.url and not self.token)):
            print('--token and --url must be used together for IBMQ provider or not at all',
                  file=sys.stderr)
            sys.exit(1)

        elif self.show_configuration:
            self.account_fu()
            self.backend = self.provider.get_backend(self.backend_name)
            self._pp.pprint(self.backend.configuration().to_dict())
            sys.exit(0)

        elif self.show_properties:
            self.account_fu()
            self.backend = self.provider.get_backend(self.backend_name)
            the_date_time = QisJob.gen_datetime(self.date_time) if self.date_time else None
            self._pp.pprint(self.backend.properties(datetime=the_date_time).to_dict())
            sys.exit(0)

        elif self.show_backends:
            self.account_fu()
            self._pp.pprint(self.provider.backends())
            sys.exit(0)

        elif self.show_statuses:
            self.account_fu()
            if not self.backend_name:
                print("Error, need --backend for --status")
                sys.exit(1)
            self.backend = self.provider.get_backend(self.backend_name)
            self._pp.pprint(self.get_statuses())

        elif self.jobs_status or self.job_id or self.job_result:
            if not self.backend_name:
                print("--jobs or --job_id or --job_result also require --backend")
                sys.exit(1)

            self.account_fu()
            self.backend = self.provider.get_backend(self.backend_name)
            f_string = "Job {} {}"

            if self.jobs_status:
                be_jobs = []
                if self.provider_name == "QI":
                    be_jobs = QuantumInspireAPI().get_jobs()
                else:
                    be_jobs = self.backend.jobs(limit=self.jobs_status)
                for a_job in be_jobs:
                    if self.provider_name != "QI":
                        a_job = a_job.to_dict()
                    self._pp.pprint(a_job)
                    sys.exit(0)

            elif self.job_id:
                a_job = self.backend.retrieve_job(self.job_id)
                self._pp.pprint(a_job.to_dict())
                sys.exit(0)

            elif self.job_result:
                a_job = self.backend.retrieve_job(self.job_result)
                print(f_string.format(str(a_job.job_id()), str(a_job.status())))
                self._pp.pprint(a_job.result().to_dict())
                sys.exit(0)

        else:
            self.choose_backend()
            if not self.filepaths:
                self.one_exp()
            else:
                if self.one_job:
                    self.multi_exps()
                else:
                    for f_path in self.filepaths:
                        self.one_exp(f_path)

    def verbosity(self, text, count):
        """Print text if count exceeds verbose level"""
        if self.verbose >= count:
            print(text)

    @staticmethod
    def gen_datetime(datetime_comma_string):
        """Convert comma-separated date elements to datetime."""
        the_args = []
        the_split = datetime_comma_string.split(',')
        for i in the_split:
            the_args.append(int(i))
        return datetime.datetime(*the_args)

    def ibmq_account_fu(self):
        """Load IBMQ account appropriately and return provider"""
        if self.token:
            self.provider = IBMQ.enable_account(self.token, url=self.url)
        else:
            self.provider = IBMQ.load_account()

    def qi_account_fu(self):
        """Load Quantum Inspire account appropriately and return provider"""
        if self.token:
            enable_account(self.token)
        QI.set_authentication()
        self.provider = QI

    def forest_account_fu(self):
        """Load Rigetti Forest account appropriately and return provider"""
        self.provider = ForestBackend

    def account_fu(self):
        """Load account from correct API provider"""
        if self.provider_name == "IBMQ":
            self.ibmq_account_fu()
        elif self.provider_name == "QI":
            self.qi_account_fu()
        elif self.provider_name == "Forest":
            self.forest_account_fu()

    def choose_backend(self):
        """Return backend selected by user if account will activate and allow."""
        self.backend = None

        local_sim_type = 'statevector_simulator'
        if self.use_qasm_simulator:
            local_sim_type = 'qasm_simulator'
        elif self.use_unitary_simulator:
            local_sim_type = 'unitary_simulator'

        if self.use_aer:
            from qiskit import BasicAer  # pylint: disable-msg=import-outside-toplevel
            self.backend = BasicAer.get_backend(local_sim_type)

        elif self.qcgpu:
            from qiskit_qcgpu_provider import QCGPUProvider  # pylint: disable-msg=import-outside-toplevel, line-too-long
            self.backend = QCGPUProvider().get_backend(local_sim_type)

        elif self.qvm:
            self.backend = ForestBackend.get_backend(self.backend_name, True)
            self.verbosity('qvm provider.get_backend() returns {}'.format(str(self.backend)), 3)

        else:
            self.account_fu()
            self.verbosity("Provider is {}".format(str(self.provider)), 3)
            self.verbosity("Provider.backends is {}".format(str(self.provider.backends())), 3)

            if self.backend_name:
                self.backend = self.provider.get_backend(self.backend_name)
                self.verbosity('provider.get_backend() returns {}'.format(str(self.backend)), 3)

            elif self.use_sim:
                self.backend = self.provider.get_backend('ibmq_qasm_simulator')
                self.verbosity('sim provider.get_backend() returns {}'.format(str(self.backend)), 3)

            else:
                from qiskit.providers.ibmq import least_busy  # pylint: disable-msg=import-outside-toplevel, line-too-long
                large_enough_devices = self.provider.backends(
                    filters=lambda x: x.configuration().n_qubits >= self.num_qubits
                    and not x.configuration().simulator)
                self.backend = least_busy(large_enough_devices)
                self.verbosity("The best backend is {}".format(self.backend.name()), 2)
                self.verbosity("Backend is {}".format(str(self.backend)), 1)

    @staticmethod
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

    @staticmethod
    def fig_name_str(filepath, backend):
        """Create name consisting of filepath, backend and timestamp"""
        return filepath + '_' + str(backend) + '_' + datetime.datetime.now().isoformat()

    @staticmethod
    def save_fig(figure, filepath, backend, tail):
        """Write a figure to an algorithmically named destination file"""
        figure.savefig(QisJob.fig_name_str(filepath, backend) + '.' + tail)

    @staticmethod
    def state_city_plot(result_exp, circ, figure_basename, backend, decimals=3):
        """Plot state_city style the output state
        result_exp - experiment result
        circ - the circuit
        figure_basename - base file name of output
        backend - backend run on
        decimals - how many decimal places
        """
        from qiskit.visualization import plot_state_city  # pylint: disable-msg=import-outside-toplevel, line-too-long
        outputstate = result_exp.get_statevector(circ, decimals)
        fig = plot_state_city(outputstate)
        QisJob.save_fig(fig, figure_basename, backend, 'state_city.png')

    @staticmethod
    def do_histogram(result_exp, circ, figure_basename, backend):
        """Plot histogram style the counts of
        result_exp - experiment result
        circ - the circuit
        figure_basename - base file name of output
        backend - backend run on
        """
        from qiskit.tools.visualization import plot_histogram  # pylint: disable-msg=import-outside-toplevel, line-too-long
        outputstate = result_exp.get_counts(circ)
        fig = plot_histogram(outputstate)
        QisJob.save_fig(fig, figure_basename, backend, 'histogram.png')

    def process_result(self, result_exp, circ, ofh):
        """Process the result of one circuit circ
        from result result_exp
        printing to output file handle ofh
        passing original qasm filepath for figure output filename generation
        """
        # Write qasm if requested
        if self.qasm:
            ofh.write(circ.qasm() + '\n')

        # Raw data if requested
        if self.memory:
            print(result_exp.data(circ))

        # Print counts if any measurment was taken
        if 'counts' in result_exp.data(circ):
            counts_exp = result_exp.get_counts(circ)
            self.verbosity(counts_exp, 1)
            sorted_keys = sorted(counts_exp.keys())
            sorted_counts = []
            for i in sorted_keys:
                sorted_counts.append(counts_exp.get(i))

            # Generate CSV
            output = QisJob.csv_str(str(self.backend) + ' ' + datetime.datetime.now().isoformat(),
                                    sorted_keys, sorted_counts)

            # Write CSV
            for line in output:
                ofh.write(line + '\n')

            if self.print_state_city:
                QisJob.state_city_plot(result_exp, circ, self.figure_basename,
                                       self.backend, decimals=self.print_state_city)
            if self.print_histogram:
                QisJob.do_histogram(result_exp, circ, self.figure_basename, self.backend)

    def one_exp(self, filepath_name=None):  # pylint: disable-msg=too-many-branches
        """Load qasm and run the job, print csv and other selected output"""

        if filepath_name is None:
            ifh = sys.stdin
        else:
            ifh = open(filepath_name, 'r')

        if self.outfile_path is None:
            ofh = sys.stdout
        else:
            ofh = open(self.outfile_path, 'w')

        if self.backend is None:
            print("No backend available, quitting.")
            sys.exit(100)

        self.verbosity("File path is " + ("stdin" if ifh is sys.stdin else filepath_name), 2)
        self.verbosity("File handle is {}".format(str(ifh)), 3)

        # Read source
        the_source = ifh.read()
        if ifh is not sys.stdin:
            ifh.close()
        self.verbosity("source:\n" + the_source, 1)

        if self.qc_name:
            my_glob = {}
            my_loc = {}
            exec(the_source, my_glob, my_loc)  # pylint: disable-msg=exec-used
            # self._pp.pprint(my_loc)
            circ = my_loc[self.qc_name]
        else:
            circ = QuantumCircuit.from_qasm_str(the_source)

        self.verbosity(circ.draw(), 2)

        if self.xpile:
            print(transpile(circ, backend=self.backend))

        try:
            job_exp = execute(circ, backend=self.backend, shots=self.shots,
                              max_credits=self.max_credits, memory=self.memory)

            if self.print_job:
                _op = getattr(job_exp, 'to_dict', None)
                if _op and callable(_op):
                    self._pp.pprint(job_exp.to_dict())
                else:
                    self._pp.pprint(job_exp.__dict__)

            job_monitor(job_exp)
            result_exp = job_exp.result()

            if self.show_result:
                self._pp.pprint(result_exp.to_dict())

            # Open outfile
            self.verbosity("Outfile is {}"
                           .format("stdout" if ofh is sys.stdout else self.outfile_path), 2)
            self.verbosity("File handle is {}".format(str(ofh)), 3)

            self.process_result(result_exp, circ, ofh)

        except IBMQJobFailureError:
            print(job_exp.error_message())
            sys.exit(100)

        if ofh is not sys.stdout:
            ofh.close()

    def multi_exps(self):
        """Load qasms and run all as one the job,
        print csvs and other selected output
        """
        if self.backend is None:
            print("No backend available, quitting.")
            sys.exit(100)

        if self.outfile_path is None:
            ofh = sys.stdout
        else:
            ofh = open(self.outfile_path, 'w')

        self.verbosity("Outfile is " + ("stdout" if ofh is sys.stdout else self.outfile_path), 2)
        self.verbosity("File handle is {}".format(str(ofh)), 3)

        circs = []

        for fpath in self.filepaths:
            # Get file
            self.verbosity("File path is {}".format(fpath), 2)
            ifh = open(fpath, "r")
            self.verbosity("File handle is {}".format(str(ifh)), 3)

            # Read source
            the_source = ifh.read()
            ifh.close()
            self.verbosity("source:\n" + the_source, 1)

            # Create circuit
            if self.qc_name:
                my_glob = {}
                my_loc = {}
                exec(the_source, my_glob, my_loc)  # pylint: disable-msg=exec-used
                # self._pp.pprint(my_loc)
                circ = my_loc[self.qc_name]
            else:
                circ = QuantumCircuit.from_qasm_str(the_source)

            self.verbosity(circ.draw(), 2)

            if self.xpile:
                print(transpile(circ, backend=self.backend))

            circs.append(circ)

        try:
            job_exp = execute(circs, backend=self.backend, shots=self.shots,
                              max_credits=self.max_credits, memory=self.memory)

            if self.print_job:
                self._pp.pprint(job_exp.to_dict())

            job_monitor(job_exp)
            result_exp = job_exp.result()

            if self.show_result:
                self._pp.pprint(result_exp.to_dict())

            for circ in circs:
                self.process_result(result_exp, circ, ofh)

        except IBMQJobFailureError:
            print(job_exp.error_message())
            sys.exit(100)

        if ofh is not sys.stdout:
            ofh.close()

    def get_statuses(self):
        """Return backend status tuple(s)"""
        stat = ''
        if self.backend:
            stat = self.backend.status()
        else:
            for b_e in self.provider.backends():
                stat += str(b_e.status())
        return stat
