#!/usr/bin/env python3  # pylint: disable-msg=too-many-lines
# -*- coding: utf-8 -*-
r"""qisjob.pyx ..
Load from qasm source or Qiskit QuantumCircuit source and run job with reporting.


Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051


BSD-3 license -- See LICENSE which you should have received with this code.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES."""

import argparse
import datetime
import pprint
import sys
import warnings
from qiskit import IBMQ
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit import schedule
from qiskit import QiskitError
from qiskit.providers.ibmq import IBMQJob
from qiskit.compiler import transpile
try:
    from qiskit.providers.ibmq.exceptions import IBMQAccountCredentialsNotFound
    from qiskit.providers.ibmq.job.exceptions import IBMQJobFailureError
    from qiskit.providers.exceptions import QiskitBackendNotFoundError
except ImportError:
    warnings.warn("Qiskit IBMQ provider not installed.")
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_circuit_layout
try:
    from quantuminspire.api import QuantumInspireAPI
    from quantuminspire.qiskit import QI
    from quantuminspire.credentials import enable_account as qi_enable_account
except ImportError:
    warnings.warn("QuantumInspire not installed.")
try:
    from quantastica.qiskit_forest import ForestBackend
except ImportError:
    warnings.warn("Rigetti Forest not installed.")
try:
    from qiskit_jku_provider import JKUProvider
except ImportError:
    warnings.warn("qiskit-jku-provider not installed.")


def ibmqjob_to_dict(job: IBMQJob) -> dict:
    """
    Create a dict containing job factors for which there are methods.
    Acts as a 'to_dict()'.

    Parameters
    ----------
    job : IBMQJob
        Return a dict as if there were a to_dict method

    Returns
    -------
    dict
        Job info from the IBMQ server

    """
    my_dict = {}
    # Return the backend where this job was executed.
    my_dict["backend"] = job.backend()
    # Return whether the job has been cancelled.
    my_dict["cancelled"] = job.cancelled()
    # Return job creation date, in local time.
    my_dict["creation_date"] = job.creation_date()
    # Return whether the job has successfully run.
    my_dict["done"] = job.done()
    # Provide details about the reason of failure.
    my_dict["error_message"] = job.error_message()
    # Return whether the job is in a final job state.
    my_dict["in_final_state"] = job.in_final_state()
    # Return the job ID assigned by the server.
    my_dict["job_id"] = job.job_id()
    # Return the name assigned to this job.
    my_dict["name"] = job.name()
    # Return the backend properties for this job.
    my_dict["properties"] = job.properties()
    # Return the Qobj for this job.
    my_dict["qobj"] = job.qobj()
    # Return queue information for this job.
    my_dict["queue_info"] = job.queue_info()
    # Return the position of the job in the server queue.
    my_dict["queue_position"] = job.queue_position()
    # Return whether the job is actively running.
    my_dict["result"] = job.result().to_dict()
    # Return whether the job is actively running.
    my_dict["running"] = job.running()
    # Return the scheduling mode the job is in.
    my_dict["scheduling_mode"] = job.scheduling_mode()
    # Return the share level of the job.
    my_dict["share_level"] = job.share_level()
    # Query the server for the latest job status.
    my_dict["status"] = job.status()
    # Return the tags assigned to this job.
    my_dict["tags"] = job.tags()
    # Return the date and time information on each step of the job processing.
    my_dict["time_per_step"] = job.time_per_step()
    return my_dict


