#!/usr/bin/env python3  # pylint: disable-msg=too-many-lines
# -*- coding: utf-8 -*-
"""`qisjob.py`

Load from OpenQASM source or Qiskit `QuantumCircuit` source and run job with
reporting. Many utility operations to examine provider, backends, and jobs
are also provided.

The main repository is https://github.com/jwoehr/qisjob

Copyright 2019, 2022 Jack Woehr jwoehr@softwoehr.com PO Box 82, Beulah, CO 81023-0082

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

The class to instance in a program is `QisJob`.

    1. Instance a QisJob with appropriate kwargs.
    2. Call the member function do_it()

    Optionally, wrapper the do_it() in try - except.

The `qisjob` script is for command-line usage which instances a `QisJob` and
calls `do_it()`.  The script provides a `--help` switch which will explain all
the optional arguments.

The `qisjob` script will be mentioned in the `QisJob` documentation. To better
understand the documentation, we recommended that the reader execute

    qisjob --help

and examine the output.

*Note* that many functions which are really private are exposed and documented
here to make it easier to understand what QisJob does in its `do_it()` method.
"""

import argparse
import datetime
from io import StringIO, TextIOWrapper
import pprint
import sys
from typing import Any
import warnings

from qiskit import (
    IBMQ,
    QuantumCircuit,
    execute,
    schedule,
    QiskitError,
    __qiskit_version__,
)
from qiskit.compiler import transpile
from qiskit.providers import BackendV2, JobV1
from qiskit.providers.ibmq import least_busy
from qiskit.providers.ibmq.job import IBMQJob
from qiskit.result import Result
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_circuit_layout, plot_state_city, plot_histogram
from qiskit import Aer
from qiskit_aer.noise import NoiseModel
from matplotlib.figure import Figure

try:
    from qiskit.providers.ibmq.exceptions import IBMQAccountCredentialsNotFound
    from qiskit.providers.ibmq.job.exceptions import IBMQJobFailureError
    from qiskit.providers.exceptions import QiskitBackendNotFoundError
except ImportError:
    warnings.warn("Qiskit IBMQ provider not installed.")

try:
    from qiskit_ibm_provider import IBMProvider, IBMInputValueError, IBMProviderError #, least_busy
    from qiskit_ibm_provider.job import IBMJob
    from qiskit_ibm_provider.job.exceptions import IBMJobFailureError
except ImportError:
    warnings.warn("Qiskit IBMProvider not installed.")

try:
    from nuqasm2 import Ast2Circ, Qasm_Exception, Ast2CircException
except ImportError:
    warnings.warn("NuQasm2 not installed.")

try:
    from quantuminspire.api import QuantumInspireAPI
    from quantuminspire.qiskit import QI
    from quantuminspire.credentials import enable_account as qi_enable_account
except ImportError:
    warnings.warn("QuantumInspire not installed.")

try:
    from quantastica.qiskit_forest import ForestBackend
except ImportError:
    warnings.warn("Quantastica Qiskit_Forest not installed.")

try:
    from mqt import ddsim
except ImportError:
    warnings.warn("MQT DDSIMProvider not installed.")

from .qisjobex import QisJobException, QisJobArgumentException, QisJobRuntimeException