class QisJob:  # pylint: disable-msg=too-many-instance-attributes, too-many-public-methods
    """Embody preparation, execution, display of Qiskit job or jobs"""
    def __init__(self, filepaths=None,  # pylint: disable-msg=too-many-arguments, too-many-locals, too-many-statements, line-too-long
                 qasm_src=None,
                 provider_name="IBMQ", backend_name=None,
                 token=None, url=None,
                 nuqasm2=None,
                 num_qubits=5, shots=1024, max_credits=3,
                 outfile_path=None, one_job=False, qasm=False,
                 use_aer=False, use_qasm_simulator=False, use_unitary_simulator=False,
                 use_statevector_gpu=False, use_unitary_gpu=False,
                 use_density_matrix_gpu=False,
                 use_sim=False, qvm=False, qvm_as=False,
                 qc_name=None, xpile=False, showsched=False, circuit_layout=False,
                 optimization_level=1,
                 print_job=False, memory=False, show_result=False,
                 jobs_status=None, job_id=None, job_result=None,
                 show_backends=False, show_configuration=False, show_properties=False,
                 show_statuses=False, date_time=None,
                 print_histogram=False, print_state_city=0, figure_basename='figout',
                 show_q_version=False, verbose=0,
                 show_qisjob_version=False,
                 use_job_monitor=False,
                 job_monitor_filepath=None):

        """


        Initialize QisJob member data

        Parameters
        ----------

        filepaths : str
            The default is `None`.

            List of fully qualified or relative filepaths for experiments.

        qasm_src : str
            The default is `None`.

            A string of OpenQASM experiment source

        provider_name : str
            The default is "IBMQ".

            The name of the backend provider. Currently supported are

                * IBMQ
                * QI
                * Forest
                * JKU

        backend_name : str
            The default is `None`.

            Name of chosen backend for given provider.
            If provider is IBMQ and backend_name is `None`, QisJob will
            search for 'least_busy'.

        token : str
            The default is `None`.

            Login token for provider. This is a string even if it looks
            like a giant hexadecimal number

        url : str
            The default is `None`.

            URL of backend provider gateway

        nuqasm2 : str
            The default is `None`.

            An include path for OpenQASM include files that also serves
            to indicate that nuqasm2 should be used as the OpenQASM compiler

        num_qubits : int
            The default is 5.

            Number of qubits required for experiment(s)

        shots : int
            The default is 1024.


        max_credits : int
            The default is 3.


        outfile_path : str
            The default is `None`.


        one_job : bool
            The default is `False`.


        qasm : bool
            The default is `False`.


        use_aer : bool
            The default is `False`.


        use_qasm_simulator : bool
            The default is `False`.


        use_unitary_simulator : bool
            The default is `False`.


        use_statevector_gpu : bool
            The default is `False`.


        use_unitary_gpu : bool
            The default is `False`.


        use_density_matrix_gpu : bool
            The default is `False`.


        use_sim : bool
            The default is `False`.


        qvm : bool
            The default is `False`.


        qvm_as : bool
            The default is `False`.


        qc_name : str
            The default is `None`.


        xpile : bool
            The default is `False`.


        showsched : bool
            The default is `False`.


        circuit_layout
            The default is `False`.


        optimization_level : int
            The default is 1.


        print_job : bool
            The default is `False`.


        memory : bool
            The default is `False`.


        show_result : bool
            The default is `False`.


        jobs_status : int
            The default is `None`.


        job_id : int
            The default is `None`.


        job_result : int
            The default is `None`.


        show_backends : bool
            The default is `False`.


        show_configuration : bool
            The default is `False`.


        show_properties : bool
            The default is `False`.


        show_statuses : bool
            The default is `False`.


        date_time : str
            The default is `None`.


        print_histogram : bool
            The default is `False`.


        print_state_city : int
            The default is 0.


        figure_basename : str
            The default is 'figout'.


        show_q_version : bool
            The default is `False`.


        verbose : int
            The default is 0.


        show_qisjob_version : bool
            The default is `False`.


        use_job_monitor : bool
            The default is `False`.


        job_monitor_filepath : str
            The default is `None`.


        """


    def qisjob_version(self) -> str:
        """


        Return version of QisJob

        Returns
        -------
        str
            version string for QisJob.

        """
        return self.my_version

    def do_it(self):  # pylint: disable-msg=too-many-branches, too-many-statements, disable-msg=too-many-return-statements
        """Run the whole program given ctor args from the driver script"""

        if self.show_qisjob_version:
            print(self.my_version)
            return

        if self.show_q_version:
            from qiskit import __qiskit_version__  # pylint: disable-msg=import-outside-toplevel
            self._pp.pprint(__qiskit_version__)
            return

        if self.provider_name == "IBMQ" and ((self.token and not self.url)
                                               or (self.url and not self.token)):
            raise QisJobArgumentException(
                'kwargs token and url must be used together for IBMQ provider or not at all'
                )

        if self.show_configuration:
            self.account_fu()
            self.backend = self.provider.get_backend(self.backend_name)
            self._pp.pprint(self.backend.configuration().to_dict())
            return

        if self.show_properties:
            self.account_fu()

            try:
                self.backend = self.provider.get_backend(self.backend_name)
            except QiskitBackendNotFoundError as err:
                raise QisJobRuntimeException(
                    "Backend {} not found: {}".format(self.backend_name, err)
                    ) from err

            the_date_time = QisJob.gen_datetime(self.date_time) if self.date_time else None
            self._pp.pprint(self.backend.properties(datetime=the_date_time).to_dict())
            return

        if self.show_backends:
            self.account_fu()
            self._pp.pprint(self.provider.backends())
            return

        if self.show_statuses:
            self.account_fu()

            if self.backend_name:
                try:
                    self.backend = self.provider.get_backend(self.backend_name)
                except QiskitBackendNotFoundError as err:
                    raise QisJobRuntimeException(
                        "Backend {} not found: {}".format(self.backend_name, err)
                        ) from err

            for stat in self.get_statuses():
                self._pp.pprint(stat)

        elif self.jobs_status or self.job_id or self.job_result:
            if not self.backend_name:
                raise QisJobArgumentException(
                    'kwargs jobs or job_id or job_result also require kwarg backend'
                    )

            self.account_fu()

            try:
                self.backend = self.provider.get_backend(self.backend_name)
            except QiskitBackendNotFoundError as err:
                raise QisJobRuntimeException(
                    "Backend {} not found: {}".format(self.backend_name, err)
                    ) from err

            f_string = "Job {} {}"

            if self.jobs_status:
                # debug
                # print(f"Provider is {self.provider_name} and jobs_status is {self.jobs_status}.")
                be_jobs = []
                if self.provider_name == "QI":
                    be_jobs = QuantumInspireAPI().get_jobs()
                else:
                    be_jobs = self.backend.jobs(limit=self.jobs_status)
                for a_job in be_jobs:
                    if self.provider_name != "QI":
                        if self.provider_name == "IBMQ":
                            a_job = ibmqjob_to_dict(a_job)
                        else:
                            a_job = a_job.to_dict()
                    self._pp.pprint(a_job)
                    return

            elif self.job_id:
                a_job = self.backend.retrieve_job(self.job_id)
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(a_job)
                    else:
                        a_job = a_job.to_dict()
                return

            elif self.job_result:
                a_job = self.backend.retrieve_job(self.job_result)
                print(f_string.format(str(a_job.job_id()), str(a_job.status())))
                self._pp.pprint(a_job.result().to_dict())
                return

        else:
            self.choose_backend()
            if self.qasm_src:
                self.qasm_result = self.qasm_exp()
            else:
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
            try:
                self.provider = IBMQ.load_account()
            except IBMQAccountCredentialsNotFound as err:
                raise QisJobRuntimeException("Error loading IBMQ Account: {}".format(err)) from err

    def qi_account_fu(self):
        """Load Quantum Inspire account appropriately and return provider"""
        if self.token:
            qi_enable_account(self.token)
        QI.set_authentication()
        self.provider = QI

    def forest_account_fu(self):
        """Load Rigetti Forest account appropriately and return provider"""
        self.provider = ForestBackend

    def jku_account_fu(self):
        """Load qiskit-jku-provider"""
        self.provider = JKUProvider()

    def account_fu(self):
        """Load account from correct API provider"""
        if self.provider_name == "IBMQ":
            self.ibmq_account_fu()
        elif self.provider_name == "QI":
            self.qi_account_fu()
        elif self.provider_name == "Forest":
            self.forest_account_fu()
        elif self.provider_name == "JKU":
            self.jku_account_fu()

    def choose_backend(self):  # pylint: disable-msg=too-many-branches, too-many-statements
        """Return backend selected by user if account will activate and allow."""
        self.backend = None

        # Choose simulator. We defaulted in __init__() to statevector_simulator
        if self.use_qasm_simulator:
            self.local_simulator_type = 'qasm_simulator'
        elif self.use_unitary_simulator:
            self.local_simulator_type = 'unitary_simulator'

        # Choose method kwarg for gpu etc if present
        if self.use_statevector_gpu:
            self.method = "statevector_gpu"
        elif self.use_unitary_gpu:
            self.method = "unitary_gpu"
        elif self.use_density_matrix_gpu:
            self.method = "density_matrix_gpu"

        if self.use_aer:
            from qiskit import Aer  # pylint: disable-msg=import-outside-toplevel
            if self.method:
                self.verbosity("self.local_simulator_type is '{}' with method '{}'"
                               .format(self.local_simulator_type,
                                       self.method),
                               2)
            else:
                self.verbosity("Aer backend is {}".format(self.backend), 2)
            self.backend = Aer.get_backend(self.local_simulator_type)

        elif self.qvm or self.qvm_as:
            self.backend = ForestBackend.get_backend(self.backend_name, self.qvm_as)
            self.verbosity('qvm provider.get_backend() returns {}'.format(str(self.backend)), 3)

        else:
            self.account_fu()
            self.verbosity("Provider is {}".format(str(self.provider)), 3)
            self.verbosity("Provider.backends is {}".format(str(self.provider.backends())), 3)

            if self.backend_name:
                try:
                    self.backend = self.provider.get_backend(self.backend_name)
                except QiskitBackendNotFoundError as err:
                    raise QisJobRuntimeException(
                        "Backend {} not found: {}".format(self.backend_name, err)
                        ) from err
                self.verbosity('provider.get_backend() returns {}'.format(str(self.backend)), 3)

            elif self.use_sim:
                self.backend = self.provider.get_backend('ibmq_qasm_simulator')
                self.verbosity('sim provider.get_backend() returns {}'.format(str(self.backend)), 3)

            elif self.provider_name == 'QI':
                for b_e in self.provider.backends():
                    if b_e.__dict__['_QuantumInspireBackend__backend']['number_of_qubits'] >= self.num_qubits:  # pylint: disable-msg=line-too-long
                        self.backend = b_e
                        self.verbosity("Backend is {}".format(str(self.backend)), 1)
                        break
                if not self.backend:
                    raise QisJobRuntimeException(
                        "No suitable backend found for {} qubits".format(str(self.num_qubits))
                        )
            else:
                from qiskit.providers.ibmq import least_busy  # pylint: disable-msg=import-outside-toplevel, line-too-long
                large_enough_devices = self.provider.backends(
                    filters=lambda x: x.configuration().n_qubits >= self.num_qubits
                    and not x.configuration().simulator)
                try:
                    self.backend = least_busy(large_enough_devices)
                except QiskitError as err:
                    raise QisJobRuntimeException(
                        "QiskitError no device found for criteria (large enough?) {}".format(err)
                        ) from err
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

    def formulate_result(self, result_exp, circ, ofh):
        """Forumulate the result of one circuit circ
        from result result_exp returning output as string
        """
        # Write qasm if requested
        if self.qasm and ofh:
            ofh.write(circ.qasm() + '\n')

        # Raw data if requested
        if self.memory:
            self._pp.pprint(result_exp.data(circ))

        # Print statevector ... this doesn't handle Forest qvm yet
        if self.use_aer and self.local_simulator_type == 'statevector_simulator':
            self._pp.pprint(result_exp.get_statevector(circ))

        output = None

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
        return output

    def process_result(self, result_exp, circ, ofh):
        """Process the result of one circuit circ
        from result result_exp
        printing to output file handle ofh
        passing original qasm filepath for figure output filename generation
        """
        output = self.formulate_result(result_exp, circ, ofh)

        if output:
            # Write CSV
            for line in output:
                ofh.write(line + '\n')

            if self.print_state_city:
                QisJob.state_city_plot(result_exp, circ, self.figure_basename,
                                       self.backend, decimals=self.print_state_city)
            if self.print_histogram:
                QisJob.do_histogram(result_exp, circ, self.figure_basename, self.backend)

    def one_exp(self, filepath_name=None):  # pylint: disable-msg=too-many-locals, too-many-branches, too-many-statements, line-too-long
        """Load qasm and run the job, print csv and other selected output"""
        circ = None

        if filepath_name is None:
            ifh = sys.stdin
        else:
            ifh = open(filepath_name, 'r')

        if self.outfile_path is None:
            ofh = sys.stdout
        else:
            ofh = open(self.outfile_path, 'w')

        if self.backend is None:
            raise QisJobRuntimeException("No backend available, quitting.")

        self.verbosity("File path is " + ("stdin" if ifh is sys.stdin else filepath_name), 2)
        self.verbosity("File handle is {}".format(str(ifh)), 3)

        # Read source
        the_source_list = []
        for line in ifh:
            the_source_list.append(line.strip())
        if ifh is not sys.stdin:
            ifh.close()
        the_source = "\n".join(the_source_list)
        self.verbosity("source:\n" + the_source, 1)

        if self.qc_name:
            my_glob = {}
            my_loc = {}
            exec(the_source, my_glob, my_loc)  # pylint: disable-msg=exec-used
            # self._pp.pprint(my_loc)
            circ = my_loc[self.qc_name]
        else:
            if self.nuqasm2:
                from nuqasm2 import (Ast2Circ,  # pylint: disable-msg=import-outside-toplevel
                                     Qasm_Exception,
                                     Ast2CircException)
                try:
                    circ = Ast2Circ.from_qasm_str(the_source_list,
                                                  include_path=self.nuqasm2,
                                                  no_unknown=True)

                except (Qasm_Exception, Ast2CircException) as err:
                    x = err.errpacket()  # pylint: disable-msg=invalid-name
                    raise QisJobRuntimeException(
                        "Filepath name error {} {} {}".format(filepath_name, err, x)
                        ) from err

                self.verbosity("Unrolled circuit's OPENQASM 2.0 source code\n{}"
                               .format(circ.qasm()), 3)

            else:
                circ = QuantumCircuit.from_qasm_str(the_source)

            self.verbosity(circ.draw(), 2)

        if self.xpile:
            new_circ = transpile(circ, backend=self.backend,
                                 optimization_level=self.optimization_level)
            print(new_circ)
            if self.circuit_layout:
                fig = plot_circuit_layout(new_circ, self.backend)
                QisJob.save_fig(fig,
                                self.figure_basename,
                                self.backend,
                                'plot_circuit.png')

            if self.showsched:
                self._pp.pprint(schedule(new_circ, self.backend))

        try:
            if self.method:
                self.verbosity("Using gpu method {}".format(self.method), 2)
                backend_options = {"method": self.method}
                job_exp = execute(circ, backend=self.backend,
                                  backend_options=backend_options,
                                  optimization_level=self.optimization_level,
                                  shots=self.shots, max_credits=self.max_credits,
                                  memory=self.memory)
            else:
                job_exp = execute(circ, backend=self.backend,
                                  optimization_level=self.optimization_level,
                                  shots=self.shots, max_credits=self.max_credits,
                                  memory=self.memory)

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("Before run:")
                self._pp.pprint(a_job)

            if self.use_job_monitor:
                if self.job_monitor_filepath:
                    self.verbosity("File for job monitor output is {}"
                                   .format(self.job_monitor_filepath), 1)
                    j_m_file = open(self.job_monitor_filepath, mode='w', buffering=1)
                    job_monitor(job_exp, output=j_m_file)
                    j_m_file.close()
                else:
                    job_monitor(job_exp)

            result_exp = job_exp.result()
            self.result_exp_dict = result_exp.to_dict()

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("After run:")
                self._pp.pprint(a_job)

            if self.use_statevector_gpu:
                try:
                    self.verbosity("Method: {}"
                                   .format(result_exp.data(circ).metadata.get('method')), 2)
                except AttributeError as err:
                    print("AttributeError error: {0}".format(err))

            if self.show_result:
                self._pp.pprint(self.result_exp_dict)

            # Open outfile
            self.verbosity("Outfile is {}"
                           .format("stdout" if ofh is sys.stdout else self.outfile_path), 2)
            self.verbosity("File handle is {}".format(str(ofh)), 3)

            self.process_result(result_exp, circ, ofh)

        except IBMQJobFailureError as err:
            raise QisJobRuntimeException(
                "Job failure {} {}".format(err, job_exp.error_message())
                ) from err

        if ofh is not sys.stdout:
            ofh.close()

    def multi_exps(self):  # pylint: disable-msg=too-many-locals, too-many-branches, too-many-statements, line-too-long
        """Load qasms and run all as one the job,
        print csvs and other selected output
        """
        if self.backend is None:
            raise QisJobRuntimeException("No backend {}")

        if self.outfile_path is None:
            ofh = sys.stdout
        else:
            ofh = open(self.outfile_path, 'w')

        self.verbosity("Outfile is " + ("stdout" if ofh is sys.stdout else self.outfile_path), 2)
        self.verbosity("File handle is {}".format(str(ofh)), 3)

        if self.nuqasm2:
            from nuqasm2 import (Ast2Circ,  # pylint: disable-msg=import-outside-toplevel
                                 Qasm_Exception,
                                 Ast2CircException)

        circs = []

        for fpath in self.filepaths:
            # Get file
            self.verbosity("File path is {}".format(fpath), 2)
            ifh = open(fpath, "r")
            self.verbosity("File handle is {}".format(str(ifh)), 3)

            # Read source
            the_source_list = []
            for line in ifh:
                the_source_list.append(line.strip())
            if ifh is not sys.stdin:
                ifh.close()
            the_source = "\n".join(the_source_list)
            self.verbosity("source:\n" + the_source, 1)

            # Create circuit
            if self.qc_name:
                my_glob = {}
                my_loc = {}
                exec(the_source, my_glob, my_loc)  # pylint: disable-msg=exec-used
                circ = my_loc[self.qc_name]
            else:
                if self.nuqasm2:
                    try:
                        circ = Ast2Circ.from_qasm_str(the_source_list,
                                                      include_path=self.nuqasm2,
                                                      no_unknown=True)

                    except (Qasm_Exception, Ast2CircException) as err:
                        x = err.errpacket()  # pylint: disable-msg=invalid-name
                        raise QisJobRuntimeException(
                            "Error in source {} {} {}".format(the_source_list, err, x)
                            ) from err

                    self.verbosity("\nUnrolled circuit's OPENQASM 2.0 source code\n{}"
                                   .format(circ.qasm()), 3)

                else:
                    circ = QuantumCircuit.from_qasm_str(the_source)

            self.verbosity(circ.draw(), 2)

            if self.xpile:
                new_circ = transpile(circ, backend=self.backend,
                                     optimization_level=self.optimization_level)
                print(new_circ)
                if self.circuit_layout:
                    fig = plot_circuit_layout(new_circ, self.backend)
                    QisJob.save_fig(fig,
                                    self.figure_basename,
                                    self.backend,
                                    'plot_circuit.png')
                if self.showsched:
                    self._pp.pprint(schedule(new_circ, self.backend))

            circs.append(circ)

        try:

            if self.use_statevector_gpu:
                self.verbosity("Using gpu", 2)
                backend_options = {"method": "statevector_gpu"}
                job_exp = execute(circs, backend=self.backend,
                                  optimization_level=self.optimization_level,
                                  backend_options=backend_options,
                                  shots=self.shots, max_credits=self.max_credits,
                                  memory=self.memory)
            else:
                job_exp = execute(circs, backend=self.backend,
                                  optimization_level=self.optimization_level,
                                  shots=self.shots, max_credits=self.max_credits,
                                  memory=self.memory)

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("Before run:")
                self._pp.pprint(a_job)

            if self.use_job_monitor:
                if self.job_monitor_filepath:
                    self.verbosity("File for job monitor output is {}"
                                   .format(self.job_monitor_filepath), 1)
                    j_m_file = open(self.job_monitor_filepath, mode='w', buffering=1)
                    job_monitor(job_exp, output=j_m_file)
                    j_m_file.close()
                else:
                    job_monitor(job_exp)

            result_exp = job_exp.result()
            self.result_exp_dict = result_exp.to_dict()

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("After run:")
                self._pp.pprint(a_job)

            if self.show_result:
                self._pp.pprint(self.result_exp_dict)

            # my_index = 0
            for circ in circs:
                self.process_result(result_exp, circ, ofh)

        except IBMQJobFailureError as err:
            raise QisJobRuntimeException(
                "Job failure {} {}".format(err, job_exp.error_message())
                ) from err

        if ofh is not sys.stdout:
            ofh.close()

    def get_statuses(self):
        """Return backend status tuple(s)"""
        stat = []
        if self.backend:
            stat.append(self.backend.status().to_dict())
        else:
            for b_e in self.provider.backends():
                stat.append(b_e.status().to_dict())
        return stat

    def qasm_exp(self):  # pylint: disable-msg=too-many-locals, too-many-branches, too-many-statements, line-too-long
        """Given qasm source, run the job
        and return in a string csv and other selected output
        """
        the_source = self.qasm_src
        self.verbosity("source:\n" + the_source, 1)

        circ = None

        if self.nuqasm2:
            from nuqasm2 import (Ast2Circ,  # pylint: disable-msg=import-outside-toplevel
                                 Qasm_Exception,
                                 Ast2CircException)
            try:
                circ = Ast2Circ.from_qasm_str(the_source,
                                              include_path=self.nuqasm2,
                                              no_unknown=True)

            except (Qasm_Exception, Ast2CircException) as err:
                x = err.errpacket()  # pylint: disable-msg=invalid-name
                raise QisJobRuntimeException(
                    "Source error {} {} {}".format(the_source, err, x)
                    ) from err

            self.verbosity("Unrolled circuit's OPENQASM 2.0 source code\n{}"
                           .format(circ.qasm()), 3)

        else:
            circ = QuantumCircuit.from_qasm_str(the_source)

        self.verbosity(circ.draw(), 2)

        if self.xpile:
            new_circ = transpile(circ, backend=self.backend,
                                 optimization_level=self.optimization_level)
            print(new_circ)
            if self.circuit_layout:
                fig = plot_circuit_layout(new_circ, self.backend)
                QisJob.save_fig(fig,
                                self.figure_basename,
                                self.backend,
                                'plot_circuit.png')

            if self.showsched:
                self._pp.pprint(schedule(new_circ, self.backend))

        try:
            if self.method:
                self.verbosity("Using gpu method {}".format(self.method), 2)
                backend_options = {"method": self.method}
                job_exp = execute(circ, backend=self.backend,
                                  optimization_level=self.optimization_level,
                                  backend_options=backend_options,
                                  shots=self.shots, max_credits=self.max_credits,
                                  memory=self.memory)
            else:
                job_exp = execute(circ, backend=self.backend,
                                  optimization_level=self.optimization_level,
                                  shots=self.shots, max_credits=self.max_credits,
                                  memory=self.memory)

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("Before run:")
                self._pp.pprint(a_job)

            if self.use_job_monitor:
                if self.job_monitor_filepath:
                    self.verbosity("File for job monitor output is {}"
                                   .format(self.job_monitor_filepath), 1)
                    j_m_file = open(self.job_monitor_filepath, mode='w', buffering=1)
                    job_monitor(job_exp, output=j_m_file)
                    j_m_file.close()
                else:
                    job_monitor(job_exp)

            result_exp = job_exp.result()
            self.result_exp_dict = result_exp.to_dict()

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("After run:")
                self._pp.pprint(a_job)

            if self.use_statevector_gpu:
                try:
                    self.verbosity("Method: {}"
                                   .format(result_exp.data(circ).metadata.get('method')), 2)
                except AttributeError as err:
                    print("AttributeError error: {0}".format(err))

            if self.show_result:
                self._pp.pprint(result_exp.to_dict())

            return self.formulate_result(result_exp, circ, None)

        except IBMQJobFailureError as err:
            raise QisJobRuntimeException(
                "Job failure {} {}".format(err, job_exp.error_message())
                ) from err

class QisJobException(Exception):
    """Base class for QisJob exceptions"""

    def __init__(self, message: str, retval: int):
        """


        Parameters
        ----------
        message : str
            DESCRIPTION.
        retval : int
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__()
        self.message = message
        self.retval = retval


class QisJobArgumentException(QisJobException):
    """
    Argument passed to QisJob ctor is invalid.
    """

    def __init__(self, message: str):
        """


        Parameters
        ----------
        message : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(message, 1)

class QisJobRuntimeException(QisJobException):
    """
    QisJob encountered an unrecoverable runtime error.
    """

    def __init__(self, message: str):
        """


        Parameters
        ----------
        message : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__(message, 100)

if __name__ == '__main__':

    EXPLANATION = """Qisjob loads from one or more qasm source files or
    from a file containing a Qiskit QuantumCircuit definition in Python and runs as
    experiments with reporting in CSV form. Can graph results as histogram or
    state-city plot. Also can give info on backend properties, qiskit version,
    show circuit transpilation, etc. Can run as multiple jobs or all as one job.
    Exits 0 on success, 1 on argument error, 100 on runtime error.
    Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.
    BSD-3 license -- See LICENSE which you should have received with this code.
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES.
    """
    PARSER = argparse.ArgumentParser(description=EXPLANATION)
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUPB = PARSER.add_mutually_exclusive_group()
    GROUPC = PARSER.add_mutually_exclusive_group()

    GROUP.add_argument("-i", "--ibmq", action="store_true",
                       help="Use best genuine IBMQ processor (default)")
    GROUP.add_argument("-s", "--sim", action="store_true",
                       help="Use IBMQ qasm simulator")
    GROUP.add_argument("-a", "--aer", action="store_true",
                       help="""Use QISKit Aer simulator.
                       Default is Aer statevector simulator.
                       Use -a --qasm-simulator to get Aer qasm simulator.
                       Use -a --unitary-simulator to get Aer unitary simulator.""")
    GROUP.add_argument("-b", "--backend", action="store",
                       help="Use specified IBMQ backend")
    GROUPB.add_argument("--qasm_simulator", action="store_true",
                        help="""With -a use qasm simulator
                        instead of statevector simulator""")
    GROUPB.add_argument("--unitary_simulator", action="store_true",
                        help="""With -a use unitary simulator
                        instead of statevector simulator""")
    GROUPC.add_argument("--statevector_gpu", action="store_true",
                        help="""With -a and --qasm_simulator
                        use gpu statevector simulator""")
    GROUPC.add_argument("--unitary_gpu", action="store_true",
                        help="""With -a and --qasm_simulator
                        use gpu unitary simulator""")
    GROUPC.add_argument("--density_matrix_gpu", action="store_true",
                        help="""With -a and --qasm_simulator
                        use gpu density matrix simulator""")
    PARSER.add_argument("--version", action="store_true",
                        help="""Announce QisJob version""")
    PARSER.add_argument("--api_provider", action="store",
                        help="""Backend remote api provider,
                        currently supported are [IBMQ | QI | Forest | JKU].
                        Default is IBMQ.""", default="IBMQ")
    PARSER.add_argument("--qvm", action="store_true",
                        help="""Use Forest local qvm simulator described by
                        -b backend, generally one of qasm_simulator or
                        statevector_simulator. Use --qvm_as to instruct the
                        simulator to emulate a specific Rigetti QPU""")
    PARSER.add_argument("--qvm_as", action="store_true",
                        help="""Use Forest local qvm simulator to emulate the
                        specific Rigetti QPU described by -b backend. Use --qvm
                        to run the Forest local qvm simulator described by
                        -b backend.""")
    PARSER.add_argument("--backends", action="store_true",
                        help="Print list of backends to stdout and exit 0")
    PARSER.add_argument("-1", "--one_job", action="store_true",
                        help="Run all experiments as one job")
    PARSER.add_argument("-c", "--credits", type=int, action="store", default=3,
                        help="Max credits to expend on each job, default is 3")
    PARSER.add_argument("-d", "--datetime", type=str, action="store",
                        help="""Datetime 'year,month,day[,hour,min,sec]'
                        for -p,--properties""")
    PARSER.add_argument("-g", "--configuration", action="store_true",
                        help="""Print configuration for backend specified by -b
                        to stdout and exit 0""")
    PARSER.add_argument("-j", "--job", action="store_true",
                        help="Print your job's dictionary")
    PARSER.add_argument("--jobs", type=int, action="store",
                        help="""Print JOBS number of jobs and status for -b
                        backend and exit 0""")
    PARSER.add_argument("--job_id", type=str, action="store",
                        help="Print job number JOB_ID for -b backend and exit 0")
    PARSER.add_argument("--job_result", type=str, action="store",
                        help=""""Print result of job number JOB_RESULT for
                        -b backend and exit 0""")
    PARSER.add_argument("-m", "--memory", action="store_true",
                        help="Print individual results of multishot experiment")
    PARSER.add_argument("-n", "--nuqasm2", action="store",
                        help=""""Use nuqasm2 to translate OPENQASM2 source,
                        providing include path for any include directives""")
    PARSER.add_argument("-o", "--outfile", action="store",
                        help="Write appending CSV to outfile, default is stdout")
    PARSER.add_argument("-p", "--properties", action="store_true",
                        help="""Print properties for backend specified by -b to
                        stdout and exit 0""")
    PARSER.add_argument("-q", "--qubits", type=int, action="store", default=5,
                        help="Number of qubits for the experiment, default is 5")
    PARSER.add_argument("--qiskit_version", action="store_true",
                        help="Print Qiskit version and exit 0")
    PARSER.add_argument("-r", "--result", action="store_true",
                        help="Print job result")
    PARSER.add_argument("-t", "--shots", type=int, action="store", default=1024,
                        help="Number of shots for the experiment, default 1024, max 8192")
    PARSER.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity each -v up to 3")
    PARSER.add_argument("-x", "--transpile", action="store_true",
                        help="""Print circuit transpiled for chosen backend to stdout
                        before running job""")
    PARSER.add_argument("--showsched", action="store_true",
                        help="""In conjuction with -x, show schedule for transpiled
                        circuit for chosen backend to stdout before running job""")
    PARSER.add_argument("--circuit_layout", action="store_true",
                        help="""With -x, write image file of circuit layout
                        after transpile (see --figure_basename)""")
    PARSER.add_argument("--optimization_level", type=int, action="store",
                        default=1, help="""Set optimization level for
                        transpilation before run, valid values 0-3,
                        default is 1""")
    PARSER.add_argument("--histogram", action="store_true",
                        help="""Write image file of histogram of experiment
                        results (see --figure_basename)""")
    PARSER.add_argument("--plot_state_city", type=int, action="store",
                        help="""Write image file of state city plot of statevector to
                        PLOT_STATE_CITY decimal points (see --figure_basename)""")
    PARSER.add_argument("--figure_basename", type=str, action="store",
                        default='figout',
                        help="""basename including path (if any) for figure output,
                        default='figout', backend name, figure type, and timestamp
                        will be appended""")
    PARSER.add_argument("--qasm", action="store_true",
                        help="Print qasm file to stdout before running job")
    PARSER.add_argument("--qc", action="store",
                        help="Indicate circuit name of python-coded QuantumCircuit")
    PARSER.add_argument("--status", action="store_true",
                        help="""Print status of chosen --backend to stdout
                        (default all backends)
                        of --api_provider (default IBMQ)
                        and exit 0""")
    PARSER.add_argument("--token", action="store",
                        help="Use this token")
    PARSER.add_argument("--url", action="store",
                        help="Use this url")
    PARSER.add_argument("--use_job_monitor", action="store_true",
                        help="""Display job monitor instead of just waiting for
                        job result""")
    PARSER.add_argument("filepath", nargs='*',
                        help="Filepath(s) to 0 or more .qasm files, default is stdin")
    PARSER.add_argument("--job_monitor_filepath", action="store", default=None,
                        help="""Filepath for Job Monitor output if Job Monitor
                        requested by --use_job_monitor, default is sys.stdout""")
    PARSER.add_argument("-w", "--warnings", action="store_true",
                        help="Don't print warnings on missing optional modules")

    ARGS = PARSER.parse_args()

    if ARGS.warnings:
        # import warnings # already imported
        warnings.filterwarnings('ignore')

    AER = ARGS.aer
    API_PROVIDER = ARGS.api_provider.upper()
    ARGS = PARSER.parse_args()
    BACKEND_NAME = ARGS.backend
    BACKENDS = ARGS.backends
    CIRCUIT_LAYOUT = ARGS.circuit_layout
    CONFIGURATION = ARGS.configuration
    DATETIME = ARGS.datetime
    FIGURE_BASENAME = ARGS.figure_basename
    FILEPATH = ARGS.filepath
    HISTOGRAM = ARGS.histogram
    JOB = ARGS.job
    JOB_ID = ARGS.job_id
    JOB_MONITOR_FILEPATH = ARGS.job_monitor_filepath
    JOB_RESULT = ARGS.job_result
    JOBS = ARGS.jobs
    MAX_CREDITS = ARGS.credits
    MEMORY = ARGS.memory
    NUQASM2 = ARGS.nuqasm2
    ONE_JOB = ARGS.one_job
    OPTIMIZATION_LEVEL = ARGS.optimization_level
    OUTFILE = ARGS.outfile
    PLOT_STATE_CITY = ARGS.plot_state_city
    PROPERTIES = ARGS.properties
    QASM = ARGS.qasm
    QASM_SIMULATOR = ARGS.qasm_simulator
    QC_NAME = ARGS.qc
    QISJOB_VERSION = ARGS.version
    QISKIT_VERSION = ARGS.qiskit_version
    QUBITS = ARGS.qubits
    QVM = ARGS.qvm
    QVM_AS = ARGS.qvm_as
    RESULT = ARGS.result
    SHOTS = ARGS.shots
    SIM = ARGS.sim
    STATEVECTOR_GPU = ARGS.statevector_gpu
    UNITARY_GPU = ARGS.unitary_gpu
    DENSITY_MATRIX_GPU = ARGS.density_matrix_gpu
    STATUS = ARGS.status
    TOKEN = ARGS.token
    TRANSPILE = ARGS.transpile
    SHOWSCHED = ARGS.showsched
    UNITARY_SIMULATOR = ARGS.unitary_simulator
    URL = ARGS.url
    USE_JM = ARGS.use_job_monitor
    VERBOSE = ARGS.verbose

    QJ = QisJob(filepaths=FILEPATH,
                provider_name=API_PROVIDER,
                backend_name=BACKEND_NAME,
                token=TOKEN, url=URL,
                nuqasm2=NUQASM2,
                num_qubits=QUBITS, shots=SHOTS, max_credits=MAX_CREDITS,
                outfile_path=OUTFILE, one_job=ONE_JOB, qasm=QASM,
                use_aer=AER,
                use_qasm_simulator=QASM_SIMULATOR,
                use_unitary_simulator=UNITARY_SIMULATOR,
                use_statevector_gpu=STATEVECTOR_GPU,
                use_unitary_gpu=UNITARY_GPU,
                use_density_matrix_gpu=DENSITY_MATRIX_GPU,
                use_sim=SIM, qvm=QVM, qvm_as=QVM_AS,
                qc_name=QC_NAME, xpile=TRANSPILE, showsched=SHOWSCHED,
                circuit_layout=CIRCUIT_LAYOUT,
                optimization_level=OPTIMIZATION_LEVEL,
                print_job=JOB, memory=MEMORY, show_result=RESULT,
                jobs_status=JOBS, job_id=JOB_ID, job_result=JOB_RESULT,
                show_backends=BACKENDS, show_configuration=CONFIGURATION,
                show_properties=PROPERTIES,
                show_statuses=STATUS, date_time=DATETIME,
                print_histogram=HISTOGRAM, print_state_city=PLOT_STATE_CITY,
                figure_basename=FIGURE_BASENAME,
                show_q_version=QISKIT_VERSION, verbose=VERBOSE,
                show_qisjob_version=QISJOB_VERSION,
                use_job_monitor=USE_JM,
                job_monitor_filepath=JOB_MONITOR_FILEPATH)

    EXITVAL = 0
    try:
        QJ.do_it()
    except QisJobException as ex:
        print(type(ex).__name__ + ' : ' + ex.message, file=sys.stderr)
        EXITVAL = ex.retval
    sys.exit(EXITVAL)