class QisJob:  # pylint: disable-msg=too-many-instance-attributes, too-many-public-methods
    """
    Embody preparation, execution, display, and management of Qiskit job or jobs.

    A `QisJob` instance can also fetch information about provider backends.

    A `QisJob` is instanced with all the member variables governing its behavior
    and then the `do_it()` member function is called. After that, generally,
    the instance is discarded.
    """

    def __init__(  # pylint: disable-msg=too-many-arguments, too-many-locals, too-many-statements, line-too-long
        self,
        filepaths=None,
        qasm_src=None,
        provider_name="IBMQ",
        hub="ibm-q",
        group="open",
        project="main",
        providers=False,
        backend_name=None,
        token=None,
        url=None,
        nuqasm2=None,
        num_qubits=5,
        shots=1024,
        outfile_path=None,
        one_job=False,
        qasm=False,
        use_aer=False,
        use_qasm_simulator=False,
        use_unitary_simulator=False,
        use_statevector_gpu=False,
        use_unitary_gpu=False,
        use_density_matrix_gpu=False,
        use_sim=False,
        qvm=False,
        qvm_as=False,
        qc_name=None,
        xpile=False,
        showsched=False,
        circuit_layout=False,
        optimization_level=1,
        print_job=False,
        memory=False,
        show_result=False,
        jobs_status=None,
        job_id=None,
        job_result=None,
        show_backends=False,
        show_configuration=False,
        show_properties=False,
        show_statuses=False,
        date_time=None,
        print_histogram=False,
        print_state_city=0,
        figure_basename="figout",
        show_q_version=False,
        verbose=0,
        show_qisjob_version=False,
        use_job_monitor=False,
        job_monitor_filepath=None,
        job_monitor_line="\r",
        noisy_sim=False,
    ):
        """

        QisJob's initializer instances QisJob member data which control
        the instance's behavior when QisJob's main function `do_it()` is called.

        In the parameter discussion below, actions are described as being
        taken by `QisJob`. Typically, these actions are actually taken when
        the `do_it()` method is called, not when member variables are instanced
        at `__init__` time.

        Parameters
        ----------

        filepaths : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: Any and all undecorated
            arguments following the `--` decorated switch arguments are taken
            to be files to add to the `filepaths` kwarg.

            List of fully qualified or relative filepaths for experiments.

            If `filepaths` is `None` source is read from stdin.

            If `qasm_src` is set, this kwarg is ignored.

        qasm_src : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: _none_

            A string of OpenQASM experiment source.

            If `qasm_src` is set, it takes precedence and `filepaths`
            is ignored.

        provider_name : str
            The default is "IBMQ".

            _Corresponding `qisjob` script argument_: `--api_provider`

            The name of the backend provider. Currently supported are

                * IBMQ
                * Forest
                * MQT
                * QI

        hub: str

            The default is 'ibm-q'.

            _Corresponding `qisjob` script argument_: `--hub`

            Provider hub. For instance, IBMQ accounts have 3 attributes,
            the names and defaults for which are

                hub='ibm-q', group='open', project='main'

        group: str
            The default is 'open'.

            _Corresponding `qisjob` script argument_: `--group`

            Provider group. For instance, IBMQ accounts have 3 attributes,
            the names and defaults for which are

                hub='ibm-q', group='open', project='main'

        project: str
            The default is 'main'.

            _Corresponding `qisjob` script argument_: `--project`

            Provider project. For instance, IBMQ accounts have 3 attributes,
            the names and defaults for which are

                hub='ibm-q', group='open', project='main'

        providers: bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--providers`

            List providers for IBM Q and return.

        backend_name : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `-b, --backend`

            Name of chosen backend for given provider.

            If provider is IBMQ and backend_name is `None`, `QisJob`
            will search for
            [`least_busy()`](https://qiskit.org/documentation/stubs/qiskit.providers.ibmq.least_busy.html). # pylint: disable=line-too-long

        token : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--token`

            Login token for provider. This is a string even if it looks
            like a giant hexadecimal number.

            If provided, then `url` must also be provided.

            If not provided, `QisJob` will either attempt the supported
            provider's automatic load of login credentials or simply
            attempt the connection without credentials.

        url : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--url`

            URL of backend provider gateway

            If provided, then `token` must also be provided.

            If not provided, `QisJob` will assume the default URL
            for the supported provider's backend.

        nuqasm2 : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--nuqasm2`

            This is a "double purpose" switch. Its target is an include path
            for OpenQASM include files, which, if present, serves
            to indicate that [nuqasm2](https://github.com/jwoehr/nuqasm2)
            should be used as the OpenQASM compiler.

        num_qubits : int
            The default is 5.

            _Corresponding `qisjob` script argument_: `-q, --qubits`

            Number of qubits required for any and all experiment(s).

        shots : int
            The default is 1024.

            _Corresponding `qisjob` script argument_: `-t, --shots`

            Number of shots performed for any and all experiment(s).
            Subject to limitation of the provider backend.

        outfile_path : str
            The default is stdout.

            _Corresponding `qisjob` script argument_: `-o, --outfile`

            Write CSV output of experiment(s) to the target argument.

        one_job : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-1, --one_job`

            Run all experiments provided via the `filepaths` member in one job.

            The default is to submit one job per experiment.

        qasm : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--qasm`

            If `True`, print each qasm file to stdout before running job.

        use_aer : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-a, --aer`

            If `True` use QISKit Aer simulator.

            The default Aer simulator is the Aer statevector simulator.
            In conjunction with this kwarg:

                * Set use_qasm_simulator True for Aer qasm simulator.
                * Set use_unitary_simulator True for Aer unitary simulator.

            It is an error to set both `qasm_simulator` and `unitary_simulator`
            `True`.

        use_qasm_simulator : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--qasm_simulator`

            In conjunction with `use_aer`, use Aer's qasm simulator.

        use_unitary_simulator : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--unitary-simulator`

            In conjunction with `use_aer`, use Aer's unitary simulator.

        use_statevector_gpu : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--statevector_gpu`

            If `True` and `use_aer` is `True` and `use_qasm_simulator` is
            `True`, use gpu statevector simulator.

        use_unitary_gpu : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--unitary_gpu`

            If `True` and `use_aer` is `True` and `use_qasm_simulator` is
            `True`, use gpu unitary simulator.

        use_density_matrix_gpu : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--density_matrix_gpu`

            If `True` and `use_aer` is `True` and `use_qasm_simulator` is
            `True`, use gpu density matrix simulator.

        use_sim : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-s, --sim`

            If `True`, use IBMQ online qasm simulator

        qvm : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--qvm`

            If `True`. use Forest local qvm simulator described by
            `backend_name`, generally one of `qasm_simulator` or
            `statevector_simulator`. Use `qvm_as` to instruct the
            simulator to emulate a specific Rigetti QPU.

        qvm_as : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--qvm_as`

            If `True`. use Forest local qvm simulator to emulate the
            specific Rigetti QPU described by -b backend. Use --qvm
            to run the Forest local qvm simulator described by
            -b backend

        qc_name : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--qc`

            If set, indicates the name of a variable instanced to a
            Python-coded `QuantumCircuit` to be run. If set, each and every
            file (or input from stdin) must contain valid Python code
            containing such an instance.

            Do not include any Qiskit job control in the file. All that
            needs to be included or imported is the circuit itself.

            *Warning* QisJob uses Python `exec()` to run your included
            circuit file. No sanitization is performed. The code will be
            executed as-is.

        xpile : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-x, --transpile`

            If `True`, test-transpile the circuit for chosen backend into a
            new circuit and print the new circuit to stdout before jobbing the
            original circuit.

            The level of transpilation is that indicated by the kwarg
            `optimization_level`.

        showsched : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--showsched`

            If `True`, in conjuction with `xpile`, show schedule for the
            test- transpiled circuit to stdout before jobbing the
            original circuit.

        circuit_layout
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-circuit_layout`

            If `True`, and if `xpile` is also set, write image file of circuit
            layout to the fully qualified filepath specified by the
            `figure_basename` kwarg concatenated with an algorithmically added
            filename extension indicating the type of output and time.

        optimization_level : int
            The default is 1.

            _Corresponding `qisjob` script argument_: `--optimization_level`

            Set optimization level for transpilation before run.
            Valid values are 0-3, default is 1.

            This affects not only the actual circuit, but alsothe test
            transpile, if the latter is invoked by the `xpile` kwarg.

        print_job : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-j, --job`

            If `True`, print the Job dictionary to stdout before and after run.

        memory : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-m, --memory`

            If `True`, print individual results of each multishot experiment
            to stdout.

        show_result : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-r, --result`

             If `True`, print each Job's result to stdout.

        jobs_status : int
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--jobs`

            If instanced, print that number of most recent jobs and status
            for the selected backend to stdout and return.

            See `do_it()` for the precedence of this kwarg.

        job_id : int
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--job_id`

            If instanced, print that job number (job id) for the chosen
            backend to stdout and return.

            See `do_it()` for the precedence of this kwarg.

        job_result : int
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--job_result`

            If instanced, print the result for that (completed) job number
            (job id) to stdout and return.

            See `do_it()` for the precedence of this kwarg.

        show_backends : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--backends`

            If `True`, print list of backends for chosen provider to stdout and
            return.

            See `do_it()` for the precedence of this kwarg.

        show_configuration : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-g, --configuration`

            If `True`, print configuration for backend specified by -b
            to stdout and return.

            See `do_it()` for the precedence of this kwarg.

        show_properties : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `p, --properties`

            If `True`, print properties for backend specified by -b to stdout
            and return.

            For historical properties, also set the `date_time` kwarg.

            See `do_it()` for the precedence of this kwarg.

        show_statuses : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: --status

            If `True`, print status for chosen backend to stdout and return.
            If no backend chosen, print statuses for all of the chosen
            provider's backends.

            See `do_it()` for the precedence of this kwarg.

        date_time : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `-d, --datetime`

            Datetime year,month,day[,hour,min,sec] for showing properties
            of a backend in conjunction with the `show_properties` kwarg.

        print_histogram : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--histogram`

            If `True`, write image file of histogram of experiment results
            to the fully qualified filepath specified by the `figure_basename`
            kwarg concatenated with an algorithmically added filename extension
            indicating the type of output and time.

        print_state_city : int
            The default is 0.

            _Corresponding `qisjob` script argument_: `--plot_state_city`

            If non-zero, write image file of state city plot of statevector to
            the number of decimal points indicated by the int value to the fully
            qualified filepath specified by the `figure_basename` kwarg
            concatenated with an algorithmically added filename extension
            indicating the type of output and time.

        figure_basename : str
            The default is 'figout'.

            _Corresponding `qisjob` script argument_: `--figure_basename`

            Basename including path (if any) for figure output, in conjunction
            with kwargs `print_histogram` and `print_state_city`. The backend
            name, figure type, and timestamp will be concatenated to form
            the full filename.

        show_q_version : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `-qiskit_version`

             If `True`, `do_it()` print Qiskit version to stdout and returns.

            See `do_it()` for the precedence of this kwarg.

        verbose : int
            The default is 0.

            _Corresponding `qisjob` script argument_: `-v, --verbose`

            Set the verbosity level of miscellaneous informational messages
            emitted to stderr by do_it().

            The general range is 0-3. If set precisely to 4, `do_it()`
            will print the `QisJob` instance's data dictionary and return.

        show_qisjob_version : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--version`

            If `True`, `do_it()` print QisJob version to stdout and returns.

            See `do_it()` for the precedence of this kwarg.

        use_job_monitor : bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--use_job_monitor`

            If `True`, display the periodically updated job monitor output
            instead of just blocking waiting for job result to return.

        job_monitor_filepath : str
            The default is `None`.

            _Corresponding `qisjob` script argument_: `--job_monitor_filepath`

            In conjunction with `use_job_monitor`, set an output filepath for
            job monitor output instead of the default outstream of stdout.

        job_monitor_line: str
            The default is a string consisting solely of carriage-return `0x0d`.

            _Corresponding `qisjob` script argument_: `--job_monitor_line`

            Sets the string emitted at the head of every line of job monitor
            output. The default causes the cursor to jump back to the head
            of the line on typical terminals so as to overwrite the previous
            output and update the user interactively without scrolling the
            screen. For program usage, a different string can be set.

        noisy_sim: bool
            The default is `False`.

            _Corresponding `qisjob` script argument_: `--noisy_sim`

            Performs an Aer sim noise model using the designated backend
            (see --backend) as the model backend.

        """
        self.qasm_src = qasm_src
        self.provider_name = provider_name.upper()
        self.hub = hub
        self.group = group
        self.project = project
        self.providers = providers
        self.provider = None
        self.filepaths = filepaths
        self.backend_name = backend_name
        self.backend = None
        self.token = token
        self.url = url
        self.nuqasm2 = nuqasm2
        self.num_qubits = num_qubits
        self.shots = shots
        self.outfile_path = outfile_path
        self.one_job = one_job
        self.qasm = qasm
        self.use_aer = use_aer
        self.use_qasm_simulator = use_qasm_simulator
        self.use_unitary_simulator = use_unitary_simulator
        self.use_statevector_gpu = use_statevector_gpu
        self.use_unitary_gpu = use_unitary_gpu
        self.use_density_matrix_gpu = use_density_matrix_gpu
        self.use_sim = use_sim
        self.qvm = qvm
        self.qvm_as = qvm_as
        self.qc_name = qc_name
        self.xpile = xpile
        self.showsched = showsched
        self.circuit_layout = circuit_layout
        self.optimization_level = optimization_level
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
        self.local_simulator_type = "statevector_simulator"
        self.show_qisjob_version = show_qisjob_version
        self.method = None  # methods for simulators e.g., gpu
        self.my_version = "v4.1.2.dev0"
        self.qasm_result = None
        self.result_exp_dict = None
        self.use_job_monitor = use_job_monitor
        self.job_monitor_filepath = job_monitor_filepath
        self.job_monitor_line = job_monitor_line
        self.noisy_sim = noisy_sim

    def __str__(self) -> str:
        out = StringIO()
        pprint.pprint(self.__dict__, out)
        return "{}\n{}".format(super().__str__(), out.getvalue())

    def qisjob_version(self) -> str:
        """

        Return version of QisJob

        Returns
        -------
        str
            version string for QisJob.
        """
        return self.my_version

    def do_it(
        self,
    ):  # pylint: disable-msg=too-many-branches, too-many-statements, too-many-return-statements
        """

        Run the program specified by ctor args/kwargs, usally instanced
        from the driver script. Afterwards, the QisJob instance is usually
        discarded, or the members can be carefully edited and the instance
        reused.

        `do_it()` has many logical branches depending on the request made
        as represented at instancing. Below, in order of branching, are the
        main branches.

        The best information on QisJob logic in `QisJob.do_it()` is the source
        code itself; the following is a lite summary.

            1. If show_qisjob_version print QisJob version and return.
            2. If show_q_version Qiskit version shown and return.
            3. If providers show IBM Q providers and return.
            4. If show_configuration print config for -b backend and return.
            5. If show_properties print properties for -b backend and return.
            6. If show_backends print list of backends for provider and return.
            7. If show_statuses print status or statuses for -b backend
                or if no backend specified, for all backends for provider
                and return.
            8. If jobs_status print status for n jobs and return.
            9. If job_id then print job dict for that job and return.
            10. If job_result then print job result for that job and return.

        Otherwise, proceed to job experiments provided in kwargs as follows:

            1. If qasm_src job and return.
            2. If filepaths read, job, and return.
            3. Else read stdin for qasm src. On EOF, job and return.

        Returns
        -------
            None.

        Raises
        ------
            QisJobException -+
                             |
                             + QisJobArgumentException
                             |
                             + QisJobRuntimeException


        *Note*: Applications should wrap `do_it()` in try-except `QiskitError` as
        miscellaneous instances can be raised in ways the code does not anticipate.

        See the `qisjob` script for an example of this pattern.

        """
        if self.verbose == 4:
            self._pp.pprint(self.__dict__)
            return

        if self.show_qisjob_version:
            print(self.my_version)
            return

        if self.show_q_version:
            self._pp.pprint(__qiskit_version__)
            return

        if self.provider_name == "IBMQ" and (
            (self.token and not self.url) or (self.url and not self.token)
        ):
            raise QisJobArgumentException(
                "kwargs token and url must be used together for IBMQ provider or not at all"
            )

        if self.providers:
            self.account_fu()

            try:
                self._pp.pprint(IBMQ.providers())
            except QiskitError as err:
                raise QisJobRuntimeException(
                    f"Error fetching IBMQ providers: {err}"
                ) from err
            return

        if self.show_configuration:
            self.account_fu()

            try:
                self.backend = self.provider.get_backend(self.backend_name)
            except QiskitBackendNotFoundError as err:
                raise QisJobRuntimeException(
                    f"Backend {self.backend_name} not found: {err}"
                ) from err

            self._pp.pprint(self.backend.configuration().to_dict())
            return

        if self.show_properties:
            self.account_fu()

            try:
                self.backend = self.provider.get_backend(self.backend_name)
            except QiskitBackendNotFoundError as err:
                raise QisJobRuntimeException(
                    f"Backend {self.backend_name} not found: {err}"
                ) from err

            the_date_time = (
                QisJob.gen_datetime(self.date_time) if self.date_time else None
            )
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
                        f"Backend {self.backend_name} not found: {err}"
                    ) from err

            for stat in self.get_statuses():
                self._pp.pprint(stat)

        elif self.jobs_status or self.job_id or self.job_result:
            if not self.backend_name:
                raise QisJobArgumentException(
                    "kwargs jobs or job_id or job_result also require kwarg backend"
                )

            self.account_fu()

            try:
                self.backend = self.provider.get_backend(self.backend_name)
            except QiskitBackendNotFoundError as err:
                raise QisJobRuntimeException(
                    f"Backend {self.backend_name} not found: {err}"
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
                            a_job = self.ibmqjob_to_dict(a_job)
                        else:
                            a_job = a_job.to_dict()
                    self._pp.pprint(a_job)
                return

            if self.job_id:
                a_job = self.backend.retrieve_job(self.job_id)
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(a_job)
                    else:
                        a_job = a_job.to_dict()
                return

            if self.job_result:
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

    def verbosity(self, printable: Any, count: int):
        """
        Print some printable item to stdout if count exceeds verbose level.

        Parameters
        ----------
        printable : str
            Item to print.
        count : int
            Level that self.verbose must equal or exceed to print message.

        Returns
        -------
        None.

        """
        if self.verbose >= count:
            print(printable)

    @staticmethod
    def gen_datetime(datetime_comma_string: str) -> datetime.datetime:
        """
        Convert comma-separated date elements to datetime.

        Parameters
        ----------
        datetime_comma_string : str
            String of comma-separated date elements
            year,month,day[,hour,min,sec]

        Returns
        -------
        datetime.datetime
            Python datetime object

        """
        the_args = []
        the_split = datetime_comma_string.split(",")
        for i in the_split:
            the_args.append(int(i))
        return datetime.datetime(*the_args)

    def ibmq_account_fu(self):
        """Load IBMQ account appropriately and instance self with provider"""
        try:
            try:
                if self.token:
                    self.provider = IBMProvider(token=self.token, url=self.url)
                else:
                    self.provider = IBMProvider()
            except IBMInputValueError as err:
                raise QisJobRuntimeException(
                    f"Error loading account via IBMProvider: {err}"
                ) from err

        except NameError:
            try:
                if self.token:
                    IBMQ.enable_account(self.token, url=self.url)
                else:
                    self.provider = IBMQ.load_account()
            except IBMQAccountCredentialsNotFound as err:
                raise QisJobRuntimeException(
                    f"Error loading IBMQ Account: {err}"
                ) from err
            self.provider = IBMQ.get_provider(
                hub=self.hub, group=self.group, project=self.project
            )

    def qi_account_fu(self):
        """Load Quantum Inspire account appropriately and instance self
        with provider"""
        if self.token:
            qi_enable_account(self.token)
        QI.set_authentication()
        self.provider = QI

    def forest_account_fu(self):
        """Load Rigetti Forest account appropriately and instance self with
        provider"""
        self.provider = ForestBackend

    def mqt_account_fu(self):
        """Load MQT DDSIMprovider and instance self with provider"""
        self.provider = ddsim.DDSIMProvider()

    def account_fu(self):
        """Load account from correct API provider and instance self with
        provider"""
        if self.provider_name == "IBMQ":
            self.ibmq_account_fu()
        elif self.provider_name == "QI":
            self.qi_account_fu()
        elif self.provider_name == "Forest":
            self.forest_account_fu()
        elif self.provider_name == "MQT":
            self.mqt_account_fu()

    def choose_backend(
        self,
    ):  # pylint: disable-msg=too-many-branches, too-many-statements
        """Instance self with backend selected by user if account will
        activate and allow."""
        self.backend = None

        # Choose simulator. We defaulted in __init__() to statevector_simulator
        if self.use_qasm_simulator:
            self.local_simulator_type = "qasm_simulator"
        elif self.use_unitary_simulator:
            self.local_simulator_type = "unitary_simulator"

        # Choose method kwarg for gpu etc if present
        if self.use_statevector_gpu:
            self.method = "statevector_gpu"
        elif self.use_unitary_gpu:
            self.method = "unitary_gpu"
        elif self.use_density_matrix_gpu:
            self.method = "density_matrix_gpu"

        if self.use_aer:

            if self.method:
                self.verbosity(
                    f"self.local_simulator_type is '{self.local_simulator_type}' with method '{self.method}'",  # pylint: disable-msg=line-too-long
                    2,
                )
            else:
                self.verbosity(f"Aer backend is {self.backend}", 2)
            self.backend = Aer.get_backend(self.local_simulator_type)

        elif self.qvm or self.qvm_as:
            self.backend = ForestBackend.get_backend(self.backend_name, self.qvm_as)
            self.verbosity(f"qvm provider.get_backend() returns {str(self.backend)}", 3)

        else:
            self.account_fu()
            self.verbosity(f"Provider is {str(self.provider)}", 3)
            self.verbosity(f"Provider.backends is {str(self.provider.backends())}", 3)

            if self.backend_name:
                try:
                    self.backend = self.provider.get_backend(self.backend_name)
                except QiskitBackendNotFoundError as err:
                    raise QisJobRuntimeException(
                        f"Backend {self.backend_name} not found: {err}"
                    ) from err
                self.verbosity(f"provider.get_backend() returns {str(self.backend)}", 3)

            elif self.use_sim:
                self.backend = self.provider.get_backend("ibmq_qasm_simulator")
                self.verbosity(
                    f"sim provider.get_backend() returns {str(self.backend)}", 3
                )

            elif self.provider_name == "QI":
                for b_e in self.provider.backends():
                    if (
                        b_e.__dict__["_QuantumInspireBackend__backend"][
                            "number_of_qubits"
                        ]
                        >= self.num_qubits
                    ):
                        self.backend = b_e
                        self.verbosity(f"Backend is {str(self.backend)}", 1)
                        break
                if not self.backend:
                    raise QisJobRuntimeException(
                        f"No suitable backend found for {str(self.num_qubits)} qubits"
                    )
            else:
                large_enough_devices = self.provider.backends(
                    filters=lambda x: x.configuration().n_qubits >= self.num_qubits
                    and not x.configuration().simulator
                )
                try:
                    self.backend = least_busy(large_enough_devices)
                except QiskitError as err:
                    raise QisJobRuntimeException(
                        f"QiskitError no device found for criteria (large enough?) {err}"
                    ) from err
                self.verbosity(f"The best backend is {self.backend.name()}", 2)
                self.verbosity(f"Backend is {str(self.backend)}", 1)

    @staticmethod
    def csv_str(description: str, sort_keys: list, sort_counts: list) -> list:
        """
        Generate a CSV as a list of two strings from sorted keys
        and sorted counts.

        Parameters
        ----------
        description : str
            Text description of CSV
        sort_keys : list
            List of keys (classical bit patterns)
        sort_counts : list
            List of counts

        Returns
        -------
        list
            Two strings representing the key row and count row.

        """
        csv = []
        csv.append(description)
        keys = ""
        for key in sort_keys:
            keys += key + ";"
        csv.append(keys)
        counts = ""
        for count in sort_counts:
            counts += str(count) + ";"
        csv.append(counts)
        return csv

    @staticmethod
    def fig_name_str(filepath: str, backend: BackendV2) -> str:
        """
        Create filename consisting of filepath, backend and timestamp.

        Parameters
        ----------
        filepath : str
            base filepath fqp.
        backend : BackendV2
            backend ostensibly one that experiment was run on.

        Returns
        -------
        str
            the algorithmically generated filename.

        """
        return filepath + "_" + str(backend) + "_" + datetime.datetime.now().isoformat()

    @staticmethod
    def save_fig(figure: Figure, filepath: str, backend: BackendV2, tail: str):
        """
        Write a figure to an algorithmically named destination file

        Parameters
        ----------
        figure : Figure
            The matplotlib Figure.
        filepath : str
            base filepath fqp
        backend : BackendV2
            Ostensibly the Backend the experiment was run on.
        tail : str
            uniquifying string to append to filename.

        Returns
        -------
        None.

        """
        figure.savefig(QisJob.fig_name_str(filepath, backend) + "." + tail)

    @staticmethod
    def state_city_plot(
        result_exp: Result,
        circ: QuantumCircuit,
        figure_basename: str,
        backend: BackendV2,
        decimals: int = 3,
    ):
        """
        Plot state_city-style the output state to file. Filename algorithmically
        generated from figure_basename plus concatenated type and timestamp.

        result_exp - experiment result
        circ - the circuit
        figure_basename - base file name of output
        backend - backend run on
        decimals - how many decimal places


        Parameters
        ----------
        result_exp : Result
            experiment result.
        circ : QuantumCircuit
            DESCRIPTION.
        figure_basename : str
            the circuit.
        backend : BackendV2
            backend run on.
        decimals : int, optional
            how many decimal places. The default is 3.

        Returns
        -------
        None.

        """
        outputstate = result_exp.get_statevector(circ, decimals)
        fig = plot_state_city(outputstate)
        QisJob.save_fig(fig, figure_basename, backend, "state_city.png")

    @staticmethod
    def do_histogram(
        result_exp: Result,
        circ: QuantumCircuit,
        figure_basename: str,
        backend: BackendV2,
    ):
        """
        Plot histogram-style the result to file. Filename algorithmically
        generated from figure_basename plus concatenated type and timestamp.

        Parameters
        ----------
        result_exp : Result
            experiment result
        circ : QuantumCircuit
            the circuit
        figure_basename : str
            base file name of output.
        backend : BackendV2
            backend experiment was run on.

        Returns
        -------
        None.

        """

        outputstate = result_exp.get_counts(circ)
        fig = plot_histogram(outputstate)
        QisJob.save_fig(fig, figure_basename, backend, "histogram.png")

    def formulate_result(
        self, result_exp: Result, circ: QuantumCircuit, ofh: TextIOWrapper
    ) -> list:
        """
        Formulate the result `result_exp` of one circuit `circ`
        returning output as string optionally also writing
        this same output to a file.

        Optionally also write the qasm for the circuit if the `qasm`
        kwarg was `True` when the `QisJob` was instanced. This is written
        to `ofh` but not added to the method return.

        Parameters
        ----------
        result_exp : dict
            The dict result of an experiment
        circ : QuantumCircuit
            The circuit for the experiment
        ofh : TextIOWrapper
            Output file handle to which output is written.
            May be `None`.

        Returns
        -------
        list
            The output list representing the result in csv form.
            It is also written to `ofh` if that handle is instanced.

        """
        # Write qasm if requested
        if self.qasm and ofh:
            ofh.write(circ.qasm() + "\n")

        # Raw data if requested
        if self.memory:
            self._pp.pprint(result_exp.data(circ))

        # Print statevector ... this doesn't handle Forest qvm yet
        if self.use_aer and self.local_simulator_type == "statevector_simulator":
            self._pp.pprint(result_exp.get_statevector(circ))

        output = None

        # Print counts if any measurment was taken
        if "counts" in result_exp.data(circ):
            counts_exp = result_exp.get_counts(circ)
            self.verbosity(counts_exp, 1)
            sorted_keys = sorted(counts_exp.keys())
            sorted_counts = []
            for i in sorted_keys:
                sorted_counts.append(counts_exp.get(i))

            # Generate CSV
            output = QisJob.csv_str(
                str(self.backend) + " " + datetime.datetime.now().isoformat(),
                sorted_keys,
                sorted_counts,
            )
        return output

    def process_result(
        self, result_exp: Result, circ: QuantumCircuit, ofh: TextIOWrapper
    ):
        """
        Process the result of one `QuantumCircuit circ`
        experiment from its `Result result_exp`
        printing to output file handle `ofh`
        and pass original qasm filepath to figure output.

        Parameters
        ----------
        result_exp : Result
            Result of experiment.
        circ : QuantumCircuit
            Circuit subject of experiment.
        ofh : TextIOWrapper
            Output file handle, possibly (typically) stdout.

        Returns
        -------
        None.

        """
        output = self.formulate_result(result_exp, circ, ofh)

        if output:
            # Write CSV
            for line in output:
                ofh.write(line + "\n")

            if self.print_state_city:
                QisJob.state_city_plot(
                    result_exp,
                    circ,
                    self.figure_basename,
                    self.backend,
                    decimals=self.print_state_city,
                )
            if self.print_histogram:
                QisJob.do_histogram(
                    result_exp, circ, self.figure_basename, self.backend
                )

    def one_exp(
        self, filepath_name: str = None
    ):  # pylint: disable-msg=too-many-locals, too-many-branches, too-many-statements, line-too-long
        """
        Load experiment source (OpenQASM or Python QuantumCircuit source) and
        run the job. print csv and other selected output.

        Parameters
        ----------
        filepath_name : str, optional
            Filepath to experiment source. The default is None.
            If None, read from stdin.

        Returns
        -------
        None.

        Raises
        ------
        QisJobRuntimeException
        """

        circ = None

        if filepath_name is None:
            ifh = sys.stdin
        else:
            ifh = open(filepath_name, "r")

        if self.outfile_path is None:
            ofh = sys.stdout
        else:
            ofh = open(self.outfile_path, "w")

        if self.backend is None:
            raise QisJobRuntimeException("No backend available, quitting.")

        self.verbosity(
            f"File path is {'stdin' if ifh is sys.stdin else filepath_name}", 2
        )
        self.verbosity(f"File handle is {str(ifh)}", 3)

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
                try:
                    circ = Ast2Circ.from_qasm_str(
                        the_source_list, include_path=self.nuqasm2, no_unknown=True
                    )

                except (Qasm_Exception, Ast2CircException) as err:
                    x = err.errpacket()  # pylint: disable-msg=invalid-name
                    raise QisJobRuntimeException(
                        f"Filepath name error {filepath_name} {err} {x}"
                    ) from err

                self.verbosity(
                    f"Unrolled circuit's OPENQASM source code\n{circ.qasm()}",
                    3,
                )

            else:
                circ = QuantumCircuit.from_qasm_str(the_source)

            self.verbosity(circ.draw(), 2)

        if self.xpile:
            new_circ = transpile(
                circ, backend=self.backend, optimization_level=self.optimization_level
            )
            print(new_circ)
            if self.circuit_layout:
                fig = plot_circuit_layout(new_circ, self.backend)
                QisJob.save_fig(
                    fig, self.figure_basename, self.backend, "plot_circuit.png"
                )

            if self.showsched:
                self._pp.pprint(schedule(new_circ, self.backend))

        try:
            if self.noisy_sim:
                job_exp = self.basic_noise_sim(circ, self.backend)

            elif self.method:
                self.verbosity(f"Using gpu method {self.method}", 2)
                backend_options = {"method": self.method}
                job_exp = execute(
                    circ,
                    backend=self.backend,
                    backend_options=backend_options,
                    optimization_level=self.optimization_level,
                    shots=self.shots,
                    memory=self.memory,
                )
            else:
                job_exp = execute(
                    circ,
                    backend=self.backend,
                    optimization_level=self.optimization_level,
                    shots=self.shots,
                    memory=self.memory,
                )

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("Before run:")
                self._pp.pprint(a_job)

            if self.use_job_monitor:
                if self.job_monitor_filepath:
                    self.verbosity(
                        f"File for job monitor output is {self.job_monitor_filepath}",
                        1,
                    )
                    j_m_file = open(self.job_monitor_filepath, mode="w", buffering=1)
                    if self.job_monitor_line != "\r":  # line_discipline kwarg only
                        job_monitor(
                            job_exp,  # recently added to Qiskit
                            output=j_m_file,
                            line_discipline=self.job_monitor_line,
                        )
                    else:
                        job_monitor(job_exp, output=j_m_file)
                    j_m_file.close()
                else:
                    if self.job_monitor_line != "\r":  # line_discipline kwarg only
                        job_monitor(
                            job_exp,  # recently added to Qiskit
                            line_discipline=self.job_monitor_line,
                        )
                    else:
                        job_monitor(job_exp)

            result_exp = job_exp.result()
            self.result_exp_dict = result_exp.to_dict()

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("After run:")
                self._pp.pprint(a_job)

            if self.use_statevector_gpu:
                try:
                    self.verbosity(
                        f"Method: {result_exp.data(circ).metadata.get('method')}",
                        2,
                    )
                except AttributeError as err:
                    print(f"AttributeError error: {err}")

            if self.show_result:
                self._pp.pprint(self.result_exp_dict)

            # Open outfile
            self.verbosity(
                f"Outfile is {'stdout' if ofh is sys.stdout else self.outfile_path}",
                2,
            )
            self.verbosity(f"File handle is {str(ofh)}", 3)

            self.process_result(result_exp, circ, ofh)

        except (IBMQJobFailureError, IBMJobFailureError) as err:
            raise QisJobRuntimeException(
                f"Job failure {err} {job_exp.error_message()}"
            ) from err

        if ofh is not sys.stdout:
            ofh.close()

    def multi_exps(
        self,
    ):  # pylint: disable-msg=too-many-locals, too-many-branches, too-many-statements, line-too-long
        """Load qasms and run all as one the job,
        print csvs and other selected output
        """
        if self.backend is None:
            # not sure this is right thing to print
            raise QisJobRuntimeException(f"No backend {self.backend_name}")

        if self.outfile_path is None:
            ofh = sys.stdout
        else:
            ofh = open(self.outfile_path, "w")

        self.verbosity(
            f"Outfile is {'stdout' if ofh is sys.stdout else self.outfile_path}", 2
        )
        self.verbosity(f"File handle is {str(ofh)}", 3)

        circs = []

        for fpath in self.filepaths:
            # Get file
            self.verbosity(f"File path is {fpath}", 2)
            ifh = open(fpath, "r")
            self.verbosity(f"File handle is {str(ifh)}", 3)

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
                        circ = Ast2Circ.from_qasm_str(
                            the_source_list, include_path=self.nuqasm2, no_unknown=True
                        )

                    except (Qasm_Exception, Ast2CircException) as err:
                        x = err.errpacket()  # pylint: disable-msg=invalid-name
                        raise QisJobRuntimeException(
                            f"Error in source {the_source_list} {err} {x}"
                        ) from err

                    self.verbosity(
                        f"\nUnrolled circuit's OPENQASM 2.0 source code\n{ circ.qasm()}",
                        3,
                    )

                else:
                    circ = QuantumCircuit.from_qasm_str(the_source)

            self.verbosity(circ.draw(), 2)

            if self.xpile:
                new_circ = transpile(
                    circ,
                    backend=self.backend,
                    optimization_level=self.optimization_level,
                )
                print(new_circ)
                if self.circuit_layout:
                    fig = plot_circuit_layout(new_circ, self.backend)
                    QisJob.save_fig(
                        fig, self.figure_basename, self.backend, "plot_circuit.png"
                    )
                if self.showsched:
                    self._pp.pprint(schedule(new_circ, self.backend))

            circs.append(circ)

        try:
            if self.noisy_sim:
                job_exp = self.basic_noise_sim(circ, self.backend)

            elif self.use_statevector_gpu:
                self.verbosity("Using gpu", 2)
                backend_options = {"method": "statevector_gpu"}
                job_exp = execute(
                    circs,
                    backend=self.backend,
                    optimization_level=self.optimization_level,
                    backend_options=backend_options,
                    shots=self.shots,
                    memory=self.memory,
                )
            else:
                job_exp = execute(
                    circs,
                    backend=self.backend,
                    optimization_level=self.optimization_level,
                    shots=self.shots,
                    memory=self.memory,
                )

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("Before run:")
                self._pp.pprint(a_job)

            if self.use_job_monitor:
                if self.job_monitor_filepath:
                    self.verbosity(
                        f"File for job monitor output is {self.job_monitor_filepath}",
                        1,
                    )
                    j_m_file = open(self.job_monitor_filepath, mode="w", buffering=1)
                    if self.job_monitor_line != "\r":  # line_discipline kwarg only
                        job_monitor(
                            job_exp,  # recently added to Qiskit
                            output=j_m_file,
                            line_discipline=self.job_monitor_line,
                        )
                    else:
                        job_monitor(job_exp, output=j_m_file)
                    j_m_file.close()
                else:
                    if self.job_monitor_line != "\r":  # line_discipline kwarg only
                        job_monitor(
                            job_exp,  # recently added to Qiskit
                            line_discipline=self.job_monitor_line,
                        )
                    else:
                        job_monitor(job_exp)

            result_exp = job_exp.result()
            self.result_exp_dict = result_exp.to_dict()

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(job_exp)
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

        except (IBMQJobFailureError, IBMJobFailureError) as err:
            raise QisJobRuntimeException(
                f"Job failure {err} {job_exp.error_message()}"
            ) from err

        if ofh is not sys.stdout:
            ofh.close()

    def get_statuses(self) -> list:
        """
        Return backend status tuple(s)

        Returns
        -------
        list
            Backend status tuple(s)

        """
        stat = []
        if self.backend:
            stat.append(self.backend.status().to_dict())
        else:
            for b_e in self.provider.backends():
                stat.append(b_e.status().to_dict())
        return stat

    def qasm_exp(
        self,
    ) -> list:  # pylint: disable-msg=too-many-locals, too-many-branches, too-many-statements, line-too-long
        """
        Given qasm source, run the job and return list of string csv and other selected output.

        Returns
        -------
        list
            The output list representing the result in csv form.
            It is also written to `ofh` if that handle is instanced.

        Raises
        ------
            QisJobRuntimeException
        """

        the_source = self.qasm_src
        self.verbosity("source:\n" + the_source, 1)

        circ = None

        if self.nuqasm2:
            try:
                circ = Ast2Circ.from_qasm_str(
                    the_source, include_path=self.nuqasm2, no_unknown=True
                )

            except (Qasm_Exception, Ast2CircException) as err:
                x = err.errpacket()  # pylint: disable-msg=invalid-name
                raise QisJobRuntimeException(
                    f"Source error {the_source} {err} {x}"
                ) from err

            self.verbosity(
                f"Unrolled circuit's OPENQASM 2.0 source code\n{circ.qasm()}", 3
            )

        else:
            circ = QuantumCircuit.from_qasm_str(the_source)

        self.verbosity(circ.draw(), 2)

        if self.xpile:
            new_circ = transpile(
                circ, backend=self.backend, optimization_level=self.optimization_level
            )
            print(new_circ)
            if self.circuit_layout:
                fig = plot_circuit_layout(new_circ, self.backend)
                QisJob.save_fig(
                    fig, self.figure_basename, self.backend, "plot_circuit.png"
                )

            if self.showsched:
                self._pp.pprint(schedule(new_circ, self.backend))

        try:
            if self.method:
                self.verbosity(f"Using gpu method {self.method}", 2)
                backend_options = {"method": self.method}
                job_exp = execute(
                    circ,
                    backend=self.backend,
                    optimization_level=self.optimization_level,
                    backend_options=backend_options,
                    shots=self.shots,
                    memory=self.memory,
                )
            else:
                job_exp = execute(
                    circ,
                    backend=self.backend,
                    optimization_level=self.optimization_level,
                    shots=self.shots,
                    memory=self.memory,
                )

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("Before run:")
                self._pp.pprint(a_job)

            if self.use_job_monitor:
                if self.job_monitor_filepath:
                    self.verbosity(
                        f"File for job monitor output is {self.job_monitor_filepath}",
                        1,
                    )
                    j_m_file = open(self.job_monitor_filepath, mode="w", buffering=1)
                    if self.job_monitor_line != "\r":  # line_discipline kwarg only
                        job_monitor(
                            job_exp,  # recently added to Qiskit
                            output=j_m_file,
                            line_discipline=self.job_monitor_line,
                        )
                    else:
                        job_monitor(job_exp, output=j_m_file)
                    j_m_file.close()
                else:
                    if self.job_monitor_line != "\r":  # line_discipline kwarg only
                        job_monitor(
                            job_exp,  # recently added to Qiskit
                            line_discipline=self.job_monitor_line,
                        )
                    else:
                        job_monitor(job_exp)

            result_exp = job_exp.result()
            self.result_exp_dict = result_exp.to_dict()

            if self.print_job:
                if self.provider_name != "QI":
                    if self.provider_name == "IBMQ":
                        a_job = self.ibmqjob_to_dict(job_exp)
                    else:
                        a_job = job_exp.to_dict()
                else:
                    a_job = job_exp
                print("After run:")
                self._pp.pprint(a_job)

            if self.use_statevector_gpu:
                try:
                    self.verbosity(
                        f"Method: {result_exp.data(circ).metadata.get('method')}",
                        2,
                    )
                except AttributeError as err:
                    print(f"AttributeError error: {err}")

            if self.show_result:
                self._pp.pprint(result_exp.to_dict())

            return self.formulate_result(result_exp, circ, None)

        except (IBMQJobFailureError, IBMJobFailureError) as err:
            raise QisJobRuntimeException(
                f"Job failure {err} {job_exp.error_message()}"
            ) from err

    @staticmethod
    def ibmqjob_to_dict(job: IBMQJob) -> dict:
        """
        Create a dict containing job factors for which there are methods.
        Acts as a `to_dict()`.

        Parameters
        ----------
        job : IBMQJob
            An instance of `qiskit.providers.ibmq.job.IBMQJob`

        Returns
        -------
        dict
            Return a dict containing IBMQ Provider Job info as if
            `qiskit.providers.ibmq.job.IBMQJob` had a `to_dict()` method.

            Actually, currently there is such a method, but it is deprecated
            and will be removed in the next release.

            The members should correspond to the methods documented in the
            [Qiskit IBM Quantum Provider documentation](https://qiskit.org/documentation/stubs/qiskit.providers.ibmq.job.IBMQJob.html#qiskit.providers.ibmq.job.IBMQJob) # pylint: disable=line-too-long

            Not all members are present on all platforms, so we try/except
            each one.

        """

        my_dict = {}
        # Return the backend where this job was executed.
        try:
            my_dict["backend"] = job.backend()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return whether the job has been cancelled.
        try:
            my_dict["cancelled"] = job.cancelled()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return job creation date, in local time.
        try:
            my_dict["creation_date"] = job.creation_date()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return whether the job has successfully run.
        try:
            my_dict["done"] = job.done()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Provide details about the reason of failure.
        try:
            my_dict["error_message"] = job.error_message()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return whether the job is in a final job state.
        try:
            my_dict["in_final_state"] = job.in_final_state()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the job ID assigned by the server.
        try:
            my_dict["job_id"] = job.job_id()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the name assigned to this job.
        try:
            my_dict["name"] = job.name()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the backend properties for this job.
        try:
            my_dict["properties"] = job.properties()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the Qobj for this job.
        try:
            my_dict["qobj"] = job.qobj()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return queue information for this job.
        try:
            my_dict["queue_info"] = job.queue_info()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the position of the job in the server queue.
        try:
            my_dict["queue_position"] = job.queue_position()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return whether the job is actively running.
        try:
            my_dict["result"] = job.result().to_dict()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return whether the job is actively running.
        try:
            my_dict["running"] = job.running()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the scheduling mode the job is in.
        try:
            my_dict["scheduling_mode"] = job.scheduling_mode()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the share level of the job.
        try:
            my_dict["share_level"] = job.share_level()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Query the server for the latest job status.
        try:
            my_dict["status"] = job.status()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the tags assigned to this job.
        try:
            my_dict["tags"] = job.tags()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        # Return the date and time information on each step of the job processing.
        try:
            my_dict["time_per_step"] = job.time_per_step()
        except Exception:  # pylint: disable-msg=broad-except
            pass
        return my_dict

    @staticmethod
    def basic_noise_sim(circuit: QuantumCircuit, model_backend: BackendV2) -> JobV1:
        """
        Execute a simulator job with a basic noise model from a known backend.

        Parameters
        ----------
        model_backend : BackendV2
            The BackendV2 instance whose noise model is to be used
        circuit : QuantumCircuit
            The QuantumCircuit instance to execute

        Returns
        -------
        JobV1
            The job which is executing the circuit

        """

        noise_model = NoiseModel.from_backend(model_backend)
        coupling_map = model_backend.configuration().coupling_map
        basis_gates = noise_model.basis_gates

        # Perform noisy simulation
        sim_backend = Aer.get_backend("qasm_simulator")
        job = execute(
            circuit,
            sim_backend,
            coupling_map=coupling_map,
            noise_model=noise_model,
            basis_gates=basis_gates,
        )
        return job


if __name__ == "__main__":

    EXPLANATION = """Qisjob loads from one or more OpenQASM source files or
    from a file containing a Qiskit QuantumCircuit definition in Python and runs as
    experiments with reporting in CSV form. Can graph results as histogram or
    state-city plot. Also can give info on backend properties, qiskit version,
    show circuit transpilation, etc. Can run as multiple jobs or all as one job.
    Exits 0 on success, 1 on argument error, 100 on runtime error, 200 on QiskitError.
    Copyright 2019 Jack Woehr jwoehr@softwoehr.com PO Box 51, Golden, CO 80402-0051.

    Apache License, Version 2.0 -- See LICENSE which you should have received with this code.

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    """
    PARSER = argparse.ArgumentParser(description=EXPLANATION)
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUPB = PARSER.add_mutually_exclusive_group()
    GROUPC = PARSER.add_mutually_exclusive_group()

    GROUP.add_argument(
        "-i",
        "--ibmq",
        action="store_true",
        help="Use best genuine IBMQ processor (default)",
    )
    GROUP.add_argument(
        "-s", "--sim", action="store_true", help="Use IBMQ qasm simulator"
    )
    GROUP.add_argument(
        "-a",
        "--aer",
        action="store_true",
        help="""Use QISKit Aer simulator.
                       Default is Aer statevector simulator.
                       Use -a --qasm-simulator to get Aer qasm simulator.
                       Use -a --unitary-simulator to get Aer unitary simulator.""",
    )
    GROUP.add_argument(
        "-b", "--backend", action="store", help="Use specified IBMQ backend"
    )
    GROUPB.add_argument(
        "--qasm_simulator",
        action="store_true",
        help="""With -a use qasm simulator
                        instead of statevector simulator""",
    )
    GROUPB.add_argument(
        "--unitary_simulator",
        action="store_true",
        help="""With -a use unitary simulator
                        instead of statevector simulator""",
    )
    GROUPC.add_argument(
        "--statevector_gpu",
        action="store_true",
        help="""With -a and --qasm_simulator
                        use gpu statevector simulator""",
    )
    GROUPC.add_argument(
        "--unitary_gpu",
        action="store_true",
        help="""With -a and --qasm_simulator
                        use gpu unitary simulator""",
    )
    GROUPC.add_argument(
        "--density_matrix_gpu",
        action="store_true",
        help="""With -a and --qasm_simulator
                        use gpu density matrix simulator""",
    )
    PARSER.add_argument(
        "--version", action="store_true", help="""Announce QisJob version"""
    )
    PARSER.add_argument(
        "--api_provider",
        action="store",
        help="""Backend remote api provider,
                        currently supported are [IBMQ | Forest | MQT | QI].
                        Default is IBMQ.""",
        default="IBMQ",
    )
    PARSER.add_argument(
        "--hub",
        action="store",
        default="ibm-q",
        help="Provider hub, default is 'ibm-q'",
    )
    PARSER.add_argument(
        "--group",
        action="store",
        default="open",
        help="Provider group, default is 'open'",
    )
    PARSER.add_argument(
        "--project",
        action="store",
        default="main",
        help="Provider project, default is 'main'",
    )
    PARSER.add_argument(
        "--providers",
        action="store_true",
        help="List hub/group/project providers for IBMQ",
    )
    PARSER.add_argument(
        "--noisy_sim",
        action="store_true",
        help="""Perform circuit(s) as Aer simulation using the
                        designated backend (see --backend) as the
                        model backend.""",
    )
    PARSER.add_argument(
        "--qvm",
        action="store_true",
        help="""Use Forest local qvm simulator described by
                        -b backend, generally one of qasm_simulator or
                        statevector_simulator. Use --qvm_as to instruct the
                        simulator to emulate a specific Rigetti QPU""",
    )
    PARSER.add_argument(
        "--qvm_as",
        action="store_true",
        help="""Use Forest local qvm simulator to emulate the
                        specific Rigetti QPU described by -b backend. Use --qvm
                        to run the Forest local qvm simulator described by
                        -b backend.""",
    )
    PARSER.add_argument(
        "--backends",
        action="store_true",
        help="Print list of backends to stdout and exit 0",
    )
    PARSER.add_argument(
        "-1", "--one_job", action="store_true", help="Run all experiments as one job"
    )
    PARSER.add_argument(
        "-d",
        "--datetime",
        type=str,
        action="store",
        help="""Datetime 'year,month,day[,hour,min,sec]'
                        for -p,--properties""",
    )
    PARSER.add_argument(
        "-g",
        "--configuration",
        action="store_true",
        help="""Print configuration for backend specified by -b
                        to stdout and exit 0""",
    )
    PARSER.add_argument(
        "-j", "--job", action="store_true", help="Print your job's dictionary"
    )
    PARSER.add_argument(
        "--jobs",
        type=int,
        action="store",
        help="""Print JOBS number of jobs and status for -b
                        backend and exit 0""",
    )
    PARSER.add_argument(
        "--job_id",
        type=str,
        action="store",
        help="Print job number JOB_ID for -b backend and exit 0",
    )
    PARSER.add_argument(
        "--job_result",
        type=str,
        action="store",
        help=""""Print result of job number JOB_RESULT for
                        -b backend and exit 0""",
    )
    PARSER.add_argument(
        "-m",
        "--memory",
        action="store_true",
        help="Print individual results of multishot experiment",
    )
    PARSER.add_argument(
        "-n",
        "--nuqasm2",
        action="store",
        help=""""Use nuqasm2 to translate OPENQASM2 source,
                        providing include path for any include directives""",
    )
    PARSER.add_argument(
        "-o",
        "--outfile",
        action="store",
        help="Write appending CSV to outfile, default is stdout",
    )
    PARSER.add_argument(
        "-p",
        "--properties",
        action="store_true",
        help="""Print properties for backend specified by -b to
                        stdout and exit 0""",
    )
    PARSER.add_argument(
        "-q",
        "--qubits",
        type=int,
        action="store",
        default=5,
        help="Number of qubits for the experiment, default is 5",
    )
    PARSER.add_argument(
        "--qiskit_version", action="store_true", help="Print Qiskit version and exit 0"
    )
    PARSER.add_argument("-r", "--result", action="store_true", help="Print job result")
    PARSER.add_argument(
        "-t",
        "--shots",
        type=int,
        action="store",
        default=1024,
        help="Number of shots for the experiment, default 1024, max 8192",
    )
    PARSER.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="""Increase runtime verbosity each -v up to 3. If
                        precisely 4, prettyprint QisJob's data dictionary and
                        return (good for debugging script arguments)""",
    )
    PARSER.add_argument(
        "-x",
        "--transpile",
        action="store_true",
        help="""Print circuit transpiled for chosen backend to stdout
                        before running job""",
    )
    PARSER.add_argument(
        "--showsched",
        action="store_true",
        help="""In conjuction with -x, show schedule for transpiled
                        circuit for chosen backend to stdout before running job""",
    )
    PARSER.add_argument(
        "--circuit_layout",
        action="store_true",
        help="""With -x, write image file of circuit layout
                        after transpile (see --figure_basename)""",
    )
    PARSER.add_argument(
        "--optimization_level",
        type=int,
        action="store",
        default=1,
        help="""Set optimization level for
                        transpilation before run, valid values 0-3,
                        default is 1""",
    )
    PARSER.add_argument(
        "--histogram",
        action="store_true",
        help="""Write image file of histogram of experiment
                        results (see --figure_basename)""",
    )
    PARSER.add_argument(
        "--plot_state_city",
        type=int,
        action="store",
        help="""Write image file of state city plot of statevector to
                        PLOT_STATE_CITY decimal points (see --figure_basename)""",
    )
    PARSER.add_argument(
        "--figure_basename",
        type=str,
        action="store",
        default="figout",
        help="""basename including path (if any) for figure output,
                        default='figout', backend name, figure type, and timestamp
                        will be appended""",
    )
    PARSER.add_argument(
        "--qasm",
        action="store_true",
        help="Print qasm file to stdout before running job",
    )
    PARSER.add_argument(
        "--qc",
        action="store",
        help="Indicate variable name of Python-coded QuantumCircuit",
    )
    PARSER.add_argument(
        "--status",
        action="store_true",
        help="""Print status of chosen --backend to stdout
                        (default all backends)
                        of --api_provider (default IBMQ)
                        and exit 0""",
    )
    PARSER.add_argument("--token", action="store", help="Use this token")
    PARSER.add_argument("--url", action="store", help="Use this url")
    PARSER.add_argument(
        "--use_job_monitor",
        action="store_true",
        help="""Display job monitor instead of just waiting for
                        job result""",
    )
    PARSER.add_argument(
        "--job_monitor_line",
        action="store",
        default="0x0d",
        help="""Comma-separated list of hex values for
                        character(s) to emit at the head of each line of job
                        monitor output, default is '0x0d'""",
    )
    PARSER.add_argument(
        "filepath",
        nargs="*",
        help="Filepath(s) to 0 or more .qasm files, default is stdin",
    )
    PARSER.add_argument(
        "--job_monitor_filepath",
        action="store",
        default=None,
        help="""Filepath for Job Monitor output if Job Monitor
                        requested by --use_job_monitor, default is sys.stdout""",
    )
    PARSER.add_argument(
        "-w",
        "--warnings",
        action="store_true",
        help="Don't print warnings on missing optional modules",
    )

    ARGS = PARSER.parse_args()

    if ARGS.warnings:
        # import warnings # already imported
        warnings.filterwarnings("ignore")

    AER = ARGS.aer
    API_PROVIDER = ARGS.api_provider.upper()
    HUB = ARGS.hub
    GROUP = ARGS.group
    PROJECT = ARGS.project
    PROVIDERS = ARGS.providers
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
    JOB_MONITOR_LINE = "".join(
        chr(int(lstr, 16)) for lstr in ARGS.job_monitor_line.split(",")
    )
    JOB_RESULT = ARGS.job_result
    JOBS = ARGS.jobs
    MEMORY = ARGS.memory
    NOISY_SIM = ARGS.noisy_sim
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

    QJ = QisJob(
        filepaths=FILEPATH,
        provider_name=API_PROVIDER,
        hub=HUB,
        group=GROUP,
        project=PROJECT,
        providers=PROVIDERS,
        backend_name=BACKEND_NAME,
        token=TOKEN,
        url=URL,
        nuqasm2=NUQASM2,
        num_qubits=QUBITS,
        shots=SHOTS,
        outfile_path=OUTFILE,
        one_job=ONE_JOB,
        qasm=QASM,
        use_aer=AER,
        use_qasm_simulator=QASM_SIMULATOR,
        use_unitary_simulator=UNITARY_SIMULATOR,
        use_statevector_gpu=STATEVECTOR_GPU,
        use_unitary_gpu=UNITARY_GPU,
        use_density_matrix_gpu=DENSITY_MATRIX_GPU,
        use_sim=SIM,
        qvm=QVM,
        qvm_as=QVM_AS,
        qc_name=QC_NAME,
        xpile=TRANSPILE,
        showsched=SHOWSCHED,
        circuit_layout=CIRCUIT_LAYOUT,
        optimization_level=OPTIMIZATION_LEVEL,
        print_job=JOB,
        memory=MEMORY,
        show_result=RESULT,
        jobs_status=JOBS,
        job_id=JOB_ID,
        job_result=JOB_RESULT,
        show_backends=BACKENDS,
        show_configuration=CONFIGURATION,
        show_properties=PROPERTIES,
        show_statuses=STATUS,
        date_time=DATETIME,
        print_histogram=HISTOGRAM,
        print_state_city=PLOT_STATE_CITY,
        figure_basename=FIGURE_BASENAME,
        show_q_version=QISKIT_VERSION,
        verbose=VERBOSE,
        show_qisjob_version=QISJOB_VERSION,
        use_job_monitor=USE_JM,
        job_monitor_filepath=JOB_MONITOR_FILEPATH,
        job_monitor_line=JOB_MONITOR_LINE,
        noisy_sim=NOISY_SIM,
    )

    EXITVAL = 0
    try:
        QJ.do_it()
    except QisJobException as ex:
        print(type(ex).__name__ + " : " + ex.message, file=sys.stderr)
        EXITVAL = ex.retval
    except QiskitError as qex:
        print(qex)
        EXITVAL = 200
    sys.exit(EXITVAL)
